# ARCar Showroom - Documentación Técnica

## 📋 **Índice**

1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [Módulos Principales](#módulos-principales)
5. [Flujo de Estados](#flujo-de-estados)
6. [Reconocimiento Facial](#reconocimiento-facial)
7. [Renderizado AR](#renderizado-ar)
8. [Control por Voz](#control-por-voz)
9. [Gestión de Datos](#gestión-de-datos)
10. [Configuración](#configuración)
11. [Instalación y Configuración](#instalación-y-configuración)
12. [Guía de Uso](#guía-de-uso)
13. [Troubleshooting](#troubleshooting)
14. [API Reference](#api-reference)

---

## 🎯 **Resumen del Proyecto**

**ARCar Showroom** es una aplicación de **Realidad Aumentada (AR)** que demuestra los principios de **Computación Ubicua e Inteligencia Ambiental**. El sistema permite a los usuarios visualizar modelos 3D de automóviles mediante **reconocimiento facial automático**, **marcadores ArUco** y **control por voz natural**.

La aplicación integra tecnologías de **Computer Vision**, **Machine Learning** y **Renderizado 3D** para crear una experiencia **ubicua e inteligente** donde la tecnología funciona de forma **transparente** y se **adapta automáticamente** al contexto y usuario.

### **Principios de Computación Ubicua Implementados:**

- 🌐 **Transparencia**: Tecnología invisible que funciona sin intervención manual
- 🧠 **Inteligencia Ambiental**: Reconocimiento automático y adaptación contextual
- 🔄 **Adaptabilidad**: Configuración automática según hardware disponible
- 🎭 **Multimodalidad**: Interacción natural por voz, visión y gestos
- 📱 **Ubicuidad**: Funciona consistentemente con diferentes dispositivos

### **Características Principales:**

- ✅ **Autenticación facial transparente** con algoritmo LBPH personalizado
- ✅ **Renderizado AR contextual** de modelos 3D (Ferrari F40, Porsche 911)
- ✅ **Control por voz natural** con comandos en español
- ✅ **Detección automática de marcadores ArUco** para posicionamiento 3D
- ✅ **Gestión inteligente de usuarios** con registro y entrenamiento automático
- ✅ **Soporte ubicuo multicámara** (Webcam PC, DroidCam, cámaras externas)

### **Tecnologías Utilizadas:**

- **Python 3.8+** - Lenguaje principal
- **OpenCV 4.x** - Computer Vision y procesamiento de imágenes
- **Trimesh + Pyrender** - Carga y renderizado de modelos 3D
- **SpeechRecognition + PyAudio** - Reconocimiento de voz
- **NumPy** - Operaciones matemáticas y matrices
- **Pillow (PIL)** - Manipulación de imágenes

---

## 🏗️ **Arquitectura del Sistema**

### **Patrón de Diseño: Estado-Manager**

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN APPLICATION                        │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   Camera    │────│  AppManager  │────│  State Engine │  │
│  │  Detection  │    │   (Core)     │    │               │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
    ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
    │   Vision    │     │  AR Render  │     │  Audio      │
    │ Processing  │     │             │     │ Processing  │
    │             │     │             │     │             │
    │ • Facial    │     │ • 3D Models │     │ • Voice     │
    │   Auth      │     │ • ArUco     │     │   Commands  │
    │ • ArUco     │     │ • Pyrender  │     │ • Speech    │
    │   Detection │     │             │     │   Recognition │
    └─────────────┘     └─────────────┘     └─────────────┘
           │                    │                    │
    ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
    │    Data     │     │    Core     │     │   Assets    │
    │ Management  │     │   Config    │     │             │
    │             │     │             │     │ • 3D Models │
    │ • Users     │     │ • States    │     │ • Cascades  │
    │ • Models    │     │ • Camera    │     │ • Textures  │
    │ • Training  │     │ • Thresholds│     │             │
    └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 📁 **Estructura de Directorios**

```
ARCar_Showroom/
├── 📁 ar_rendering/              # Módulo de Renderizado AR
│   ├── ar_menu.py               # Menú AR superpuesto
│   ├── scene_renderer.py        # Renderizador 3D principal
│   └── __init__.py
├── 📁 assets/                   # Recursos del proyecto
│   ├── 📁 3d_models/           # Modelos 3D de automóviles
│   │   ├── ferrari-f40/
│   │   │   └── source/
│   │   │       └── f40.obj     # Modelo Ferrari F40
│   │   └── porsche-911/
│   │       └── 911.glb         # Modelo Porsche 911
│   ├── 📁 face_data/          # Datos de reconocimiento facial
│   │   ├── 📁 cascades/       # Clasificadores Haar
│   │   │   └── haarcascade_frontalface_default.xml
│   │   └── 📁 embeddings/     # Datos de usuarios
│   │       ├── 📁 {user_id}/  # Directorio por usuario
│   │       │   ├── face_000.jpg ... face_049.jpg  # 50 imágenes
│   │       └── 📁 models/     # Modelos LBPH entrenados
│   │           └── {user_id}.yml
│   └── 📁 markers/            # Marcadores ArUco (opcional)
├── 📁 audio_processing/         # Módulo de Audio y Voz
│   ├── voice_commands.py       # Controlador de comandos de voz
│   └── __init__.py
├── 📁 core/                    # Núcleo del sistema
│   ├── app_manager.py          # Gestor principal de la aplicación
│   ├── config.py              # Configuraciones globales
│   └── __init__.py
├── 📁 data_management/         # Gestión de datos
│   ├── user_manager.py         # Gestión de usuarios CLI
│   ├── user_id_map.json       # Mapeo de IDs de usuario
│   └── __init__.py
├── 📁 vision_processing/       # Procesamiento de visión
│   ├── facial_auth.py         # Autenticación facial
│   ├── marker_detection.py    # Detección de marcadores ArUco
│   └── __init__.py
├── 📄 main.py                  # Punto de entrada principal
├── 📄 test_cameras.py          # Test de cámaras disponibles
├── 📄 test_voice.py           # Test de reconocimiento de voz
├── 📄 requirements.txt         # Dependencias Python
└── 📄 Documentation.md         # Este archivo
```

---

## 🔧 **Módulos Principales**

### **1. Core Module (`core/`)**

#### **AppManager (`core/app_manager.py`)**

**Clase principal que orquesta toda la aplicación.**

```python
class AppManager:
    def __init__(self, project_root_path: str)
    def process_frame(self, frame: np.ndarray) -> np.ndarray
    def handle_input(self, key: int, current_frame: np.ndarray) -> None
    def get_current_state(self) -> str
    def cleanup(self) -> None
```

**Responsabilidades:**

- 🎯 **Gestión de estados** - Controla transiciones entre WELCOME, LOGIN, REGISTER, AR_MENU
- 📹 **Procesamiento de frames** - Pipeline principal de procesamiento de imagen
- 🎮 **Manejo de entrada** - Teclado y comandos de voz
- 🔧 **Configuración automática** - Detección de cámara y calibración de umbrales
- 🧠 **Coordinación de módulos** - Facial auth, AR rendering, voice control

**Estados del Sistema:**

```python
STATE_WELCOME           # Pantalla de bienvenida
STATE_LOGIN             # Autenticación facial
STATE_REGISTER_PROMPT_ID    # Solicitar ID para registro
STATE_REGISTER_CAPTURE      # Capturar 50 imágenes
STATE_REGISTER_TRAIN        # Entrenamiento del modelo
STATE_MAIN_MENU_AR          # Menú AR principal
```

#### **Configuration (`core/config.py`)**

**Configuraciones centralizadas del sistema.**

```python
# Estados de la aplicación
STATE_WELCOME = "STATE_WELCOME"
STATE_LOGIN = "STATE_LOGIN"
# ... otros estados

# Configuraciones de cámara
CAMERA_INDEX = 2  # DroidCam por defecto
CAMERA_FALLBACK = 0  # Webcam PC como fallback

# Reconocimiento facial
NUM_IMAGES_FOR_REGISTRATION = 50
HAAR_CASCADE_PATH_REL_TO_PROJECT_ROOT = 'assets/face_data/cascades/...'

# Modelos 3D disponibles
AVAILABLE_CARS = [
    {
        "id": 1,
        "name": "Ferrari F40",
        "model_path": "ferrari-f40/source/f40.obj",
        "scale": 0.05,
        "elevation": 0.01
    },
    # ...
]
```

### **2. Vision Processing (`vision_processing/`)**

#### **Facial Authentication (`facial_auth.py`)**

**Sistema de autenticación basado en LBPH (Local Binary Pattern Histogram).**

```python
def load_cascade(project_root_path: str) -> bool
def detect_faces(frame: np.ndarray) -> Tuple[np.ndarray, List]
```

**Algoritmo LBPH:**

- 🔍 **Detección**: Usa Haar Cascades para detectar caras
- 📊 **Extracción**: Genera patrones binarios locales
- 🧠 **Entrenamiento**: Crea modelo personalizado por usuario
- ✅ **Reconocimiento**: Compara con umbral de confianza adaptativo

**Configuración Automática de Umbrales:**

```python
CONFIDENCE_THRESHOLDS = {
    'webcam_pc': 50,      # Cámara PC (más estricto)
    'droidcam': 80,       # DroidCam (más permisivo)
    'unknown': 60         # Desconocida (intermedio)
}
```

#### **ArUco Detection (`marker_detection.py`)**

**Detección y estimación de pose para marcadores ArUco.**

```python
def initialize_aruco_detector() -> bool
def detect_and_estimate_pose(frame, camera_matrix, dist_coeffs, marker_size)
    -> Tuple[corners, ids, annotated_frame, rvecs, tvecs]
```

**Marcadores Utilizados:**

- 🆔 **ID 23**: Marcador de menú AR
- 🆔 **ID 24**: Marcador de modelo 3D (futuro uso)

### **3. AR Rendering (`ar_rendering/`)**

#### **3D Model Viewer (`scene_renderer.py`)**

**Renderizador 3D usando Pyrender con soporte para GLB y OBJ.**

```python
class PyrenderModelViewer:
    def load_car_model(self, car_dict: dict) -> bool
    def render_model_on_marker(self, frame, rvec, tvec, camera_matrix, dist_coeffs) -> np.ndarray
    def setup_scene(self, camera_matrix, frame_width, frame_height) -> None
    def cleanup(self) -> None
```

**Pipeline de Renderizado:**

1. 🔄 **Carga**: Trimesh para importar modelos 3D
2. 🎨 **Materiales**: Sanitización automática de texturas problemáticas
3. 💡 **Iluminación**: Configuración adaptativa según tipo de modelo
4. 🎬 **Renderizado**: Pyrender con cámara calibrada
5. 🖼️ **Composición**: Alpha blending sobre frame de cámara

**Formatos Soportados:**

- ✅ **OBJ + MTL** - Modelos con materiales externos
- ✅ **GLB/GLTF** - Modelos embebidos con texturas

#### **AR Menu (`ar_menu.py`)**

**Interfaz de menú superpuesto sobre marcadores ArUco.**

```python
class ARMenu:
    def draw_menu_overlay(self, frame: np.ndarray, corners) -> np.ndarray
    def handle_selection(self, key: int) -> Union[dict, str, None]
```

### **4. Audio Processing (`audio_processing/`)**

#### **Voice Commands (`voice_commands.py`)**

**Sistema de reconocimiento de voz con comandos en español.**

```python
class VoiceController:
    def get_voice_command(self) -> Optional[dict]
    def toggle_listening(self) -> None
    def get_status_text(self) -> str
    def cleanup(self) -> None
```

**Comandos Soportados:**

```python
VOICE_COMMANDS = {
    'ferrari': {'action': 'select_car', 'car_id': 1},
    'porsche': {'action': 'select_car', 'car_id': 2},
    'menú': {'action': 'menu'},
    'salir': {'action': 'logout'},
    'volver': {'action': 'back'}
}
```

**Estados del Micrófono:**

- 🔇 **OFF**: Micrófono desactivado
- 🎙️ **ON**: Escuchando comandos
- ⚠️ **ERROR**: Problema con el micrófono

### **5. Data Management (`data_management/`)**

#### **User Manager (`user_manager.py`)**

**CLI para gestión avanzada de usuarios registrados.**

```bash
# Comandos disponibles
python user_manager.py list                    # Listar usuarios
python user_manager.py details <user_id>       # Detalles de usuario
python user_manager.py delete <user_id>        # Eliminar usuario
python user_manager.py fix-structure          # Reparar directorios
python user_manager.py retrain <user_id>      # Reentrenar modelo
```

**Funcionalidades:**

- 📋 **Listado**: Usuarios con estadísticas de imágenes y modelos
- 🔍 **Detalles**: Información completa por usuario
- 🗑️ **Eliminación**: Limpieza completa de datos
- 🔧 **Reparación**: Reestructuración de directorios inconsistentes
- 🧠 **Reentrenamiento**: Regeneración de modelos LBPH

---

## 🔄 **Flujo de Estados**

### **Diagrama de Estados:**

```
    START
      │
      ▼
┌─────────────┐
│   WELCOME   │◄─────────────────────────┐
│             │                          │
│ L: Login    │                          │
│ R: Register │                          │
│ Q: Quit     │                          │
└─────┬───────┘                          │
      │                                  │
      ▼                                  │
┌─────────────┐  ESC  ┌─────────────┐    │
│    LOGIN    │──────►│  REGISTER   │    │
│             │       │   PROMPT    │    │
│ Facial Auth │       │             │    │
│ ENTER: Menu │       └─────┬───────┘    │
└─────┬───────┘             │            │
      │                     ▼            │
┌─────────────┐      ┌─────────────┐      │
│  MAIN_MENU  │      │  REGISTER   │      │
│     AR      │      │  CAPTURE    │      │
│             │      │             │      │
│ Voice Ctrl  │      │ 50 images   │      │
│ ArUco Menu  │      └─────┬───────┘      │
│ 3D Models   │            │              │
└─────┬───────┘     ┌─────────────┐       │
      │             │  REGISTER   │       │
      │             │   TRAIN     │       │
      │             │             │       │
      │             │ LBPH Model  │       │
      │             └─────┬───────┘       │
      │                   │               │
      │                   ▼               │
      │             ┌─────────────┐       │
      │             │    LOGIN    │       │
      │             └─────┬───────┘       │
      │                   │               │
      └───────────────────┼───────────────┘
                          │
      Q: Logout ──────────┘
```

### **Transiciones Detalladas:**

#### **WELCOME → LOGIN:**

- ✅ Usuario presiona 'L'
- 🎯 Activación de reconocimiento facial
- 📹 Inicio de procesamiento en tiempo real

#### **WELCOME → REGISTER:**

- ✅ Usuario presiona 'R'
- 📝 Transición a REGISTER_PROMPT_ID
- ⌨️ Solicitud de ID por terminal

#### **LOGIN → MAIN_MENU_AR:**

- ✅ Reconocimiento facial exitoso (confianza < umbral)
- ✅ Usuario presiona ENTER para confirmar
- 🚀 Activación de AR, voz y detección ArUco

#### **Estados de Registro:**

1. **REGISTER_PROMPT_ID**: Solicitar nombre de usuario
2. **REGISTER_CAPTURE**: Capturar 50 imágenes faciales
3. **REGISTER_TRAIN**: Entrenar modelo LBPH
4. **LOGIN**: Redirigir para autenticación

---

## 👨‍💻 **Créditos y Autoría**

### **Desarrollador Principal:**

- **👤 Nombre**: David González Palma
- **🎓 Universidad**: Universidad de Granada (UGR)
- **📚 Asignatura**: CUIA (Computación Ubicua e Inteligencia Ambiental)
- **📅 Año Académico**: 2024-2025

### **Contexto Académico:**

Este proyecto ha sido desarrollado como **trabajo práctico** para la asignatura **CUIA (Computación Ubicua e Inteligencia Ambiental)** del programa de estudios de la **Universidad de Granada**. El objetivo es demostrar la integración de tecnologías de **Realidad Aumentada**, **Computer Vision** y **Machine Learning** en una aplicación de **computación ubicua** que proporciona una experiencia **inteligente y adaptativa**.

### **Relación con Computación Ubicua e Inteligencia Ambiental:**

- ✅ **Computación Ubicua**: Sistema AR que se integra naturalmente en el entorno físico
- ✅ **Inteligencia Ambiental**: Reconocimiento facial automático y adaptación por contexto
- ✅ **Interacción Natural**: Control por voz y gestos visuales sin interfaces tradicionales
- ✅ **Adaptabilidad**: Configuración automática según hardware disponible
- ✅ **Transparencia**: Tecnología que funciona de forma invisible al usuario

### **Tecnologías Demostradas:**

- ✅ **Computer Vision**: Detección facial, ArUco markers, calibración de cámara
- ✅ **Machine Learning**: Algoritmo LBPH para reconocimiento facial personalizado
- ✅ **Realidad Aumentada**: Renderizado 3D contextual sobre marcadores físicos
- ✅ **Procesamiento de Audio**: Reconocimiento de voz en tiempo real
- ✅ **Computación Ubicua**: Integración transparente de múltiples modalidades
- ✅ **Inteligencia Ambiental**: Adaptación automática al contexto y usuario

### **Objetivos Académicos de CUIA Cumplidos:**

1. 🎯 **Ubicuidad**: Sistema que funciona de forma natural en el entorno
2. 🧠 **Inteligencia Ambiental**: Reconocimiento automático y adaptación contextual
3. 🔄 **Interacción Natural**: Múltiples modalidades sin interfaces tradicionales
4. 📊 **Adaptabilidad**: Configuración automática según hardware disponible
5. 🌐 **Integración Transparente**: Tecnología invisible al usuario final
6. 📚 **Documentación Técnica**: Análisis completo de aspectos ubicuos

---

## 🏛️ **Información Institucional**

### **Universidad de Granada**

- 🌐 **Web**: https://www.ugr.es
- 📍 **Ubicación**: Granada, Andalucía, España
- 🎓 **Facultad**: Escuela Técnica Superior de Ingenierías Informática y de Telecomunicación (ETSIIT)

### **Asignatura CUIA**

- 📖 **Nombre Completo**: Computación Ubicua e Inteligencia Ambiental
- 🎯 **Objetivos**: Desarrollo de sistemas que integren computación ubicua con inteligencia ambiental
- 🔬 **Metodología**: Proyectos prácticos con tecnologías ubicuas y adaptativas
- 📊 **Evaluación**: Implementación, análisis de ubicuidad y presentación de soluciones

### **Aspectos de Computación Ubicua Implementados:**

- 🌐 **Transparencia**: El sistema funciona sin que el usuario perciba la complejidad tecnológica
- 🔄 **Adaptabilidad**: Configuración automática según cámara y hardware disponible
- 🎭 **Multimodalidad**: Integración de voz, visión y gestos de forma natural
- 🧠 **Inteligencia**: Reconocimiento facial personalizado y contextual
- 📱 **Ubicuidad**: Funciona con diferentes tipos de cámara (PC, móvil, externa)

---

## 📜 **Declaración Académica**

Este proyecto constituye un **trabajo original** desarrollado específicamente para la asignatura **CUIA (Computación Ubicua e Inteligencia Ambiental)** de la Universidad de Granada. Todas las implementaciones, diseños y documentación han sido realizados como parte del proceso de aprendizaje y evaluación académica en el ámbito de la **computación ubicua**.

### **Contribución a la Computación Ubicua:**

El proyecto demuestra cómo las tecnologías de **Computer Vision**, **Machine Learning** y **Realidad Aumentada** pueden integrarse para crear un sistema **ubicuo** que:

- 🔍 **Reconoce automáticamente** a los usuarios sin intervención manual
- 🎨 **Adapta la experiencia** según el contexto y preferencias
- 🎙️ **Responde a comandos naturales** por voz en español
- 📹 **Funciona con hardware diverso** de forma transparente
- 🎯 **Proporciona información contextual** mediante AR

### **Licencia y Uso Académico:**

- ✅ **Uso Educativo**: Permitido para fines académicos y de aprendizaje
- ✅ **Código Abierto**: Disponible para revisión y mejora
- ⚠️ **Atribución**: Requerida para cualquier uso o modificación
- 📚 **Documentación**: Debe mantenerse la referencia académica original

---

## 🚀 **Conclusión**

**ARCar Showroom** representa una implementación completa de un sistema de **Computación Ubica e Inteligencia Ambiental** desarrollado como **proyecto académico** para la asignatura **CUIA** de la **Universidad de Granada**. El sistema demuestra cómo integrar múltiples tecnologías para crear una experiencia **ubicua, inteligente y natural**.

### **Logros en Computación Ubicua:**

- ✅ **Transparencia Tecnológica**: El usuario no percibe la complejidad del sistema
- ✅ **Adaptabilidad Contextual**: Configuración automática según hardware y usuario
- ✅ **Interacción Natural**: Múltiples modalidades sin interfaces tradicionales
- ✅ **Inteligencia Ambiental**: Reconocimiento y adaptación automática
- ✅ **Ubicuidad**: Funciona con hardware diverso de forma consistente

### **Tecnologías Integradas para Ubicuidad:**

- 🔬 **Computer Vision**: Percepción visual del entorno y usuarios
- 🧠 **Machine Learning**: Inteligencia adaptativa y reconocimiento personalizado
- 🎨 **Realidad Aumentada**: Información contextual superpuesta al mundo real
- 🎙️ **Procesamiento de Audio**: Interacción natural por voz
- 💾 **Gestión Inteligente**: Adaptación automática de configuraciones

### **Valor Académico para CUIA:**

Este proyecto demuestra la **aplicación práctica** de conceptos de **Computación Ubicua e Inteligencia Ambiental** en un contexto real. La integración transparente de múltiples tecnologías y la adaptación automática al contexto reflejan un **entendimiento profundo** de los principios de ubicuidad e inteligencia ambiental impartidos en la asignatura.

### **Casos de Uso Ubicuos:**

- 🚗 **Showrooms Inteligentes**: Experiencias adaptativas según el usuario
- 🏢 **Espacios Reactivos**: Entornos que responden al contexto
- 🎓 **Educación Ubicua**: Aprendizaje natural e inmersivo
- 🔬 **Investigación Aplicada**: Base para sistemas ubicuos más complejos

### **Contribución Académica:**

El sistema está diseñado para ser **ubicuo**, **inteligente** y **educativo**, proporcionando una base sólida tanto para la **evaluación académica** en CUIA como para el **desarrollo futuro** de aplicaciones de computación ubicua más avanzadas.

---

**Desarrollado por: David González Palma**  
**Universidad de Granada - Asignatura CUIA**  
**Computación Ubicua e Inteligencia Ambiental**  
**Proyecto Académico 2024-2025**

---

**© 2025 David González Palma - Universidad de Granada - Asignatura CUIA**  
**ARCar Showroom - Proyecto Académico de Computación Ubicua e Inteligencia Ambiental**
