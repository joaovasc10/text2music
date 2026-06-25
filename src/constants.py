"""
Módulo de Constantes - TextoMúsica

Centraliza todos os valores padrão e tabelas de mapeamento.
Não é uma classe instanciável — é um módulo de constantes globais.
Separar os dados da lógica garante que qualquer mudança de regra
seja feita em um único lugar sem tocar nas outras classes.
"""

# ============================================================================
# Valores padrão para o sistema
# ============================================================================
DEFAULT_VOLUME = 64  # Escala MIDI 0-127
DEFAULT_OCTAVE = 4
DEFAULT_BPM = 120
DEFAULT_INSTRUMENT = 1  # Piano (General MIDI)
MAX_VOLUME = 127
MAX_OCTAVE = 8
MIN_BPM = 40
MAX_BPM = 240
BPM_STEP = 10  # Incremento/decremento por '>' e '<'

# ============================================================================
# Configurações padrão por voz (Fase 2 — Fuga)
# Índice = número da linha (0 = primeira voz)
# ============================================================================
VOICE_DEFAULTS = [
    {'octave': 6, 'volume': 100, 'instrument': 6},   # V0: Harpsichord
    {'octave': 5, 'volume': 80,  'instrument': 19},  # V1: Church Organ
    {'octave': 4, 'volume': 60,  'instrument': 73},  # V2: Flute
    {'octave': 3, 'volume': 40,  'instrument': 48},  # V3: Strings
]

# ============================================================================
# Mapeamento de letras maiúsculas para nomes de notas musicais
# ============================================================================
NOTE_MAP = {
    'A': 'La',
    'B': 'Si',
    'C': 'Do',
    'D': 'Re',
    'E': 'Mi',
    'F': 'Fa',
    'G': 'Sol',
    'H': 'SiBemol'
}

# ============================================================================
# Letras minúsculas que representam silêncio (pausa)
# ============================================================================
SILENCE_CHARS = set('abcdefgh')

# ============================================================================
# Mapeamento de caracteres especiais para números MIDI de instrumentos
# Referência: General MIDI Instrument Numbers
# ============================================================================
INSTRUMENT_MAP = {
    '!': 24,      # Bandoneon
    'O': 110,     # Gaita de Foles (vowel)
    'o': 110,     # Gaita de Foles (lowercase)
    'I': 110,     # Gaita de Foles (vowel)
    'i': 110,     # Gaita de Foles (lowercase)
    'U': 110,     # Gaita de Foles (vowel)
    'u': 110,     # Gaita de Foles (lowercase)
    ',': 114,     # Agogô
    ';': 15,      # Tubular Bells
    'NL': 123,    # Ondas do Mar (newline)
}

# ============================================================================
# Mapeamento de nomes de notas para números MIDI (oitava 4 como base)
# Fórmula: MIDI note = base + (octave - 4) * 12
# ============================================================================
NOTE_MIDI = {
    'Do': 60,
    'Re': 62,
    'Mi': 64,
    'Fa': 65,
    'Sol': 67,
    'La': 69,
    'Si': 71,
    'SiBemol': 70,
    'MiBemol': 63,  # Eb4 — adicionado na Fase 2 via token 'Mb'
}

# ============================================================================
# Lista de instrumentos principais para exibir na interface
# ============================================================================
MAIN_INSTRUMENTS = [
    (1, "01 Piano"),
    (24, "24 Bandoneon"),
    (41, "41 Violino"),
    (110, "110 Gaita de Foles"),
    (114, "114 Agogô"),
    (123, "123 Ondas do Mar"),
]
