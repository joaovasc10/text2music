"""
Classe MusicSystem - TextoMúsica

Implementa o padrão Facade, unindo todos os módulos.

A interface web (via servidor HTTP) interage exclusivamente com MusicSystem.
Mudanças internas (ex: trocar o Player) não exigem alterações na interface.
"""

import threading

from context import Context
from character_mapper import CharacterMapper
from text_reader import TextReader
from interpreter import Interpreter
from player import Player


class MusicSystem:
    """
    Fachada do sistema.
    
    Instancia internamente: Context, CharacterMapper, TextReader,
    Interpreter, Player.
    
    Expõe uma interface simples para o servidor HTTP.
    """
    
    def __init__(self):
        """Inicializa o MusicSystem com todos os seus componentes."""
        # Criar instâncias internas
        self.interpreter = Interpreter()  # Já contém Context, CharacterMapper, TextReader
        self.player = Player()
        
        # Inicializar pygame.midi
        self.player.initialize()
        
        # Referência ao Context do Interpreter para acesso rápido
        self.context = self.interpreter.context
    
    def configure(self, bpm, instrument, octave, volume):
        """
        Repassa os parâmetros iniciais ao Context antes de iniciar
        a reprodução.
        
        Args:
            bpm (int): Batidas por minuto (tempo)
            instrument (int): Instrumento MIDI (0-127)
            octave (int): Oitava base (0-8)
            volume (int): Volume (0-127)
        """
        self.context.set_bpm(bpm)
        self.context.set_instrument(instrument)
        self.context.set_octave(octave)
        self.context.set_volume(volume)
    
    def run(self, text):
        """
        Processa o texto e inicia a reprodução.
        
        Chama interpret_text() para gerar eventos, depois inicia
        play_sequence() em uma thread separada para não bloquear
        a interface web.
        
        Args:
            text (str): Texto a processar
        """
        try:
            # Processar o texto e gerar eventos
            events = self.interpreter.interpret_text(text)
            
            # Iniciar reprodução em thread separada
            playback_thread = threading.Thread(
                target=self.player.play_sequence,
                args=[events],
                daemon=True
            )
            playback_thread.start()
            
            return len(events)
        except Exception as e:
            print(f"ERRO em MusicSystem.run(): {e}")
            return 0
    
    def stop(self):
        """
        Para a reprodução em andamento.
        
        Chama player.stop(), que seta is_playing = False.
        play_sequence() vai parar na próxima iteração.
        """
        self.player.stop()
    
    def reset(self):
        """
        Reseta o sistema aos valores padrão.
        
        Chama context.reset(), restaurando todos os parâmetros
        ao estado inicial.
        """
        self.context.reset()
        self.player.stop()
