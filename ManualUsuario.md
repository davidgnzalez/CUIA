# ARCar Showroom - Manual de Usuario

## 📋 **Índice**

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Primera Configuración](#primera-configuración)
5. [Guía de Inicio Rápido](#guía-de-inicio-rápido)
6. [Registro de Usuario](#registro-de-usuario)
7. [Inicio de Sesión](#inicio-de-sesión)
8. [Experiencia AR](#experiencia-ar)
9. [Control por Voz](#control-por-voz)
10. [Gestión de Usuarios](#gestión-de-usuarios)
11. [Solución de Problemas](#solución-de-problemas)
12. [Preguntas Frecuentes](#preguntas-frecuentes)
13. [Consejos y Trucos](#consejos-y-trucos)
14. [Soporte](#soporte)

---

## 🎯 **Introducción**

¡Bienvenido a **ARCar Showroom**! Esta aplicación te permite explorar modelos 3D de automóviles de lujo mediante **Realidad Aumentada (AR)**. El sistema utiliza **reconocimiento facial** para identificarte automáticamente y te permite interactuar con los modelos usando **comandos de voz** y **marcadores ArUco**.

### **¿Qué puedes hacer con ARCar Showroom?**

- 🚗 **Visualizar modelos 3D** de Ferrari F40 y Porsche 911
- 👤 **Autenticación automática** mediante reconocimiento facial
- 🎙️ **Control por voz** con comandos en español
- 📱 **Flexibilidad de cámara** - funciona con webcam del PC, DroidCam o cámaras externas
- 🎨 **Experiencia inmersiva** con realidad aumentada

### **Principios de Diseño**

ARCar Showroom está diseñado siguiendo los principios de **Computación Ubicua e Inteligencia Ambiental**:

- 🌐 **Transparencia**: La tecnología funciona sin que notes su complejidad
- 🧠 **Inteligencia**: Se adapta automáticamente a ti y tu hardware
- 🔄 **Naturalidad**: Interacción por voz y gestos, sin interfaces complicadas
- 📱 **Ubicuidad**: Funciona consistentemente en diferentes dispositivos

---

## 💻 **Requisitos del Sistema**

### **Requisitos Mínimos**

- **Sistema Operativo**: Linux (Ubuntu 18.04+), Windows 10+, macOS 10.14+
- **Python**: 3.8 o superior
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Cámara**: Webcam integrada, USB o DroidCam
- **Micrófono**: Para control por voz (opcional)
- **Conexión a Internet**: Para reconocimiento de voz

### **Hardware Recomendado**

- **Procesador**: Intel i5 o AMD Ryzen 5 (o superior)
- **Gráficos**: Tarjeta gráfica compatible con OpenGL 3.3+
- **Cámara**: Resolución mínima 640x480, preferible 720p o superior
- **Iluminación**: Ambiente bien iluminado para mejor reconocimiento facial

### **Software Necesario**

- **Python 3.8+** con pip
- **OpenCV 4.x** con módulos contrib
- **Dependencias específicas** (se instalan automáticamente):
  - Trimesh + Pyrender
  - SpeechRecognition + PyAudio
  - NumPy, Pillow

---

## 🛠️ **Instalación**

### **Paso 1: Preparar el Entorno**

#### **En Linux (Ubuntu/Debian):**

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade

# Instalar dependencias del sistema
sudo apt install python3 python3-pip python3-venv
sudo apt install portaudio19-dev python3-pyaudio
sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 libxss1
```

#### **En Windows:**

```powershell
# Instalar Python desde https://python.org
# Asegurarse de marcar "Add Python to PATH"
# Instalar Microsoft Visual C++ Redistributable
```

#### **En macOS:**

```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install python portaudio
```

### **Paso 2: Obtener ARCar Showroom**

```bash
# Opción 1: Clonar desde repositorio
git clone <repository_url>
cd ARCar_Showroom

# Opción 2: Descomprimir archivo
unzip ARCar_Showroom.zip
cd ARCar_Showroom
```

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### **Paso 4: Instalar Dependencias**

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### **Paso 5: Verificar Instalación**

```bash
# Test de cámaras disponibles
python test_cameras.py

# Test de reconocimiento de voz
python test_voice.py

# Si todo funciona, verás:
# ✅ Cámaras detectadas
# ✅ Micrófono funcionando
```

---

## ⚙️ **Primera Configuración**

### **Configuración de Cámara**

#### **Opción 1: Usar Webcam del PC (Recomendado)**

- ✅ **Automático**: ARCar Showroom detecta automáticamente tu webcam
- 📹 **Índice 0**: Normalmente es la cámara integrada del portátil
- 💡 **Mejor rendimiento**: Ideal para reconocimiento facial

#### **Opción 2: Configurar DroidCam (Móvil como cámara)**

**En el móvil:**

1. 📱 Descarga **DroidCam** desde Play Store/App Store
2. 🌐 Conecta móvil y PC a la misma red WiFi
3. ▶️ Abre DroidCam y anota la **IP que aparece**

**En el PC:**

```bash
# Linux: Instalar DroidCam Client
sudo apt install droidcam

# Conectar (sustituye IP_DEL_MOVIL por la IP real)
droidcam-cli wifi IP_DEL_MOVIL 4747

# Ejemplo: droidcam-cli wifi 192.168.1.100 4747
```

**En Windows:**

1. 💻 Descarga DroidCam Client desde [droidcam.com](https://droidcam.com)
2. 🔗 Conecta usando la IP mostrada en el móvil

### **Configuración de Marcadores ArUco**

#### **Imprimir Marcador (Obligatorio para AR)**

1. 📄 Ve a la carpeta `assets/markers/`
2. 🖨️ Imprime el marcador **ID 23** en papel blanco
3. 📏 **Tamaño recomendado**: 5cm x 5cm mínimo
4. ✂️ Recorta con precisión, manteniendo el borde blanco

#### **Consejos para el Marcador:**

- 📝 **Papel mate**: Evita brillos que confundan la cámara
- 📐 **Bordes limpios**: Recorta con precisión
- 🏠 **Superficie plana**: Coloca sobre mesa o superficie estable
- 💡 **Buena iluminación**: Evita sombras sobre el marcador

### **Test de Configuración**

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar test completo
python test_cameras.py
python test_voice.py

# Iniciar aplicación por primera vez
python main.py
```

---

## 🚀 **Guía de Inicio Rápido**

### **Tu Primera Sesión (5 minutos)**

#### **1. Ejecutar la Aplicación**

```bash
cd ARCar_Showroom
source venv/bin/activate  # Solo en Linux/Mac
python main.py
```

#### **2. Pantalla de Bienvenida**

```
🏠 BIENVENIDO A ARCar SHOWROOM
┌─────────────────────────────────┐
│  Presiona 'L' para Login        │
│  Presiona 'R' para Registrarte  │  ← ¡Empieza aquí!
│  Presiona 'Q' para Salir        │
└─────────────────────────────────┘
```

#### **3. Registro Rápido**

1. ⌨️ **Presiona 'R'** para registrarte
2. 📝 **Escribe tu nombre** en el terminal (ej: "maria")
3. 📸 **Mira a la cámara** hasta que veas 1 cara detectada
4. 🔄 **Presiona 'C'** repetidamente para capturar 50 fotos
5. ⏳ **Espera** el entrenamiento automático (30-60 segundos)

#### **4. Primer Login**

1. 👤 **Mira a la cámara** - deberías ver tu nombre en verde
2. ⏎ **Presiona ENTER** para confirmar
3. 🎉 **¡Bienvenido al showroom AR!**

#### **5. Experiencia AR**

1. 📄 **Coloca el marcador impreso** frente a la cámara
2. 🎛️ **Verás el menú AR** superpuesto sobre el marcador
3. 🔢 **Presiona '1'** para Ferrari o **'2'** para Porsche
4. 🚗 **¡Disfruta del modelo 3D!**

---

## 👤 **Registro de Usuario**

### **Proceso Detallado**

#### **Inicio del Registro**

1. 🏠 Desde la pantalla de bienvenida, presiona **'R'**
2. 📝 El sistema te pedirá tu nombre en el terminal:
   ```
   👤 REGISTRO DE NUEVO USUARIO
   ============================
   Introduce tu ID de usuario: _
   ```

#### **Elegir un Buen ID de Usuario**

- ✅ **Solo letras y números**: Sin espacios ni caracteres especiales
- ✅ **Único**: No puede existir otro usuario con el mismo nombre
- ✅ **Fácil de recordar**: Tu nombre, apodo o iniciales
- ❌ **Evitar**: Caracteres especiales como ñ, acentos, espacios

**Ejemplos válidos:** `david`, `maria123`, `juanperez`, `admin`

#### **Captura de Imágenes Faciales**

```
📸 CAPTURA DE IMÁGENES - INSTRUCCIONES:
=====================================
• Colócate frente a la cámara con buena iluminación
• Mantén la cara visible y sin obstáculos
• Cuando veas "✅ 1 cara detectada", presiona 'C'
• Necesitas capturar 50 imágenes variadas
• Varía ligeramente la posición entre capturas
```

#### **Consejos para Mejores Resultados**

- 💡 **Iluminación frontal**: Evita sombras en la cara
- 👓 **Sin obstáculos**: Quítate gafas de sol o gorras si es posible
- 📐 **Ángulos variados**: Gira ligeramente la cabeza entre capturas
- 😊 **Expresiones naturales**: Sonríe, serio, neutral
- 📏 **Distancia consistente**: 50-100cm de la cámara

#### **Progreso de Captura**

```
📸 Capturando imágenes: 15/50
✅ 1 cara detectada - Presiona 'C' para capturar
⚠️ Imagen guardada: face_015.jpg
```

#### **Entrenamiento Automático**

Una vez capturadas las 50 imágenes:

```
🧠 ENTRENANDO MODELO FACIAL...
==============================
• Procesando 50 imágenes...
• Creando modelo LBPH personalizado...
• Guardando en: assets/face_data/embeddings/models/
✅ ¡Entrenamiento completado!
```

#### **Finalización**

- ✅ **Modelo guardado** automáticamente
- 🔄 **Redirigido al login** para probar el reconocimiento
- 📊 **Usuario añadido** al sistema permanentemente

---

## 🔐 **Inicio de Sesión**

### **Autenticación Facial**

#### **Acceso al Login**

1. 🏠 Desde la pantalla de bienvenida, presiona **'L'**
2. 📹 La cámara comenzará a buscar tu cara automáticamente

#### **Proceso de Reconocimiento**

```
🔍 BUSCANDO USUARIO...
=====================
• Mira directamente a la cámara
• Mantén buena iluminación
• El sistema comparará con usuarios registrados
```

#### **Estados del Reconocimiento**

**Usuario Detectado (Verde):**

```
✅ Usuario reconocido: maria
Confianza: 45.2 (Excelente)
⏎ Presiona ENTER para continuar
```

**Usuario No Detectado (Rojo):**

```
❌ Usuario no reconocido
Confianza: 78.9 (Insuficiente)
🔄 Intenta mejorar la iluminación
```

**Sin Cara Detectada (Amarillo):**

```
⚠️ No se detecta ninguna cara
📸 Colócate frente a la cámara
```

#### **Controles Durante Login**

- ⏎ **ENTER**: Confirmar usuario reconocido
- 🔙 **B**: Volver a la pantalla de bienvenida
- ⚠️ **ESC**: Cancelar y volver al menú

#### **Consejos para Mejor Reconocimiento**

- 💡 **Iluminación similar**: Usa condiciones parecidas al registro
- 👤 **Posición frontal**: Mira directamente a la cámara
- 📏 **Distancia consistente**: Misma distancia que durante el registro
- ⏰ **Paciencia**: El sistema necesita unos segundos para analizar

### **Solución de Problemas de Login**

#### **"No me reconoce nunca"**

1. 🔧 Verifica la iluminación - debe ser similar al registro
2. 📐 Ajusta la distancia a la cámara
3. 🔄 Considera reentrenar tu modelo:
   ```bash
   python data_management/user_manager.py retrain tu_nombre
   ```

#### **"Me reconoce a veces"**

- 💡 Mejora la iluminación ambiental
- 📹 Limpia la lente de la cámara
- 👤 Mantén posición frontal estable

#### **"Reconoce a otra persona"**

- 🔧 El modelo necesita más imágenes de entrenamiento
- 🗑️ Considera eliminar y re-registrar el usuario:
  ```bash
  python data_management/user_manager.py delete usuario_problema
  ```

---

## 🎨 **Experiencia AR**

### **Navegación en el Showroom**

#### **Interfaz Principal**

Una vez autenticado, accedes al **Showroom AR** donde puedes:

- 🎨 Ver modelos 3D de automóviles
- 🎙️ Controlar por voz
- 📱 Interactuar con marcadores ArUco
- 🔄 Cambiar entre diferentes coches

#### **Usando Marcadores ArUco**

**Preparación:**

1. 📄 **Coloca el marcador impreso** sobre una superficie plana
2. 📹 **Apunta la cámara** hacia el marcador
3. 💡 **Asegura buena iluminación** sin sombras sobre el marcador

**Detección Automática:**

```
🎯 MARCADOR DETECTADO - ID: 23
═══════════════════════════════
┌─────────────────────┐
│  🚗 SELECCIONA:     │
│  [1] Ferrari F40    │  ← Presiona '1'
│  [2] Porsche 911    │  ← Presiona '2'
│  [M] Menú          │
└─────────────────────┘
```

### **Modelos 3D Disponibles**

#### **Ferrari F40**

- 🔢 **Activación**: Presiona '1' o di "ferrari"
- 🎨 **Características**: Modelo detallado con materiales metálicos
- 📏 **Escala**: Optimizada para marcadores de 5cm
- 🚗 **Detalles**: Icónico superdeportivo de los 80s

#### **Porsche 911**

- 🔢 **Activación**: Presiona '2' o di "porsche"
- 🎨 **Características**: Modelo GLB con texturas embebidas
- 📏 **Escala**: Ligeramente más pequeño que el Ferrari
- 🚗 **Detalles**: Clásico deportivo alemán

### **Controles de la Experiencia AR**

#### **Teclado:**

- 🔢 **'1'**: Seleccionar Ferrari F40
- 🔢 **'2'**: Seleccionar Porsche 911
- 🎛️ **'M'**: Volver al menú de selección
- 🚪 **'Q'**: Cerrar sesión (logout)
- 🎙️ **'V'**: Activar/desactivar control por voz
- ⚠️ **ESC**: Cancelar acción actual

#### **Estados Visuales:**

**Modelo Cargado Correctamente:**

```
✅ Ferrari F40 renderizado
🎨 Material: Rojo metálico
📐 Escala: 5% del tamaño real
🎯 Posición: Centrado en marcador
```

**Error de Carga:**

```
❌ Error cargando modelo
🔄 Intentando fallback...
⚠️ Usando material por defecto
```

### **Optimización de la Experiencia**

#### **Rendimiento:**

- 📱 **Cámara estable**: Evita movimientos bruscos
- 💻 **Cierra aplicaciones**: Libera RAM para mejor rendimiento
- 🌐 **Marcador visible**: Mantén el marcador completamente visible

#### **Calidad Visual:**

- 💡 **Iluminación uniforme**: Sin sombras directas
- 📄 **Marcador plano**: Sin arrugas ni dobleces
- 📏 **Distancia óptima**: 20-50cm entre cámara y marcador

---

## 🎙️ **Control por Voz**

### **Activación del Control por Voz**

#### **Habilitar Micrófono:**

1. 🎨 Asegúrate de estar en el **Showroom AR**
2. 🎙️ **Presiona 'V'** para activar el control por voz
3. 🟢 Verás el indicador cambiar a **"🎙️ VOZ ON"**

#### **Estados del Micrófono:**

- 🔇 **VOZ OFF**: Micrófono desactivado
- 🎙️ **VOZ ON**: Escuchando comandos activamente
- ⚠️ **SIN MIC**: Problema con el micrófono

### **Comandos de Voz Disponibles**

#### **Selección de Modelos:**

```
🎙️ COMANDOS PARA COCHES:
========================
• "ferrari" → Mostrar Ferrari F40
• "f cuarenta" → Mostrar Ferrari F40
• "porsche" → Mostrar Porsche 911
• "novecientos once" → Mostrar Porsche 911
```

#### **Navegación:**

```
🎙️ COMANDOS DE NAVEGACIÓN:
==========================
• "menú" / "menu" → Volver al menú
• "volver" → Volver al menú
• "salir" → Cerrar sesión
```

### **Consejos para Mejor Reconocimiento**

#### **Técnica de Voz:**

- 🗣️ **Habla claro**: Pronunciación clara y pausada
- 🔊 **Volumen moderado**: Ni muy bajo ni muy alto
- ⏰ **Espera confirmación**: Pausa entre comandos
- 🌐 **Conexión a internet**: Necesaria para el reconocimiento

#### **Entorno Ideal:**

- 🔇 **Ambiente silencioso**: Minimiza ruido de fondo
- 📱 **Micrófono cerca**: Máximo 50cm de distancia
- 💨 **Sin viento**: Evita corrientes de aire

#### **Solución de Problemas de Voz:**

**"No responde a comandos":**

1. 🔍 Verifica que el indicador muestre "🎙️ VOZ ON"
2. 🌐 Comprueba conexión a internet
3. 🔧 Test del micrófono:
   ```bash
   python test_voice.py
   ```

**"Reconoce comandos incorrectos":**

- 🗣️ Habla más pausado y claro
- 🔇 Reduce ruido ambiental
- 📱 Acércate más al micrófono

**"Error de micrófono":**

```bash
# Linux: Instalar dependencias
sudo apt install portaudio19-dev python3-pyaudio

# Verificar permisos de micrófono
# En configuración del sistema
```

### **Feedback Visual**

#### **Comando Reconocido:**

```
🎙️ Comando detectado: "ferrari"
✅ Cargando Ferrari F40...
🚗 ¡Modelo mostrado!
```

#### **Comando No Reconocido:**

```
🎙️ Audio captado: "algo incomprensible"
❌ Comando no reconocido
💡 Intenta: "ferrari", "porsche", "menú"
```

---

## 👥 **Gestión de Usuarios**

### **Herramienta de Línea de Comandos**

ARCar Showroom incluye un **potente gestor de usuarios** que te permite administrar todos los usuarios registrados.

#### **Acceso al Gestor:**

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar gestor de usuarios
python data_management/user_manager.py
```

### **Comandos Principales**

#### **Listar Todos los Usuarios**

```bash
python data_management/user_manager.py list
```

**Ejemplo de salida:**

```
👥 USUARIOS REGISTRADOS
==================================================
👤 david           | ID: 0   | Imágenes: 50  | Modelo: ✅
👤 maria           | ID: 1   | Imágenes: 50  | Modelo: ✅
👤 carlos          | ID: 2   | Imágenes: 45  | Modelo: ❌
```

#### **Ver Detalles de Usuario**

```bash
python data_management/user_manager.py details maria
```

**Ejemplo de salida:**

```
👤 DETALLES DE USUARIO: maria
========================================
ID numérico: 1
Directorio: /path/to/embeddings/maria
Imágenes: 50
Modelo existe: ✅
Imágenes existen: ✅
```

#### **Eliminar Usuario**

```bash
python data_management/user_manager.py delete carlos
```

**Proceso interactivo:**

```
🗑️ ELIMINANDO USUARIO: carlos
⚠️ ¿Estás seguro de eliminar 'carlos'? (y/N): y
✅ Directorio de imágenes eliminado
✅ Modelo eliminado
✅ Usuario 'carlos' eliminado completamente
```

#### **Reentrenar Modelo de Usuario**

```bash
python data_management/user_manager.py retrain david
```

**Proceso:**

```
🔧 REENTRENANDO MODELO: david
📚 Entrenando con 50 imágenes...
✅ Modelo reentrenado: david.yml
```

#### **Reparar Estructura de Directorios**

```bash
python data_management/user_manager.py fix-structure
```

**Utilidad:**

- 🔧 Reorganiza directorios mal estructurados
- 📁 Mueve imágenes a ubicaciones correctas
- 🧹 Limpia archivos temporales

### **Casos de Uso Comunes**

#### **Usuario No Se Reconoce:**

1. 🔍 **Verificar datos**:
   ```bash
   python data_management/user_manager.py details usuario_problema
   ```
2. 🔧 **Reentrenar modelo**:
   ```bash
   python data_management/user_manager.py retrain usuario_problema
   ```

#### **Limpiar Usuarios de Prueba:**

```bash
# Eliminar usuarios de prueba
python data_management/user_manager.py delete test
python data_management/user_manager.py delete prueba
python data_management/user_manager.py delete temporal
```

#### **Backup de Usuarios:**

```bash
# Copiar directorio completo
cp -r assets/face_data/embeddings/ backup_usuarios_$(date +%Y%m%d)/
cp data_management/user_id_map.json backup_usuarios_$(date +%Y%m%d)/
```

#### **Restaurar Usuario:**

```bash
# Copiar desde backup
cp -r backup_usuarios_20241201/maria/ assets/face_data/embeddings/
cp backup_usuarios_20241201/maria.yml assets/face_data/embeddings/models/
# Editar user_id_map.json manualmente
```

---

## 🔧 **Solución de Problemas**

### **Problemas de Cámara**

#### **"No se detecta ninguna cámara"**

**Diagnóstico:**

```bash
python test_cameras.py
```

**Soluciones:**

1. 📹 **Verificar conexión física** de la cámara
2. 🔄 **Cerrar otras aplicaciones** que usen la cámara (Zoom, Skype, etc.)
3. 🐧 **En Linux**, verificar permisos:
   ```bash
   sudo usermod -a -G video $USER
   # Reiniciar sesión
   ```
4. 🔧 **Probar diferentes índices**:
   ```bash
   # Editar core/config.py
   CAMERA_INDEX = 0  # Probar 0, 1, 2, etc.
   ```

#### **"Cámara se congela o va lenta"**

**Soluciones:**

- 💻 **Cerrar aplicaciones** que consuman CPU
- 📹 **Limpiar lente** de la cámara
- 🔄 **Reiniciar aplicación**:
  ```bash
  # Ctrl+C para cerrar
  python main.py  # Reiniciar
  ```

#### **"DroidCam no conecta"**

**Verificaciones:**

1. 🌐 **Misma red WiFi** - móvil y PC conectados
2. 📱 **DroidCam activo** en el móvil
3. 🔗 **IP correcta** - verificar en la app del móvil
4. 🚪 **Puerto 4747** - debe estar abierto

**Test de conexión:**

```bash
# Ping al móvil
ping IP_DEL_MOVIL

# Test de puerto
telnet IP_DEL_MOVIL 4747
```

### **Problemas de Reconocimiento Facial**

#### **"Nunca me reconoce"**

**Diagnóstico paso a paso:**

1. 🔍 **Verificar usuario existe**:

   ```bash
   python data_management/user_manager.py details tu_nombre
   ```

2. 📊 **Estadísticas esperadas**:

   - ✅ Imágenes: 50
   - ✅ Modelo existe: ✅
   - ✅ ID numérico: asignado

3. 🔧 **Reentrenar modelo**:

   ```bash
   python data_management/user_manager.py retrain tu_nombre
   ```

4. 🎯 **Ajustar umbral** (si usas DroidCam):
   ```python
   # En core/app_manager.py, línea ~32:
   # Aumentar umbral para DroidCam
   if camera_index == 2:
       confidence_threshold = 90  # Más permisivo
   ```

#### **"Me confunde con otro usuario"**

**Soluciones:**

1. 🗑️ **Eliminar usuarios problemáticos**:

   ```bash
   python data_management/user_manager.py delete usuario_problema
   ```

2. 📸 **Re-registrarse con más variedad**:

   - Diferentes ángulos de cara
   - Varias expresiones
   - Ligeros cambios de iluminación

3. 🎯 **Hacer umbrales más estrictos**:
   ```python
   # En core/app_manager.py:
   confidence_threshold = 40  # Más estricto
   ```

#### **"Reconocimiento inconsistente"**

**Optimizaciones:**

- 💡 **Iluminación consistente** - misma luz que durante registro
- 📏 **Distancia fija** - mantener 50-100cm de la cámara
- 👤 **Posición frontal** - evitar perfiles o ángulos extremos
- ⏰ **Paciencia** - dar 2-3 segundos para que analice

### **Problemas de Renderizado 3D**

#### **"Modelos no aparecen"**

**Verificaciones:**

1. 📄 **Marcador visible** - completamente dentro del frame
2. 💡 **Iluminación del marcador** - sin sombras
3. 📐 **Marcador plano** - sin arrugas ni dobleces
4. 🎯 **ID correcto** - debe ser marcador ID 23

**Diagnóstico de archivos:**

```bash
# Verificar modelos 3D existen
ls -la assets/3d_models/ferrari-f40/source/f40.obj
ls -la assets/3d_models/porsche-911/911.glb
```

#### **"Modelos aparecen en rojo/sin texturas"**

**Explicación:**

- ✅ **Comportamiento normal** - el sistema usa fallback automático
- 🎨 **Material de respaldo** - rojo metálico cuando hay problemas de texturas
- 🔧 **No requiere acción** - el modelo es funcional

#### **"Error de OpenGL"**

**En servidores remotos (SSH):**

```bash
export PYOPENGL_PLATFORM=osmesa
python main.py
```

**En Linux con problemas gráficos:**

```bash
sudo apt install mesa-utils
glxinfo | grep OpenGL  # Verificar soporte OpenGL
```

### **Problemas de Audio/Voz**

#### **"Control por voz no funciona"**

**Test de micrófono:**

```bash
python test_voice.py
```

**Soluciones Linux:**

```bash
# Instalar dependencias
sudo apt install portaudio19-dev python3-pyaudio

# Verificar micrófono detectado
arecord -l
```

**Soluciones Windows:**

- 🎙️ **Verificar permisos** de micrófono en Configuración
- 🔊 **Configurar dispositivo** por defecto
- 🔄 **Reinstalar PyAudio**:
  ```powershell
  pip uninstall pyaudio
  pip install pyaudio
  ```

#### **"Reconoce mal los comandos"**

**Optimizaciones:**

- 🗣️ **Hablar más claro** y pausado
- 🔇 **Reducir ruido** ambiental
- 🌐 **Verificar internet** - necesario para Google Speech API
- 📱 **Acercarse al micrófono** - máximo 50cm

### **Problemas de Rendimiento**

#### **"Aplicación va lenta"**

**Optimizaciones:**

1. 💻 **Cerrar aplicaciones** innecesarias
2. 📱 **Usar resolución menor** en DroidCam (640x480)
3. 🔧 **Reducir calidad de cámara**:
   ```python
   # En main.py, después de cv2.VideoCapture():
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

#### **"Mucho uso de CPU"**

**Monitoreo:**

```bash
# Ver uso de recursos
top -p $(pgrep -f "python main.py")
```

**Optimizaciones:**

- 🎯 **Limitar FPS**:
  ```python
  # En main.py, en el bucle principal:
  time.sleep(0.033)  # ~30 FPS
  ```

---

## ❓ **Preguntas Frecuentes**

### **Funcionalidad General**

#### **¿Qué tipos de archivos 3D soporta?**

- ✅ **OBJ + MTL** - Modelos con materiales externos
- ✅ **GLB/GLTF** - Modelos con texturas embebidas
- ❌ **STL, PLY, DAE** - No soportados actualmente

#### **¿Puedo añadir mis propios modelos 3D?**

Sí, editando el archivo `core/config.py`:

```python
AVAILABLE_CARS.append({
    "id": 3,
    "name": "Mi Coche",
    "model_path": "mi-coche/modelo.obj",
    "scale": 0.05,
    "elevation": 0.01
})
```

#### **¿Cuántos usuarios puede manejar el sistema?**

- 👥 **Recomendado**: 5-10 usuarios para mejor rendimiento
- 🔢 **Máximo teórico**: Sin límite, pero el reconocimiento se vuelve más lento
- 💾 **Almacenamiento**: Cada usuario ocupa ~10MB (50 imágenes + modelo)

### **Cámaras y Hardware**

#### **¿Qué cámaras son compatibles?**

- ✅ **Webcam integrada** (laptops)
- ✅ **Cámara USB** externa
- ✅ **DroidCam** (móvil como webcam)
- ✅ **Cámaras IP** (con configuración manual)

#### **¿Necesito una cámara especial para AR?**

No, cualquier cámara que funcione con OpenCV es suficiente:

- 📹 **Resolución mínima**: 640x480
- 🎯 **Recomendada**: 720p o superior
- 📱 **Autofocus**: Preferible pero no obligatorio

#### **¿Funciona en Raspberry Pi?**

Sí, pero con limitaciones:

- 🐧 **SO**: Raspberry Pi OS
- 💻 **Modelo**: Pi 4 con 4GB RAM mínimo
- 🎨 **Renderizado**: Usar modo headless con osmesa
- ⚡ **Rendimiento**: Más lento, ~10-15 FPS

### **Reconocimiento Facial**

#### **¿Es seguro el reconocimiento facial?**

- 🔒 **Local**: Todo se procesa en tu ordenador
- 📁 **Privado**: No se envían datos a servidores externos
- 🗑️ **Eliminable**: Puedes borrar tus datos cuando quieras

#### **¿Qué algoritmo usa?**

**LBPH (Local Binary Pattern Histogram)**:

- 🧠 **Ventajas**: Rápido, ligero, funciona offline
- 📊 **Precisión**: Buena para usuarios conocidos
- 🔧 **Desventajas**: Sensible a cambios de iluminación

#### **¿Puedo usar el sistema con gafas?**

Sí, pero:

- ✅ **Gafas normales**: Sin problema
- ⚠️ **Gafas de sol**: Pueden reducir precisión
- 🔧 **Consejo**: Registrarse con y sin gafas alternadamente

### **Control por Voz**

#### **¿Qué idiomas soporta?**

- 🇪🇸 **Español**: Totalmente soportado
- 🇺🇸 **Inglés**: Parcialmente (comandos básicos)
- 🌐 **Otros**: Modificable en `audio_processing/voice_commands.py`

#### **¿Necesita internet?**

- 🌐 **Sí**: Para el reconocimiento de voz (Google Speech API)
- 📱 **Offline**: El resto de funciones trabajan sin internet
- 🔧 **Alternativa**: Posible implementar Vosk para uso offline

#### **¿Puedo añadir mis propios comandos?**

Sí, editando `audio_processing/voice_commands.py`:

```python
VOICE_COMMANDS.update({
    'mi_comando': {'action': 'custom_action', 'param': 'valor'}
})
```

### **Problemas Comunes**

#### **"La aplicación se cierra inesperadamente"**

**Causas comunes:**

1. 📹 **Cámara en uso** por otra aplicación
2. 💾 **Falta memoria** RAM
3. 🔧 **Dependencias faltantes**

**Ejecutar con debug:**

```bash
python main.py 2>&1 | tee debug.log
```

#### **"Los modelos 3D se ven raros"**

**Comportamientos normales:**

- 🔴 **Color rojo**: Material de fallback automático
- 📐 **Escala pequeña**: Optimizado para marcadores 5cm
- 🌀 **Rotación**: El modelo puede rotar según el marcador

#### **"¿Por qué necesito 50 imágenes?"**

- 🧠 **Variabilidad**: Para capturar diferentes ángulos y expresiones
- 📊 **Precisión**: Más datos = mejor reconocimiento
- ⚡ **Velocidad**: Algoritmo LBPH necesita muestras suficientes

---

## 💡 **Consejos y Trucos**

### **Optimización del Reconocimiento Facial**

#### **Durante el Registro:**

- 📸 **Varía las expresiones**: Sonríe, serio, sorprendido
- 📐 **Diferentes ángulos**: Gira ligeramente la cabeza (±15°)
- 💡 **Varias iluminaciones**: Registro en diferentes momentos del día
- 👤 **Distintas distancias**: 50cm, 70cm, 100cm de la cámara
- 🎭 **Con/sin accesorios**: Gafas, gorras (si las usas habitualmente)

#### **Para Mejor Reconocimiento:**

- 🕐 **Horario consistente**: Usar a las mismas horas si es posible
- 💡 **Setup de iluminación**: LED frontal suave, evitar sombras duras
- 📱 **Cámara fija**: Montar en trípode o soporte estable
- 🧹 **Lente limpia**: Limpiar regularmente la lente de la cámara

### **Configuración Avanzada**

#### **Crear Perfil de Usuario Robusto:**

```bash
# 1. Registro inicial
python main.py  # Registrarse normalmente

# 2. Añadir más variabilidad
python main.py  # Registrar nuevamente con condiciones diferentes
# (el sistema creará un segundo perfil interno)

# 3. Verificar robustez
python data_management/user_manager.py details tu_nombre
```

#### **Optimizar para tu Hardware:**

```python
# En core/config.py, ajustar según tu PC:

# PC potente (i7, 16GB RAM):
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# PC básico (i3, 4GB RAM):
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
```

#### **Configuración Multi-Usuario Familiar:**

```bash
# Crear usuarios familiares
python main.py
# Registrar: papa, mama, hijo1, hijo2
```
