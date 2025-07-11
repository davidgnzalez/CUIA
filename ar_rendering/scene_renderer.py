# ARCar_Showroom/ar_rendering/scene_renderer.py
import OpenGL
OpenGL.ERROR_CHECKING = True
from OpenGL.GL import *
from OpenGL.GLU import *
import cv2
import numpy as np
from PIL import Image # Asegurarse que está importado
import pyrender
import trimesh
from pyrender.constants import RenderFlags

MARKER_SIZE_METERS = 0.05

initialized = False
viewport_width = 0
viewport_height = 0
texture_id_test = None # Esta variable se llenará desde AppManager

def check_gl_error(operation_name=""): # Mantener esta útil función
    err = glGetError()
    if err != GL_NO_ERROR:
        print(f"OpenGL Error ({operation_name}): {gluErrorString(err)}")
        return True
    return False

def load_texture(image_path): # Usaremos tu versión que funcionaba
    print(f"DEBUG_SR_TEX: Intentando cargar textura desde: {image_path}")
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA") # Asegurar formato RGBA para transparencia
        img_data = np.array(list(img.getdata()), np.uint8)  # ✅ CORRECCIÓN

        tex_ids = glGenTextures(1)
        tex_id = tex_ids if isinstance(tex_ids, int) else tex_ids[0]
        glBindTexture(GL_TEXTURE_2D, tex_id); check_gl_error("glBindTexture")

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR); check_gl_error("glTexParameteri MIN_FILTER")
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR); check_gl_error("glTexParameteri MAG_FILTER")
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE); check_gl_error("glTexParameteri WRAP_S")
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE); check_gl_error("glTexParameteri WRAP_T")
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data); check_gl_error("glTexImage2D")
        glGenerateMipmap(GL_TEXTURE_2D); check_gl_error("glGenerateMipmap")
        
        glBindTexture(GL_TEXTURE_2D, 0); check_gl_error("glBindTexture(0)") # Desactivar
        print(f"DEBUG_SR_TEX: Textura cargada OK ({image_path}), ID: {tex_id}, Modo: {img.mode}, Tamaño: {img.size}")
        return tex_id
    except FileNotFoundError:
        print(f"Error: Archivo de textura no encontrado en {image_path}")
        return None
    except Exception as e:
        print(f"Error cargando textura {image_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def init_opengl(width, height):
    global initialized, viewport_width, viewport_height
    if initialized: return

    viewport_width = width
    viewport_height = height
    glViewport(0, 0, width, height); check_gl_error("glViewport")
    
    glEnable(GL_DEPTH_TEST); check_gl_error("glEnable(GL_DEPTH_TEST)")
    glDepthFunc(GL_LEQUAL); check_gl_error("glDepthFunc(GL_LEQUAL)")
    
    glDisable(GL_LIGHTING); check_gl_error("glDisable(GL_LIGHTING)")
    glDisable(GL_CULL_FACE); check_gl_error("glDisable(GL_CULL_FACE)")
    
    glEnable(GL_BLEND); check_gl_error("glEnable(GL_BLEND)") # Habilitar blending para RGBA
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); check_gl_error("glBlendFunc")

    glClearColor(0.0, 0.0, 0.0, 0.0); # Fondo negro y COMPLETAMENTE TRANSPARENTE
    check_gl_error("glClearColor")
    
    initialized = True
    print("OpenGL inicializado (Texturizado Activado, sin iluminación, sin culling, con blending).")

def draw_cube_with_texture_on_front(size=1.0): # Renombrada para claridad
    global texture_id_test
    # print("DEBUG_SR_CUBE: Dibujando cubo con textura en cara frontal.")
    s = size 
    v = [ # Vértices del cubo
        [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s], # Frontal: 0,1,2,3
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s]  # Trasera: 4,5,6,7
    ]
    # Coordenadas de Textura (para la cara frontal)
    tc = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL); check_gl_error("glPolygonMode")
    glBegin(GL_QUADS); check_gl_error("glBegin(GL_QUADS) for cube")
    
    # Cara Frontal: Aplicar textura
    if texture_id_test is not None:
        glEnable(GL_TEXTURE_2D); check_gl_error("glEnable(GL_TEXTURE_2D) for front face")
        glBindTexture(GL_TEXTURE_2D, texture_id_test); check_gl_error("glBindTexture for front face")
        # Usar glColor4f para posible transparencia de la textura si la imagen la tiene.
        # Si la textura es completamente opaca, el canal alfa de glColor no tendrá mucho efecto visible aquí
        # más allá de asegurar que no se tiñe de forma inesperada.
        glColor4f(1.0, 1.0, 1.0, 1.0) # Blanco opaco para que la textura se vea pura
        glTexCoord2fv(tc[0]); glVertex3fv(v[0])
        glTexCoord2fv(tc[1]); glVertex3fv(v[1])
        glTexCoord2fv(tc[2]); glVertex3fv(v[2])  # ✅ CORREGIDO: Paréntesis cerrado
        glTexCoord2fv(tc[3]); glVertex3fv(v[3])  # ✅ CORREGIDO: Paréntesis cerrado
        glBindTexture(GL_TEXTURE_2D, 0) # Desactivar la textura específica
        glDisable(GL_TEXTURE_2D) # Deshabilitar texturizado para las siguientes caras
        check_gl_error("Front face texturing")
    else: # Si no hay textura, dibujar en rojo
        glColor3f(1.0, 0.0, 0.0); glVertex3fv(v[0]); glVertex3fv(v[1]); glVertex3fv(v[2]); glVertex3fv(v[3])
    
    # Otras caras con colores sólidos
    glColor3f(0.0, 0.0, 1.0); glVertex3fv(v[4]); glVertex3fv(v[7]); glVertex3fv(v[6]); glVertex3fv(v[5]) # Trasera (AZUL)
    glColor3f(0.0, 1.0, 0.0); glVertex3fv(v[3]); glVertex3fv(v[2]); glVertex3fv(v[6]); glVertex3fv(v[7]) # Superior (VERDE)
    glColor3f(1.0, 1.0, 0.0); glVertex3fv(v[0]); glVertex3fv(v[4]); glVertex3fv(v[5]); glVertex3fv(v[1]) # Inferior (AMARILLO)
    glColor3f(1.0, 0.0, 1.0); glVertex3fv(v[1]); glVertex3fv(v[5]); glVertex3fv(v[6]); glVertex3fv(v[2]) # Derecha (MAGENTA)
    glColor3f(0.0, 1.0, 1.0); glVertex3fv(v[4]); glVertex3fv(v[0]); glVertex3fv(v[3]); glVertex3fv(v[7]) # Izquierda (CYAN)
    
    glEnd(); check_gl_error("glEnd() for cube")

def draw_scene_on_marker(frame_bgr, rvec, tvec, camera_matrix_cv, dist_coeffs_cv):
    """FUNCIÓN DESHABILITADA - Solo usar para menú sin modelo"""
    # NO ejecutar nada si hay modelo 3D cargado
    return frame_bgr

class PyrenderModelViewer:
    def __init__(self):
        self.scene = None
        self.renderer = None
        self.camera_node = None
        self.mesh_node = None
        self.mesh_nodes = []
        self.current_model = None
        self.initialized = False
        
    def load_car_model(self, car_dict):
        import os
        from trimesh.transformations import rotation_matrix, translation_matrix

        # Debug inicial...
        print(f"DEBUG_MODEL: 🏎️ === CARGANDO MODELO ===")
        print(f"DEBUG_MODEL: Coche recibido: {car_dict}")
        print(f"DEBUG_MODEL: Nombre: {car_dict.get('name', 'DESCONOCIDO')}")
        print(f"DEBUG_MODEL: Ruta: {car_dict.get('model_path', 'SIN RUTA')}")
        print(f"DEBUG_MODEL: ================================")

        model_path = f"assets/3d_models/{car_dict['model_path']}"
        scale = car_dict.get('scale', 0.05)
        elevation = car_dict.get('elevation', 0.01)
        
        self._current_model_name = car_dict.get('name', 'Modelo desconocido')

        print(f"DEBUG_MODEL: Ruta completa: {model_path}")
        print(f"DEBUG_MODEL: Ruta absoluta: {os.path.abspath(model_path)}")
        print(f"DEBUG_MODEL: ¿Existe archivo? {os.path.exists(model_path)}")

        if not os.path.exists(model_path):
            print(f"DEBUG_MODEL: ❌ Modelo no encontrado: {model_path}")
            return False

        _, ext = os.path.splitext(model_path)
        ext = ext.lower()
        self._current_file_ext = ext
        print(f"DEBUG_MODEL: 📁 Tipo de archivo: {ext}")

        if ext in ['.glb', '.gltf']:
            print("DEBUG_MODEL: 🎨 Cargando GLB/GLTF con sanitización de texturas")
            model = trimesh.load(model_path, process=True)
        elif ext == '.obj':
            print("DEBUG_MODEL: 🎨 Cargando OBJ con materiales MTL")
            model = trimesh.load(model_path, process=True)
        else:
            print(f"DEBUG_MODEL: ❌ Formato {ext} no soportado")
            return False

        if isinstance(model, trimesh.Scene):
            print("DEBUG_MODEL: Escena detectada, creando meshes individuales")
            combined = model.dump(concatenate=True)

            from trimesh.transformations import scale_matrix
            cent_trans = translation_matrix(-combined.centroid)
            scale_mat = scale_matrix(scale)
            rot_x = rotation_matrix(np.radians(90), [1, 0, 0])
            lift = translation_matrix([0, 0, elevation])
            transform = lift @ rot_x @ scale_mat @ cent_trans

            meshes = []
            for node_name in model.graph.nodes_geometry:
                pose, geom_name = model.graph[node_name]
                geom = model.geometry[geom_name].copy()
                geom.apply_transform(pose)
                
                # 🔧 SANITIZAR MATERIALES PROBLEMÁTICOS PARA GLB
                if ext in ['.glb', '.gltf']:
                    self._sanitize_glb_materials(geom)
                
                geom.apply_transform(transform)
                meshes.append(pyrender.Mesh.from_trimesh(geom, smooth=ext in ['.glb', '.gltf']))

            self.current_model = meshes
        else:
            # Modelo simple (Ferrari OBJ)
            model.apply_translation(-model.centroid)
            model.apply_scale(scale)
            rot_x = rotation_matrix(np.radians(90), [1, 0, 0])
            model.apply_transform(rot_x)
            lift = translation_matrix([0, 0, elevation])
            model.apply_transform(lift)
            
            # 🔧 SANITIZAR MATERIALES PARA OBJ TAMBIÉN
            if ext == '.obj':
                self._sanitize_obj_materials(model)

            self.current_model = [pyrender.Mesh.from_trimesh(model, smooth=True)]
        
        print(f"DEBUG_MODEL: ✅ Modelo {self._current_model_name} cargado correctamente")
        print(f"DEBUG_MODEL: Creados {len(self.current_model)} meshes")
        return True

    def _sanitize_glb_materials(self, geom):
        """Sanitizar materiales de GLB para evitar errores de texturas"""
        print("DEBUG_MODEL: 🧹 Sanitizando materiales GLB...")
        
        if hasattr(geom, 'visual') and hasattr(geom.visual, 'material'):
            mat = geom.visual.material
            if mat is not None:
                print(f"DEBUG_MODEL: Material encontrado: {type(mat)}")
                
                # 🔧 OPCIÓN 1: Reemplazar con material sólido simple
                from trimesh.visual.material import PBRMaterial
                
                # Crear material sólido basado en el color base si existe
                base_color = [0.5, 0.5, 0.5, 1.0]  # Gris por defecto
                
                if hasattr(mat, 'baseColorFactor') and mat.baseColorFactor is not None:
                    base_color = mat.baseColorFactor
                    print(f"DEBUG_MODEL: Usando color base: {base_color}")
                
                # Crear material simple sin texturas problemáticas
                safe_material = PBRMaterial(
                    baseColorFactor=base_color,
                    metallicFactor=0.1,
                    roughnessFactor=0.7,
                    # No incluir texturas que pueden causar problemas
                    baseColorTexture=None,
                    metallicRoughnessTexture=None,
                    normalTexture=None,
                    occlusionTexture=None,
                    emissiveTexture=None
                )
                
                geom.visual.material = safe_material
                print("DEBUG_MODEL: ✅ Material GLB sanitizado con colores sólidos")

    def _sanitize_obj_materials(self, model):
        """Sanitizar materiales de OBJ para mantener compatibilidad"""
        print("DEBUG_MODEL: 🧹 Verificando materiales OBJ...")
        
        if hasattr(model, 'visual') and hasattr(model.visual, 'material'):
            if model.visual.material is not None:
                print("DEBUG_MODEL: ✅ Material OBJ preservado (compatible)")
            else:
                print("DEBUG_MODEL: ⚠️ OBJ sin material - se aplicará rojo por defecto")
        else:
            print("DEBUG_MODEL: ⚠️ OBJ sin visual.material - se aplicará rojo por defecto")

    # MODIFICAR render_model_on_marker() - Manejo de errores de texturas:

    def render_model_on_marker(self, frame, rvec, tvec, camera_matrix, dist_coeffs):
        """Renderizar con manejo robusto de errores de texturas"""
        
        # Obtener nombre del modelo
        model_name = "Modelo desconocido"
        if hasattr(self, '_current_model_name'):
            model_name = self._current_model_name
        elif hasattr(self, '_current_file_ext'):
            if self._current_file_ext == '.obj':
                model_name = "Ferrari F40"
            elif self._current_file_ext in ['.glb', '.gltf']:
                model_name = "Porsche 911"
        
        print(f"DEBUG_MODEL: 🎬 Renderizando {model_name}...")
        
        if not self.current_model:
            print(f"DEBUG_MODEL: No hay modelo cargado")
            return frame
        
        try:
            # Configurar escena solo la primera vez
            self.setup_scene(camera_matrix, frame.shape[1], frame.shape[0])
            
            if not self.initialized:
                print(f"DEBUG_MODEL: ❌ Escena no inicializada")
                return frame
            
            # Calcular pose
            R, _ = cv2.Rodrigues(rvec)
            T = tvec.reshape(3)
            
            pose_cv = np.eye(4)
            pose_cv[:3, :3] = R
            pose_cv[:3, 3] = T
            
            print(f"DEBUG_MODEL: 📍 Posición marcador: {T}")
            
            # Convertir a sistema OpenGL
            cv_to_gl = np.array([[1, 0,  0, 0],
                                 [0, -1, 0, 0],
                                 [0, 0, -1, 0],
                                 [0, 0,  0, 1]], dtype=np.float32)
            
            pose_gl = cv_to_gl @ pose_cv
            print(f"DEBUG_MODEL: 🔄 Pose OpenGL calculada")
            
            # Actualizar pose del modelo
            for node in self.mesh_nodes:
                node.matrix = pose_gl
            
            # 🔧 RENDERIZAR CON MANEJO DE ERRORES DE TEXTURAS
            print(f"DEBUG_MODEL: 🎨 Intentando renderizar {model_name}...")
            try:
                color, depth = self.renderer.render(self.scene, flags=RenderFlags.RGBA)
                print(f"DEBUG_MODEL: ✅ Renderizado exitoso de {model_name}")
                
            except Exception as texture_error:
                print(f"DEBUG_MODEL: ⚠️ Error de texturas en {model_name}: {texture_error}")
                
                # 🔧 FALLBACK: Recrear escena con materiales limpios
                print(f"DEBUG_MODEL: 🔄 Intentando fallback sin texturas...")
                
                # Limpiar escena actual
                self.cleanup()
                self.initialized = False
                
                # Recargar modelo con materiales forzados limpios
                if hasattr(self, '_current_file_ext') and self._current_file_ext in ['.glb', '.gltf']:
                    # Forzar colores sólidos para GLB
                    for mesh in self.current_model:
                        if hasattr(mesh, 'primitives'):
                            for primitive in mesh.primitives:
                                # Material sólido simple
                                primitive.material = pyrender.MetallicRoughnessMaterial(
                                    baseColorFactor=[0.2, 0.4, 0.8, 1.0],  # Azul Porsche
                                    metallicFactor=0.3,
                                    roughnessFactor=0.7
                                )
                
                # Reintentar configurar escena
                self.setup_scene(camera_matrix, frame.shape[1], frame.shape[0])
                
                # Actualizar poses de nuevo
                for node in self.mesh_nodes:
                    node.matrix = pose_gl
                
                # Renderizar con materiales limpios
                color, depth = self.renderer.render(self.scene, flags=RenderFlags.RGBA)
                print(f"DEBUG_MODEL: ✅ Fallback exitoso para {model_name}")
        
            # Procesar resultado del renderizado
            print(f"DEBUG_MODEL: 🖼️ Color shape: {color.shape}")
            print(f"DEBUG_MODEL: 🎨 Color range: {color.min()}-{color.max()}")
            
            # Aplicar al frame
            mask = color[:, :, 3] > 0
            pixel_count = np.sum(mask)
            print(f"DEBUG_MODEL: 🔢 Píxeles visibles: {pixel_count} de {color.shape[0]*color.shape[1]}")
            
            if pixel_count > 0:
                color_bgr = cv2.cvtColor(color, cv2.COLOR_RGBA2BGR)
                frame[mask] = color_bgr[mask]
                print(f"DEBUG_MODEL: ✅ {model_name} renderizado con píxeles visibles!")
            else:
                print(f"DEBUG_MODEL: ⚠️ {model_name} renderizado pero SIN píxeles visibles")
                # Indicador visual
                cv2.circle(frame, (320, 240), 30, (255, 0, 255), 3)
                cv2.putText(frame, f"{model_name} (invisible)", (200, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        
            return frame
            
        except Exception as e:
            print(f"DEBUG_MODEL: 💥 Error crítico renderizando {model_name}: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback final: Círculo verde
            cv2.circle(frame, (320, 240), 50, (0, 255, 0), 3)
            cv2.putText(frame, f"{model_name} (ERROR)", (250, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            return frame
        
    def setup_scene(self, camera_matrix, frame_width, frame_height):
        """Configurar escena detectando materiales en GLB y OBJ"""
        print(f"DEBUG_MODEL: 🔧 === CONFIGURANDO ESCENA ===")
        print(f"DEBUG_MODEL: initialized: {self.initialized}")
        print(f"DEBUG_MODEL: current_model: {self.current_model is not None}")
        
        if self.initialized or not self.current_model:
            print(f"DEBUG_MODEL: ⚠️ Saltando setup_scene - ya inicializado o sin modelo")
            return
        
        print("DEBUG_MODEL: 🔧 Configurando escena...")
        
        # Crear escena Pyrender
        self.scene = pyrender.Scene(bg_color=[0, 0, 0, 0])
        
        # Cámara
        camera = pyrender.IntrinsicsCamera(
            fx=camera_matrix[0, 0],
            fy=camera_matrix[1, 1],
            cx=camera_matrix[0, 2],
            cy=camera_matrix[1, 2]
        )
        self.camera_node = self.scene.add(camera)
        
        # 🔍 DETECTAR SI EL MODELO YA TIENE MATERIALES (GLB O OBJ+MTL)
        has_materials = False
        meshes = self.current_model if isinstance(self.current_model, list) else [self.current_model]
        for mesh in meshes:
            if hasattr(mesh, 'primitives'):
                print(f"DEBUG_MODEL: 🔍 Analizando {len(mesh.primitives)} primitivas...")
                for i, primitive in enumerate(mesh.primitives):
                    if primitive.material is not None:
                        has_materials = True
                        print(f"DEBUG_MODEL: Primitiva {i} tiene material: {type(primitive.material).__name__}")

                        # 🔍 DEBUG DETALLADO DEL MATERIAL
                        mat = primitive.material
                        print(f"DEBUG_MODEL: --- Material {i} Detalles ---")
                        if hasattr(mat, 'baseColorFactor'):
                            print(f"DEBUG_MODEL: baseColorFactor: {mat.baseColorFactor}")
                        if hasattr(mat, 'baseColorTexture'):
                            print(f"DEBUG_MODEL: baseColorTexture: {mat.baseColorTexture}")
                        if hasattr(mat, 'metallicFactor'):
                            print(f"DEBUG_MODEL: metallicFactor: {mat.metallicFactor}")
                        if hasattr(mat, 'roughnessFactor'):
                            print(f"DEBUG_MODEL: roughnessFactor: {mat.roughnessFactor}")
                        if hasattr(mat, 'name'):
                            print(f"DEBUG_MODEL: Material name: {mat.name}")
                        print(f"DEBUG_MODEL: --- Fin Material {i} ---")
                    else:
                        print(f"DEBUG_MODEL: Primitiva {i} SIN material")

        print(f"DEBUG_MODEL: ¿Tiene materiales? {has_materials}")

        # 🔆 CONFIGURAR LUCES SEGÚN PRESENCIA DE MATERIALES
        if has_materials:
            # Modelo con materiales (GLB o OBJ+MTL): Luces moderadas
            model_type = "GLB" if hasattr(self, '_current_file_ext') and self._current_file_ext in ['.glb', '.gltf'] else "OBJ+MTL"
            print(f"DEBUG_MODEL: 💡 Configurando luces MODERADAS para {model_type}")
            
            # Luces moderadas para preservar texturas/materiales
            light_intensity = 1.5   # Moderado
            ambient_intensity = 0.8  # Ambiental moderado
            
            # Luz direccional principal
            light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=light_intensity)
            self.scene.add(light, pose=np.eye(4))
            
            # Luz ambiental
            ambient_light = pyrender.DirectionalLight(color=[0.6, 0.6, 0.6], intensity=ambient_intensity)
            ambient_pose = np.eye(4)
            ambient_pose[:3, 3] = [0, 0, -0.1]
            self.scene.add(ambient_light, pose=ambient_pose)
            
            # Luz lateral
            side_light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
            side_pose = np.eye(4)
            side_pose[:3, 3] = [0.1, 0.1, 0.05]
            self.scene.add(side_light, pose=side_pose)
            
            print(f"DEBUG_MODEL: 💡 Luces {model_type} - Direccional: {light_intensity}, Ambiental: {ambient_intensity}, Lateral: 2.0")
            
            # 🎨 NO APLICAR MATERIAL - Usar los materiales originales
            print(f"DEBUG_MODEL: 🎨 Manteniendo materiales originales del {model_type}")
            
        else:
            # Modelo sin materiales: Aplicar material rojo por defecto
            print("DEBUG_MODEL: 💡 Configurando luces INTENSAS para modelo sin materiales")
            light_intensity = 8.0
            point_intensity = 10.0
            
            light = pyrender.DirectionalLight(color=np.ones(3), intensity=light_intensity)
            self.scene.add(light, pose=np.eye(4))
            
            light2 = pyrender.PointLight(color=np.ones(3), intensity=point_intensity)
            light_pose = np.eye(4)
            light_pose[:3, 3] = [0, 0, 0.1]
            self.scene.add(light2, pose=light_pose)
            
            print(f"DEBUG_MODEL: 💡 Luces intensas - Direccional: {light_intensity}, Puntual: {point_intensity}")
        
            # 🎨 APLICAR MATERIAL ROJO SOLO SI NO HAY MATERIALES
            print("DEBUG_MODEL: 🎨 Aplicando material rojo por defecto")
            material_rojo = pyrender.MetallicRoughnessMaterial(
                baseColorFactor=[1.0, 0.0, 0.0, 1.0],
                metallicFactor=0.8,
                roughnessFactor=0.2,
                emissiveFactor=[0.2, 0.0, 0.0]
            )

            for mesh in meshes:
                if hasattr(mesh, 'primitives'):
                    for primitive in mesh.primitives:
                        primitive.material = material_rojo
        
        # Añadir modelo a la escena
        self.mesh_nodes = []
        for mesh in meshes:
            node = self.scene.add(mesh, pose=np.eye(4))
            self.mesh_nodes.append(node)
        
        # Crear renderer
        self.renderer = pyrender.OffscreenRenderer(frame_width, frame_height)
        
        self.initialized = True
        print("DEBUG_MODEL: ✅ Escena configurada exitosamente")

    def cleanup(self):
        """Limpiar recursos del renderer"""
        print("DEBUG_MODEL: 🧹 Limpiando recursos...")
        
        # Limpiar renderer
        if hasattr(self, 'renderer') and self.renderer is not None:
            try:
                self.renderer.delete()
                print("DEBUG_MODEL: Renderer limpiado")
            except Exception as e:
                print(f"DEBUG_MODEL: Error limpiando renderer: {e}")
            self.renderer = None
        
        # Limpiar escena
        if hasattr(self, 'scene') and self.scene is not None:
            self.scene = None
            print("DEBUG_MODEL: Escena limpiada")
        
        # Limpiar nodos
        if hasattr(self, 'mesh_nodes'):
            self.mesh_nodes = []
            print("DEBUG_MODEL: Nodos de mesh limpiados")
        
        # Limpiar variables de estado
        self.camera_node = None
        self.mesh_node = None
        self.current_model = None
        self.initialized = False
        
        # Limpiar variables de debug si existen
        if hasattr(self, '_current_model_name'):
            delattr(self, '_current_model_name')
        if hasattr(self, '_current_file_ext'):
            delattr(self, '_current_file_ext')
        
        print("DEBUG_MODEL: ✅ Todos los recursos limpiados")

