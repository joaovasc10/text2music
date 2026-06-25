"""
Classe Interpreter - TextoMúsica

Orquestrador central. Usa TextReader para iterar, CharacterMapper para
classificar e Context para manter o estado. Produz uma lista de MusicEvents
para o Player.

A interpretação de cada caractere é feita por uma lista ordenada de regras
(_rules). Cada regra é um método pequeno que tenta tratar o caractere e
devolve o tipo do evento ('note', 'silence', 'control') ou None se não se
aplica. Isso substitui a antiga cascata de if/elif por unidades testáveis e
facilita adicionar novas regras (princípio Aberto/Fechado).
"""

from music_event import MusicEvent
from context import Context
from character_mapper import CharacterMapper
from text_reader import TextReader


class Interpreter:
    """
    Transforma texto em uma sequência de eventos musicais.

    Atributos:
        context (Context): Estado dinâmico da execução
        mapper (CharacterMapper): Classificador de caracteres
        reader (TextReader): Leitor do texto
    """

    def __init__(self):
        """Inicializa o Interpreter com seus componentes e a lista de regras."""
        self.context = Context()
        self.mapper = CharacterMapper()
        self.reader = TextReader()

        # Ordem importa: a primeira regra que devolver um tipo de evento vence.
        self._rules = [
            self._rule_mi_bemol,
            self._rule_lower_octave,
            self._rule_change_bpm,
            self._rule_note,
            self._rule_silence,
            self._rule_double_volume,
            self._rule_raise_octave,
            self._rule_even_digit,
            self._rule_odd_digit,
            self._rule_instrument_change,
            self._rule_repeat,
        ]

    def interpret_text(self, text):
        """
        Processa todo o texto e retorna a lista de MusicEvents.

        Args:
            text (str): Texto a processar

        Returns:
            list[MusicEvent]: Lista de eventos gerados
        """
        self.reader.load(text)

        events = []
        for token in self.reader.characters():
            if token == 'NL':
                # Fase 2: a nova linha é apenas separador de vozes
                continue
            if self._is_delay_token(token):
                events.extend(self._build_delay(token))
            else:
                events.append(self.interpret_char(token))
        return events

    def interpret_char(self, char):
        """
        Processa um único token e retorna um MusicEvent.

        Aplica as regras em ordem; a primeira que devolver um tipo de evento
        define o resultado. Se nenhuma se aplicar, o padrão é silêncio.

        Args:
            char (str): Token a processar

        Returns:
            MusicEvent: Evento gerado (snapshot do Context atual)
        """
        event_type = None
        for rule in self._rules:
            event_type = rule(char)
            if event_type is not None:
                break

        if event_type is None:
            event_type = 'silence'

        return self._build_event(event_type)

    # ------------------------------------------------------------------
    # Construção de eventos
    # ------------------------------------------------------------------

    def _build_event(self, event_type):
        """Monta um MusicEvent com um snapshot dos valores atuais do Context."""
        return MusicEvent(
            type_=event_type,
            note=self.context.get_last_note(),
            octave=self.context.get_octave(),
            volume=self.context.get_volume(),
            instrument=self.context.get_instrument(),
            duration_ms=self.context.note_duration_ms(),
        )

    @staticmethod
    def _is_delay_token(token):
        """True se o token é um atraso de entrada no formato [n]."""
        return token.startswith('[') and token.endswith(']') and token[1:-1].isdigit()

    def _build_delay(self, token):
        """Expande um token [n] em n eventos de silêncio (atraso de entrada)."""
        n = int(token[1:-1])
        return [self._build_event('silence') for _ in range(n)]

    # ------------------------------------------------------------------
    # Regras de mapeamento (cada uma devolve o tipo de evento ou None)
    # ------------------------------------------------------------------

    def _rule_mi_bemol(self, char):
        if char == 'Mb':
            self.context.set_last_note('MiBemol')
            return 'note'
        return None

    def _rule_lower_octave(self, char):
        if self.mapper.should_lower_octave(char):
            self.context.lower_octave()
            return 'control'
        return None

    def _rule_change_bpm(self, char):
        if self.mapper.should_accelerate(char):
            self.context.increase_bpm()
            return 'control'
        if self.mapper.should_decelerate(char):
            self.context.decrease_bpm()
            return 'control'
        return None

    def _rule_note(self, char):
        if self.mapper.is_note(char):
            self.context.set_last_note(self.mapper.get_note(char))
            return 'note'
        return None

    def _rule_silence(self, char):
        if self.mapper.is_silence(char):
            self.context.set_last_note(None)
            return 'silence'
        return None

    def _rule_double_volume(self, char):
        if self.mapper.should_double_volume(char):
            self.context.set_volume(self.context.get_volume() * 2)
            return 'control'
        return None

    def _rule_raise_octave(self, char):
        if self.mapper.should_raise_octave(char):
            self.context.set_octave(self.context.get_octave() + 1)
            return 'control'
        return None

    def _rule_even_digit(self, char):
        offset = self.mapper.get_even_digit_offset(char)
        if offset is not None:
            self.context.set_instrument(self.context.get_instrument() + offset)
            return 'control'
        return None

    def _rule_odd_digit(self, char):
        instrument = self.mapper.get_odd_digit_instrument(char)
        if instrument is not None:
            self.context.set_instrument(instrument)
            return 'control'
        return None

    def _rule_instrument_change(self, char):
        instrument = self.mapper.get_instrument_change(char)
        if instrument is not None:
            self.context.set_instrument(instrument)
            return 'control'
        return None

    def _rule_repeat(self, char):
        if self.mapper.is_repeat_condition(char):
            # Repete a última nota se houver; caso contrário, silêncio
            return 'note' if self.context.get_last_note() is not None else 'silence'
        return None
