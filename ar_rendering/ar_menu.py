import cv2
import numpy as np

class ARMenu:
    def __init__(self):
        self.menu_items = []
        self.selected_index = 0
        print(f"DEBUG_MENU: ARMenu inicializado con {len(self.menu_items)} elementos")
        
    def draw_menu_overlay(self, frame, marker_corners):
        """Dibuja el menú con múltiples coches"""
        if not self.menu_items or marker_corners is None or len(marker_corners) == 0:
            print(f"DEBUG_MENU: No hay elementos ({len(self.menu_items)}) o marcador")
            return frame
        
        print(f"DEBUG_MENU: Dibujando menú con {len(self.menu_items)} coches")
        for i, car in enumerate(self.menu_items):
            print(f"DEBUG_MENU: {i+1}. {car['name']} - {car['model_path']}")
        
        # Obtener las esquinas del marcador
        corners = marker_corners[0].reshape(-1, 2)
        
        # Calcular el centro del marcador
        center_x = int(np.mean(corners[:, 0]))
        center_y = int(np.mean(corners[:, 1]))
        
        # Calcular tamaño proporcional al marcador
        marker_width = int(np.max(corners[:, 0]) - np.min(corners[:, 0]))
        marker_height = int(np.max(corners[:, 1]) - np.min(corners[:, 1]))
        
        # Dimensiones del menú (más grande para múltiples opciones)
        menu_width = max(500, marker_width * 4)
        menu_height = max(300, marker_height * 3)
        
        # Posición del menú centrada sobre el marcador
        menu_x = center_x - menu_width // 2
        menu_y = center_y - menu_height // 2
        
        # Asegurar que no se salga de pantalla
        menu_x = max(10, min(menu_x, frame.shape[1] - menu_width - 10))
        menu_y = max(10, min(menu_y, frame.shape[0] - menu_height - 10))
        
        # Crear overlay semitransparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (menu_x, menu_y), (menu_x + menu_width, menu_y + menu_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Borde del menú
        cv2.rectangle(frame, (menu_x, menu_y), (menu_x + menu_width, menu_y + menu_height), (255, 255, 255), 3)
        
        # Título del menú
        title_y = menu_y + 50
        cv2.putText(frame, "=== CAR SHOWROOM ===", (menu_x + 50, title_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mostrar todas las opciones disponibles
        option_y_start = title_y + 80
        for i, car in enumerate(self.menu_items):
            option_y = option_y_start + (i * 80)
            
            # Color según selección
            color = (0, 255, 0) if i == self.selected_index else (255, 255, 255)
            
            # Mostrar número y nombre del coche
            cv2.putText(frame, f"{i+1}. {car['name']}", (menu_x + 60, option_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, car['description'], (menu_x + 80, option_y + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Instrucciones
        instructions_y = menu_y + menu_height - 60
        cv2.putText(frame, "1-2: Seleccionar | ESPACIO: Ver modelo 3D", (menu_x + 30, instructions_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return frame

    def handle_selection(self, key):
        """Maneja la selección de múltiples coches"""
        print(f"DEBUG_MENU: Tecla presionada: {chr(key) if 32 <= key <= 126 else key}")
        
        # Selección numérica
        if key >= ord('1') and key <= ord('9'):
            index = key - ord('1')  # Convertir '1' a índice 0
            if index < len(self.menu_items):
                self.selected_index = index
                print(f"DEBUG_MENU: Navegando a índice {index}: {self.menu_items[index]['name']}")
            else:
                print(f"DEBUG_MENU: Índice {index} fuera de rango (máximo {len(self.menu_items)-1})")
        
        # Navegación con flechas (opcional)
        elif key == 82:  # Flecha arriba (en algunos sistemas)
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            print(f"DEBUG_MENU: Flecha arriba - Seleccionado: {self.menu_items[self.selected_index]['name']}")
        elif key == 84:  # Flecha abajo (en algunos sistemas)
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            print(f"DEBUG_MENU: Flecha abajo - Seleccionado: {self.menu_items[self.selected_index]['name']}")
        
        # Confirmar selección con ESPACIO
        elif key == ord(' '):
            if 0 <= self.selected_index < len(self.menu_items):
                selected_car = self.menu_items[self.selected_index]
                print(f"DEBUG_MENU: ✅ CONFIRMADO: {selected_car['name']}")
                return selected_car
            else:
                print(f"DEBUG_MENU: Índice seleccionado inválido: {self.selected_index}")
        
        return None