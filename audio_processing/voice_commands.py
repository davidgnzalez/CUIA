import speech_recognition as sr
import threading
import time
from queue import Queue, Empty
import logging

# Si falta algún import, añadirlo al principio del archivo

class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.voice_queue = Queue()
        self.listening = False
        self.listen_thread = None
        
        # Palabras clave para coches
        self.car_keywords = {
            'ferrari': ['ferrari', 'ferari', 'ferrary', 'f40', 'f cuarenta'],
            'porsche': ['porsche', 'porche', 'porshe', 'novecientos once', '911', 'nueve uno uno']
        }
        
        # Palabras de control adicionales
        self.control_keywords = {
            'menu': ['menu', 'menú', 'volver', 'atrás', 'back'],
            'logout': ['salir', 'logout', 'cerrar sesión', 'quit']
        }
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configurar micrófono
        self._setup_microphone()
        
    def _setup_microphone(self):
        """Configurar y calibrar micrófono"""
        try:
            self.microphone = sr.Microphone()
            print("DEBUG_VOICE: 🎤 Calibrando micrófono...")
            
            with self.microphone as source:
                # Ajustar para ruido ambiental (más tiempo para mejor calibración)
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                # Configurar sensibilidad
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                
            print("DEBUG_VOICE: ✅ Micrófono configurado correctamente")
            print(f"DEBUG_VOICE: Energy threshold: {self.recognizer.energy_threshold}")
            return True
            
        except Exception as e:
            print(f"DEBUG_VOICE: ❌ Error configurando micrófono: {e}")
            self.microphone = None
            return False
    
    def start_listening(self):
        """Iniciar escucha en segundo plano"""
        if not self.microphone:
            print("DEBUG_VOICE: ❌ No hay micrófono disponible")
            return False
            
        if self.listening:
            print("DEBUG_VOICE: ⚠️ Ya está escuchando")
            return True
            
        self.listening = True
        self.listen_thread = threading.Thread(target=self._listen_continuously, daemon=True)
        self.listen_thread.start()
        print("DEBUG_VOICE: 🎤 Reconocimiento de voz INICIADO")
        print("DEBUG_VOICE: 🗣️ Puedes decir: 'Ferrari', 'Porsche', 'Menú', 'Salir'")
        return True
    
    def stop_listening(self):
        """Detener escucha"""
        self.listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        print("DEBUG_VOICE: 🔇 Reconocimiento de voz DETENIDO")
    
    def _listen_continuously(self):
        """Escuchar continuamente en segundo plano"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.listening:
            try:
                with self.microphone as source:
                    # Escuchar con timeout corto para no bloquear
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                
                try:
                    # Reconocer texto en español
                    text = self.recognizer.recognize_google(audio, language='es-ES')
                    text_lower = text.lower().strip()
                    
                    print(f"DEBUG_VOICE: 🔊 Escuchado: '{text}'")
                    
                    # Detectar comandos
                    command = self._detect_command(text_lower)
                    if command:
                        self.voice_queue.put(command)
                        print(f"DEBUG_VOICE: ✅ Comando detectado: {command}")
                    
                    # Reset contador de errores en éxito
                    consecutive_errors = 0
                        
                except sr.UnknownValueError:
                    # No se entendió el audio - normal, no hacer nada
                    pass
                except sr.RequestError as e:
                    consecutive_errors += 1
                    print(f"DEBUG_VOICE: ❌ Error del servicio ({consecutive_errors}/{max_consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print("DEBUG_VOICE: 🚫 Demasiados errores consecutivos, pausando...")
                        time.sleep(5)
                        consecutive_errors = 0
                    
            except sr.WaitTimeoutError:
                # Timeout normal - continuar escuchando
                pass
            except Exception as e:
                consecutive_errors += 1
                print(f"DEBUG_VOICE: ❌ Error inesperado ({consecutive_errors}): {e}")
                if consecutive_errors >= max_consecutive_errors:
                    print("DEBUG_VOICE: 🚫 Demasiados errores, pausando...")
                    time.sleep(3)
                    consecutive_errors = 0
                else:
                    time.sleep(0.5)  # Pausa breve antes de reintentar
    
    def _detect_command(self, text):
        """Detectar comando en el texto hablado"""
        text_words = text.split()
        
        # Buscar palabras clave de Ferrari
        for keyword in self.car_keywords['ferrari']:
            if keyword in text:
                print(f"DEBUG_VOICE: 🏎️ Ferrari detectado con palabra '{keyword}' en '{text}'")
                return {'type': 'car_selection', 'car': 'ferrari'}
        
        # Buscar palabras clave de Porsche
        for keyword in self.car_keywords['porsche']:
            if keyword in text:
                print(f"DEBUG_VOICE: 🚗 Porsche detectado con palabra '{keyword}' en '{text}'")
                return {'type': 'car_selection', 'car': 'porsche'}
        
        # Buscar comandos de control
        for keyword in self.control_keywords['menu']:
            if keyword in text:
                print(f"DEBUG_VOICE: 🔙 Comando menú detectado con palabra '{keyword}' en '{text}'")
                return {'type': 'navigation', 'action': 'menu'}
        
        for keyword in self.control_keywords['logout']:
            if keyword in text:
                print(f"DEBUG_VOICE: 🚪 Comando logout detectado con palabra '{keyword}' en '{text}'")
                return {'type': 'navigation', 'action': 'logout'}
        
        return None
    
    def get_voice_command(self):
        """Obtener comando de voz si hay alguno"""
        try:
            return self.voice_queue.get_nowait()
        except Empty:
            return None
    
    def is_listening(self):
        """Verificar si está escuchando"""
        return self.listening
    
    def get_status_text(self):
        """Obtener texto de estado para mostrar en UI"""
        if self.listening:
            return "🎤 VOZ ON"
        else:
            return "🔇 VOZ OFF"
    
    def get_instructions_text(self):
        """Obtener texto de instrucciones para mostrar en UI"""
        if self.listening:
            return "Di: 'Ferrari', 'Porsche', 'Menú', 'Salir' | V: Desactivar voz"
        else:
            return "Presiona 'V' para activar control de voz"
    
    def cleanup(self):
        """Limpiar recursos"""
        self.stop_listening()
        print("DEBUG_VOICE: 🧹 Recursos de voz limpiados")

# Función de utilidad para crear instancia global
_voice_controller_instance = None

def get_voice_controller():
    """Obtener instancia única del controlador de voz"""
    global _voice_controller_instance
    if _voice_controller_instance is None:
        _voice_controller_instance = VoiceController()
    return _voice_controller_instance

def cleanup_voice_controller():
    """Limpiar controlador de voz global"""
    global _voice_controller_instance
    if _voice_controller_instance:
        _voice_controller_instance.cleanup()
        _voice_controller_instance = None

