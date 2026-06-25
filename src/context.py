"""
Classe Context - TextoMúsica

Mantém o estado dinâmico da execução musical.

Centralizar o estado aqui evita variáveis globais e facilita reset e extensão.
O Interpreter atualiza o Context a cada caractere; o MusicEvent é montado
a partir dos valores atuais do Context.
"""

from constants import (
    DEFAULT_VOLUME,
    DEFAULT_OCTAVE,
    DEFAULT_BPM,
    DEFAULT_INSTRUMENT,
    MAX_VOLUME,
    MAX_OCTAVE,
    MIN_BPM,
    MAX_BPM,
    BPM_STEP,
)


class Context:
    """
    Encapsula todo o estado da execução musical.
    
    Atributos:
        volume (int): Volume atual (0-127)
        octave (int): Oitava atual (0-8)
        bpm (int): Batidas por minuto (tempo)
        instrument (int): Instrumento MIDI ativo (0-127)
        last_note (str | None): Última nota tocada; None se nenhuma foi gerada ainda
    """
    
    def __init__(self):
        """Inicializa o Context com os valores padrão."""
        self.volume = DEFAULT_VOLUME
        self.octave = DEFAULT_OCTAVE
        self.bpm = DEFAULT_BPM
        self.instrument = DEFAULT_INSTRUMENT
        self.last_note = None
    
    def reset(self):
        """
        Restaura todos os atributos aos valores padrão de Constants.
        
        Usado quando o usuário clica em "Limpar" ou quando o sistema
        precisa ser reiniciado.
        """
        self.volume = DEFAULT_VOLUME
        self.octave = DEFAULT_OCTAVE
        self.bpm = DEFAULT_BPM
        self.instrument = DEFAULT_INSTRUMENT
        self.last_note = None
    
    def set_volume(self, value):
        """
        Define o volume.
        
        Se value > MAX_VOLUME, usa MAX_VOLUME (clamp).
        
        Args:
            value (int): Novo volume (0-127)
        """
        self.volume = min(value, MAX_VOLUME)
    
    def get_volume(self):
        """Retorna o volume atual."""
        return self.volume
    
    def set_octave(self, value):
        """
        Define a oitava.
        
        Se value > MAX_OCTAVE, volta ao DEFAULT_OCTAVE.
        
        Args:
            value (int): Nova oitava (0-8)
        """
        if value > MAX_OCTAVE:
            self.octave = DEFAULT_OCTAVE
        else:
            self.octave = value
    
    def get_octave(self):
        """Retorna a oitava atual."""
        return self.octave
    
    def set_bpm(self, value):
        """
        Define o BPM (tempo).
        
        Args:
            value (int): Novo BPM
        """
        self.bpm = value
    
    def get_bpm(self):
        """Retorna o BPM atual."""
        return self.bpm
    
    def set_instrument(self, value):
        """
        Define o instrumento General MIDI ativo.
        
        Args:
            value (int): Instrumento MIDI (0-127)
        """
        self.instrument = value
    
    def get_instrument(self):
        """Retorna o instrumento ativo."""
        return self.instrument
    
    def set_last_note(self, note):
        """
        Atualiza a última nota tocada.
        
        Controla o comportamento de repetição: quando um caractere
        é 'repetição', ele toca a última nota novamente.
        
        Args:
            note (str | None): Nome da nota ou None
        """
        self.last_note = note
    
    def get_last_note(self):
        """
        Retorna a última nota, ou None.
        
        Returns:
            str | None: Nome da nota ou None se nenhuma foi tocada ainda
        """
        return self.last_note
    
    def increase_bpm(self):
        self.bpm = min(self.bpm + BPM_STEP, MAX_BPM)

    def decrease_bpm(self):
        self.bpm = max(self.bpm - BPM_STEP, MIN_BPM)

    def lower_octave(self):
        if self.octave > 0:
            self.octave -= 1

    def note_duration_ms(self):
        """
        Retorna a duração de uma nota em milissegundos com base no BPM.
        
        Fórmula: (60 / bpm) * 1000
        
        Por exemplo, em 120 BPM (2 batidas por segundo),
        cada nota dura (60/120)*1000 = 500ms.
        
        Returns:
            int: Duração em ms
        """
        return int((60 / self.bpm) * 1000)
