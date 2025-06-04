# ARCar_Showroom/vision_processing/facial_auth.py
import cv2
import os
# Importar la constante de la ruta del cascade desde config
from core.config import HAAR_CASCADE_PATH_REL_TO_PROJECT_ROOT

face_cascade = None

# MODIFICADO: load_cascade ahora toma project_root_path
def load_cascade(project_root_path):
    """Carga el clasificador Haar Cascade para detección de rostros."""
    global face_cascade
    
    # Construir la ruta absoluta al archivo cascade
    cascade_full_path = os.path.join(project_root_path, HAAR_CASCADE_PATH_REL_TO_PROJECT_ROOT)

    if not os.path.exists(cascade_full_path):
        print(f"Error en facial_auth: No se encontró el archivo Haar Cascade en {cascade_full_path}")
        print("Asegúrate de que el archivo exista y la ruta en core/config.py sea correcta.")
        return False
    
    face_cascade = cv2.CascadeClassifier(cascade_full_path)
    if face_cascade.empty():
        print(f"Error en facial_auth: No se pudo cargar el clasificador Haar Cascade desde {cascade_full_path}")
        return False
    print("Clasificador Haar Cascade cargado exitosamente (por facial_auth).")
    return True

def detect_faces(frame):
    """
    Detecta rostros en un frame dado.
    Devuelve el frame con rectángulos dibujados y las coordenadas de los rostros.
    """
    if face_cascade is None or face_cascade.empty():
        # print("Advertencia: Clasificador Haar no cargado. No se detectarán rostros.")
        return frame, [] # Devuelve el frame original y una lista vacía de rostros

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray_frame, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30) 
    )

    # Dibujar rectángulos SOLO si se va a mostrar (lo hacemos en AppManager ahora)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2) 
    # La función ahora solo devuelve las coordenadas y el frame original (o una copia)
    # El dibujo lo hará el AppManager según el contexto.
    # No, es mejor que facial_auth siga dibujando si se le pide, o que AppManager lo haga.
    # Por ahora, facial_auth dibuja, AppManager solo añade texto. Mantenemos el dibujo aquí.
    
    frame_with_rects = frame.copy() # Dibujar sobre una copia para no afectar el original si no se desea
    for (x, y, w, h) in faces:
        cv2.rectangle(frame_with_rects, (x, y), (x+w, y+h), (255, 0, 0), 2) # Dibuja un rectángulo azul

    return frame_with_rects, faces # Devolvemos el frame con rectángulos y las coordenadas
