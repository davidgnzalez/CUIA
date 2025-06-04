# CREAR ARCHIVO DE TEST: test_voice.py

from audio_processing.voice_commands import VoiceController
import time

def test_voice():
    print("🎤 Test del controlador de voz")
    controller = VoiceController()
    
    if not controller.microphone:
        print("❌ No hay micrófono disponible")
        return
    
    print("✅ Micrófono detectado")
    print("🔧 Iniciando escucha...")
    
    success = controller.start_listening()
    if success:
        print("✅ Control de voz activado")
        print("🗣️ Di 'Ferrari' o 'Porsche'...")
        
        # Escuchar por 10 segundos
        for i in range(10):
            time.sleep(1)
            command = controller.get_voice_command()
            if command:
                print(f"🎙️ Comando detectado: {command}")
                break
            print(f"⏳ Esperando... {10-i}s restantes")
    else:
        print("❌ No se pudo activar control de voz")
    
    controller.cleanup()
    print("🧹 Test completado")

if __name__ == "__main__":
    test_voice()