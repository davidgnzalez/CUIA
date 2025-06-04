# CREAR ARCHIVO: data_management/user_manager.py

import os
import json
import shutil
import numpy as np
from pathlib import Path

# Imports opcionales para evitar errores
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    print("⚠️ OpenCV no disponible. Algunas funciones estarán limitadas.")
    CV2_AVAILABLE = False

class UserManager:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.embeddings_dir = self.project_root / "assets/face_data/embeddings"
        self.models_dir = self.embeddings_dir / "models"
        self.user_map_file = self.project_root / "data_management/user_id_map.json"
        
        # Crear directorios si no existen
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.user_map_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_user_map(self):
        """Cargar mapa de usuarios"""
        try:
            if self.user_map_file.exists():
                with open(self.user_map_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Error cargando user_id_map.json: {e}")
            return {}
    
    def save_user_map(self, user_map):
        """Guardar mapa de usuarios"""
        try:
            with open(self.user_map_file, 'w') as f:
                json.dump(user_map, f, indent=4)
            print(f"✅ Mapa de usuarios guardado")
        except Exception as e:
            print(f"❌ Error guardando user_id_map.json: {e}")
    
    def list_users(self):
        """Listar todos los usuarios registrados"""
        print("\n" + "="*50)
        print("👥 USUARIOS REGISTRADOS")
        print("="*50)
        
        user_map = self.load_user_map()
        
        if not user_map:
            print("❌ No hay usuarios registrados")
            return
        
        for user_id, numeric_id in user_map.items():
            user_dir = self.embeddings_dir / user_id
            model_file = self.models_dir / f"{user_id}.yml"
            
            # Contar imágenes
            images_count = 0
            if user_dir.exists():
                images_count = len([f for f in user_dir.glob("*.jpg")])
            
            # Verificar modelo
            model_exists = "✅" if model_file.exists() else "❌"
            
            print(f"👤 {user_id:<15} | ID: {numeric_id:<3} | Imágenes: {images_count:<3} | Modelo: {model_exists}")
    
    def get_user_details(self, user_id):
        """Obtener detalles de un usuario específico"""
        user_map = self.load_user_map()
        
        if user_id not in user_map:
            print(f"❌ Usuario '{user_id}' no encontrado")
            return None
        
        user_dir = self.embeddings_dir / user_id
        model_file = self.models_dir / f"{user_id}.yml"
        
        details = {
            'user_id': user_id,
            'numeric_id': user_map[user_id],
            'images_dir': user_dir,
            'model_file': model_file,
            'images_count': 0,
            'model_exists': model_file.exists(),
            'images_exist': user_dir.exists()
        }
        
        if user_dir.exists():
            details['images_count'] = len([f for f in user_dir.glob("*.jpg")])
        
        return details
    
    def delete_user(self, user_id):
        """Eliminar usuario completamente"""
        print(f"\n🗑️ ELIMINANDO USUARIO: {user_id}")
        
        user_map = self.load_user_map()
        
        if user_id not in user_map:
            print(f"❌ Usuario '{user_id}' no encontrado")
            return False
        
        # Confirmar eliminación
        confirm = input(f"⚠️ ¿Estás seguro de eliminar '{user_id}'? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Eliminación cancelada")
            return False
        
        try:
            # Eliminar directorio de imágenes
            user_dir = self.embeddings_dir / user_id
            if user_dir.exists():
                shutil.rmtree(user_dir)
                print(f"✅ Directorio de imágenes eliminado: {user_dir}")
            
            # Eliminar modelo
            model_file = self.models_dir / f"{user_id}.yml"
            if model_file.exists():
                model_file.unlink()
                print(f"✅ Modelo eliminado: {model_file}")
            
            # Actualizar mapa de usuarios
            del user_map[user_id]
            self.save_user_map(user_map)
            
            print(f"✅ Usuario '{user_id}' eliminado completamente")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando usuario: {e}")
            return False
    
    def fix_directory_structure(self):
        """Arreglar estructura de directorios inconsistente"""
        print("\n🔧 ARREGLANDO ESTRUCTURA DE DIRECTORIOS...")
        
        images_dir = self.embeddings_dir / "images"
        
        if not images_dir.exists():
            print("✅ No hay directorio 'images' que arreglar")
            return
        
        # Mover cada usuario de images/ a embeddings/
        for user_subdir in images_dir.iterdir():
            if user_subdir.is_dir():
                user_id = user_subdir.name
                target_dir = self.embeddings_dir / user_id
                
                print(f"📂 Moviendo {user_id}...")
                
                # Crear directorio objetivo
                target_dir.mkdir(exist_ok=True)
                
                # Mover todas las imágenes
                moved_count = 0
                for img_file in user_subdir.glob("*.*"):
                    # Renombrar de .png a .jpg si es necesario
                    if img_file.suffix.lower() == '.png':
                        target_file = target_dir / f"face_{moved_count:03d}.jpg"
                        
                        # 🔧 CONVERSIÓN SIN CV2 SI NO ESTÁ DISPONIBLE
                        if CV2_AVAILABLE:
                            # Convertir PNG a JPG con OpenCV
                            img = cv2.imread(str(img_file))
                            cv2.imwrite(str(target_file), img)
                        else:
                            # Fallback: simplemente copiar como JPG
                            shutil.copy2(str(img_file), str(target_file.with_suffix('.png')))
                            # Luego renombrar a .jpg
                            target_file.with_suffix('.png').rename(target_file)
                        
                        moved_count += 1
                    else:
                        target_file = target_dir / img_file.name
                        shutil.move(str(img_file), str(target_file))
                        moved_count += 1
                
                print(f"✅ {moved_count} imágenes movidas para {user_id}")
        
        # Eliminar directorio images vacío
        try:
            shutil.rmtree(images_dir)
            print("🗑️ Directorio 'images' eliminado")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar directorio 'images': {e}")
        
        print("✅ Estructura de directorios arreglada")
    
    def retrain_user_model(self, user_id):
        """Reentrenar modelo de un usuario"""
        if not CV2_AVAILABLE:
            print("❌ OpenCV no disponible. No se puede reentrenar modelos.")
            print("💡 Ejecuta desde el entorno virtual: source venv/bin/activate")
            return False
        
        print(f"\n🔧 REENTRENANDO MODELO: {user_id}")
        
        user_details = self.get_user_details(user_id)
        if not user_details:
            return False
        
        if user_details['images_count'] == 0:
            print(f"❌ No hay imágenes para entrenar '{user_id}'")
            return False
        
        try:
            # Simular el proceso de entrenamiento
            user_dir = user_details['images_dir']
            faces = []
            labels = []
            numeric_id = user_details['numeric_id']
            
            # Cargar todas las imágenes
            for img_file in user_dir.glob("*.jpg"):
                face_img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                if face_img is not None:
                    faces.append(face_img)
                    labels.append(numeric_id)
            
            if len(faces) == 0:
                print("❌ No se encontraron imágenes válidas")
                return False
            
            print(f"📚 Entrenando con {len(faces)} imágenes...")
            
            # Entrenar modelo LBPH
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, np.array(labels))
            
            # Guardar modelo
            model_path = user_details['model_file']
            recognizer.write(str(model_path))
            
            print(f"✅ Modelo reentrenado: {model_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error reentrenando modelo: {e}")
            return False

def main():
    """Interfaz de línea de comandos para gestión de usuarios"""
    import sys
    
    project_root = "/home/dgnp18/Documentos/CUIA/ARCar_Showroom"
    manager = UserManager(project_root)
    
    # 🔧 MOSTRAR ADVERTENCIA SI CV2 NO ESTÁ DISPONIBLE
    if not CV2_AVAILABLE:
        print("⚠️ ADVERTENCIA: OpenCV no está disponible")
        print("💡 Para funcionalidad completa, ejecuta:")
        print("   cd /home/dgnp18/Documentos/CUIA/ARCar_Showroom")
        print("   source venv/bin/activate")
        print("   python data_management/user_manager.py <comando>")
        print()
    
    if len(sys.argv) < 2:
        print("\n🛠️ GESTOR DE USUARIOS ARCar Showroom")
        print("="*40)
        print("Uso: python user_manager.py <comando> [argumentos]")
        print("\nComandos disponibles:")
        print("  list                    - Listar todos los usuarios")
        print("  details <user_id>       - Detalles de un usuario")
        print("  delete <user_id>        - Eliminar un usuario")
        print("  fix-structure          - Arreglar estructura de directorios")
        print("  retrain <user_id>      - Reentrenar modelo de usuario (requiere OpenCV)")
        print("\nEjemplos:")
        print("  python user_manager.py list")
        print("  python user_manager.py details marcos")
        print("  python user_manager.py delete test")
        print("  python user_manager.py fix-structure")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        manager.list_users()
    
    elif command == "details":
        if len(sys.argv) < 3:
            print("❌ Falta el ID de usuario")
            return
        user_id = sys.argv[2]
        details = manager.get_user_details(user_id)
        if details:
            print(f"\n👤 DETALLES DE USUARIO: {details['user_id']}")
            print("="*40)
            print(f"ID numérico: {details['numeric_id']}")
            print(f"Directorio: {details['images_dir']}")
            print(f"Imágenes: {details['images_count']}")
            print(f"Modelo existe: {'✅' if details['model_exists'] else '❌'}")
            print(f"Imágenes existen: {'✅' if details['images_exist'] else '❌'}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Falta el ID de usuario")
            return
        user_id = sys.argv[2]
        manager.delete_user(user_id)
    
    elif command == "fix-structure":
        manager.fix_directory_structure()
    
    elif command == "retrain":
        if len(sys.argv) < 3:
            print("❌ Falta el ID de usuario")
            return
        user_id = sys.argv[2]
        manager.retrain_user_model(user_id)
    
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == "__main__":
    main()

