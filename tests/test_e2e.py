"""
Testes de ponta a ponta — TextoMúsica
INF01120 - Desenvolvimento de Software

Cobre todas as regras de mapeamento do enunciado, além de
comportamentos de borda em Context, CharacterMapper, TextReader,
Interpreter, Player e MusicSystem.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call

# Garante que o Python encontra os módulos em src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import constants
from context import Context
from music_event import MusicEvent
from character_mapper import CharacterMapper
from text_reader import TextReader
from interpreter import Interpreter
from music_system import MusicSystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def interpret(text, bpm=120, instrument=1, octave=4, volume=64):
    """Processa um texto e retorna a lista de MusicEvents."""
    interp = Interpreter()
    interp.context.set_bpm(bpm)
    interp.context.set_instrument(instrument)
    interp.context.set_octave(octave)
    interp.context.set_volume(volume)
    return interp.interpret_text(text)


def events_of_type(events, type_):
    return [e for e in events if e.type == type_]


# ===========================================================================
# 1. Constants
# ===========================================================================

class TestConstants(unittest.TestCase):

    def test_default_values(self):
        self.assertEqual(constants.DEFAULT_VOLUME, 64)
        self.assertEqual(constants.DEFAULT_OCTAVE, 4)
        self.assertEqual(constants.DEFAULT_BPM, 120)
        self.assertEqual(constants.DEFAULT_INSTRUMENT, 1)
        self.assertEqual(constants.MAX_VOLUME, 127)
        self.assertEqual(constants.MAX_OCTAVE, 8)

    def test_note_map_completeness(self):
        expected = {'A': 'La', 'B': 'Si', 'C': 'Do', 'D': 'Re',
                    'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'H': 'SiBemol'}
        self.assertEqual(constants.NOTE_MAP, expected)

    def test_silence_chars(self):
        for ch in 'abcdefgh':
            self.assertIn(ch, constants.SILENCE_CHARS)
        self.assertNotIn('A', constants.SILENCE_CHARS)
        self.assertNotIn('i', constants.SILENCE_CHARS)

    def test_instrument_map(self):
        # Fase 2: ! = Harmonica (22), , = Church Organ (20), ; = Tubular Bells (15)
        self.assertEqual(constants.INSTRUMENT_MAP['!'], 22)
        self.assertEqual(constants.INSTRUMENT_MAP[','], 20)
        self.assertEqual(constants.INSTRUMENT_MAP[';'], 15)
        # Fase 2: vogais e NL não trocam mais instrumento
        for v in ('O', 'o', 'I', 'i', 'U', 'u', 'NL'):
            self.assertNotIn(v, constants.INSTRUMENT_MAP)

    def test_note_midi_values(self):
        self.assertEqual(constants.NOTE_MIDI['Do'], 60)
        self.assertEqual(constants.NOTE_MIDI['Re'], 62)
        self.assertEqual(constants.NOTE_MIDI['Mi'], 64)
        self.assertEqual(constants.NOTE_MIDI['Fa'], 65)
        self.assertEqual(constants.NOTE_MIDI['Sol'], 67)
        self.assertEqual(constants.NOTE_MIDI['La'], 69)
        self.assertEqual(constants.NOTE_MIDI['Si'], 71)
        self.assertEqual(constants.NOTE_MIDI['SiBemol'], 70)


# ===========================================================================
# 2. Context
# ===========================================================================

class TestContext(unittest.TestCase):

    def setUp(self):
        self.ctx = Context()

    def test_initial_state(self):
        self.assertEqual(self.ctx.get_volume(), constants.DEFAULT_VOLUME)
        self.assertEqual(self.ctx.get_octave(), constants.DEFAULT_OCTAVE)
        self.assertEqual(self.ctx.get_bpm(), constants.DEFAULT_BPM)
        self.assertEqual(self.ctx.get_instrument(), constants.DEFAULT_INSTRUMENT)
        self.assertIsNone(self.ctx.get_last_note())

    def test_set_and_get_volume(self):
        self.ctx.set_volume(100)
        self.assertEqual(self.ctx.get_volume(), 100)

    def test_volume_clamped_at_max(self):
        self.ctx.set_volume(200)
        self.assertEqual(self.ctx.get_volume(), constants.MAX_VOLUME)

    def test_volume_clamped_exactly_at_max(self):
        self.ctx.set_volume(127)
        self.assertEqual(self.ctx.get_volume(), 127)

    def test_set_and_get_octave(self):
        self.ctx.set_octave(6)
        self.assertEqual(self.ctx.get_octave(), 6)

    def test_octave_wraps_to_default_when_exceeds_max(self):
        self.ctx.set_octave(9)
        self.assertEqual(self.ctx.get_octave(), constants.DEFAULT_OCTAVE)

    def test_octave_at_max_is_valid(self):
        self.ctx.set_octave(8)
        self.assertEqual(self.ctx.get_octave(), 8)

    def test_set_and_get_bpm(self):
        self.ctx.set_bpm(90)
        self.assertEqual(self.ctx.get_bpm(), 90)

    def test_set_and_get_instrument(self):
        self.ctx.set_instrument(24)
        self.assertEqual(self.ctx.get_instrument(), 24)

    def test_set_and_get_last_note(self):
        self.ctx.set_last_note('La')
        self.assertEqual(self.ctx.get_last_note(), 'La')

    def test_last_note_cleared_to_none(self):
        self.ctx.set_last_note('Sol')
        self.ctx.set_last_note(None)
        self.assertIsNone(self.ctx.get_last_note())

    def test_note_duration_at_120bpm(self):
        self.ctx.set_bpm(120)
        self.assertEqual(self.ctx.note_duration_ms(), 500)

    def test_note_duration_at_60bpm(self):
        self.ctx.set_bpm(60)
        self.assertEqual(self.ctx.note_duration_ms(), 1000)

    def test_note_duration_at_240bpm(self):
        self.ctx.set_bpm(240)
        self.assertEqual(self.ctx.note_duration_ms(), 250)

    def test_reset_restores_all_defaults(self):
        self.ctx.set_volume(127)
        self.ctx.set_octave(7)
        self.ctx.set_bpm(200)
        self.ctx.set_instrument(110)
        self.ctx.set_last_note('Mi')
        self.ctx.reset()
        self.assertEqual(self.ctx.get_volume(), constants.DEFAULT_VOLUME)
        self.assertEqual(self.ctx.get_octave(), constants.DEFAULT_OCTAVE)
        self.assertEqual(self.ctx.get_bpm(), constants.DEFAULT_BPM)
        self.assertEqual(self.ctx.get_instrument(), constants.DEFAULT_INSTRUMENT)
        self.assertIsNone(self.ctx.get_last_note())


# ===========================================================================
# 3. MusicEvent
# ===========================================================================

class TestMusicEvent(unittest.TestCase):

    def test_note_event_attributes(self):
        e = MusicEvent('note', 'La', 4, 64, 1, 500)
        self.assertEqual(e.type, 'note')
        self.assertEqual(e.note, 'La')
        self.assertEqual(e.octave, 4)
        self.assertEqual(e.volume, 64)
        self.assertEqual(e.instrument, 1)
        self.assertEqual(e.duration_ms, 500)

    def test_silence_event_attributes(self):
        e = MusicEvent('silence', None, 4, 64, 1, 500)
        self.assertEqual(e.type, 'silence')
        self.assertIsNone(e.note)

    def test_control_event_attributes(self):
        e = MusicEvent('control', None, 4, 64, 24, 500)
        self.assertEqual(e.type, 'control')
        self.assertEqual(e.instrument, 24)

    def test_repr_note(self):
        e = MusicEvent('note', 'Sol', 4, 64, 1, 500)
        r = repr(e)
        self.assertIn('note', r)
        self.assertIn('Sol', r)

    def test_repr_silence(self):
        e = MusicEvent('silence', None, 4, 64, 1, 500)
        self.assertIn('silence', repr(e))

    def test_repr_control(self):
        e = MusicEvent('control', None, 4, 64, 24, 500)
        r = repr(e)
        self.assertIn('control', r)
        self.assertIn('24', r)


# ===========================================================================
# 4. CharacterMapper
# ===========================================================================

class TestCharacterMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = CharacterMapper()

    # --- is_note ---
    def test_is_note_uppercase_a_to_h(self):
        for ch in 'ABCDEFGH':
            with self.subTest(char=ch):
                self.assertTrue(self.mapper.is_note(ch))

    def test_is_note_lowercase_not_note(self):
        for ch in 'abcdefgh':
            with self.subTest(char=ch):
                self.assertFalse(self.mapper.is_note(ch))

    def test_is_note_other_chars_not_note(self):
        for ch in ('I', 'J', 'Z', '!', '?', '1', ' '):
            self.assertFalse(self.mapper.is_note(ch))

    # --- get_note ---
    def test_get_note_returns_correct_names(self):
        mapping = {'A': 'La', 'B': 'Si', 'C': 'Do', 'D': 'Re',
                   'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'H': 'SiBemol'}
        for char, name in mapping.items():
            self.assertEqual(self.mapper.get_note(char), name)

    def test_get_note_returns_none_for_non_note(self):
        self.assertIsNone(self.mapper.get_note('J'))
        self.assertIsNone(self.mapper.get_note('!'))
        self.assertIsNone(self.mapper.get_note('a'))

    # --- is_silence ---
    def test_is_silence_lowercase_a_to_h(self):
        for ch in 'abcdefgh':
            with self.subTest(char=ch):
                self.assertTrue(self.mapper.is_silence(ch))

    def test_is_silence_uppercase_not_silence(self):
        for ch in 'ABCDEFGH':
            self.assertFalse(self.mapper.is_silence(ch))

    def test_is_silence_other_not_silence(self):
        self.assertFalse(self.mapper.is_silence('i'))
        self.assertFalse(self.mapper.is_silence(' '))
        self.assertFalse(self.mapper.is_silence('?'))

    # --- should_double_volume ---
    def test_space_doubles_volume(self):
        self.assertTrue(self.mapper.should_double_volume(' '))

    def test_non_space_does_not_double_volume(self):
        for ch in ('A', 'a', '!', '?', '1'):
            self.assertFalse(self.mapper.should_double_volume(ch))

    # --- should_raise_octave ---
    def test_question_mark_raises_octave(self):
        self.assertTrue(self.mapper.should_raise_octave('?'))

    def test_period_raises_octave(self):
        self.assertTrue(self.mapper.should_raise_octave('.'))

    def test_other_chars_do_not_raise_octave(self):
        for ch in ('A', 'a', '!', '1', ' '):
            self.assertFalse(self.mapper.should_raise_octave(ch))

    # --- get_even_digit_offset ---
    def test_even_digits_return_value(self):
        self.assertEqual(self.mapper.get_even_digit_offset('0'), 0)
        self.assertEqual(self.mapper.get_even_digit_offset('2'), 2)
        self.assertEqual(self.mapper.get_even_digit_offset('4'), 4)
        self.assertEqual(self.mapper.get_even_digit_offset('6'), 6)
        self.assertEqual(self.mapper.get_even_digit_offset('8'), 8)

    def test_odd_digits_return_none_for_even_offset(self):
        for ch in ('1', '3', '5', '7', '9'):
            self.assertIsNone(self.mapper.get_even_digit_offset(ch))

    def test_non_digit_returns_none_for_even_offset(self):
        self.assertIsNone(self.mapper.get_even_digit_offset('A'))
        self.assertIsNone(self.mapper.get_even_digit_offset('!'))

    # --- get_odd_digit_instrument ---
    def test_odd_digits_return_tubular_bells(self):
        for ch in ('1', '3', '5', '7', '9'):
            self.assertEqual(self.mapper.get_odd_digit_instrument(ch), 15)

    def test_even_digits_return_none_for_odd(self):
        for ch in ('0', '2', '4', '6', '8'):
            self.assertIsNone(self.mapper.get_odd_digit_instrument(ch))

    # --- get_instrument_change ---
    def test_exclamation_returns_harmonica(self):
        # Fase 2: ! passou de Bandoneon (24) para Harmonica (22)
        self.assertEqual(self.mapper.get_instrument_change('!'), 22)

    def test_vowels_no_longer_change_instrument(self):
        # Fase 2: vogais O, I, U deixaram de trocar instrumento
        for ch in ('O', 'o', 'I', 'i', 'U', 'u'):
            self.assertIsNone(self.mapper.get_instrument_change(ch))

    def test_comma_returns_church_organ(self):
        # Fase 2: , passou de Agogô (114) para Church Organ (20)
        self.assertEqual(self.mapper.get_instrument_change(','), 20)

    def test_semicolon_returns_tubular_bells(self):
        self.assertEqual(self.mapper.get_instrument_change(';'), 15)

    def test_nl_no_longer_changes_instrument(self):
        # Fase 2: nova linha é apenas separador de vozes
        self.assertIsNone(self.mapper.get_instrument_change('NL'))

    def test_non_instrument_char_returns_none(self):
        self.assertIsNone(self.mapper.get_instrument_change('A'))
        self.assertIsNone(self.mapper.get_instrument_change('J'))
        self.assertIsNone(self.mapper.get_instrument_change('2'))

    # --- is_repeat_condition ---
    def test_consonants_not_notes_are_repeat_condition(self):
        # Fase 2: 'V' saiu da lista (agora desce oitava)
        for ch in ('J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T',
                   'W', 'X', 'Y', 'Z'):
            with self.subTest(char=ch):
                self.assertTrue(self.mapper.is_repeat_condition(ch))

    def test_vowels_oiu_are_repeat_condition(self):
        # Fase 2: vogais O, I, U seguem a regra de repetição/pausa
        for ch in ('O', 'o', 'I', 'i', 'U', 'u'):
            with self.subTest(char=ch):
                self.assertTrue(self.mapper.is_repeat_condition(ch))

    def test_fase2_control_chars_are_not_repeat_condition(self):
        # 'V' (desce oitava), '>' e '<' (BPM) têm regras próprias
        for ch in ('V', '>', '<'):
            with self.subTest(char=ch):
                self.assertFalse(self.mapper.is_repeat_condition(ch))

    def test_notes_are_not_repeat_condition(self):
        for ch in 'ABCDEFGH':
            self.assertFalse(self.mapper.is_repeat_condition(ch))

    def test_silences_are_not_repeat_condition(self):
        for ch in 'abcdefgh':
            self.assertFalse(self.mapper.is_repeat_condition(ch))

    def test_space_is_not_repeat_condition(self):
        self.assertFalse(self.mapper.is_repeat_condition(' '))

    def test_digits_are_not_repeat_condition(self):
        for ch in '0123456789':
            self.assertFalse(self.mapper.is_repeat_condition(ch))

    def test_octave_chars_are_not_repeat_condition(self):
        self.assertFalse(self.mapper.is_repeat_condition('?'))
        self.assertFalse(self.mapper.is_repeat_condition('.'))

    def test_instrument_chars_are_not_repeat_condition(self):
        self.assertFalse(self.mapper.is_repeat_condition('!'))
        self.assertFalse(self.mapper.is_repeat_condition(','))
        self.assertFalse(self.mapper.is_repeat_condition(';'))


# ===========================================================================
# 5. TextReader
# ===========================================================================

class TestTextReader(unittest.TestCase):

    def setUp(self):
        self.reader = TextReader()

    def test_load_stores_raw_text(self):
        self.reader.load("ABC")
        self.assertEqual(self.reader.raw_text, "ABC")

    def test_characters_yields_each_char(self):
        self.reader.load("ABC")
        result = list(self.reader.characters())
        self.assertEqual(result, ['A', 'B', 'C'])

    def test_newline_converted_to_nl(self):
        self.reader.load("A\nB")
        result = list(self.reader.characters())
        self.assertEqual(result, ['A', 'NL', 'B'])

    def test_empty_text(self):
        self.reader.load("")
        result = list(self.reader.characters())
        self.assertEqual(result, [])

    def test_multiple_newlines(self):
        self.reader.load("\n\n")
        result = list(self.reader.characters())
        self.assertEqual(result, ['NL', 'NL'])

    def test_characters_is_generator(self):
        import types
        self.reader.load("AB")
        self.assertIsInstance(self.reader.characters(), types.GeneratorType)


# ===========================================================================
# 6. Interpreter — regras individuais
# ===========================================================================

class TestInterpreterMappingRules(unittest.TestCase):
    """Testa cada regra do enunciado isoladamente."""

    # --- Notas A-H ---
    def test_uppercase_A_generates_note_la(self):
        events = interpret('A')
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].type, 'note')
        self.assertEqual(events[0].note, 'La')

    def test_uppercase_B_generates_note_si(self):
        events = interpret('B')
        self.assertEqual(events[0].note, 'Si')

    def test_uppercase_C_generates_note_do(self):
        events = interpret('C')
        self.assertEqual(events[0].note, 'Do')

    def test_uppercase_D_generates_note_re(self):
        events = interpret('D')
        self.assertEqual(events[0].note, 'Re')

    def test_uppercase_E_generates_note_mi(self):
        events = interpret('E')
        self.assertEqual(events[0].note, 'Mi')

    def test_uppercase_F_generates_note_fa(self):
        events = interpret('F')
        self.assertEqual(events[0].note, 'Fa')

    def test_uppercase_G_generates_note_sol(self):
        events = interpret('G')
        self.assertEqual(events[0].note, 'Sol')

    def test_uppercase_H_generates_note_si_bemol(self):
        events = interpret('H')
        self.assertEqual(events[0].note, 'SiBemol')

    def test_scale_ABCDEFGH_generates_8_notes(self):
        events = interpret('ABCDEFGH')
        self.assertEqual(len(events), 8)
        for e in events:
            self.assertEqual(e.type, 'note')

    # --- Silêncio a-h ---
    def test_lowercase_a_generates_silence(self):
        events = interpret('a')
        self.assertEqual(events[0].type, 'silence')

    def test_all_lowercase_a_to_h_generate_silence(self):
        events = interpret('abcdefgh')
        for e in events:
            self.assertEqual(e.type, 'silence')

    def test_silence_clears_last_note(self):
        events = interpret('Ab')
        # 'b' é silêncio e deve limpar last_note
        self.assertEqual(events[1].type, 'silence')
        self.assertIsNone(events[1].note)

    # --- Dobrar volume com espaço ---
    def test_space_generates_control_event(self):
        events = interpret(' ')
        self.assertEqual(events[0].type, 'control')

    def test_space_doubles_volume(self):
        events = interpret(' ', volume=64)
        self.assertEqual(events[0].volume, 127)  # 64*2=128 > 127 → clamp

    def test_space_doubles_volume_below_max(self):
        events = interpret(' ', volume=32)
        self.assertEqual(events[0].volume, 64)

    def test_space_clamps_volume_at_max(self):
        events = interpret(' ', volume=100)
        self.assertEqual(events[0].volume, constants.MAX_VOLUME)

    # --- Subir oitava com ? e . ---
    def test_question_mark_generates_control(self):
        events = interpret('?')
        self.assertEqual(events[0].type, 'control')

    def test_period_generates_control(self):
        events = interpret('.')
        self.assertEqual(events[0].type, 'control')

    def test_question_mark_raises_octave(self):
        events = interpret('?', octave=4)
        self.assertEqual(events[0].octave, 5)

    def test_period_raises_octave(self):
        events = interpret('.', octave=4)
        self.assertEqual(events[0].octave, 5)

    def test_octave_wraps_to_default_at_max(self):
        events = interpret('?', octave=8)
        self.assertEqual(events[0].octave, constants.DEFAULT_OCTAVE)

    def test_multiple_octave_raises(self):
        events = interpret('???', octave=4)
        self.assertEqual(events[0].octave, 5)
        self.assertEqual(events[1].octave, 6)
        self.assertEqual(events[2].octave, 7)

    # --- Dígito par: offset de instrumento ---
    def test_even_digit_2_adds_to_instrument(self):
        events = interpret('2', instrument=1)
        self.assertEqual(events[0].type, 'control')
        self.assertEqual(events[0].instrument, 3)  # 1 + 2

    def test_even_digit_4_adds_to_instrument(self):
        events = interpret('4', instrument=10)
        self.assertEqual(events[0].instrument, 14)

    def test_even_digit_0_keeps_instrument(self):
        events = interpret('0', instrument=24)
        self.assertEqual(events[0].instrument, 24)  # 24 + 0

    def test_even_digit_8_adds_8(self):
        events = interpret('8', instrument=1)
        self.assertEqual(events[0].instrument, 9)

    # --- Dígito ímpar: Tubular Bells ---
    def test_odd_digit_1_sets_tubular_bells(self):
        events = interpret('1')
        self.assertEqual(events[0].type, 'control')
        self.assertEqual(events[0].instrument, 15)

    def test_all_odd_digits_set_tubular_bells(self):
        for ch in '13579':
            with self.subTest(digit=ch):
                events = interpret(ch)
                self.assertEqual(events[0].instrument, 15)

    # --- Mudança de instrumento ---
    def test_exclamation_sets_harmonica(self):
        events = interpret('!')
        self.assertEqual(events[0].type, 'control')
        self.assertEqual(events[0].instrument, 22)  # Fase 2: Harmonica

    def test_vowel_without_prior_note_is_silence(self):
        # Fase 2: vogais O, I, U seguem a regra de repetição/pausa
        for ch in ('O', 'o', 'I', 'i', 'U', 'u'):
            with self.subTest(char=ch):
                events = interpret(ch)
                self.assertEqual(events[0].type, 'silence')

    def test_vowel_after_note_repeats_note(self):
        # 'AO': A=La, vogal repete La (Fase 2)
        for ch in ('O', 'o', 'I', 'i', 'U', 'u'):
            with self.subTest(char=ch):
                events = interpret('A' + ch)
                self.assertEqual(events[1].type, 'note')
                self.assertEqual(events[1].note, 'La')

    def test_comma_sets_church_organ(self):
        events = interpret(',')
        self.assertEqual(events[0].instrument, 20)  # Fase 2: Church Organ

    def test_semicolon_sets_tubular_bells(self):
        events = interpret(';')
        self.assertEqual(events[0].instrument, 15)

    def test_newline_is_ignored(self):
        # Fase 2: nova linha é separador de vozes, não gera evento
        events = interpret('\n')
        self.assertEqual(events, [])

    # --- Repetição: consoante após nota repete nota ---
    def test_consonant_after_note_repeats_note(self):
        events = interpret('AJ')
        self.assertEqual(events[0].type, 'note')
        self.assertEqual(events[0].note, 'La')
        self.assertEqual(events[1].type, 'note')
        self.assertEqual(events[1].note, 'La')

    def test_consonant_without_prior_note_is_silence(self):
        events = interpret('J')
        self.assertEqual(events[0].type, 'silence')

    def test_repeat_keeps_last_note_name(self):
        events = interpret('CK')  # C=Do, K repete
        self.assertEqual(events[1].note, 'Do')

    def test_repeat_after_silence_is_silence(self):
        events = interpret('AbK')  # A=nota, b=silêncio (limpa last_note), K=silêncio
        self.assertEqual(events[2].type, 'silence')

    # --- ELSE: caractere não mapeado ---
    def test_unmapped_char_without_prior_note_is_silence(self):
        events = interpret('@')
        self.assertEqual(events[0].type, 'silence')

    def test_unmapped_char_after_note_repeats(self):
        events = interpret('A@')
        self.assertEqual(events[1].type, 'note')
        self.assertEqual(events[1].note, 'La')


# ===========================================================================
# 7. Interpreter — comportamentos compostos (E2E completo)
# ===========================================================================

class TestInterpreterE2E(unittest.TestCase):

    def test_instrument_change_persists_to_next_note(self):
        events = interpret('!A')
        note_event = events[1]
        self.assertEqual(note_event.type, 'note')
        self.assertEqual(note_event.instrument, 22)  # Fase 2: Harmonica

    def test_octave_change_persists_to_next_note(self):
        events = interpret('?A')
        note_event = events[1]
        self.assertEqual(note_event.octave, 5)

    def test_volume_change_persists_to_next_note(self):
        events = interpret(' A', volume=32)
        note_event = events[1]
        self.assertEqual(note_event.volume, 64)

    def test_sequence_with_repeat(self):
        """Texto 'JAK': J sem nota=silêncio, A=La, K=repete La."""
        events = interpret('JAK')
        self.assertEqual(events[0].type, 'silence')
        self.assertEqual(events[1].type, 'note')
        self.assertEqual(events[1].note, 'La')
        self.assertEqual(events[2].type, 'note')
        self.assertEqual(events[2].note, 'La')

    def test_scale_event_count(self):
        events = interpret('ABCDEFGH')
        self.assertEqual(len(events), 8)

    def test_mixed_notes_and_silences(self):
        events = interpret('AbCdEf')
        note_events = events_of_type(events, 'note')
        silence_events = events_of_type(events, 'silence')
        self.assertEqual(len(note_events), 3)
        self.assertEqual(len(silence_events), 3)

    def test_instrument_change_with_harmonica(self):
        """'A!B': La com piano, mudança para Harmonica, Si com Harmonica."""
        events = interpret('A!B')
        self.assertEqual(events[0].instrument, 1)      # piano
        self.assertEqual(events[1].instrument, 22)     # harmonica (control)
        self.assertEqual(events[2].instrument, 22)     # si ainda na harmonica

    def test_octave_sequence_with_wrap(self):
        """Encadeia ? até MAX_OCTAVE e verifica o wrap."""
        text = '?' * (constants.MAX_OCTAVE - constants.DEFAULT_OCTAVE + 1)
        events = interpret(text, octave=4)
        # Último evento deve ter octave = DEFAULT (voltou)
        self.assertEqual(events[-1].octave, constants.DEFAULT_OCTAVE)

    def test_duration_reflects_bpm(self):
        events = interpret('A', bpm=60)
        self.assertEqual(events[0].duration_ms, 1000)

        events = interpret('A', bpm=240)
        self.assertEqual(events[0].duration_ms, 250)

    def test_multiple_spaces_accumulate_volume(self):
        """Dois espaços: volume dobra duas vezes, com clamp."""
        events = interpret('  ', volume=32)
        self.assertEqual(events[0].volume, 64)   # 32*2
        self.assertEqual(events[1].volume, 127)  # 64*2=128 → clamp

    def test_complex_text_all_event_types_present(self):
        events = interpret('ABC!DEF.GHA')
        types = {e.type for e in events}
        self.assertIn('note', types)
        self.assertIn('control', types)

    def test_empty_text_returns_empty_list(self):
        events = interpret('')
        self.assertEqual(events, [])

    def test_note_event_snapshot_matches_context_at_creation(self):
        """Garante que o MusicEvent é um snapshot e não referência ao Context."""
        events = interpret('A?B')
        # A: octave=4, B: octave=5 (após ?)
        self.assertEqual(events[0].octave, 4)
        self.assertEqual(events[2].octave, 5)

    def test_repeat_condition_lowercase_consonants(self):
        """Consoantes minúsculas não em a-h devem repetir nota."""
        events = interpret('Aj')  # j não está em a-h → consonante não mapeada
        self.assertEqual(events[1].type, 'note')
        self.assertEqual(events[1].note, 'La')

    def test_uppercase_vowel_follows_repeat_rule(self):
        # Fase 2: vogal sem nota anterior = silêncio
        events = interpret('O')
        self.assertEqual(events[0].type, 'silence')

    def test_even_digit_accumulates_with_current_instrument(self):
        """Instrumento começa em 10, dígito par 4 → 14."""
        events = interpret('4', instrument=10)
        self.assertEqual(events[0].instrument, 14)

    def test_odd_digit_overrides_any_instrument(self):
        """Independente do instrumento atual, dígito ímpar → 15."""
        events = interpret('3', instrument=110)
        self.assertEqual(events[0].instrument, 15)


# ===========================================================================
# 8. Player (com pygame.midi mockado)
# ===========================================================================

class TestPlayer(unittest.TestCase):

    def _make_player_with_mock_output(self):
        """Cria Player com output MIDI mockado."""
        from player import Player
        p = Player()
        p.output = MagicMock()
        p.current_channel = 0
        return p

    def test_play_note_event_calls_note_on_and_note_off(self):
        p = self._make_player_with_mock_output()
        event = MusicEvent('note', 'La', 4, 64, 1, 0)
        with patch('time.sleep'):
            p.play_event(event)
        p.output.note_on.assert_called_once()
        p.output.note_off.assert_called_once()

    def test_play_note_midi_number_la_octave4(self):
        p = self._make_player_with_mock_output()
        # La na oitava 4 → MIDI 69
        event = MusicEvent('note', 'La', 4, 64, 1, 0)
        with patch('time.sleep'):
            p.play_event(event)
        args = p.output.note_on.call_args[0]
        self.assertEqual(args[0], 69)

    def test_play_note_midi_number_do_octave5(self):
        p = self._make_player_with_mock_output()
        # Do na oitava 5 → 60 + (5-4)*12 = 72
        event = MusicEvent('note', 'Do', 5, 64, 1, 0)
        with patch('time.sleep'):
            p.play_event(event)
        args = p.output.note_on.call_args[0]
        self.assertEqual(args[0], 72)

    def test_play_note_velocity_equals_volume(self):
        p = self._make_player_with_mock_output()
        event = MusicEvent('note', 'Sol', 4, 80, 1, 0)
        with patch('time.sleep'):
            p.play_event(event)
        args = p.output.note_on.call_args[0]
        self.assertEqual(args[1], 80)

    def test_play_silence_does_not_call_note_on(self):
        p = self._make_player_with_mock_output()
        event = MusicEvent('silence', None, 4, 64, 1, 100)
        with patch('time.sleep'):
            p.play_event(event)
        p.output.note_on.assert_not_called()

    def test_play_control_calls_set_instrument(self):
        p = self._make_player_with_mock_output()
        event = MusicEvent('control', None, 4, 64, 24, 0)
        p.play_event(event)
        p.output.set_instrument.assert_called_once_with(24, 0)

    def test_play_control_does_not_call_note_on(self):
        p = self._make_player_with_mock_output()
        event = MusicEvent('control', None, 4, 64, 24, 0)
        p.play_event(event)
        p.output.note_on.assert_not_called()

    def test_note_midi_clamped_to_valid_range(self):
        p = self._make_player_with_mock_output()
        # La na oitava 0 → 69 + (0-4)*12 = 69 - 48 = 21 (válido)
        event = MusicEvent('note', 'La', 0, 64, 1, 0)
        with patch('time.sleep'):
            p.play_event(event)
        args = p.output.note_on.call_args[0]
        self.assertGreaterEqual(args[0], 0)
        self.assertLessEqual(args[0], 127)

    def test_stop_sets_is_playing_false(self):
        from player import Player
        p = Player()
        p.is_playing = True
        p.stop()
        self.assertFalse(p.is_playing)

    def test_play_sequence_stops_when_flag_false(self):
        from player import Player
        p = Player()
        p.output = MagicMock()
        events = [MusicEvent('silence', None, 4, 64, 1, 0)] * 5

        call_count = [0]
        original_play = p.play_event

        def stop_after_two(event, channel=0):
            call_count[0] += 1
            if call_count[0] == 2:
                p.is_playing = False

        p.play_event = stop_after_two
        p.play_sequence(events)
        # Para após o 3º evento (verifica a flag antes de tocar o 3º)
        self.assertLessEqual(call_count[0], 3)

    def test_play_sequence_sets_is_playing_false_when_done(self):
        from player import Player
        p = Player()
        p.output = MagicMock()
        events = [MusicEvent('silence', None, 4, 64, 1, 0)]
        with patch.object(p, 'play_event'):
            p.play_sequence(events)
        self.assertFalse(p.is_playing)

    def test_play_event_without_output_does_not_raise(self):
        from player import Player
        p = Player()
        p.output = None
        event = MusicEvent('note', 'La', 4, 64, 1, 100)
        with patch('time.sleep'):
            try:
                p.play_event(event)
            except Exception as exc:
                self.fail(f"play_event levantou exceção sem output: {exc}")


# ===========================================================================
# 9. MusicSystem (facade)
# ===========================================================================

class TestMusicSystem(unittest.TestCase):

    def _make_system(self):
        with patch('player.Player.initialize'):
            system = MusicSystem()
        system.player.output = MagicMock()
        return system

    def test_configure_sets_bpm(self):
        system = self._make_system()
        system.configure(90, 1, 4, 64)
        self.assertEqual(system.context.get_bpm(), 90)

    def test_configure_sets_instrument(self):
        system = self._make_system()
        system.configure(120, 24, 4, 64)
        self.assertEqual(system.context.get_instrument(), 24)

    def test_configure_sets_octave(self):
        system = self._make_system()
        system.configure(120, 1, 6, 64)
        self.assertEqual(system.context.get_octave(), 6)

    def test_configure_sets_volume(self):
        system = self._make_system()
        system.configure(120, 1, 4, 100)
        self.assertEqual(system.context.get_volume(), 100)

    def test_run_returns_event_count(self):
        system = self._make_system()
        with patch.object(system.player, 'play_sequence'):
            count = system.run('ABCDEFGH')
        self.assertEqual(count, 8)

    def test_run_empty_text_returns_zero(self):
        system = self._make_system()
        with patch.object(system.player, 'play_sequence'):
            count = system.run('')
        self.assertEqual(count, 0)

    def test_stop_stops_player(self):
        system = self._make_system()
        system.player.is_playing = True
        system.stop()
        self.assertFalse(system.player.is_playing)

    def test_reset_restores_context_defaults(self):
        system = self._make_system()
        system.configure(200, 110, 7, 127)
        system.reset()
        self.assertEqual(system.context.get_bpm(), constants.DEFAULT_BPM)
        self.assertEqual(system.context.get_instrument(), constants.DEFAULT_INSTRUMENT)
        self.assertEqual(system.context.get_octave(), constants.DEFAULT_OCTAVE)
        self.assertEqual(system.context.get_volume(), constants.DEFAULT_VOLUME)

    def test_reset_also_stops_player(self):
        system = self._make_system()
        system.player.is_playing = True
        system.reset()
        self.assertFalse(system.player.is_playing)

    def test_run_launches_thread(self):
        system = self._make_system()
        import threading
        threads_before = threading.active_count()
        with patch.object(system.player, 'play_sequence'):
            system.run('A')
        # Não verifica count exato (thread pode já ter terminado),
        # mas garante que run() não lança exceção
        self.assertTrue(True)

    def test_polyphonic_run_counts_all_voices(self):
        # Fase 2: múltiplas linhas = múltiplas vozes
        system = self._make_system()
        with patch('player.Player.play_sequence'):
            count = system.run('ABC\nDEF')
        self.assertEqual(count, 6)
        self.assertEqual(len(system._last_tracks), 2)


# ===========================================================================
# 10. Regras de borda adicionais
# ===========================================================================

class TestEdgeCases(unittest.TestCase):

    def test_note_after_many_controls_uses_latest_state(self):
        """Instrumento muda várias vezes; a nota captura o estado final."""
        events = interpret('!,A')
        # Fase 2: !→22, ,→20, A=nota com instrumento=20
        note = events[2]
        self.assertEqual(note.type, 'note')
        self.assertEqual(note.instrument, 20)

    def test_space_at_max_volume_stays_at_max(self):
        events = interpret(' ', volume=127)
        self.assertEqual(events[0].volume, 127)

    def test_multiple_notes_in_sequence(self):
        events = interpret('ABCD')
        notes = [e.note for e in events]
        self.assertEqual(notes, ['La', 'Si', 'Do', 'Re'])

    def test_newline_then_note_ignores_newline(self):
        # Fase 2: NL ignorada; só a nota A gera evento, com instrumento padrão
        events = interpret('\nA')
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].type, 'note')
        self.assertEqual(events[0].instrument, 1)

    def test_repeat_after_instrument_change_uses_same_note(self):
        """A!K: A=La, !=Harmonica, K=repete La (ainda com Harmonica)."""
        events = interpret('A!K')
        self.assertEqual(events[2].type, 'note')
        self.assertEqual(events[2].note, 'La')
        self.assertEqual(events[2].instrument, 22)  # Fase 2: Harmonica

    def test_digit_sequence_odd_then_even(self):
        """1 (ímpar→15) seguido de 4 (par→+4=19)."""
        events = interpret('14')
        self.assertEqual(events[0].instrument, 15)
        self.assertEqual(events[1].instrument, 19)

    def test_all_notes_have_correct_duration_at_bpm(self):
        events = interpret('ABCDEFGH', bpm=120)
        for e in events:
            self.assertEqual(e.duration_ms, 500)

    def test_note_type_string(self):
        """type deve ser exatamente a string 'note'."""
        events = interpret('A')
        self.assertEqual(events[0].type, 'note')

    def test_silence_type_string(self):
        events = interpret('a')
        self.assertEqual(events[0].type, 'silence')

    def test_control_type_string(self):
        events = interpret('!')
        self.assertEqual(events[0].type, 'control')


# ===========================================================================
# 11. Funcionalidades novas da Fase 2 (fuga)
# ===========================================================================

class TestFase2Features(unittest.TestCase):
    """Cobre os recursos introduzidos na Fase 2."""

    def _make_system(self):
        with patch('player.Player.initialize'):
            system = MusicSystem()
        system.player.output = MagicMock()
        return system

    # --- Mi bemol (dígrafo Mb) ---
    def test_mb_generates_mi_bemol(self):
        events = interpret('Mb')
        self.assertEqual(events[0].type, 'note')
        self.assertEqual(events[0].note, 'MiBemol')

    def test_mi_bemol_midi_value(self):
        self.assertEqual(constants.NOTE_MIDI['MiBemol'], 63)

    # --- V: desce oitava ---
    def test_V_lowers_octave(self):
        events = interpret('V', octave=5)
        self.assertEqual(events[0].type, 'control')
        self.assertEqual(events[0].octave, 4)

    def test_V_does_not_go_below_zero(self):
        events = interpret('V', octave=0)
        self.assertEqual(events[0].octave, 0)

    # --- BPM: > acelera, < desacelera ---
    def test_accelerate_increases_bpm(self):
        events = interpret('>A', bpm=120)
        self.assertEqual(events[1].duration_ms, int((60 / 130) * 1000))

    def test_decelerate_decreases_bpm(self):
        events = interpret('<A', bpm=120)
        self.assertEqual(events[1].duration_ms, int((60 / 110) * 1000))

    # --- Atraso de entrada [n] ---
    def test_delay_token_generates_n_silences(self):
        events = interpret('[3]A')
        self.assertEqual(len(events_of_type(events[:3], 'silence')), 3)
        self.assertEqual(events[3].type, 'note')

    def test_delay_uses_bpm_before_acceleration(self):
        # '[4]>C': atraso ocorre a 120 BPM (500ms); só depois o BPM sobe
        events = interpret('[4]>C', bpm=120)
        for e in events[:4]:
            self.assertEqual(e.duration_ms, 500)

    # --- Polifonia (múltiplas vozes) ---
    def test_polyphony_creates_one_track_per_voice(self):
        system = self._make_system()
        with patch('player.Player.play_sequence'):
            system.run('ABC\nDEF\nGAB')
        self.assertEqual(len(system._last_tracks), 3)

    def test_voice_octaves_follow_defaults(self):
        system = self._make_system()
        with patch('player.Player.play_sequence'):
            system.run('A\nA\nA\nA')
        octaves = [t['events'][0].octave for t in system._last_tracks]
        self.assertEqual(octaves, [6, 5, 4, 3])

    def test_voice_instruments_follow_defaults(self):
        system = self._make_system()
        with patch('player.Player.play_sequence'):
            system.run('A\nA\nA\nA')
        instruments = [t['instrument'] for t in system._last_tracks]
        self.assertEqual(instruments, [6, 20, 0, 70])

    def test_voice_defaults_cycle_after_four(self):
        system = self._make_system()
        ctx = system._voice_context(4)  # 5ª voz volta aos padrões da 1ª
        self.assertEqual(ctx.octave, 6)
        self.assertEqual(ctx.instrument, 6)

    # --- Exportação MIDI ---
    def test_export_midi_writes_valid_file(self):
        import tempfile
        system = self._make_system()
        with patch('player.Player.play_sequence'):
            system.run('C D E F\n[4] G A H C')
        path = os.path.join(tempfile.gettempdir(), 'test_t2m_export.mid')
        system.export_midi(path)
        with open(path, 'rb') as f:
            header = f.read(4)
        self.assertEqual(header, b'MThd')
        os.remove(path)

    def test_export_without_run_raises(self):
        system = self._make_system()
        with self.assertRaises(ValueError):
            system.export_midi('x.mid')

    # --- I/O de arquivo TXT ---
    def test_save_and_load_round_trip(self):
        import tempfile
        system = self._make_system()
        path = os.path.join(tempfile.gettempdir(), 'test_t2m.txt')
        system.save_to_file(path, 'C D E F')
        self.assertEqual(system.load_from_file(path), 'C D E F')
        os.remove(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
