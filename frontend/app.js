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
const clearLink = document.getElementById("clear-link");
const statusText = document.getElementById("status-text");

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Atualizar displays iniciais
  updateDisplays();

  // Adicionar event listeners
  setupEventListeners();
});

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
  clearLink.addEventListener("click", handleClear);
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

    // Restaurar interface aos valores padrão
    inputText.value = "";
    bpmSlider.value = 120;
    volumeSlider.value = 64;
    instrumentSelect.value = 1;
    octaveDisplay.textContent = 4;

    // Atualizar displays
    updateDisplays();

    // Restaurar status
    statusText.textContent = "Pronto";
    statusText.style.color = "#27ae60";
    isPlaying = false;
    playButton.disabled = false;

  } catch (error) {
    console.error("Erro ao limpar:", error);
    alert("Erro ao resetar o sistema.");
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
