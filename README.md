# Text2Music - Gerador de Sequências Musicais a partir de Texto

Um sistema Python com interface web que transforma texto em sequências musicais reproduzíveis via MIDI.

## 📋 Descrição

TextoMúsica é um gerador de sequências musicais que processa texto e o transforma em notas musicais de acordo com regras de mapeamento pré-definidas. O sistema foi desenvolvido seguindo princípios de engenharia de software como:

- Separação de responsabilidades (Single Responsibility Principle)
- Baixo acoplamento e alta coesão
- Princípios SOLID
- Modularidade e extensibilidade

## 📂 Estrutura do Projeto

```
text2music/
├── src/
│   ├── constants.py           # Constantes e mapeamentos globais
│   ├── music_event.py         # Classe MusicEvent
│   ├── context.py             # Classe Context (estado da execução)
│   ├── character_mapper.py    # Mapeador de caracteres para ações musicais
│   ├── text_reader.py         # Leitor de texto
│   ├── interpreter.py         # Orquestrador central
│   ├── player.py              # Reprodutor de áudio (pygame.midi)
│   ├── music_system.py        # Fachada do sistema
│   └── server.py              # Servidor HTTP
├── frontend/
│   ├── index.html             # Interface principal
│   ├── style.css              # Estilos
│   └── app.js                 # Lógica da interface
└── requirements.txt           # Dependências Python
```

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)

### 2. Instalação de Dependências

No diretório raiz do projeto, execute:

```bash
pip install -r requirements.txt
```

Isso instalará o pygame, necessário para reprodução de áudio via MIDI.

### 3. Iniciar o Servidor

```bash
python src/server.py
```

O servidor iniciará em `http://127.0.0.1:8000`

### 4. Acessar a Interface

Abra seu navegador web e acesse:

```
http://localhost:8000
```

## 🎵 Regras de Mapeamento (Fase 1)

### Notas Musicais

| Caractere | Ação |
|-----------|------|
| A (maiúscula) | Toca nota Lá |
| B (maiúscula) | Toca nota Si |
| C (maiúscula) | Toca nota Dó |
| D (maiúscula) | Toca nota Ré |
| E (maiúscula) | Toca nota Mi |
| F (maiúscula) | Toca nota Fá |
| G (maiúscula) | Toca nota Sol |
| H (maiúscula) | Toca nota Si Bemol |

### Silêncio/Pausa

| Caractere | Ação |
|-----------|------|
| a-h (minúsculas) | Silêncio/Pausa |

### Controles

| Caractere | Ação |
|-----------|------|
| Espaço | Dobra o volume (máximo: 127) |
| ? ou . | Sobe uma oitava (máximo: 8, volta ao padrão se exceder) |
| ! | Muda para instrumento Bandoneon (MIDI #24) |
| O, o, I, i, U, u | Muda para instrumento Gaita de Foles (MIDI #110) |
| ; ou dígito ímpar | Muda para instrumento Tubular Bells (MIDI #15) |
| , (vírgula) | Muda para instrumento Agogô (MIDI #114) |
| Newline (\n) | Muda para instrumento Ondas do Mar (MIDI #123) |
| Dígito par | Soma o dígito ao instrumento atual |

### Repetição

| Condição | Ação |
|----------|------|
| Consoante não-nota ou caractere não-mapeado | Se há nota anterior, repete; senão, silêncio |

## 🎮 Interface

### Coluna Esquerda

- **Contexto de Entrada**: Área de texto para inserir o texto a processar
- **Reprodução**: 
  - Slider de BPM (60-200, padrão: 120)
  - Slider de Volume (0-127, padrão: 64)

### Coluna Direita

- **Configurações de Instrumento**:
  - Seletor de instrumento principal
  - Controle +/- para oitava base (0-8, padrão: 4)

### Rodapé

- **TOCAR FAIXA**: Inicia a reprodução (verde)
- **PARAR**: Para a reprodução em andamento (cinza)
- **LIMPAR**: Limpa o texto e reseta configurações (azul)

## 💻 Arquitetura de Classes

### Constants
Módulo de constantes globais: valores padrão, mapeamentos de notas, instrumentos.

### MusicEvent
Representa um evento musical atômico (nota, silêncio ou controle).
Atributos: `type`, `note`, `octave`, `volume`, `instrument`, `duration_ms`.

### Context
Mantém o estado dinâmico da execução: volume, octava, BPM, instrumento, última nota.

### CharacterMapper
Classifica caracteres e determina ações musicais, consultando Constants.
Métodos: `is_note()`, `is_silence()`, `should_double_volume()`, etc.

### TextReader
Carrega e fornece caracteres do texto um de cada vez (gerador).

### Interpreter
Orquestrador central que converte texto em lista de MusicEvents.
Usa TextReader, CharacterMapper e Context.

### Player
Reproduz MusicEvents via pygame.midi em thread separada.
Métodos: `initialize()`, `play_event()`, `play_sequence()`, `stop()`.

### MusicSystem (Facade)
Fachada que une todos os módulos. Interface com o servidor HTTP.
Métodos: `configure()`, `run()`, `stop()`, `reset()`.

### Server
Servidor HTTP simples com rotas:
- `GET /` → Serve index.html
- `POST /play` → Processa e toca sequência
- `POST /stop` → Para reprodução
- `POST /reset` → Reseta configurações

## 🧪 Testes Manuais

### Exemplo 1: Escala

Texto: `ABCDEFGH`

Resultado: Escala de Lá a Si Bemol.

### Exemplo 2: Com Pausa

Texto: `A b C`

Resultado: Lá, pausa, Dó.

### Exemplo 3: Com Mudança de Instrumento

Texto: `A!A`

Resultado: Lá com piano, depois Lá com bandoneon.

### Exemplo 4: Com Volume e Oitava

Texto: `A AAA?AAA`

Resultado: Lá (1x), depois 3 Lá (volume dobrado), depois sobe oitava, depois 3 Lá em oitava mais alta.

## 📝 Notas Importantes

- O sistema desabilita áudio se pygame não estiver instalado (com aviso)
- A reprodução ocorre em thread separada para não bloquear a interface web
- Todos os valores vêm de `constants.py` (fácil extensão)
- Código bem comentado para fins didáticos

## 🔄 Fluxo Completo

1. Usuário insere texto e clica "TOCAR FAIXA"
2. Servidor recebe requisição POST /play com parâmetros
3. MusicSystem configura o Context com parâmetros
4. Interpreter processa o texto caractere por caractere
5. Para cada caractere, CharacterMapper classifica e Context atualiza
6. MusicEvents são criados (snapshots do Context)
7. Player reproduz os eventos em thread separada
8. Interface mostra status em tempo real

## 🛠️ Modificações Futuras (Fase 2+)

Este projeto foi projetado para ser facilmente extensível:

- Adicione novos mapeamentos em `constants.py`
- Estenda `CharacterMapper` com novos métodos
- Altere `Player` para suportar outras bibliotecas de áudio
- Expanda `MusicEvent` com novos campos

## 📚 Referências

- [General MIDI Specification](https://en.wikipedia.org/wiki/General_MIDI)
- [Notação Musical](https://en.wikipedia.org/wiki/Music_notation)
- [pygame.midi Documentation](https://www.pygame.org/docs/ref/midi.html)

## 👥 Grupo

- Gabriel Oliveira Souto
- Alisson Oliveira de Siqueira
- João Maciel Santos Vasconcelos
- Miguel Gil de Souza Franskowiak

**Disciplina**: INF01120 - Desenvolvimento de Software

**Professor**: Marcelo Soares Pimenta

---

**Desenvolvido com propósito educacional para aplicar conceitos de engenharia de software.**
