"""
Classe MusicSystem - TextoMúsica

Implementa o padrão Facade, unindo todos os módulos.

Fase 2: suporte a múltiplas vozes (polifonia). Cada linha não-vazia do texto
é interpretada como uma voz independente com oitava, volume e instrumento
barrocos próprios, tocada em thread separada em canal MIDI diferente.
"""

import threading

from constants import VOICE_DEFAULTS
from context import Context
from interpreter import Interpreter
from player import Player
from midi_writer import write_midi


class MusicSystem:
    """
    Fachada do sistema.

    Expõe interface simples para o servidor HTTP:
        configure() → parâmetros iniciais (BPM, instrumento, oitava, volume)
        run()       → processa texto e inicia reprodução (mono ou polifônica)
        stop()      → para todas as vozes ativas
        reset()     → restaura estado padrão
    """

    def __init__(self):
        self.player = Player()
        self.player.initialize()
        self.context = Context()
        self._active_players = []
        # Trilhas da última execução, usadas para exportar o MIDI gerado
        self._last_tracks = []

    def configure(self, bpm, instrument, octave, volume):
        """
        Define parâmetros iniciais antes de run().

        Em modo single-voice esses valores são usados diretamente.
        Em modo multi-voice apenas o BPM é propagado às vozes; oitava,
        instrumento e volume vêm dos VOICE_DEFAULTS.

        Args:
            bpm (int): Batidas por minuto
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

        Se houver múltiplas linhas não-vazias, cada linha é uma voz
        tocada em paralelo (Fuga — Fase 2). Caso contrário, reprodução
        original de voz única.

        Args:
            text (str): Texto a processar

        Returns:
            int: Total de eventos gerados
        """
        try:
            voices = [line for line in text.split('\n') if line.strip()]

            if len(voices) <= 1:
                return self._run_single(text)
            else:
                return self._run_polyphonic(voices)

        except Exception as e:
            print(f"ERRO em MusicSystem.run(): {e}")
            return 0

    def _run_single(self, text):
        """Modo voz única — comportamento original da Fase 1."""
        interp = Interpreter()
        interp.context.set_bpm(self.context.bpm)
        interp.context.set_instrument(self.context.instrument)
        interp.context.set_octave(self.context.octave)
        interp.context.set_volume(self.context.volume)

        events = interp.interpret_text(text)
        self._active_players = [self.player]
        instrument = events[0].instrument if events else self.context.instrument
        self._last_tracks = [{'channel': 0, 'instrument': instrument, 'events': events}]

        t = threading.Thread(
            target=self.player.play_sequence,
            args=(events, 0),
            daemon=True
        )
        t.start()
        return len(events)

    def _run_polyphonic(self, voices):
        """Modo polifônico — uma thread por voz, canal MIDI distinto."""
        self._active_players = []
        self._last_tracks = []
        total = 0

        for i, voice_text in enumerate(voices):
            channel = i % 16
            if channel == 9:
                channel = 10  # Canal 9 é reservado para percussão no GM

            ctx = self._voice_context(i)
            interp = Interpreter()
            interp.context = ctx

            events = interp.interpret_text(voice_text)
            total += len(events)

            instrument = events[0].instrument if events else ctx.instrument
            self._last_tracks.append(
                {'channel': channel, 'instrument': instrument, 'events': events}
            )

            # Cada voz tem seu próprio Player mas compartilha o dispositivo MIDI
            vplayer = Player()
            vplayer.output = self.player.output
            self._active_players.append(vplayer)

            t = threading.Thread(
                target=vplayer.play_sequence,
                args=(events, channel),
                daemon=True
            )
            t.start()

        return total

    def _voice_context(self, index):
        """Cria um Context com os padrões barrocos para a voz de índice index."""
        ctx = Context()
        # Fase 2: a partir da 5ª voz o ciclo se repete (voz 4 = voz 0, etc.)
        defaults = VOICE_DEFAULTS[index % len(VOICE_DEFAULTS)]
        ctx.set_bpm(self.context.bpm)
        ctx.set_octave(defaults['octave'])
        ctx.set_volume(defaults['volume'])
        ctx.set_instrument(defaults['instrument'])
        return ctx

    def stop(self):
        """Para todas as vozes ativas."""
        for p in self._active_players:
            p.stop()
        self.player.stop()

    def reset(self):
        """Reseta o sistema aos valores padrão."""
        self.stop()
        self.context.reset()

    def load_from_file(self, path):
        """
        Lê um arquivo .txt e retorna o conteúdo.

        Args:
            path (str): Caminho do arquivo

        Returns:
            str: Conteúdo do arquivo
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_to_file(self, path, text):
        """
        Salva o texto em um arquivo .txt.

        Args:
            path (str): Caminho de destino
            text (str): Conteúdo a salvar
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    def export_midi(self, path):
        """
        Exporta a última sequência gerada como arquivo MIDI (.mid).

        Cada voz é gravada em uma trilha própria, preservando a polifonia.

        Args:
            path (str): Caminho de destino (ex: 'musica.mid')

        Returns:
            str: O caminho do arquivo gravado
        """
        if not self._last_tracks:
            raise ValueError("Nenhuma sequência gerada ainda. Toque algo antes de exportar.")
        write_midi(path, self._last_tracks)
        return path
