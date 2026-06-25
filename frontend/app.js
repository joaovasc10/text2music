/*
 * app.js - TextoMúsica
 * 
 * Script frontend que gerencia a interface e comunica com o servidor via HTTP.
 * Sem dependências externas, apenas JavaScript puro.
 */

// ============================================================================
// ESTADO DA APLICAÇÃO
// ============================================================================

let isPlaying = false;

// Elementos do DOM
const inputText = document.getElementById("input-text");
const bpmSlider = document.getElementById("bpm-slider");
const bpmDisplay = document.getElementById("bpm-display");
const volumeSlider = document.getElementById("volume-slider");
const volumeDisplay = document.getElementById("volume-display");
const instrumentSelect = document.getElementById("instrument-select");
const octaveMinus = document.getElementById("octave-minus");
const octavePlus = document.getElementById("octave-plus");
const octaveDisplay = document.getElementById("octave-display");
const playButton = document.getElementById("play-button");
const stopButton = document.getElementById("stop-button");
const exportButton = document.getElementById("export-button");
const clearLink = document.getElementById("clear-link");
const statusText = document.getElementById("status-text");
const fileInput = document.getElementById("file-input");
const loadButton = document.getElementById("load-button");
const saveButton = document.getElementById("save-button");

// Nome do último arquivo carregado (para "salvar substituindo o original")
let currentFileName = "musica.txt";

// Nomes dos 128 instrumentos do padrão General MIDI (0-127)
const GM_INSTRUMENTS = [
  "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano",
  "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
  "Celesta", "Glockenspiel", "Music Box", "Vibraphone",
  "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
  "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
  "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
  "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)",
  "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics",
  "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
  "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
  "Violin", "Viola", "Cello", "Contrabass",
  "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
  "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2",
  "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
  "Trumpet", "Trombone", "Tuba", "Muted Trumpet",
  "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
  "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax",
  "Oboe", "English Horn", "Bassoon", "Clarinet",
  "Piccolo", "Flute", "Recorder", "Pan Flute",
  "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
  "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)",
  "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
  "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
  "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
  "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
  "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
  "Sitar", "Banjo", "Shamisen", "Koto",
  "Kalimba", "Bag pipe", "Fiddle", "Shanai",
  "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock",
  "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
  "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet",
  "Telephone Ring", "Helicopter", "Applause", "Gunshot"
];

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Preencher o seletor com os 128 instrumentos GM
  populateInstruments();

  // Atualizar displays iniciais
  updateDisplays();

  // Adicionar event listeners
  setupEventListeners();
});

/**
 * Preenche o seletor de instrumentos com os 128 instrumentos General MIDI.
 * Atende à MUDANÇA 3 da Fase 2.
 */
function populateInstruments() {
  instrumentSelect.innerHTML = "";
  GM_INSTRUMENTS.forEach((name, i) => {
    const option = document.createElement("option");
    option.value = i;
    option.textContent = `${i} — ${name}`;
    instrumentSelect.appendChild(option);
  });
  instrumentSelect.value = 1; // Piano como padrão
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
  // Sliders
  bpmSlider.addEventListener("input", updateDisplays);
  volumeSlider.addEventListener("input", updateDisplays);

  // Octava
  octaveMinus.addEventListener("click", decreaseOctave);
  octavePlus.addEventListener("click", increaseOctave);

  // Botões de ação
  playButton.addEventListener("click", handlePlay);
  stopButton.addEventListener("click", handleStop);
  exportButton.addEventListener("click", handleExportMidi);
  clearLink.addEventListener("click", handleClear);

  // Arquivo: carregar (cliente) e salvar (servidor)
  loadButton.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleLoadFile);
  saveButton.addEventListener("click", handleSaveTxt);
}

// ============================================================================
// ATUALIZAÇÃO DE DISPLAYS
// ============================================================================

function updateDisplays() {
  // Atualizar display de BPM
  bpmDisplay.textContent = bpmSlider.value;

  // Atualizar display de Volume
  volumeDisplay.textContent = volumeSlider.value;
}

// ============================================================================
// CONTROLE DE OITAVA
// ============================================================================

function decreaseOctave() {
  let octave = parseInt(octaveDisplay.textContent);
  if (octave > 0) {
    octave--;
    octaveDisplay.textContent = octave;
  }
}

function increaseOctave() {
  let octave = parseInt(octaveDisplay.textContent);
  if (octave < 8) {
    octave++;
    octaveDisplay.textContent = octave;
  }
}

// ============================================================================
// AÇÕES PRINCIPAIS
// ============================================================================

/**
 * Toca a sequência musical.
 * 
 * Coleta os valores dos controles e envia uma requisição POST /play.
 * Durante a reprodução, desabilita o botão TOCAR.
 */
async function handlePlay() {
  // Validar entrada
  if (!inputText.value.trim()) {
    alert("Por favor, insira um texto para tocar!");
    return;
  }

  // Desabilitar botão e mostrar status
  playButton.disabled = true;
  isPlaying = true;
  statusText.textContent = "Tocando...";
  statusText.style.color = "#e74c3c"; // Vermelho

  try {
    // Preparar dados
    const payload = {
      text: inputText.value,
      bpm: parseInt(bpmSlider.value),
      instrument: parseInt(instrumentSelect.value),
      octave: parseInt(octaveDisplay.textContent),
      volume: parseInt(volumeSlider.value)
    };

    // Enviar requisição
    const response = await fetch("/play", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }

    const data = await response.json();

    // Mostrar quantidade de eventos gerados
    console.log(`${data.events} eventos musicais gerados.`);
    statusText.textContent = `Reproduzindo (${data.events} eventos)...`;

    // Aguardar fim da reprodução (aproximadamente)
    // Nota: Isso é uma estimativa. Idealmente, o servidor deveria
    // avisar quando terminar, mas por simplicidade, usamos timeout.
    await simulatePlaybackDuration(payload.bpm, data.events);

  } catch (error) {
    console.error("Erro ao tocar:", error);
    alert("Erro ao processar a sequência. Verifique o console.");
    statusText.textContent = "Erro";
    statusText.style.color = "#e74c3c";
  } finally {
    // Reabilitar botão
    playButton.disabled = false;
    isPlaying = false;
    statusText.textContent = "Pronto";
    statusText.style.color = "#27ae60"; // Verde
  }
}

/**
 * Para a reprodução.
 * 
 * Envia uma requisição POST /stop.
 */
async function handleStop() {
  try {
    const response = await fetch("/stop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }

    statusText.textContent = "Parado";
    statusText.style.color = "#f39c12"; // Laranja
    isPlaying = false;
    playButton.disabled = false;

  } catch (error) {
    console.error("Erro ao parar:", error);
  }
}

/**
 * Limpa o texto e reseta configurações aos valores padrão.
 * 
 * Envia uma requisição POST /reset e restaura os controles.
 */
async function handleClear(event) {
  event.preventDefault();

  try {
    // Enviar reset ao servidor
    const response = await fetch("/reset", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }

    restoreInterfaceDefaults();

  } catch (error) {
    console.error("Erro ao limpar:", error);
    alert("Erro ao resetar o sistema.");
  }
}

/**
 * Restaura todos os controles da interface aos valores padrão.
 * Extraído de handleClear() em resposta à revisão por pares.
 */
function restoreInterfaceDefaults() {
  inputText.value = "";
  bpmSlider.value = 120;
  volumeSlider.value = 64;
  instrumentSelect.value = 1;
  octaveDisplay.textContent = 4;
  updateDisplays();

  statusText.textContent = "Pronto";
  statusText.style.color = "#27ae60";
  isPlaying = false;
  playButton.disabled = false;
}

// ============================================================================
// ARQUIVO (TXT) E EXPORTAÇÃO MIDI
// ============================================================================

/**
 * Carrega um arquivo .txt escolhido pelo usuário para o campo de texto.
 * A leitura é feita no navegador (FileReader), sem depender do servidor.
 */
function handleLoadFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  currentFileName = file.name;

  const reader = new FileReader();
  reader.onload = (e) => {
    inputText.value = e.target.result;
    statusText.textContent = `Carregado: ${file.name}`;
  };
  reader.readAsText(file);
  fileInput.value = ""; // permite recarregar o mesmo arquivo
}

/**
 * Salva o texto atual em um arquivo .txt no servidor.
 * O nome padrão é o do arquivo carregado (substitui o original).
 */
async function handleSaveTxt() {
  const name = prompt("Salvar texto como:", currentFileName);
  if (!name) return;

  try {
    const response = await fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText.value, path: name })
    });
    if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
    const data = await response.json();
    currentFileName = name;
    statusText.textContent = `Salvo: ${data.path}`;
  } catch (error) {
    console.error("Erro ao salvar:", error);
    alert("Erro ao salvar o arquivo.");
  }
}

/**
 * Exporta a sequência atual como arquivo MIDI (.mid) no servidor.
 * Atende à MUDANÇA 2 da Fase 2.
 */
async function handleExportMidi() {
  if (!inputText.value.trim()) {
    alert("Insira um texto antes de exportar o MIDI!");
    return;
  }
  const name = prompt("Salvar MIDI como:", currentFileName.replace(/\.txt$/i, "") + ".mid");
  if (!name) return;

  try {
    const response = await fetch("/export_midi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputText.value,
        bpm: parseInt(bpmSlider.value),
        instrument: parseInt(instrumentSelect.value),
        octave: parseInt(octaveDisplay.textContent),
        volume: parseInt(volumeSlider.value),
        path: name
      })
    });
    if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
    const data = await response.json();
    statusText.textContent = `MIDI salvo: ${data.path}`;
  } catch (error) {
    console.error("Erro ao exportar MIDI:", error);
    alert("Erro ao exportar o arquivo MIDI.");
  }
}

// ============================================================================
// UTILITÁRIOS
// ============================================================================

/**
 * Simula a duração da reprodução.
 * 
 * Calcula aproximadamente quanto tempo a reprodução levará,
 * baseado no BPM e número de eventos.
 * 
 * Fórmula:
 *   duration_ms = (60 / bpm) * 1000 * num_events
 * 
 * Args:
 *   bpm (int): Batidas por minuto
 *   num_events (int): Número de eventos musicais
 * 
 * Returns:
 *   Promise: Resolve após a duração estimada
 */
function simulatePlaybackDuration(bpm, num_events) {
  const ms_per_note = (60 / bpm) * 1000;
  const total_ms = ms_per_note * num_events;

  // Adicionar um pequeno buffer
  const buffer_ms = 500;
  const wait_ms = Math.min(total_ms + buffer_ms, 60000); // Max 60 segundos

  return new Promise(resolve => {
    setTimeout(resolve, wait_ms);
  });
}

// ============================================================================
// DEBUG / LOGGING
// ============================================================================

// Log de inicialização
console.log("TextoMúsica - Interface carregada com sucesso!");
console.log("Pronto para processar texto em música.");
