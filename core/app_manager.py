# ARCar_Showroom/core/app_manager.py
import cv2
import os
import numpy as np
import json
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
        
        self.camera_matrix_cv = None # Aquí cargarías tu matriz de cámara calibrada
        self.dist_coeffs_cv = None   # Y tus coeficientes de distorsión
        
        # Ejemplo de matriz de cámara genérica (¡REEMPLAZAR CON CALIBRACIÓN!)
        # Esto es solo para que el código se ejecute. La calidad será mala.
        # Asumimos un frame de 640x480 como ejemplo para calcular cx, cy
        frame_w_example, frame_h_example = 640, 480 
        fx_est, fy_est = frame_w_example, frame_w_example # Estimación simple
        cx_est, cy_est = frame_w_example / 2, frame_h_example / 2
        self.camera_matrix_cv = np.array([
            [fx_est, 0, cx_est],
            [0, fy_est, cy_est],
            [0, 0, 1]
        ], dtype=np.float32)
        self.dist_coeffs_cv = np.zeros((4,1), dtype=np.float32) # Asumir sin distorsión

        if not facial_auth.load_cascade(self.project_root_path):
            print("ALERTA CRÍTICA en AppManager: Haar Cascade no pudo ser cargado.")
        
        # Inicializar el detector ArUco
        if not marker_detection.initialize_aruco_detector():
            print("ALERTA CRÍTICA en AppManager: Detector ArUco no pudo ser inicializado.")
            # Podríamos decidir si la app puede continuar sin esto o no.
            # Por ahora, el detector simplemente no funcionará si falla.
        
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        self._load_all_trained_models() # Cargar modelos al inicio

        # Importar la configuración
        from core.config import AVAILABLE_CARS
        
        # Nuevas variables para el sistema AR
        self.ar_menu = ARMenu()
        self.ar_menu.menu_items = AVAILABLE_CARS  # ← ASEGURAR que se cargan los coches
        
        # 🔥 DEBUG CRÍTICO: Verificar que se cargan ambos coches
        print(f"DEBUG_APP: Menu inicializado con {len(AVAILABLE_CARS)} coches:")
        for i, car in enumerate(AVAILABLE_CARS):
            print(f"DEBUG_APP: {i+1}. {car['name']} - {car['model_path']} (escala: {car.get('scale', 0.05)})")
        
        self.model_viewer = PyrenderModelViewer()
        self.selected_car = None
        self.model_marker_id = MODEL_MARKER_ID

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
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 🚫 COMENTAR TODA LA INICIALIZACIÓN OPENGL DEL CUBO
        # if not self.camera_initialized_for_gl:
        #     print("DEBUG_AM: Inicializando OpenGL y cargando textura...")
        #     scene_renderer.init_opengl(width, height)
        #     
        #     texture_full_path = os.path.join(self.project_root_path, self.texture_path_test_rel)
        #     scene_renderer.texture_id_test = scene_renderer.load_texture(texture_full_path)
        #     
        #     if scene_renderer.texture_id_test is not None:
        #         print(f"DEBUG_AM: Textura de prueba cargada con ID: {scene_renderer.texture_id_test}")
        #     else:
        #         print("DEBUG_AM: Falló la carga de la textura de prueba. La cara frontal será roja.")
        #     self.camera_initialized_for_gl = True

        # ✅ MARCAR COMO INICIALIZADO SIN USAR OPENGL
        if not self.camera_initialized_for_gl:
            print("DEBUG_AM: ✅ Saltando inicialización OpenGL - Solo pyrender")
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
                        if best_match_user_id_str and lowest_confidence < LBPH_CONFIDENCE_THRESHOLD:
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
                    cv2.putText(display_frame, "ESPACIO: Seleccionar Ferrari F40", (10, 120), 
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
                        # Agregar información sobre el coche seleccionado
                        cv2.putText(display_frame, f"🏎️ {self.selected_car['name']} - MODELO 3D REAL", (10, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Archivo: {self.selected_car['model_path']}", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                        cv2.putText(display_frame, "Presiona 'C' para volver al menu", (10, 180), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    except Exception as e:
                        print(f"ERROR_PYRENDER: {e}")
                        display_frame = frame_with_aruco_markers
                        cv2.putText(display_frame, f"❌ Error cargando {self.selected_car['name']}", (10, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            else:
                # No hay marcador visible
                display_frame = frame_with_aruco_markers
                cv2.putText(display_frame, "Muestra marcador ID 23 para menu", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,150,0), 1)
                if self.selected_car:
                    cv2.putText(display_frame, f"Ferrari seleccionado: {self.selected_car['name']}", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.putText(display_frame, "Muestra marcador ID 23 para ver Ferrari 3D", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            # Textos del estado
            cv2.putText(display_frame, "Estado: FERRARI SHOWROOM", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            welcome_message = f"Bienvenido, {self.logged_in_user_str if self.logged_in_user_str else 'Usuario'}!"
            cv2.putText(display_frame, welcome_message, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        
        else:  # Estado desconocido
            cv2.putText(display_frame, f"Estado: {self.current_state}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
        
        return display_frame

    def handle_input(self, key, current_frame):
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
            # Manejar navegación del menú AR cuando se detecta marcador ID 23
            corners, ids, _, _, _ = marker_detection.detect_and_estimate_pose(
                current_frame, self.camera_matrix_cv, self.dist_coeffs_cv, scene_renderer.MARKER_SIZE_METERS
            )
            
            # Si hay marcador ID 23 visible, permitir selección del Ferrari
            if ids is not None and 23 in ids:
                selected_car = self.ar_menu.handle_selection(key)
                if selected_car:
                    # 🔥 DEBUG CRÍTICO: Verificar qué coche se selecciona
                    print(f"DEBUG_APP: 🏎️ === COCHE SELECCIONADO ===")
                    print(f"DEBUG_APP: Nombre: {selected_car['name']}")
                    print(f"DEBUG_APP: Ruta: {selected_car['model_path']}")
                    print(f"DEBUG_APP: Escala: {selected_car.get('scale', 0.05)}")
                    print(f"DEBUG_APP: Elevación: {selected_car.get('elevation', 0.01)}")
                    print(f"DEBUG_APP: =====================================")
                    
                    self.selected_car = selected_car
                    print(f"DEBUG_APP: Coche seleccionado: {selected_car['name']}")
                    print(f"DEBUG_APP: Intentando cargar modelo: {selected_car['model_path']}")
                    
                    # CARGAR EL MODELO INMEDIATAMENTE con debug completo
                    print("DEBUG_APP: 🔥 INICIANDO CARGA DE MODELO...")
                    
                    # 🔧 CORRECCIÓN: Pasar el diccionario completo, NO solo la ruta
                    model_loaded = self.model_viewer.load_car_model(selected_car)
                    
                    if model_loaded:
                        print(f"DEBUG_APP: ✅ Modelo {selected_car['name']} cargado exitosamente")
                        print(f"DEBUG_APP: current_model = {self.model_viewer.current_model}")
                    else:
                        print(f"DEBUG_APP: ❌ Error cargando modelo para {selected_car['name']}")
                        # Intentar carga alternativa
                        print("DEBUG_APP: 🔄 Intentando carga alternativa...")
                        alt_path = "ferrari-f40"  # Carpeta directa
                        if self.model_viewer.load_car_model(alt_path):
                            print("DEBUG_APP: ✅ Carga alternativa exitosa")
                        else:
                            print("DEBUG_APP: ❌ Carga alternativa falló")

            # Manejar otras teclas del menú principal
            if key == ord('q'): # Logout
                print(f"Cerrando sesión de {self.logged_in_user_str}. Volviendo al menú de bienvenida.")
                self.logged_in_user_str = None
                self.selected_car = None
                self.current_state = STATE_WELCOME
            elif key == ord('c'): # Limpiar selección
                print("Limpiando selección de coche.")
                self.selected_car = None
                # Limpiar modelo cargado correctamente
                self.model_viewer.cleanup()
                self.model_viewer.current_model = None

        elif self.current_state == STATE_AR_MENU_SELECTION:
            selected_car = self.ar_menu.handle_selection(key)
            if selected_car:
                self.selected_car = selected_car
                print(f"Coche seleccionado: {selected_car['name']}")
                # Intentar cargar el modelo (opcional por ahora)
                # self.model_viewer.load_car_model(selected_car["model_path"])
                self.current_state = STATE_MAIN_MENU_AR  # Volver al menú principal
            elif key == ord('b'):  # Volver
                self.current_state = STATE_MAIN_MENU_AR

        elif self.current_state == STATE_AR_MODEL_VIEWER:
            if key == ord('b'):  # Volver al menú
                self.current_state = STATE_MAIN_MENU_AR
                self.selected_car = None

    def _reset_registration_vars(self):
        self.user_id_for_registration = None
        self.captured_images_count = 0

    def _capture_image_for_registration(self, frame):
        if not self.user_id_for_registration:
            print("Error de lógica: Intento de captura sin user_id_for_registration.")
            return

        if self.captured_images_count >= NUM_IMAGES_FOR_REGISTRATION:
            print("Ya se han capturado todas las imágenes necesarias.")
            return

        _, faces = facial_auth.detect_faces(frame.copy()) 

        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            face_roi = frame[y:y+h, x:x+w]
            gray_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

            user_data_folder_base = os.path.join(self.project_root_path, USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT)
            user_specific_image_folder = os.path.join(user_data_folder_base, "images", self.user_id_for_registration) # Carpeta "images"
            os.makedirs(user_specific_image_folder, exist_ok=True)

            self.captured_images_count += 1
            image_filename = f"{self.captured_images_count}.png"
            full_image_path = os.path.join(user_specific_image_folder, image_filename)

            try:
                cv2.imwrite(full_image_path, gray_face_roi)

                if self.captured_images_count == NUM_IMAGES_FOR_REGISTRATION:
                    print(f"¡Todas las imágenes para '{self.user_id_for_registration}' capturadas!")
                    self.current_state = STATE_REGISTER_TRAIN
                    print(f"Transicionando a {STATE_REGISTER_TRAIN} para {self.user_id_for_registration}")
                    self._train_lbph_model()
            except Exception as e:
                print(f"Error al guardar la imagen {full_image_path}: {e}")
                self.captured_images_count -= 1
        
        elif len(faces) == 0:
            pass
        else:
            pass

    def _train_lbph_model(self):
        if not self.user_id_for_registration:
            print("Error: No hay usuario especificado para el entrenamiento.")
            self.current_state = STATE_WELCOME
            return

        print(f"Iniciando entrenamiento LBPH para: {self.user_id_for_registration}")

        user_images_path_base = os.path.join(self.project_root_path, USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT, "images")
        user_image_folder = os.path.join(user_images_path_base, self.user_id_for_registration)

        if not os.path.exists(user_image_folder):
            print(f"Error: No se encontró la carpeta de imágenes para {self.user_id_for_registration} en {user_image_folder}")
            self.current_state = STATE_WELCOME
            return

        face_samples = []
        ids = []

        if self.user_id_for_registration not in self.user_id_map:
            current_numeric_id = self.next_user_numeric_id
            self.user_id_map[self.user_id_for_registration] = current_numeric_id
            self.next_user_numeric_id += 1
            self._save_user_id_map()
            # Actualizar el mapa inverso DESPUÉS de guardar el mapa principal
            self.numeric_id_to_user_str_map = {v: k for k, v in self.user_id_map.items()}
        else:
            current_numeric_id = self.user_id_map[self.user_id_for_registration]
        
        print(f"ID numérico para '{self.user_id_for_registration}': {current_numeric_id}")

        image_paths = [os.path.join(user_image_folder, f) for f in os.listdir(user_image_folder)]

        for image_path in image_paths:
            try:
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"Advertencia: No se pudo cargar la imagen {image_path}")
                    continue
                
                face_samples.append(img)
                ids.append(current_numeric_id) 
            except Exception as e:
                print(f"Error procesando imagen {image_path}: {e}")

        if not face_samples or not ids:
            print(f"No se encontraron imágenes válidas para entrenar para {self.user_id_for_registration}.")
            self.current_state = STATE_WELCOME
            self._reset_registration_vars()
            return

        print(f"Entrenando con {len(face_samples)} imágenes...")
        
        recognizer_instance = cv2.face.LBPHFaceRecognizer_create()
        recognizer_instance.train(face_samples, np.array(ids))

        model_filename = f"{self.user_id_for_registration}.yml"
        model_save_path = os.path.join(self.lbph_models_dir, model_filename)
        
        try:
            recognizer_instance.save(model_save_path)
            print(f"Modelo LBPH para '{self.user_id_for_registration}' guardado en: {model_save_path}")
        except Exception as e:
            print(f"Error al guardar el modelo LBPH: {e}")
            self.current_state = STATE_WELCOME
            self._reset_registration_vars()
            return

        print("Entrenamiento completado.")
        self.current_state = STATE_WELCOME # CAMBIO AQUÍ: Volver a Bienvenida
        self._reset_registration_vars()
        self._load_all_trained_models()  # Volver a cargar modelos por si se añadió uno nuevo
        self.logged_in_user_str = None  # Resetear el usuario logueado después del entrenamiento

    def prompt_for_user_id(self):
        if self.current_state == STATE_REGISTER_PROMPT_ID:
            try:
                user_input_id = input(f"Introduce un ID (o 'cancelar' para volver al menu): ").strip()
                
                if user_input_id.lower() == 'cancelar':
                    print("Solicitud de ID cancelada. Volviendo a menu bienvenida.")
                    self.current_state = STATE_WELCOME # CAMBIO AQUÍ
                    self._reset_registration_vars()
                    return

                is_valid_id = all(c.isalnum() or c == '_' for c in user_input_id) and ' ' not in user_input_id and user_input_id

                if is_valid_id:
                    self.user_id_for_registration = user_input_id.lower()
                    
                    # Comprobar si el usuario ya tiene un modelo entrenado o imágenes
                    user_images_path_base = os.path.join(self.project_root_path, USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT, "images")
                    user_specific_image_folder = os.path.join(user_images_path_base, self.user_id_for_registration)
                    model_path_check = os.path.join(self.lbph_models_dir, f"{self.user_id_for_registration}.yml")

                    # Si ya existen imágenes o un modelo, preguntar
                    if os.path.exists(user_specific_image_folder) or os.path.exists(model_path_check):
                        overwrite = input(f"El ID '{self.user_id_for_registration}' ya tiene datos/modelo. ¿Continuar y sobrescribir/re-entrenar? (s/N): ").strip().lower()
                        if overwrite != 's':
                            print("Registro/Re-entrenamiento cancelado. Elige otro ID o cancela.")
                            self.user_id_for_registration = None
                            return
                    
                    self.captured_images_count = 0 
                    print(f"ID '{self.user_id_for_registration}' aceptado. Iniciando captura de imágenes.")
                    self.current_state = STATE_REGISTER_CAPTURE
                else:
                    print("ID no válido. Usa solo letras, números y guion bajo, sin espacios. Inténtalo de nuevo o presiona 'q' en la ventana para volver a Login.")
            except EOFError:
                print("Entrada cancelada. Volviendo a menu bienvenida.")
                self.current_state = STATE_WELCOME # CAMBIO AQUÍ
                self._reset_registration_vars()

    def get_current_state(self):
        return self.current_state

    def cleanup(self):
        """Limpiar recursos antes de cerrar la aplicación"""
        if hasattr(self, 'model_viewer') and self.model_viewer:
            self.model_viewer.cleanup()  # Limpiar pyrender
        cv2.destroyAllWindows()
        print("AppManager: Recursos de ventana limpiados.")
