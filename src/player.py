"""
Classe Player - TextoMúsica

Responsabilidade única: receber MusicEvents e reproduzi-los via pygame.midi.

Se a biblioteca de áudio mudar, somente esta classe é afetada.
A reprodução ocorre em thread separada para não bloquear a interface.
"""

import time

try:
    import pygame.midi
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("AVISO: pygame não instalado. Áudio desabilitado.")

from constants import NOTE_MIDI


class Player:
    """
    Encapsula a reprodução de áudio via pygame.midi.
    
    Atributos:
        is_playing (bool): Flag controlada pela interface para parar a reprodução
        output (pygame.midi.Output | None): Saída MIDI
        current_channel (int): Canal MIDI atual
    """
    
    def __init__(self):
        """Inicializa o Player."""
        self.is_playing = False
        self.output = None
        self.current_channel = 0
    
    def initialize(self):
        """
        Inicializa pygame.midi e abre o dispositivo de saída.

        Usa o dispositivo padrão do sistema. Se não houver padrão,
        percorre todos os dispositivos e abre o primeiro disponível.
        """
        if not PYGAME_AVAILABLE:
            print("AVISO: pygame.midi não disponível. Reprodução de áudio desabilitada.")
            return

        try:
            pygame.midi.init()

            device_id = pygame.midi.get_default_output_id()

            # Se não houver padrão, procura qualquer saída disponível
            if device_id == -1:
                for i in range(pygame.midi.get_count()):
                    info = pygame.midi.get_device_info(i)
                    # info = (interface, name, is_input, is_output, opened)
                    if info[3]:  # is_output
                        device_id = i
                        break

            if device_id == -1:
                print("AVISO: Nenhum dispositivo MIDI encontrado. Reprodução desabilitada.")
                return

            self.output = pygame.midi.Output(device_id)

        except Exception as e:
            print(f"ERRO ao inicializar pygame.midi: {e}")
            self.output = None
    
    def play_event(self, event, channel=0):
        """
        Reproduz um MusicEvent no canal MIDI especificado.

        Args:
            event (MusicEvent): Evento a reproduzir
            channel (int): Canal MIDI (0-15)
        """
        if not self.output:
            if event.type in ('note', 'silence'):
                time.sleep(event.duration_ms / 1000.0)
            return

        try:
            if event.type == 'note' and event.note:
                midi_base = NOTE_MIDI.get(event.note, 60)
                # Fórmula: note_midi = base + (octave - 4) * 12
                midi_note = midi_base + (event.octave - 4) * 12
                midi_note = max(0, min(127, midi_note))

                self.output.note_on(midi_note, event.volume, channel)
                time.sleep(event.duration_ms / 1000.0)
                self.output.note_off(midi_note, 0, channel)

            elif event.type == 'silence':
                time.sleep(event.duration_ms / 1000.0)

            elif event.type == 'control':
                self.output.set_instrument(event.instrument, channel)

        except Exception as e:
            print(f"ERRO ao reproduzir evento: {e}")

    def play_sequence(self, events, channel=0):
        """
        Loop de reprodução em thread separada.

        Args:
            events (list[MusicEvent]): Lista de eventos a reproduzir
            channel (int): Canal MIDI desta voz (0-15)
        """
        self.is_playing = True

        if events and self.output:
            self.output.set_instrument(events[0].instrument, channel)

        for event in events:
            if not self.is_playing:
                break
            self.play_event(event, channel)

        self.is_playing = False
    
    def stop(self):
        """
        Para a reprodução.
        
        Seta is_playing = False, interrompendo play_sequence
        na próxima iteração.
        """
        self.is_playing = False
