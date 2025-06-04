import cv2
import numpy as np

# Elige el diccionario y el ID
# DICT_NAME = cv2.aruco.DICT_6X6_250 # Nombre del diccionario
DICT_NAME_STR = "DICT_6X6_250"
MARKER_ID = 23  # Elige un ID (ej. 0, 1, 23, etc.)
MARKER_SIZE_PIXELS = 300 # Tamaño de la imagen del marcador a generar

try:
    if hasattr(cv2.aruco, DICT_NAME_STR):
        aruco_dict_id = getattr(cv2.aruco, DICT_NAME_STR)
        aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_id)
        print(f"Generando marcador ID {MARKER_ID} del diccionario {DICT_NAME_STR}...")
        
        marker_image = np.zeros((MARKER_SIZE_PIXELS, MARKER_SIZE_PIXELS), dtype=np.uint8)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, MARKER_ID, MARKER_SIZE_PIXELS, marker_image, 1)
        # Para versiones más antiguas:
        # cv2.aruco.drawMarker(aruco_dict, MARKER_ID, MARKER_SIZE_PIXELS, marker_image, 1)


        filename = f"aruco_{DICT_NAME_STR}_id{MARKER_ID}.png"
        cv2.imwrite(filename, marker_image)
        print(f"Marcador guardado como {filename}")
        cv2.imshow(f"Marcador ID {MARKER_ID}", marker_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"Error: Diccionario ArUco '{DICT_NAME_STR}' no encontrado.")

except Exception as e:
    print(f"Ocurrió un error: {e}")