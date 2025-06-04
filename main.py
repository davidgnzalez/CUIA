# ARCar_Showroom/main.py
import cv2
import sys
import os # Para obtener la ruta del proyecto
from core.app_manager import AppManager
from core.config import (
    CAMERA_INDEX, WINDOW_NAME, 
    STATE_REGISTER_PROMPT_ID, STATE_LOGIN, STATE_REGISTER_CAPTURE,
    STATE_WELCOME # Importar el nuevo estado
)

def main():
    # Obtener la ruta absoluta al directorio raíz del proyecto (ARCar_Showroom)
    project_root_path = os.path.dirname(os.path.abspath(__file__))

    # Inicializar el gestor de la aplicación
    app_manager = AppManager(project_root_path)

    # Inicializar la cámara
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara (índice {CAMERA_INDEX}).")
        sys.exit("Aplicación terminada: Falla al iniciar la cámara.")
    print(f"Cámara (índice {CAMERA_INDEX}) iniciada. Presiona 'q' para salir (excepto en modo captura).")

    running = True
    while running:
        current_app_state = app_manager.get_current_state()

        if current_app_state == STATE_REGISTER_PROMPT_ID:
            cv2.waitKey(1) 
            app_manager.prompt_for_user_id()
            key_prompt = cv2.waitKey(1) & 0xFF 
            if key_prompt == ord('q'):
                print("Saliendo de solicitud de ID por tecla 'q'. Volviendo a LOGIN.")
                app_manager.current_state = STATE_LOGIN 
            continue

        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame de la cámara. Fin del stream o error.")
            running = False
            break

        display_frame = app_manager.process_frame(frame)
        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(1) & 0xFF

        # Primero permitir que AppManager maneje la tecla
        if key != 255:
            app_manager.handle_input(key, frame)
        
        # Después verificar si 'q' debe cerrar la aplicación
        if key == ord('q'):
            # Simplificación: 'q' siempre intenta salir de la aplicación
            # Cualquier manejo específico de estado ya fue atendido por app_manager.handle_input()
            print("Tecla 'q' presionada. Cerrando aplicación...")
            running = False

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
