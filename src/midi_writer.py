"""
Módulo midi_writer - TextoMúsica

Escreve um Standard MIDI File (formato 1) em Python puro, sem dependências.
Cada voz vira uma trilha (MTrk) própria, em seu canal MIDI, o que preserva
a polifonia da Fase 2 ao abrir o arquivo em qualquer player.

Atende à MUDANÇA 2 da Fase 2: além da saída sonora, salvar o MIDI gerado.
"""

from constants import NOTE_MIDI

# Tempo fixo de referência: 120 BPM (500000 microssegundos por semínima).
# As durações reais (duration_ms) já embutem o BPM de cada nota, então
# converter ms -> ticks neste tempo fixo preserva a sincronia entre vozes.
_REF_MS_PER_BEAT = 500


def _var_len(value):
    """Codifica um inteiro como variable-length quantity (VLQ) do padrão MIDI."""
    if value <= 0:
        return b'\x00'
    chunks = []
    while value > 0:
        chunks.append(value & 0x7F)
        value >>= 7
    chunks.reverse()
    out = bytearray()
    for i, chunk in enumerate(chunks):
        # Todos os bytes menos o último têm o bit de continuação (0x80) ligado
        out.append(chunk | 0x80 if i != len(chunks) - 1 else chunk)
    return bytes(out)


def _note_to_midi(note_name, octave):
    """Converte nome de nota + oitava em número MIDI (0-127)."""
    base = NOTE_MIDI.get(note_name, 60)
    return max(0, min(127, base + (octave - 4) * 12))


def _track_chunk(events, channel, instrument, division, include_tempo):
    """Monta um chunk MTrk a partir da lista de MusicEvents de uma voz."""
    ch = channel & 0x0F
    data = bytearray()

    if include_tempo:
        # Meta evento Set Tempo: FF 51 03 + 500000 us (=120 BPM)
        data += _var_len(0) + bytes([0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20])

    # Program change inicial (escolhe o instrumento da voz)
    data += _var_len(0) + bytes([0xC0 | ch, instrument & 0x7F])

    pending = 0  # ticks de silêncio acumulados antes do próximo evento
    for ev in events:
        ticks = round(ev.duration_ms * division / _REF_MS_PER_BEAT)

        if ev.type == 'note' and ev.note:
            note = _note_to_midi(ev.note, ev.octave)
            data += _var_len(pending) + bytes([0x90 | ch, note, ev.volume & 0x7F])
            data += _var_len(ticks) + bytes([0x80 | ch, note, 0])
            pending = 0
        elif ev.type == 'silence':
            pending += ticks
        elif ev.type == 'control':
            data += _var_len(pending) + bytes([0xC0 | ch, ev.instrument & 0x7F])
            pending = 0

    # Meta evento End of Track: FF 2F 00
    data += _var_len(pending) + bytes([0xFF, 0x2F, 0x00])

    return b'MTrk' + len(data).to_bytes(4, 'big') + bytes(data)


def write_midi(path, tracks, division=480):
    """
    Escreve um arquivo MIDI (formato 1) no caminho indicado.

    Args:
        path (str): caminho de saída (ex: 'musica.mid')
        tracks (list[dict]): cada item tem as chaves
            'channel' (int 0-15), 'instrument' (int 0-127), 'events' (list[MusicEvent])
        division (int): ticks por semínima (resolução)
    """
    ntracks = max(1, len(tracks))
    header = (
        b'MThd'
        + (6).to_bytes(4, 'big')
        + (1).to_bytes(2, 'big')          # formato 1
        + ntracks.to_bytes(2, 'big')      # número de trilhas
        + division.to_bytes(2, 'big')     # divisão (ticks por semínima)
    )

    body = bytearray()
    for i, track in enumerate(tracks):
        body += _track_chunk(
            track['events'],
            track['channel'],
            track['instrument'],
            division,
            include_tempo=(i == 0),
        )

    with open(path, 'wb') as f:
        f.write(header + bytes(body))
