# ARCar_Showroom/core/config.py

# Estados de la aplicación (usaremos strings simples por ahora, Enum podría ser otra opción)
STATE_WELCOME = "STATE_WELCOME" # Nuevo estado inicial
STATE_LOGIN = "STATE_LOGIN"
STATE_REGISTER_PROMPT_ID = "STATE_REGISTER_PROMPT_ID" # Nuevo estado para pedir ID
STATE_REGISTER_CAPTURE = "STATE_REGISTER_CAPTURE"
STATE_REGISTER_TRAIN = "STATE_REGISTER_TRAIN" # Lo usaremos más adelante
STATE_MAIN_MENU_AR = "STATE_MAIN_MENU_AR"
STATE_AR_MENU_SELECTION = "STATE_AR_MENU_SELECTION"
STATE_AR_MODEL_VIEWER = "STATE_AR_MODEL_VIEWER"
# ... y otros estados que definamos más adelante

# Configuraciones de Cámara y Ventana
CAMERA_INDEX = 2  # ← CAMBIAR de 0 a 2 (DroidCam detectado)
CAMERA_FALLBACK = 0  # ← AÑADIR fallback a cámara del PC
WINDOW_NAME = "ARCar Showroom"

# Configuraciones de Reconocimiento Facial
# (Mantenemos la ruta aquí, pero facial_auth.py la usará)
HAAR_CASCADE_PATH_REL_TO_PROJECT_ROOT = 'assets/face_data/cascades/haarcascade_frontalface_default.xml'
NUM_IMAGES_FOR_REGISTRATION = 50 # Según el PDF

# ⚠️ IMPORTANTE: Todas las imágenes van DIRECTAMENTE en embeddings/<user_id>/
USER_FACE_DATA_DIR_REL_TO_PROJECT_ROOT = 'assets/face_data/embeddings'  # Sin /images/

# Ruta donde se guardarán los modelos LBPH entrenados
LBPH_MODELS_DIR_REL_TO_PROJECT_ROOT = 'assets/face_data/embeddings/models'

# Ruta para el archivo que mapea ID de usuario a ID numérico
USER_ID_MAP_PATH_REL_TO_PROJECT_ROOT = 'data_management/user_id_map.json'

# Configuración de menú
MENU_MARKER_ID = 23  # Marcador para mostrar menú
MODEL_MARKER_ID = 24  # Marcador para mostrar modelo 3D
AVAILABLE_CARS = [
    {
        "id": 1,
        "name": "Ferrari F40",
        "model_path": "ferrari-f40/source/f40.obj",  # ← CAMBIO: Añadir /source/
        "description": "Superdeportivo clásico italiano",
        "scale": 0.05,
        "elevation": 0.01
    },
    {
        "id": 2,
        "name": "Porsche 911",
        "model_path": "porsche-911/911.glb",
        "description": "Deportivo alemán icónico",
        "scale": 0.03,
        "elevation": 0.015
    }
]

# Umbrales de confianza según tipo de cámara
CONFIDENCE_THRESHOLDS = {
    'webcam_pc': 50,      # Cámara del PC (original)
    'droidcam': 60,       # DroidCam (más permisivo)
    'unknown': 40         # Desconocida (intermedio)
}

# Configuración automática de cámara
CAMERA_AUTO_DETECT = True  # Activar detección automática
