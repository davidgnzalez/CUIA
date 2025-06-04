"""
Módulo de procesamiento de audio para ARCar Showroom
Incluye reconocimiento de voz y comandos por voz
"""

from .voice_commands import VoiceController, get_voice_controller, cleanup_voice_controller

__all__ = ['VoiceController', 'get_voice_controller', 'cleanup_voice_controller']

