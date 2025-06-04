# ARCar_Showroom/core/app_manager.py
import cv2
import os
import numpy as np
import json
import time
from PIL import Image # Asegúrate de tener Pillow: pip install Pillow

from core.config import (
    STATE_WELCOME, # Añadir nuevo estado
    STATE_LOGIN, STATE_REGISTER_PROMPT_ID, STATE_REGISTER_CAPTURE, STATE_REGISTER_TRAIN,
    STATE_MAIN_MENU_AR, STATE_AR_MODEL_VIEWER, STATE_AR_MENU_SELECTION, # ← Agregado STATE_AR_MENU_SELECTION
    NUM_IMAGES_FOR_REGISTRATION, WINDOW_NAME,
    USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT,
    USER_ID_MAP_PATH_REL_TO_PROJECT_ROOT,
    LBPH_MODELS_DIR_REL_TO_PROJECT_ROOT,
    AVAILABLE_CARS, MODEL_MARKER_ID
)
from vision_processing import facial_auth
from vision_processing import marker_detection  # Importar el nuevo módulo
from ar_rendering import scene_renderer # Importar el renderizador de escena
from ar_rendering.ar_menu import ARMenu
from ar_rendering.scene_renderer import PyrenderModelViewer
from audio_processing import get_voice_controller

# Umbral de confianza para LBPH. Valores MÁS BAJOS son MEJOR confianza.
# Un valor de 0 es una coincidencia perfecta.
# Tendrás que experimentar con este valor. Empecemos con algo como 70.
# Si tu PDF dice 85% de confianza, para LBPH podría ser 100 - 85 = 15, pero
# la escala de confianza de LBPH no es un porcentaje directo.
# Un valor entre 40-70 suele ser un buen punto de partida para LBPH.
LBPH_CONFIDENCE_THRESHOLD = 50 # Ajusta esto según tus pruebas

class AppManager:
    def __init__(self, project_root_path):
        self.project_root_path = project_root_path
        self.current_state = STATE_WELCOME # CAMBIAR ESTADO INICIAL
        self.user_id_for_registration = None
        self.captured_images_count = 0
        self.logged_in_user_str = None # Nueva variable para usuario logueado
        self.texture_path_test_rel = "assets/ui_elements/test_texture.png" # Ruta relativa
        self.camera_initialized_for_gl = False
        
        self.recognizer = cv2.face.LBPHFaceRecognizer_create() # Instancia principal
        self.loaded_recognizers = {} # Para guardar modelos cargados: {"user_id_str": recognizer_instance}
        self.user_id_map_path = os.path.join(self.project_root_path, USER_ID_MAP_PATH_REL_TO_PROJECT_ROOT)
        self.user_id_map = self._load_user_id_map() # {"user_id_str": numeric_id}
        self.numeric_id_to_user_str_map = {v: k for k, v in self.user_id_map.items()} # Mapa inverso

        self.next_user_numeric_id = max(self.user_id_map.values()) + 1 if self.user_id_map else 0

        self.lbph_models_dir = os.path.join(self.project_root_path, LBPH_MODELS_DIR_REL_TO_PROJECT_ROOT)
        os.makedirs(self.lbph_models_dir, exist_ok=True)

        # 🔧 CONFIGURACIÓN AUTOMÁTICA SEGÚN TIPO DE CÁMARA
        camera_config = self._detect_camera_config()
        
        # Configurar matriz de cámara con parámetros específicos
        frame_w_example = camera_config['width']
        frame_h_example = camera_config['height']
        focal_multiplier = camera_config['focal_multiplier']
        
        # Parámetros ajustados según el tipo de cámara
        fx_est = frame_w_example * focal_multiplier
        fy_est = frame_w_example * focal_multiplier
        cx_est = frame_w_example / 2
        cy_est = frame_h_example / 2

        self.camera_matrix_cv = np.array([
            [fx_est, 0, cx_est],
            [0, fy_est, cy_est],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Coeficientes de distorsión (asumir cero para simplificar)
        self.dist_coeffs_cv = np.zeros((4,1), dtype=np.float32)

        # 🔧 INICIALIZAR UMBRAL DE CONFIANZA SEGÚN CÁMARA
        self.lbph_confidence_threshold = camera_config['confidence_threshold']
        
        print(f"DEBUG_CAMERA: Tipo: {camera_config['type']}")
        print(f"DEBUG_CAMERA: Resolución: {frame_w_example}x{frame_h_example}")
        print(f"DEBUG_CAMERA: Focal multiplier: {focal_multiplier}")
        print(f"DEBUG_CAMERA: Focal length: fx={fx_est:.1f}, fy={fy_est:.1f}")
        print(f"DEBUG_CAMERA: Centro óptico: cx={cx_est:.1f}, cy={cy_est:.1f}")
        print(f"DEBUG_CAMERA: Umbral de confianza: {self.lbph_confidence_threshold}")
        
        if not facial_auth.load_cascade(self.project_root_path):
            print("ALERTA CRÍTICA en AppManager: Haar Cascade no pudo ser cargado.")
        
        # Inicializar el detector ArUco
        if not marker_detection.initialize_aruco_detector():
            print("ALERTA CRÍTICA en AppManager: Detector ArUco no pudo ser inicializado.")
    
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        self._load_all_trained_models() # Cargar modelos al inicio

        # Importar la configuración
        from core.config import AVAILABLE_CARS
        
        # Nuevas variables para el sistema AR
        self.ar_menu = ARMenu()
        self.ar_menu.menu_items = AVAILABLE_CARS
        
        # 🔥 DEBUG CRÍTICO: Verificar que se cargan ambos coches
        print(f"DEBUG_APP: Menu inicializado con {len(AVAILABLE_CARS)} coches:")
        for i, car in enumerate(AVAILABLE_CARS):
            print(f"DEBUG_APP: {i+1}. {car['name']} - {car['model_path']} (escala: {car.get('scale', 0.05)})")
        
        self.model_viewer = PyrenderModelViewer()
        self.selected_car = None
        self.model_marker_id = MODEL_MARKER_ID

        # 🔧 AÑADIR CONTROLADOR DE VOZ
        self.voice_controller = get_voice_controller()
        print("DEBUG_APP: Controlador de voz inicializado")
        
        # 🔧 AÑADIR DEBUG DETALLADO
        print(f"DEBUG_VOICE: ¿Controlador creado? {self.voice_controller is not None}")
        print(f"DEBUG_VOICE: ¿Micrófono disponible? {self.voice_controller.microphone is not None}")
        print(f"DEBUG_VOICE: Estado inicial: {self.voice_controller.get_status_text()}")

        print(f"AppManager inicializado. Estado: {self.current_state}")

    def _load_user_id_map(self):
        try:
            if os.path.exists(self.user_id_map_path):
                with open(self.user_id_map_path, 'r') as f:
                    data = json.load(f)
                    # Asegurar que los valores son enteros si se guardaron como string
                    return {k: int(v) for k,v in data.items()} 
            return {}
        except Exception as e:
            print(f"Error cargando user_id_map.json: {e}. Se usará un mapa vacío.")
            return {}

    def _save_user_id_map(self):
        try:
            os.makedirs(os.path.dirname(self.user_id_map_path), exist_ok=True)
            with open(self.user_id_map_path, 'w') as f:
                json.dump(self.user_id_map, f, indent=4)
            print(f"Mapa de IDs de usuario guardado en {self.user_id_map_path}")
        except Exception as e:
            print(f"Error guardando user_id_map.json: {e}")
            
    def _load_all_trained_models(self):
        """Carga todos los modelos .yml encontrados en el directorio de modelos."""
        print("Cargando modelos LBPH entrenados...")
        self.loaded_recognizers = {} # Limpiar modelos previos
        if not os.path.exists(self.lbph_models_dir):
            print(f"Directorio de modelos no encontrado: {self.lbph_models_dir}")
            return

        for model_file in os.listdir(self.lbph_models_dir):
            if model_file.endswith(".yml"):
                user_id_str = model_file.replace(".yml", "")
                model_path = os.path.join(self.lbph_models_dir, model_file)
                try:
                    recognizer_instance = cv2.face.LBPHFaceRecognizer_create()
                    recognizer_instance.read(model_path) # Cargar el modelo entrenado
                    self.loaded_recognizers[user_id_str] = recognizer_instance
                    print(f"Modelo cargado para '{user_id_str}' desde {model_path}")
                except Exception as e:
                    print(f"Error al cargar el modelo para '{user_id_str}' desde {model_path}: {e}")
        
        if not self.loaded_recognizers:
            print("No se cargaron modelos LBPH entrenados.")
        else:
            # Actualizar el mapa inverso en caso de que el user_id_map se haya modificado externamente
            self.numeric_id_to_user_str_map = {v: k for k, v in self.user_id_map.items()}

    def process_frame(self, frame):
        """Procesar frame según el estado actual con control de voz"""
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 🔧 ELIMINAR MENSAJE CONFUSO Y SIMPLIFICAR
        if not self.camera_initialized_for_gl:
            # Solo marcar como inicializado, sin mensaje confuso
            self.camera_initialized_for_gl = True

        recognition_text_color = (0, 0, 255)  # Default rojo para desconocido

        if self.current_state == STATE_WELCOME:
            # Limpiar cualquier usuario logueado previamente si volvemos a este estado
            self.logged_in_user_str = None

            cv2.putText(display_frame, "Bienvenido a ARCar Showroom", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 0), 2)
            cv2.putText(display_frame, "Presiona 'L' para Iniciar Sesion", (50, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, "Presiona 'R' para Registrar Nuevo Usuario", (50, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(display_frame, "Presiona 'Q' para Salir", (50, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        elif self.current_state == STATE_LOGIN:
            # Detectar caras primero
            frame_with_rects, detected_faces_coords = facial_auth.detect_faces(display_frame)
            display_frame = frame_with_rects # Usar el frame con rectángulos de detección

            # Si no hay un usuario pre-reconocido, intentamos reconocer
            if not self.logged_in_user_str:
                if len(detected_faces_coords) > 0 and self.loaded_recognizers:
                    for (x, y, w, h) in detected_faces_coords:
                        face_roi = display_frame[y:y+h, x:x+w]
                        gray_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                        
                        best_match_user_id_str = None
                        lowest_confidence = float('inf')

                        for user_id_str, recognizer_inst in self.loaded_recognizers.items():
                            try:
                                _, confidence = recognizer_inst.predict(gray_face_roi)
                                if confidence < lowest_confidence:
                                    lowest_confidence = confidence
                                    best_match_user_id_str = user_id_str
                            except cv2.error as e:
                                continue
                        
                        # Después de intentar encontrar el mejor match con todos los reconocedores
                        if best_match_user_id_str:  # Si hubo algún intento de match
                            print(f"DEBUG: Intento de match: {best_match_user_id_str}, Conf Raw: {lowest_confidence:.2f}, Umbral: {LBPH_CONFIDENCE_THRESHOLD}")
                        
                        # Si encontramos un match con suficiente confianza
                        if best_match_user_id_str and lowest_confidence < self.lbph_confidence_threshold:
                            self.logged_in_user_str = best_match_user_id_str  # Guardar para confirmación
                            recognition_text_color = (0, 255, 0)  # Verde para reconocido
                            
                            # Dibujar nombre y confianza sobre el rectángulo de la cara
                            text_to_display = f"{self.logged_in_user_str} ({lowest_confidence:.2f})"
                            cv2.putText(display_frame, text_to_display, (x, y-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, recognition_text_color, 2)
                            
                            print(f"Usuario reconocido: {self.logged_in_user_str} con confianza: {lowest_confidence:.2f}")
                            print("Esperando confirmación para iniciar sesión.")
                            break  # Salir del bucle de caras
                        else:
                            # No se reconoció con suficiente confianza
                            if best_match_user_id_str:
                                text_to_display = f"{best_match_user_id_str}? ({lowest_confidence:.2f})"
                            else:
                                text_to_display = "Desconocido"
                            cv2.putText(display_frame, text_to_display, (x, y-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)

            # Textos generales del estado LOGIN
            cv2.putText(display_frame, "Estado: LOGIN FACIAL", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Si hay un usuario pre-reconocido
            if self.logged_in_user_str:
                cv2.putText(display_frame, f"Bienvenido {self.logged_in_user_str}!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, "Presiona ENTER para continuar", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
                cv2.putText(display_frame, "Presiona 'B' para Volver al Menu Inicial", (10, 120), # Opción para volver
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
                
                # Mensaje grande centrado
                text_size = cv2.getTextSize(f"Bienvenido {self.logged_in_user_str}! Presiona ENTER", 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                text_x = (display_frame.shape[1] - text_size[0]) // 2
                text_y = display_frame.shape[0] // 2
                cv2.putText(display_frame, f"Bienvenido {self.logged_in_user_str}! Presiona ENTER", 
                            (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "Coloca tu rostro para identificarte...", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 0), 2)
                cv2.putText(display_frame, "Presiona 'B' para Volver al Menu Inicial", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)

        elif self.current_state == STATE_REGISTER_CAPTURE:
            display_frame, faces = facial_auth.detect_faces(display_frame)
            info_text = f"REGISTRO: {self.user_id_for_registration}"
            cv2.putText(display_frame, info_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Capturadas: {self.captured_images_count}/{NUM_IMAGES_FOR_REGISTRATION}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
            if len(faces) == 1:
                cv2.putText(display_frame, "Mueve la cabeza. Presiona 'c' para Capturar", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            elif len(faces) == 0:
                cv2.putText(display_frame, "Muestra tu rostro a la camara", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 1)
            else:
                cv2.putText(display_frame, "Solo un rostro permitido para registro", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(display_frame, "Presiona 'ESC' para Cancelar Registro", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)

        elif self.current_state == STATE_REGISTER_TRAIN:
            cv2.putText(display_frame, f"Entrenando modelo para: {self.user_id_for_registration}...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(display_frame, "Esto puede tardar unos segundos.", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        elif self.current_state == STATE_MAIN_MENU_AR:
            # 🔧 MANEJAR COMANDOS DE VOZ PRIMERO
            voice_command = self.voice_controller.get_voice_command()
            if voice_command:
                self._handle_voice_command(voice_command)
            
            # Detectar marcador de menú (ID 23)
            corners, ids, frame_with_aruco_markers, rvecs, tvecs = \
                marker_detection.detect_and_estimate_pose(
                    display_frame, 
                    self.camera_matrix_cv,
                    self.dist_coeffs_cv,
                    scene_renderer.MARKER_SIZE_METERS
                )
            
            if ids is not None and 23 in ids:
                marker_index = list(ids.flatten()).index(23)
                
                # Si NO hay coche seleccionado, mostrar menú
                if not self.selected_car:
                    display_frame = self.ar_menu.draw_menu_overlay(frame_with_aruco_markers, corners)
                    cv2.putText(display_frame, "1-2: Seleccionar | ESPACIO: Ver modelo 3D", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Si YA hay coche seleccionado, mostrar modelo 3D REAL
                else:
                    print(f"DEBUG_RENDER: Renderizando {self.selected_car['name']} REAL...")
                    
                    try:
                        display_frame = self.model_viewer.render_model_on_marker(
                            display_frame,
                            rvecs[marker_index], 
                            tvecs[marker_index], 
                            self.camera_matrix_cv, 
                            self.dist_coeffs_cv
                        )
                        
                        # 🔧 INFORMACIÓN MÁS LIMPIA Y COMPACTA
                        # Solo mostrar nombre del coche
                        cv2.putText(display_frame, f"{self.selected_car['name']}", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        # Instrucciones simplificadas
                        cv2.putText(display_frame, "M: Menu | Q: Logout", (10, 130), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                       
                    except Exception as e:
                        print(f"ERROR_PYRENDER: {e}")
                        display_frame = frame_with_aruco_markers
                        cv2.putText(display_frame, f"Error: {self.selected_car['name']}", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            else:
                # No hay marcador visible
                display_frame = frame_with_aruco_markers
                
                if self.selected_car:
                    # Hay coche seleccionado pero no se ve el marcador
                    cv2.putText(display_frame, f"Coche seleccionado: {self.selected_car['name']}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Muestra marcador ID 23 para ver modelo 3D", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    cv2.putText(display_frame, "Presiona 'M' para volver al menu sin marcador", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 150, 0), 1)
                else:
                    # No hay coche seleccionado
                    cv2.putText(display_frame, "Muestra marcador ID 23 para abrir menu", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,150,0), 2)
                    cv2.putText(display_frame, "Selecciona Ferrari F40 o Porsche 911", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # 🔧 TÍTULO DINÁMICO LIMPIO (SIN SÍMBOLOS EXTRAÑOS)
            if self.selected_car:
                titulo = f"Estado: {self.selected_car['name'].upper()} SHOWROOM"
                color_titulo = (0, 255, 255)  # Cyan para modelo seleccionado
            else:
                titulo = "Estado: CAR SHOWROOM - Selecciona tu coche"
                color_titulo = (255, 0, 0)  # Rojo para menú

            cv2.putText(display_frame, titulo, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_titulo, 2)  # ← Tamaño reducido de 0.8 a 0.7

            # Mensaje de bienvenida más pequeño
            welcome_message = f"Bienvenido, {self.logged_in_user_str}!"
            cv2.putText(display_frame, welcome_message, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)  # ← Tamaño reducido de 0.7 a 0.6
        
        else:  # Estado desconocido
            cv2.putText(display_frame, f"Estado: {self.current_state}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
        
        # 🔧 MOSTRAR ESTADO DEL CONTROL DE VOZ
        voice_status = self.voice_controller.get_status_text()
        cv2.putText(display_frame, voice_status, (display_frame.shape[1] - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Mostrar instrucciones de voz
        if not self.selected_car:  # Solo en el menú
            instructions = self.voice_controller.get_instructions_text()
            cv2.putText(display_frame, instructions, (10, display_frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # 🔧 MOSTRAR FEEDBACK DE COMANDO DE VOZ
        if hasattr(self, '_voice_feedback_message') and hasattr(self, '_voice_feedback_timer'):
            # Mostrar mensaje por 3 segundos
            if time.time() - self._voice_feedback_timer < 3.0:
                cv2.putText(display_frame, self._voice_feedback_message, (10, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Limpiar mensaje después de 3 segundos
                delattr(self, '_voice_feedback_message')
                delattr(self, '_voice_feedback_timer')
        
        return display_frame

    def _handle_voice_command(self, command):
        """Manejar comandos de voz"""
        print(f"DEBUG_VOICE: 🎙️ Procesando comando: {command}")
        
        if command['type'] == 'car_selection':
            car_name = command['car']
            
            # Buscar el coche correspondiente
            target_car = None
            
            if car_name == 'ferrari':
                for car in self.ar_menu.menu_items:
                    if 'ferrari' in car['name'].lower():
                        target_car = car
                        break
                        
            elif car_name == 'porsche':
                for car in self.ar_menu.menu_items:
                    if 'porsche' in car['name'].lower():
                        target_car = car
                        break
            
            if target_car:
                print(f"DEBUG_VOICE: 🚗 Cargando {target_car['name']} por comando de voz")
                
                # Seleccionar el coche automáticamente
                self.selected_car = target_car
                
                # Cargar el modelo inmediatamente
                success = self.model_viewer.load_car_model(target_car)
                if success:
                    print(f"DEBUG_VOICE: ✅ {target_car['name']} cargado por voz")
                    
                    # Mostrar mensaje visual
                    self._voice_feedback_message = f"🎙️ {target_car['name']} seleccionado por voz"
                    self._voice_feedback_timer = time.time()
                    
                else:
                    print(f"DEBUG_VOICE: ❌ Error cargando {target_car['name']} por voz")
                    self.selected_car = None
            else:
                print(f"DEBUG_VOICE: ❌ No se encontró coche para '{car_name}'")
        
        elif command['type'] == 'navigation':
            action = command['action']
            
            if action == 'menu':
                if self.selected_car:
                    print(f"DEBUG_VOICE: 🔙 Volviendo al menú desde {self.selected_car['name']} por voz")
                    self.selected_car = None
                    # Limpiar modelo cargado
                    self.model_viewer.cleanup()
                    self.model_viewer.current_model = None
                    
                    # Feedback visual
                    self._voice_feedback_message = "🎙️ Vuelto al menú por voz"
                    self._voice_feedback_timer = time.time()
                else:
                    print("DEBUG_VOICE: Ya estás en el menú principal")
            
            elif action == 'logout':
                print(f"DEBUG_VOICE: 🚪 Cerrando sesión por comando de voz")
                self.logged_in_user_str = None
                self.selected_car = None
                # Limpiar modelo
                self.model_viewer.cleanup()
                self.model_viewer.current_model = None
                self.current_state = STATE_WELCOME
                
                # Feedback visual temporal
                self._voice_feedback_message = "🎙️ Sesión cerrada por voz"
                self._voice_feedback_timer = time.time()

    def handle_input(self, key, current_frame):
        """Manejar entrada con control de voz activado/desactivado"""
        
        if self.current_state == STATE_WELCOME:
            if key == ord('l'): # 'L' para Login
                print("Transicionando a STATE_LOGIN")
                self.logged_in_user_str = None # Asegurar que empezamos el login limpios
                self.current_state = STATE_LOGIN
            elif key == ord('r'): # 'R' para Registrar
                print("Transicionando a STATE_REGISTER_PROMPT_ID")
                self.logged_in_user_str = None 
                self.current_state = STATE_REGISTER_PROMPT_ID
            # La 'Q' para salir se maneja en main.py

        elif self.current_state == STATE_LOGIN:
            if key == ord('r'): # Si alguien está en Login y quiere registrarse (aunque ya tenemos opción en WELCOME)
                print("Transicionando a STATE_REGISTER_PROMPT_ID desde LOGIN")
                self.logged_in_user_str = None 
                self.current_state = STATE_REGISTER_PROMPT_ID
            elif self.logged_in_user_str and key == 13: # Enter para confirmar login
                print(f"Login confirmado para {self.logged_in_user_str}. Transicionando a {STATE_MAIN_MENU_AR}")
                self.current_state = STATE_MAIN_MENU_AR
            elif key == ord('b'): # 'B' para Volver al menú de bienvenida
                print("Volviendo al menú de bienvenida desde LOGIN.")
                self.logged_in_user_str = None
                self.current_state = STATE_WELCOME

        elif self.current_state == STATE_REGISTER_CAPTURE:
            if key == ord('c'):
                self._capture_image_for_registration(current_frame) 
            elif key == 27: # Tecla ESC
                print("Registro cancelado. Volviendo al menú de bienvenida.") # Cambiado para ir a WELCOME
                self._reset_registration_vars()
                self.logged_in_user_str = None
                self.current_state = STATE_WELCOME # Volver a WELCOME en lugar de LOGIN directo
        
        elif self.current_state == STATE_MAIN_MENU_AR:
            # Obtener ids de marcadores antes de usarlos
            corners, ids, frame_with_aruco_markers, rvecs, tvecs = marker_detection.detect_and_estimate_pose(
                current_frame,
                self.camera_matrix_cv,
                self.dist_coeffs_cv,
                scene_renderer.MARKER_SIZE_METERS
            )

            # 🔧 MANEJAR TECLA 'M' PARA VOLVER AL MENÚ (SIN NECESIDAD DE MARCADOR)
            if key == ord('m') or key == ord('M'):
                if self.selected_car:
                    print(f"Volviendo al menú desde {self.selected_car['name']}")
                    self.selected_car = None
                    # Limpiar modelo cargado
                    self.model_viewer.cleanup()
                    self.model_viewer.current_model = None
                    print("Modelo limpiado. De vuelta al menú principal.")
                else:
                    print("Ya estás en el menú principal")
                return  # ← IMPORTANTE: return para no procesar más
            
            # 🔧 MANEJAR TECLA 'Q' PARA LOGOUT (SIN NECESIDAD DE MARCADOR)
            elif key == ord('q') or key == ord('Q'):
                print(f"Cerrando sesión de {self.logged_in_user_str}. Volviendo al menú de bienvenida.")
                self.logged_in_user_str = None
                self.selected_car = None
                # Limpiar modelo
                self.model_viewer.cleanup()
                self.model_viewer.current_model = None
                self.current_state = STATE_WELCOME
                return  # ← IMPORTANTE: return para no procesar más
            
            # 🔧 AÑADIR TECLA 'V' PARA ACTIVAR/DESACTIVAR VOZ
            elif key == ord('v') or key == ord('V'):
                if self.voice_controller.is_listening():
                    self.voice_controller.stop_listening()
                    print("DEBUG_VOICE: 🔇 Control de voz DESACTIVADO")
                else:
                    success = self.voice_controller.start_listening()
                    if success:
                        print("DEBUG_VOICE: 🎤 Control de voz ACTIVADO")
                        print("DEBUG_VOICE: 🗣️ Di 'Ferrari', 'Porsche', 'Menú' o 'Salir'")
                    else:
                        print("DEBUG_VOICE: ❌ No se pudo activar control de voz")
                return  # ← IMPORTANTE: return para no procesar más
            
            # Si hay marcador ID 23 visible, permitir selección
            if ids is not None and 23 in ids:
                selected_car = self.ar_menu.handle_selection(key)
                if selected_car:
                    # 🔧 MANEJAR OPCIÓN VOLVER
                    if selected_car == "VOLVER":
                        print("Volviendo al LOGIN desde el menú")
                        self.logged_in_user_str = None
                        self.selected_car = None
                        # Limpiar modelo
                        self.model_viewer.cleanup()
                        self.model_viewer.current_model = None
                        self.current_state = STATE_LOGIN
                        return
                    
                    # Coche seleccionado normal
                    print(f"DEBUG_APP: 🏎️ === COCHE SELECCIONADO ===")
                    print(f"DEBUG_APP: Nombre: {selected_car['name']}")
                    print(f"DEBUG_APP: Ruta: {selected_car['model_path']}")
                    
                    self.selected_car = selected_car
                    
                    # 🔧 CARGAR EL MODELO INMEDIATAMENTE
                    print(f"DEBUG_APP: 🚗 Cargando modelo {selected_car['name']}...")
                    success = self.model_viewer.load_car_model(selected_car)
                    if success:
                        print(f"DEBUG_APP: ✅ Modelo {selected_car['name']} cargado exitosamente")
                    else:
                        print(f"DEBUG_APP: ❌ Error cargando modelo {selected_car['name']}")
                        self.selected_car = None  # Limpiar selección si falla

    # 🔧 AÑADIR ESTOS MÉTODOS AL FINAL DE LA CLASE:
    def get_current_state(self):
        """Devuelve el estado actual de la aplicación"""
        return self.current_state

    def set_current_state(self, new_state):
        """Cambia el estado actual de la aplicación"""
        print(f"DEBUG_APP: Cambiando estado de {self.current_state} a {new_state}")
        self.current_state = new_state

    def cleanup(self):
        """Limpiar recursos al cerrar la aplicación"""
        if hasattr(self, 'model_viewer') and self.model_viewer:
            self.model_viewer.cleanup()
        # 🔧 LIMPIAR CONTROL DE VOZ
        if hasattr(self, 'voice_controller'):
            self.voice_controller.cleanup()
        
        # También limpiar instancia global
        from audio_processing import cleanup_voice_controller
        cleanup_voice_controller()
        
        print("AppManager: Recursos limpiados incluyendo control de voz.")

    # AÑADIR debug en load_car_model() - Verificar carga exitosa:

    def load_car_model(self, car_dict):
        import os
        from trimesh.transformations import rotation_matrix, translation_matrix

        # 🔥 DEBUG CRÍTICO: Verificar qué coche se está cargando
        print(f"DEBUG_MODEL: 🏎️ === CARGANDO MODELO ===")
        print(f"DEBUG_MODEL: Coche recibido: {car_dict}")
        print(f"DEBUG_MODEL: Nombre: {car_dict.get('name', 'DESCONOCIDO')}")
        print(f"DEBUG_MODEL: Ruta: {car_dict.get('model_path', 'SIN RUTA')}")
        print(f"DEBUG_MODEL: Escala: {car_dict.get('scale', 0.05)}")
        print(f"DEBUG_MODEL: Elevación: {car_dict.get('elevation', 0.01)}")
        print(f"DEBUG_MODEL: ================================")

        model_path = f"assets/3d_models/{car_dict['model_path']}"
        scale = car_dict.get('scale', 0.05)
        elevation = car_dict.get('elevation', 0.01)
        
        # 🔧 GUARDAR NOMBRE DEL MODELO PARA LOGS
        self._current_model_name = car_dict.get('name', 'Modelo desconocido')

        print(f"DEBUG_MODEL: Ruta completa: {model_path}")
        print(f"DEBUG_MODEL: Ruta absoluta: {os.path.abspath(model_path)}")
        print(f"DEBUG_MODEL: ¿Existe archivo? {os.path.exists(model_path)}")

        if not os.path.exists(model_path):
            print(f"DEBUG_MODEL: ❌ Modelo no encontrado: {model_path}")
            # 🔍 DEBUG: Listar qué hay en el directorio
            dir_path = os.path.dirname(model_path)
            if os.path.exists(dir_path):
                print(f"DEBUG_MODEL: Contenido de {dir_path}:")
                for item in os.listdir(dir_path):
                    print(f"DEBUG_MODEL:   - {item}")
            return False

        # ... resto del código sin cambios ...

        print(f"DEBUG_MODEL: ✅ Modelo {self._current_model_name} cargado correctamente")
        print(f"DEBUG_MODEL: Meshes creados: {len(self.current_model)}")
        return True

    def prompt_for_user_id(self):
        """Solicitar ID de usuario para registro desde terminal"""
        try:
            if not hasattr(self, '_user_id_input_started'):
                print("\n" + "="*50)
                print("🆔 REGISTRO DE NUEVO USUARIO")
                print("="*50)
                self._user_id_input_started = True
            
            # Solicitar ID si no se ha hecho aún
            if not self.user_id_for_registration:
                user_id = input("Introduce tu nombre de usuario (sin espacios): ").strip()
                
                if not user_id:
                    print("❌ El ID no puede estar vacío. Inténtalo de nuevo.")
                    return
                
                if ' ' in user_id:
                    print("❌ El ID no puede contener espacios. Inténtalo de nuevo.")
                    return
                
                # Verificar que no existe ya
                if user_id in self.user_id_map:
                    print(f"❌ El usuario '{user_id}' ya existe. Elige otro nombre.")
                    return
                
                # ID válido y único
                self.user_id_for_registration = user_id
                print(f"✅ ID '{user_id}' disponible. Transicionando a captura...")
                
                # Limpiar flag
                if hasattr(self, '_user_id_input_started'):
                    delattr(self, '_user_id_input_started')
                
                # Cambiar al estado de captura
                self.current_state = STATE_REGISTER_CAPTURE
                self.captured_images_count = 0
                
        except EOFError:
            print("\n❌ Entrada cancelada. Volviendo al menú principal.")
            self._reset_registration_vars()
            self.current_state = STATE_WELCOME
        except KeyboardInterrupt:
            print("\n❌ Registro cancelado por el usuario.")
            self._reset_registration_vars()
            self.current_state = STATE_WELCOME

    def _reset_registration_vars(self):
        """Limpiar variables de registro"""
        self.user_id_for_registration = None
        self.captured_images_count = 0
        if hasattr(self, '_user_id_input_started'):
            delattr(self, '_user_id_input_started')
        print("DEBUG_REGISTER: Variables de registro limpiadas")

    def _capture_image_for_registration(self, frame):
        """Capturar imagen para entrenamiento del modelo facial"""
        print(f"DEBUG_REGISTER: Intentando capturar imagen {self.captured_images_count + 1}")
        
        # Detectar caras en el frame actual
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade_path = os.path.join(self.project_root_path, 
                                        'assets/face_data/cascades/haarcascade_frontalface_default.xml')
        
        if not os.path.exists(face_cascade_path):
            print(f"❌ No se encuentra el archivo cascade: {face_cascade_path}")
            return
        
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
        
        if len(faces) != 1:
            print(f"❌ Se necesita exactamente 1 cara, detectadas: {len(faces)}")
            return
        
        # Extraer la cara detectada
        (x, y, w, h) = faces[0]
        face_roi = gray_frame[y:y+h, x:x+w]
        
        # Crear directorio del usuario
        user_dir = os.path.join(self.project_root_path, 
                             USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT, 
                             self.user_id_for_registration)
        os.makedirs(user_dir, exist_ok=True)
        
        # Guardar imagen
        img_filename = f"face_{self.captured_images_count:03d}.jpg"
        img_path = os.path.join(user_dir, img_filename)
        
        # Redimensionar cara a tamaño estándar
        face_resized = cv2.resize(face_roi, (100, 100))
        cv2.imwrite(img_path, face_resized)
        
        self.captured_images_count += 1
        print(f"✅ Imagen {self.captured_images_count}/{NUM_IMAGES_FOR_REGISTRATION} capturada: {img_filename}")
        
        # Si hemos capturado suficientes imágenes, entrenar modelo
        if self.captured_images_count >= NUM_IMAGES_FOR_REGISTRATION:
            print(f"🎯 {NUM_IMAGES_FOR_REGISTRATION} imágenes capturadas. Iniciando entrenamiento...")
            self.current_state = STATE_REGISTER_TRAIN
            self._train_user_model()

    def _train_user_model(self):
        """Entrenar modelo LBPH para el usuario registrado"""
        print(f"🔧 Entrenando modelo para {self.user_id_for_registration}...")
        
        try:
            # Cargar imágenes del usuario
            user_dir = os.path.join(self.project_root_path, 
                                   USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT, 
                                   self.user_id_for_registration)
            
            faces = []
            labels = []
            
            # Asignar ID numérico al usuario
            if self.user_id_for_registration not in self.user_id_map:
                numeric_id = self.next_user_numeric_id
                self.user_id_map[self.user_id_for_registration] = numeric_id
                self.numeric_id_to_user_str_map[numeric_id] = self.user_id_for_registration
                self.next_user_numeric_id += 1
                self._save_user_id_map()
                print(f"✅ ID numérico {numeric_id} asignado a '{self.user_id_for_registration}'")
            
            numeric_id = self.user_id_map[self.user_id_for_registration]
            
            # Cargar todas las imágenes
            for img_file in os.listdir(user_dir):
                if img_file.endswith('.jpg'):
                    img_path = os.path.join(user_dir, img_file)
                    face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if face_img is not None:
                        faces.append(face_img)
                        labels.append(numeric_id)
            
            if len(faces) == 0:
                print("❌ No se encontraron imágenes válidas para entrenar")
                self._reset_registration_vars()
                self.current_state = STATE_WELCOME
                return
            
            print(f"📚 Entrenando con {len(faces)} imágenes...")
            
            # Entrenar modelo LBPH
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, np.array(labels))
            
            # Guardar modelo
            model_filename = f"{self.user_id_for_registration}.yml"
            model_path = os.path.join(self.lbph_models_dir, model_filename)
            recognizer.write(model_path)
            
            # Cargar en memoria
            self.loaded_recognizers[self.user_id_for_registration] = recognizer
            
            print(f"✅ Modelo entrenado y guardado: {model_path}")
            print(f"🎉 Usuario '{self.user_id_for_registration}' registrado correctamente!")
            
            # Limpiar variables y volver a login
            self._reset_registration_vars()
            self.current_state = STATE_LOGIN
            
        except Exception as e:
            print(f"❌ Error durante el entrenamiento: {e}")
            import traceback
            traceback.print_exc()
            self._reset_registration_vars()
            self.current_state = STATE_WELCOME

    # MODIFICAR core/app_manager.py - Umbral adaptativo según cámara:

    def _detect_camera_config(self):
        """Detectar configuración óptima según tipo de cámara"""
        # Obtener la cámara que se está usando desde config
        from core.config import CAMERA_INDEX
        camera_index = CAMERA_INDEX
        
        if camera_index == 2:
            # DroidCam detectado - parámetros conservadores
            return {
                'type': 'DroidCam',
                'width': 640,
                'height': 480,
                'focal_multiplier': 0.6,  # Menos zoom para DroidCam
                'confidence_threshold': 60  # ← UMBRAL MÁS ALTO PARA DROIDCAM
            }
        elif camera_index == 0:
            # Cámara del PC - parámetros estándar
            return {
                'type': 'Webcam PC',
                'width': 640,
                'height': 480,
                'focal_multiplier': 0.8,
                'confidence_threshold': 50  # ← UMBRAL ORIGINAL PARA PC
            }
        else:
            # Otra cámara - parámetros por defecto
            return {
                'type': 'Desconocida',
                'width': 640,
                'height': 480,
                'focal_multiplier': 0.7,
                'confidence_threshold': 70  # ← INTERMEDIO
            }