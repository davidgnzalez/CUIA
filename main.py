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

# core/app_manager.py (añadir a la clase AppManager)

def get_current_state(self):
    """Devuelve el estado actual de la aplicación"""
    return self.current_state

def set_current_state(self, new_state):
    """Cambia el estado actual de la aplicación"""
    print(f"DEBUG_APP: Cambiando estado de {self.current_state} a {new_state}")
    self.current_state = new_state
