"""
Classe MusicEvent - TextoMúsica

Representa um evento musical atômico: o resultado de processar um único
caractere do texto de entrada.

É a unidade de saída do Interpreter e de entrada do Player.
Desacopla quem interpreta de quem toca — o Player não precisa saber
nada sobre o texto original.
"""


class MusicEvent:
    """
    Encapsula os dados de um evento musical.
    
    Atributos:
        type (str): Tipo do evento: 'note' (nota), 'silence' (pausa) ou 
                    'control' (mudança de instrumento/volume/oitava)
        note (str | None): Nome da nota (ex: 'La', 'SiBemol'); None se não for nota
        octave (int): Oitava ativa no momento da criação do evento
        volume (int): Volume ativo no momento da criação (0-127)
        instrument (int): Instrumento General MIDI ativo no momento
        duration_ms (int): Duração em milissegundos, calculada a partir do BPM
    """
    
    def __init__(self, type_, note, octave, volume, instrument, duration_ms):
        """
        Inicializa um MusicEvent com os valores atuais do contexto.
        
        Este é um snapshot do estado do Context no momento exato da criação
        do evento. Permite que o Player execute de forma independente do
        que acontece com o Context posteriormente.
        
        Args:
            type_ (str): 'note', 'silence' ou 'control'
            note (str | None): Nome da nota ou None
            octave (int): Oitava (0-8)
            volume (int): Volume (0-127)
            instrument (int): Instrumento MIDI (0-127)
            duration_ms (int): Duração em ms
        """
        self.type = type_
        self.note = note
        self.octave = octave
        self.volume = volume
        self.instrument = instrument
        self.duration_ms = duration_ms
    
    def __repr__(self):
        """
        Retorna uma representação textual do evento, útil para debug e testes.
        
        Exemplo de saída:
            MusicEvent(note='La', octave=4, volume=64, duration_ms=500)
            MusicEvent(silence, duration_ms=500)
            MusicEvent(control, instrument=24)
        """
        if self.type == 'note':
            return (f"MusicEvent(note='{self.note}', octave={self.octave}, "
                   f"volume={self.volume}, duration_ms={self.duration_ms})")
        elif self.type == 'silence':
            return f"MusicEvent(silence, duration_ms={self.duration_ms})"
        else:  # control
            return (f"MusicEvent(control, instrument={self.instrument}, "
                   f"volume={self.volume})")
