# ARCar_Showroom/vision_processing/marker_detection.py
import cv2
import numpy as np

# Diccionario ArUco que vamos a usar
# ARUCO_DICT = cv2.aruco.DICT_6X6_250 # Ejemplo
ARUCO_DICT_NAME = "DICT_6X6_250" # Guardamos el nombre para cargarlo dinámicamente
ARUCO_DICT = None 
ARUCO_PARAMETERS = None

# Definir camera_matrix y dist_coeffs (idealmente de calibración)
# Si no, podemos estimar una matriz de cámara simple o pasar None
# y la estimación de pose no será precisa.

# Para pruebas sin calibración:
# Si sabes el ancho y alto de tu frame, puedes hacer una estimación aproximada:
# fx = fy = frame_width 
# cx = frame_width / 2
# cy = frame_height / 2
# camera_matrix_est = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
# dist_coeffs_est = np.zeros((4,1)) # Asumir sin distorsión

# O simplemente None si la función lo maneja
CAMERA_MATRIX_FOR_POSE = None 
DIST_COEFFS_FOR_POSE = None

def initialize_aruco_detector():
    """Inicializa el diccionario y los parámetros del detector ArUco."""
    global ARUCO_DICT, ARUCO_PARAMETERS
    try:
        # Cargar el diccionario ArUco dinámicamente por su nombre
        if hasattr(cv2.aruco, ARUCO_DICT_NAME):
            aruco_dictionary_id = getattr(cv2.aruco, ARUCO_DICT_NAME)
            ARUCO_DICT = cv2.aruco.getPredefinedDictionary(aruco_dictionary_id)
            ARUCO_PARAMETERS = cv2.aruco.DetectorParameters()
            # ARUCO_PARAMETERS = cv2.aruco.DetectorParameters_create() # Para versiones más antiguas de OpenCV
            print(f"Detector ArUco inicializado con diccionario: {ARUCO_DICT_NAME}")
            return True
        else:
            print(f"Error: Diccionario ArUco '{ARUCO_DICT_NAME}' no encontrado en cv2.aruco.")
            return False
    except Exception as e:
        print(f"Excepción al inicializar el detector ArUco: {e}")
        return False


def detect_markers(frame):
    """
    Detecta marcadores ArUco en un frame.
    Devuelve:
        - corners: Lista de esquinas de los marcadores detectados.
        - ids: Lista de IDs de los marcadores detectados.
        - rejected_img_points: Puntos candidatos rechazados (para depuración).
        - frame_with_markers: El frame con los marcadores dibujados.
    """
    if ARUCO_DICT is None or ARUCO_PARAMETERS is None:
        # print("Advertencia: Detector ArUco no inicializado.")
        return [], None, [], frame # Devuelve el frame original si no está inicializado

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Crear el detector usando los parámetros
    detector = cv2.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMETERS)
    corners, ids, rejected_img_points = detector.detectMarkers(gray)
    
    # corners, ids, rejected_img_points = cv2.aruco.detectMarkers(
    #     gray, ARUCO_DICT, parameters=ARUCO_PARAMETERS
    # ) # Para versiones más antiguas de OpenCV

    frame_with_markers = frame.copy()
    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(frame_with_markers, corners, ids)
        # print(f"Marcadores detectados: IDs {ids.flatten()}") # Para depuración
    
    return corners, ids, rejected_img_points, frame_with_markers

def detect_and_estimate_pose(frame, camera_matrix=None, dist_coeffs=None, marker_size_meters=0.05):
    """
    Detecta marcadores y estima su pose.
    Devuelve:
        - corners, ids, frame_with_markers
        - rvecs, tvecs: Vectores de rotación y traslación. None si no se detectan marcadores
                        o si faltan parámetros de cámara.
    """
    if ARUCO_DICT is None or ARUCO_PARAMETERS is None:
        return [], None, frame, None, None

    # Usar valores por defecto si no se proporcionan
    if camera_matrix is None:
        camera_matrix = CAMERA_MATRIX_FOR_POSE
    if dist_coeffs is None:
        dist_coeffs = DIST_COEFFS_FOR_POSE
        
    # Si aún no hay matriz de cámara, podemos estimarla basándonos en las dimensiones del frame
    if camera_matrix is None:
        h, w = frame.shape[:2]
        fx = fy = w  # Una aproximación simple
        cx, cy = w/2, h/2
        camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
        print("Usando matriz de cámara estimada basada en dimensiones del frame")
        
    if dist_coeffs is None:
        dist_coeffs = np.zeros((4,1), dtype=np.float32)  # Sin distorsión

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMETERS)
    corners, ids, _ = detector.detectMarkers(gray)
    
    frame_with_markers = frame.copy()
    rvecs, tvecs = None, None

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(frame_with_markers, corners, ids)
        
        # Estimar la pose si tenemos los parámetros de la cámara
        try:
            rvecs_list = []
            tvecs_list = []
            for i in range(len(ids)):
                try:
                    # La forma estándar con ArUco para estimación de pose:
                    rvec, tvec, _objPoints = cv2.aruco.estimatePoseSingleMarkers(
                        corners[i], marker_size_meters, camera_matrix, dist_coeffs
                    )
                    rvecs_list.append(rvec)
                    tvecs_list.append(tvec)
                    
                    # Dibujar el eje del marcador para verificar la pose
                    cv2.drawFrameAxes(frame_with_markers, camera_matrix, dist_coeffs, 
                                     rvec, tvec, marker_size_meters * 0.5)

                except cv2.error as e:
                    print(f"Error en estimatePoseSingleMarkers para marcador {ids[i]}: {e}")
                    # Esto puede pasar si los puntos del marcador no son válidos o la matriz de cámara es incorrecta.
            
            if rvecs_list:
                rvecs = np.array(rvecs_list)
                tvecs = np.array(tvecs_list)
        except Exception as e:
            print(f"Error general al estimar pose: {e}")
            
    return corners, ids, frame_with_markers, rvecs, tvecs