# ARCar_Showroom/main.py
import cv2
import sys
import os # Para obtener la ruta del proyecto
from core.app_manager import AppManager
from core.config import (
    CAMERA_INDEX, WINDOW_NAME, 
    STATE_REGISTER_PROMPT_ID, STATE_LOGIN, STATE_REGISTER_CAPTURE,
    STATE_REGISTER_TRAIN,  # ← AÑADIDO
    STATE_WELCOME # Importar el nuevo estado
)

def find_best_camera():
    """Encontrar la mejor cámara disponible (priorizar cámara del PC primero)"""
    print("🎥 Buscando cámaras disponibles...")
    
    available_cameras = []
    camera_info = {}
    
    # 🔧 ORDEN OPTIMIZADO: Probar primero cámara 0, luego 2 (DroidCam), después resto
    priority_order = [2,0, 1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for i in priority_order:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                resolution = width * height
                camera_info[i] = {
                    'width': width,
                    'height': height,
                    'resolution': resolution
                }
                available_cameras.append(i)
                print(f"📹 Cámara {i}: {width}x{height} ({resolution} píxeles)")
            cap.release()
        # No imprimir "NO DISPONIBLE" para evitar spam de logs
    
    if not available_cameras:
        print("❌ No se encontraron cámaras disponibles")
        return 0
    
    # 🎯 ESTRATEGIA DE SELECCIÓN SIMPLIFICADA
    # Prioridad 1: Usar la primera cámara encontrada en el orden de prioridad
    best_camera = available_cameras[0]  # Ya está ordenado por prioridad
    
    if best_camera == 0:
        reason = "cámara del PC (prioridad principal)"
    elif best_camera == 2:
        reason = "DroidCam detectado"
    else:
        reason = f"primera cámara disponible"
    
    print(f"✅ Cámaras disponibles: {available_cameras}")
    print(f"🎯 Seleccionada: Cámara {best_camera} ({reason})")
    
    cam_info = camera_info[best_camera]
    print(f"📸 Resolución: {cam_info['width']}x{cam_info['height']}")
    
    return best_camera

def main():
    # Obtener la ruta absoluta al directorio raíz del proyecto
    project_root_path = os.path.dirname(os.path.abspath(__file__))

    # Inicializar el gestor de la aplicación
    app_manager = AppManager(project_root_path)

    # 🔧 AUTODETECTAR MEJOR CÁMARA (PRIORIZAR DROIDCAM)
    camera_index = find_best_camera()
    
    # Inicializar la cámara con el índice detectado
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Error: No se pudo abrir la cámara {camera_index}.")
        
        # 🔄 FALLBACK: Probar cámara 0 si la seleccionada falla
        if camera_index != 0:
            print("🔄 Intentando fallback a cámara 0...")
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                camera_index = 0
                print("✅ Fallback exitoso a cámara 0")
            else:
                sys.exit("❌ Aplicación terminada: No se pudo iniciar ninguna cámara.")
        else:
            sys.exit("❌ Aplicación terminada: Falla al iniciar la cámara.")
    
    print(f"🚀 Cámara {camera_index} iniciada correctamente.")
    
    running = True
    while running:
        current_app_state = app_manager.get_current_state()

        # 🔧 MANEJO MEJORADO DEL REGISTRO
        if current_app_state == STATE_REGISTER_PROMPT_ID:
            # Mostrar un frame básico mientras se pide el ID
            ret, frame = cap.read()
            if ret:
                display_frame = frame.copy()
                cv2.putText(display_frame, "REGISTRO: Mira la terminal para introducir tu ID", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(display_frame, "Presiona 'ESC' para cancelar", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
                cv2.imshow(WINDOW_NAME, display_frame)
            
            # Manejar cancelación
            key_prompt = cv2.waitKey(1) & 0xFF
            if key_prompt == 27:  # ESC
                print("❌ Registro cancelado. Volviendo al menú principal.")
                app_manager._reset_registration_vars()
                app_manager.current_state = STATE_WELCOME
                continue
            elif key_prompt == ord('q'):
                print("❌ Saliendo por tecla 'q'.")
                running = False
                break
            
            # Solicitar ID (esto puede bloquear)
            try:
                app_manager.prompt_for_user_id()
            except KeyboardInterrupt:
                print("\n❌ Registro cancelado.")
                app_manager._reset_registration_vars()
                app_manager.current_state = STATE_WELCOME
            
            continue  # Importante: continuar el bucle

        # 🔧 MANEJO DEL ESTADO DE ENTRENAMIENTO
        elif current_app_state == STATE_REGISTER_TRAIN:
            # Mostrar frame de entrenamiento
            ret, frame = cap.read()
            if ret:
                display_frame = frame.copy()
                cv2.putText(display_frame, f"Entrenando modelo para: {app_manager.user_id_for_registration}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(display_frame, "Entrenamiento en progreso...", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                cv2.imshow(WINDOW_NAME, display_frame)
            
            cv2.waitKey(100)  # Pausa breve para mostrar el mensaje
            continue

        # Resto de estados normales
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame de la cámara. Fin del stream o error.")
            running = False
            break

        display_frame = app_manager.process_frame(frame)
        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(1) & 0xFF

        # 🔧 PERMITIR QUE APPMANAGER MANEJE TODAS LAS TECLAS PRIMERO
        if key != 255:
            # AppManager decide si debe procesar la tecla
            app_result = app_manager.handle_input(key, frame)
            
            # 🔧 SOLO SALIR CON 'Q' SI ESTAMOS EN WELCOME O LOGIN
            if key == ord('q'):
                if current_app_state in [STATE_WELCOME, STATE_LOGIN]:
                    print("Tecla 'q' presionada en estado permitido. Cerrando aplicación...")
                    running = False
                else:
                    print(f"Tecla 'q' manejada por AppManager en estado {current_app_state}")
                    # No cerrar la aplicación, dejar que AppManager la maneje
    
    cap.release()
    app_manager.cleanup() 
    print("Aplicación cerrada correctamente.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR INESPERADO EN MAIN: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
