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
    {'octave': 6, 'volume': 100, 'instrument': 6},   # V0: Cravo (Harpsichord)
    {'octave': 5, 'volume': 80,  'instrument': 20},  # V1: Órgão (Church Organ)
    {'octave': 4, 'volume': 60,  'instrument': 0},   # V2: Piano
    {'octave': 3, 'volume': 40,  'instrument': 70},  # V3: Fagote (Bassoon)
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
    '!': 22,   # Harmonica (Fase 2 — antes era Bandoneon #24)
    ',': 20,   # Church Organ (Fase 2 — antes era Agogô #114)
    ';': 15,   # Tubular Bells
    # Fase 2: as vogais O, I, U deixaram de trocar instrumento e passaram a
    # seguir a regra de repetição/pausa (ver CharacterMapper.is_repeat_condition).
    # Fase 2: a nova linha (NL) é apenas separador de vozes e é ignorada
    # no Interpreter (não troca mais para Ondas do Mar).
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
