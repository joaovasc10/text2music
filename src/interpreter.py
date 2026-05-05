"""
Classe Interpreter - TextoMúsica

Orquestrador central. Usa TextReader para iterar, CharacterMapper para
classificar e Context para manter o estado. Produz uma lista de MusicEvents
para o Player.

A separação entre interpret_text e interpret_char facilita testes unitários
independentes.
"""

from music_event import MusicEvent
from context import Context
from character_mapper import CharacterMapper
from text_reader import TextReader


class Interpreter:
    """
    Responsável por transformar texto em uma sequência de eventos musicais.
    
    Atributos:
        context (Context): Estado dinâmico da execução
        mapper (CharacterMapper): Classificador de caracteres
        reader (TextReader): Leitor do texto
    """
    
    def __init__(self):
        """Inicializa o Interpreter com seus componentes."""
        self.context = Context()
        self.mapper = CharacterMapper()
        self.reader = TextReader()
    
    def interpret_text(self, text):
        """
        Loop principal: processa todo o texto e retorna lista de MusicEvents.
        
        Carrega o texto no TextReader, itera caractere a caractere
        chamando interpret_char(), acumula e retorna a lista de eventos.
        
        Args:
            text (str): Texto a processar
            
        Returns:
            list[MusicEvent]: Lista de eventos gerados
        """
        # Carrega o texto no leitor
        self.reader.load(text)
        
        # Lista para acumular eventos
        events = []
        
        # Processa cada caractere
        for char in self.reader.characters():
            event = self.interpret_char(char)
            events.append(event)
        
        return events
    
    def interpret_char(self, char):
        """
        Processa um único caractere e retorna um MusicEvent.
        
        Esta é a lógica central da interpretação.
        Consulta CharacterMapper para classificar o caractere,
        atualiza Context conforme necessário e monta um MusicEvent
        com um snapshot dos valores atuais do Context.
        
        A ordem de verificação é importante! Checamos em cascata:
        1. É uma nota?
        2. É silêncio?
        3. Deve dobrar volume?
        4. Deve subir oitava?
        5. É dígito par (offset instrumento)?
        6. É dígito ímpar (Tubular Bells)?
        7. Muda instrumento?
        8. É repetição?
        
        Args:
            char (str): Caractere a processar
            
        Returns:
            MusicEvent: Evento gerado
        """
        
        event_type = None
        
        # ====================================================================
        # 1. Verificar se é uma nota (A-H maiúsculas)
        # ====================================================================
        if self.mapper.is_note(char):
            note = self.mapper.get_note(char)
            self.context.set_last_note(note)
            event_type = 'note'
        
        # ====================================================================
        # 2. Verificar se é silêncio (a-h minúsculas)
        # ====================================================================
        elif self.mapper.is_silence(char):
            self.context.set_last_note(None)
            event_type = 'silence'
        
        # ====================================================================
        # 3. Verificar se deve dobrar o volume (espaço)
        # ====================================================================
        elif self.mapper.should_double_volume(char):
            current_volume = self.context.get_volume()
            new_volume = current_volume * 2
            self.context.set_volume(new_volume)
            event_type = 'control'
        
        # ====================================================================
        # 4. Verificar se deve subir uma oitava (? ou .)
        # ====================================================================
        elif self.mapper.should_raise_octave(char):
            current_octave = self.context.get_octave()
            self.context.set_octave(current_octave + 1)
            event_type = 'control'
        
        # ====================================================================
        # 5. Verificar se é dígito par (offset de instrumento)
        # ====================================================================
        else:
            offset = self.mapper.get_even_digit_offset(char)
            if offset is not None:
                current_instrument = self.context.get_instrument()
                self.context.set_instrument(current_instrument + offset)
                event_type = 'control'
        
        # ====================================================================
        # 6. Verificar se é dígito ímpar (Tubular Bells)
        # ====================================================================
        if event_type is None:
            instrument = self.mapper.get_odd_digit_instrument(char)
            if instrument is not None:
                self.context.set_instrument(instrument)
                event_type = 'control'
        
        # ====================================================================
        # 7. Verificar se muda instrumento (!, vogais, ;, ',', NL)
        # ====================================================================
        if event_type is None:
            instr = self.mapper.get_instrument_change(char)
            if instr is not None:
                self.context.set_instrument(instr)
                event_type = 'control'
        
        # ====================================================================
        # 8. Verificar se é repetição (consoante não-nota ou ELSE)
        # ====================================================================
        if event_type is None:
            if self.mapper.is_repeat_condition(char):
                last_note = self.context.get_last_note()
                if last_note is not None:
                    # Há uma nota anterior: repetir
                    event_type = 'note'
                else:
                    # Não há nota anterior: silêncio
                    event_type = 'silence'
        
        # ====================================================================
        # Se nenhuma regra foi atendida, é silêncio (padrão)
        # ====================================================================
        if event_type is None:
            event_type = 'silence'
        
        # ====================================================================
        # Montar e retornar MusicEvent com snapshot do Context
        # ====================================================================
        event = MusicEvent(
            type_=event_type,
            note=self.context.get_last_note(),
            octave=self.context.get_octave(),
            volume=self.context.get_volume(),
            instrument=self.context.get_instrument(),
            duration_ms=self.context.note_duration_ms()
        )
        
        return event
