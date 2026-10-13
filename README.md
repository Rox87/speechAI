# 🎙️ SpeechAI

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.15-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture: Modular](https://img.shields.io/badge/Architecture-Modular%20%26%20Extensible-green.svg)](#arquitetura-do-projeto)
[![Tests: Passing](https://img.shields.io/badge/Tests-31%2F31%20passing-brightgreen.svg)](#testes-automatizados)
[![Web Studio: Included](https://img.shields.io/badge/Web%20UI-Studio%20Included-indigo.svg)](#-speechai-web-studio-interface-web)

**SpeechAI** é um framework em Python modular, moderno e robusto para **processamento de áudio**, **Speech-to-Text (STT)**, **Text-to-Speech (TTS)**, **Web Studio interativo** e **Assistentes de Voz conversacionais em tempo real**.

O projeto suporta múltiplos motores de voz (Vozes Neurais do Navegador, OpenAI TTS e Google gTTS), transcrição de fala com OpenAI/OpenRouter Whisper ou modelos locais (`faster-whisper`), reprodução de áudio à prova de vazamentos (Pygame e Windows native `winsound`), além de uma **Interface Web Studio moderna** e CLI unificada com auto-diagnóstico.

---

## 📑 Sumário

- [Visão Geral e Destaques](#-visão-geral-e-destaques)
- [SpeechAI Web Studio (Interface Web)](#-speechai-web-studio-interface-web)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Estrutura de Diretórios](#-estrutura-de-diretórios)
- [Pré-requisitos e Instalação](#-pré-requisitos-e-instalação)
- [Configuração de Variáveis de Ambiente (.env)](#-configuração-de-variáveis-de-ambiente-env)
- [Guia da CLI (Linha de Comando)](#-guia-da-cli-linha-de-comando)
- [Uso Programático (Python API)](#-uso-programático-python-api)
- [Comparativo de Motores TTS](#-comparativo-de-motores-tts)
- [Testes Automatizados](#-testes-automatizados)
- [Diagnósticos e Resolução de Problemas](#-diagnósticos-e-resolução-de-problemas)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🚀 Visão Geral e Destaques

- **🌐 SpeechAI Web Studio UI (`python src/main.py ui`)**: Interface web moderna e reativa no navegador (Dark Mode & Glassmorphism) com orb animado de voz, estúdio de TTS, estúdio de transcrição STT, auto-diagnóstico em tempo real e editor visual de `.env`.
- **🎤 Assistente de Voz Conversacional Inteligente**: Loop de diálogo com captura de microfone, transcrição, raciocínio contextual via ChatGPT (`gpt-4o-mini`, `gpt-4o`, etc.) e resposta falada.
- **✨ Vozes Neurais Humanas & Múltiplos Motores TTS**:
  - **Vozes Neurais do Navegador (Web Speech API)**: entonação humana ultra-natural (Microsoft Francisca e Antonio no Windows/Edge/Chrome), gratuita e com latência zero.
  - **OpenAI TTS** (`tts-1`, `tts-1-hd`): vozes de estúdio de alta fidelidade (`nova`, `alloy`, `echo`, `fable`, `onyx`, `shimmer`).
  - **Google TTS (`gTTS`)**: gratuito, sem necessidade de chave de API, suporte nativo a múltiplos idiomas e sotaques.
  - **Síntese Direta em Memória (`io.BytesIO`)**: sem latência de gravação de arquivos temporários em disco.
- **🎧 Speech-to-Text (STT) Híbrido**:
  - **OpenAI / OpenRouter Whisper API (`whisper-1`, `whisper-large-v3-turbo`)**: ultra rápido e preciso via nuvem.
  - **Local Whisper (`faster-whisper`)**: execução 100% offline em CPU/GPU (carregamento sob demanda lazy-loaded).
- **🔊 Player de Áudio Multi-Backend Sem Travamentos**:
  - Gerenciamento inteligente de handles no Windows (evita erros de arquivo travado `PermissionError`).
  - Fallback automático entre Pygame mixer, Windows `winsound` nativo e `playsound`.
- **🛠️ CLI Profissional Unificada**:
  - Subcomandos: `ui`, `assistant`, `speak`, `transcribe`, `play`, `check`, `clean`.
  - Ferramenta embutida de verificação de ambiente (`speechai check`).
- **🛡️ Tratamento Defensivo & Zero Crashes**:
  - Nenhum script executa código de rede ou microfone acidentalmente no import.
  - Compatível com Python 3.8 até Python 3.15+.

---

## 🌐 SpeechAI Web Studio (Interface Web)

O SpeechAI inclui um **Web Studio completo** que roda diretamente no seu navegador, sem necessidade de instalar Node.js ou frameworks pesados. Ele foi construído com servidor HTTP nativo em Python e um design premium em **Dark Mode Glassmorphism**.

### Como Iniciar

Basta executar o comando `ui`:

```bash
python src/main.py ui
```

O servidor será iniciado em **http://127.0.0.1:7860** e abrirá seu navegador padrão automaticamente.

### Parâmetros Avançados

```bash
# Executar em porta customizada:
python src/main.py ui --port 8080

# Permitir acesso de outros computadores/celulares na rede local:
python src/main.py ui --host 0.0.0.0 --port 7860

# Iniciar sem abrir o navegador automaticamente (ideal para servidores remotos/VPS):
python src/main.py ui --no-browser
```

### 🌟 Módulos Disponíveis na Interface

| Módulo | Descrição e Recursos |
| :--- | :--- |
| **🎙️ Assistente de Voz** | Orb central reativo com ondas sonoras que mudam de cor conforme o estado (*Ouvindo*, *Processando*, *Falando*). Permite alternar entre **Voz Neural Natural do Navegador** e **gTTS**, além de gravação pelo microfone local ou pelo microfone do navegador. |
| **🔊 TTS Studio** | Laboratório de Text-to-Speech: digite qualquer texto, escolha o motor (Vozes Neurais do Navegador, Google gTTS ou OpenAI/Kokoro), visualize as frequências sonoras e faça o **download imediato do MP3 gerado**. |
| **📝 STT Studio** | Laboratório de Transcrição: envie arquivos de áudio existentes (WAV/MP3/M4A) com *drag-and-drop* ou grave 5 segundos direto pelo navegador, obtendo a transcrição com medição de **latência em segundos** e botão de copiar. |
| **⚙️ Configurações & Status** | Edite variáveis do `.env` diretamente pela interface (Base URL, Modelos de Chat, Whisper e TTS), e visualize diagnósticos em tempo real da chave de API, microfones conectados (`sounddevice`) e player de áudio. |

---

## 🏗 Arquitetura do Projeto

```mermaid
flowchart TD
    User([Usuário]) -->|Linha de Comando ou Navegador| EntryPoints
    
    subgraph EntryPoints[Pontos de Entrada]
        CLI[CLI: src/main.py]
        WebUI[SpeechAI Web Studio: src/ui/]
    end
    
    subgraph Core[SpeechAI Core]
        Config[AppConfig: src/core/config.py]
        Logger[Logger ANSI: src/core/logger.py]
        Client[OpenAI / OpenRouter Client: src/core/client.py]
        Cleaner[Temp Cleaner: src/core/utils/]
        
        VA[VoiceAssistant: src/core/voice_assistant.py]
        
        subgraph AudioSub[Módulo de Áudio]
            Recorder[AudioRecorder: sounddevice]
            Transcriber[AudioTranscriber: Whisper API / Local]
            Player[AudioPlayer: Pygame / winsound]
        end
        
        subgraph TTSSub[Módulo Text-to-Speech]
            Synthesizer[Synthesizer: OpenAI / gTTS]
            ChatHandler[ChatGPTTTSHandler]
        end
    end
    
    CLI --> VA
    WebUI -->|REST APIs: /api/voice-turn, /api/chat, /api/synthesize| Core
    VA --> Recorder
    Recorder -->|BytesIO WAV| Transcriber
    Transcriber -->|Texto Transcrito| VA
    VA -->|Histórico + Mensagem| Client
    Client -->|Resposta LLM| VA
    VA --> Synthesizer
    Synthesizer -->|BytesIO / MP3| Player
    Player -->|Áudio Local| User
    WebUI -->|HTML5 Audio / Web Speech API| User
```

---

## 📁 Estrutura de Diretórios

```
speechAI/
├── .env.example                     # Modelo documentado de variáveis de ambiente
├── .gitignore                       # Ignora venv, caches, logs e arquivos de áudio temporários
├── pyproject.toml                   # Padrão moderno PEP 517/621 de empacotamento
├── requirements.txt                 # Dependências modernas e validadas
├── README.md                        # Documentação completa do projeto
├── temp/                            # Diretório temporário gerenciado para gravações/áudios
├── src/
│   ├── __init__.py                  # Torna src um pacote Python importável
│   ├── main.py                      # Ponto de entrada CLI completo
│   ├── core/
│   │   ├── __init__.py              # Exporta os componentes principais
│   │   ├── config.py                # Gerenciador de configurações centralizado (.env)
│   │   ├── logger.py                # Logging formatado com cores ANSI
│   │   ├── client.py                # Provedor do cliente OpenAI com cache
│   │   ├── voice_assistant.py       # Classe VoiceAssistant e loop de conversação
│   │   ├── audio/
│   │   │   ├── __init__.py          # Facade do módulo de áudio
│   │   │   ├── audio_transcriber.py # Transcrição com Whisper (API e local lazy-load)
│   │   │   ├── player.py            # AudioPlayer multi-backend (Pygame/winsound)
│   │   │   └── recorder.py          # Gravação de microfone para BytesIO WAV
│   │   ├── tts/
│   │   │   ├── __init__.py          # Facade do módulo TTS
│   │   │   ├── synthesizer.py       # Síntese via OpenAI TTS e Google gTTS
│   │   │   ├── chatgpt_tts_handler.py # Pipeline de conversação e fala
│   │   │   ├── text_to_speech.py    # Módulo de compatibilidade retroativa
│   │   │   └── tts_core.py          # Módulo de compatibilidade retroativa
│   │   └── utils/
│   │       ├── __init__.py          # Exporta utilitários
│   │       ├── temp_file_cleaner.py # Limpeza segura de arquivos com validações
│   │       └── clean_folder.py      # Alias de compatibilidade retroativa
│   ├── ui/                          # Interface gráfica SpeechAI Studio (Web UI)
│   │   ├── __init__.py              # Ponto de inicialização do módulo Web
│   │   ├── server.py                # Servidor HTTP REST API nativo
│   │   └── static/                  # Assets da interface web (SPA)
│   │       ├── index.html           # Layout em abas (Assistant, TTS, STT, Settings)
│   │       ├── style.css            # Design System (Dark Mode & Glassmorphism)
│   │       └── app.js               # Lógica reativa, Web Audio e Web Speech API
│   ├── audio_playback/
│   │   ├── __init__.py
│   │   ├── play_audio_playsound.py  # Script CLI seguro para playsound
│   │   └── play_audio_pygame.py     # Script CLI seguro para pygame
│   ├── realtime_processing/
│   │   ├── __init__.py
│   │   ├── realtime_gtts.py         # Fala em tempo real com gTTS e benchmark
│   │   ├── realtime_openai.py       # Fala em tempo real com OpenAI TTS e benchmark
│   │   └── speech_to_text_realtime.py # Transcrição contínua em streaming
│   └── text_to_speech/
│       ├── __init__.py
│       ├── text_to_speech_gtts.py   # Utilitário para salvar áudios com gTTS
│       ├── text_to_speech_openai.py # Utilitário para salvar áudios com OpenAI
│       └── text_to_speech_openai_realtime.py # Utilitário de fala em tempo real
└── tests/                           # Suíte de testes automatizados (unittest)
    ├── __init__.py
    ├── test_config.py               # Testes de configurações e .env
    ├── test_cleaner.py              # Testes do utilitário de limpeza de arquivos
    ├── test_player.py               # Testes do reprodutor e fallbacks
    ├── test_tts.py                  # Testes dos sintetizadores OpenAI e gTTS
    ├── test_transcriber.py          # Testes de transcrição Whisper
    └── test_voice_assistant.py      # Testes do loop conversacional e comandos de saída
```

---

## 💻 Pré-requisitos e Instalação

### 1. Pré-requisitos
- **Python 3.8+** (testado e homologado até Python 3.15).
- Microfone e alto-falantes/fones de ouvido configurados no sistema operacional.

### 2. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/speechAI.git
cd speechAI
```

### 3. Criar e ativar o ambiente virtual (recomendado)
No **Windows (PowerShell)**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No **Linux / macOS**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar as dependências
```bash
pip install -r requirements.txt
```

> **Dica**: Caso deseje suporte a transcrição offline local via `faster-whisper`:
> ```bash
> pip install faster-whisper
> ```

---

## ⚙️ Configuração de Variáveis de Ambiente (.env)

Copie o arquivo de exemplo para criar seu `.env`:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e configure suas preferências:

```ini
# =====================================================================
# Exemplo 1: Usando OpenAI Oficial
# =====================================================================
OPENAI_API_KEY=sk-proj-sua-chave-openai
# OPENAI_BASE_URL=https://api.openai.com/v1   # Padrão oficial
OPENAI_CHAT_MODEL=gpt-4o-mini
STT_ENGINE=openai
OPENAI_WHISPER_MODEL=whisper-1
TTS_ENGINE=openai
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=nova

# =====================================================================
# Exemplo 2: Usando OpenRouter (LLM + Whisper Nuvem)
# =====================================================================
OPENAI_API_KEY=sk-or-v1-sua-chave-openrouter
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_CHAT_MODEL=openai/gpt-4o-mini
STT_ENGINE=openai
OPENAI_WHISPER_MODEL=openai/whisper-large-v3-turbo
WHISPER_LANGUAGE=pt
LOCAL_WHISPER_MODEL=base
TTS_ENGINE=gtts

# =====================================================================
# Configurações de Áudio e Hardware
# =====================================================================
PLAYBACK_ENGINE=auto
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1
AUDIO_RECORD_DURATION=5.0
TEMP_DIR=temp
LOG_LEVEL=INFO
```

---

## 🎮 Guia da CLI (Linha de Comando)

O projeto oferece uma interface de linha de comando completa através de `src/main.py`:

### 1. Iniciar a Interface Gráfica (Web UI Studio)
Inicia o estúdio web moderno com orb de voz, laboratório de TTS e STT:
```bash
python src/main.py ui
```
*Opções personalizadas:*
```bash
# Executar em porta customizada:
python src/main.py ui --port 8080

# Permitir acesso via rede local / Wi-Fi:
python src/main.py ui --host 0.0.0.0

# Iniciar em modo headless (sem abrir o browser):
python src/main.py ui --no-browser
```

### 2. Iniciar o Assistente de Voz no Terminal (CLI)
Inicia a escuta contínua pelo microfone com respostas de áudio do assistente:
```bash
python src/main.py assistant
```
*Opções personalizadas:*
```bash
python src/main.py assistant --model gpt-4o-mini --tts openai --stt openai
```
> Para encerrar a qualquer momento, fale: `"sair"`, `"tchau"`, `"exit"` ou pressione `Ctrl + C`.

### 3. Diagnóstico do Sistema
Verifique se microfones, reprodutores e chaves de API estão funcionais:
```bash
python src/main.py check
```

### 4. Falar um Texto (Text-to-Speech)
Sintetiza e reproduz o texto imediatamente:
```bash
# Com gTTS (Google, gratuito e sem chave de API):
python src/main.py speak "Olá, seja muito bem-vindo ao SpeechAI!" --engine gtts

# Com OpenAI TTS:
python src/main.py speak "Hello, I am your intelligent speech assistant." --engine openai --voice nova

# Apenas salvar em arquivo sem reproduzir:
python src/main.py speak "Texto para áudio" --engine gtts --save temp/audio.mp3 --no-play
```

### 5. Transcrever Áudio (Speech-to-Text)
Transcreva um arquivo de áudio existente ou grave diretamente do microfone:
```bash
# Gravar 5 segundos do microfone e transcrever:
python src/main.py transcribe --record 5

# Transcrever um arquivo de áudio existente:
python src/main.py transcribe temp/audio.mp3
```

### 6. Reproduzir um Arquivo de Áudio
Reproduz arquivos WAV, MP3 ou OGG com liberação garantida dos descritores de arquivo:
```bash
python src/main.py play temp/audio.mp3
```

### 7. Limpar Arquivos Temporários
Remove com segurança todos os arquivos gerados em `temp/`:
```bash
python src/main.py clean
```

---

## 🐍 Uso Programático (Python API)

Você pode importar e utilizar o SpeechAI dentro de qualquer script ou aplicação Python:

### Síntese de Voz (TTS)
```python
from src.core.tts import synthesize_text, synthesize_to_bytes
from src.core.audio import play_audio

# 1. Síntese direta em arquivo (escolha 'openai' ou 'gtts')
audio_file = synthesize_text("Olá mundo!", output_file="temp/ola.mp3", engine="gtts")
play_audio(audio_file)

# 2. Síntese em memória (zero disco, menor latência)
audio_buffer = synthesize_to_bytes("Reproduzindo diretamente da memória RAM.", engine="gtts")
play_audio(audio_buffer)
```

### Gravação e Transcrição (STT)
```python
from src.core.audio import record_audio_to_bytes, transcribe_audio

# Grava 3 segundos do microfone diretamente para buffer WAV em memória
wav_buffer = record_audio_to_bytes(duration=3.0)

# Transcreve usando o Whisper
texto = transcribe_audio(wav_buffer, engine="openai")
print(f"Você disse: {texto}")
```

### Instanciando um Assistente de Voz Personalizado
```python
from src.core.voice_assistant import VoiceAssistant

assistente = VoiceAssistant(
    system_prompt="Você é um professor particular de inglês focado em pronúncia.",
    chat_model="gpt-4o-mini",
    tts_engine="openai",
)

# Faz uma pergunta e recebe a resposta falada
resposta = assistente.chat_and_speak("How can I improve my English pronunciation?")
print(resposta)
```

---

## 📊 Comparativo de Motores TTS

| Recurso | Vozes Neurais do Navegador (Web Speech) | OpenAI TTS (`tts-1` / `tts-1-hd`) | Google TTS (`gTTS`) |
| :--- | :--- | :--- | :--- |
| **Qualidade da Voz** | ✨ **Ultra natural, humana e calorosa** (Microsoft Francisca/Antonio) | ✨ **Ultra natural, expressiva e estúdio** (`nova`, `alloy`) | 🤖 Padrão robótico / concatenativa (Google Tradutor) |
| **Necessita Chave de API** | ❌ **Não (100% Gratuito)** | Sim (`OPENAI_API_KEY`) | ❌ **Não (100% Gratuito)** |
| **Vozes Disponíveis** | Vozes online do Windows/Edge/Chrome (pt-BR, en-US, etc.) | 6 vozes (`nova`, `alloy`, `echo`, `fable`, `onyx`, `shimmer`) | Voz padrão por idioma/país |
| **Suporte a Idiomas** | Todos os idiomas suportados pelo sistema | Múltiplos idiomas | Extenso (+100 idiomas) |
| **Velocidade de Geração** | ⚡ **Instantânea (Latência Zero)** | Rápida via API de rede | Muito rápida |
| **Custo** | **Gratuito** | Pago por caractere sintetizado | **Gratuito** |
| **Onde utilizar** | No Web Studio (`python src/main.py ui`) | Na CLI, Python API e Web Studio | Na CLI, Python API e Web Studio |

---

## 🧪 Testes Automatizados

O projeto inclui uma suíte completa de testes unitários que não requer conexões externas (mocks completos de APIs de rede):

Para executar todos os testes:
```bash
python -m unittest discover tests
```

Saída esperada:
```
Ran 31 tests in 0.512s

OK
```

---

## 🔧 Diagnósticos e Resolução de Problemas

Execute sempre a ferramenta de diagnóstico para identificar inconsistências no ambiente:
```bash
python src/main.py check
```

### Problemas Frequentes:

1. **`OPENAI_API_KEY is not configured`**:
   - Certifique-se de ter criado o arquivo `.env` na raiz do projeto com sua chave válida da OpenAI.
   - Alternativamente, use o motor gratuito `gtts` passando `--engine gtts` ou alterando `TTS_ENGINE=gtts` no `.env`.

2. **Microfone não detectado (`sounddevice`)**:
   - No Windows: Verifique as Configurações de Privacidade do Windows -> Permissões de Aplicativo -> Microfone -> "Permitir que os aplicativos da área de trabalho acessem o microfone".

3. **Erro de compilação do `pygame` no Windows**:
   - Utilize a versão moderna comunitária `pygame-ce` (já configurada no `requirements.txt`), que disponibiliza rodas pré-compiladas binárias inclusive para versões recentes do Python.

4. **Arquivos temporários bloqueados no Windows**:
   - O `AudioPlayer` implementado no SpeechAI invoca automaticamente `pygame.mixer.music.unload()` e `stop()` após a execução para garantir a liberação do arquivo no Windows File System.

5. **A voz do assistente soa robótica**:
   - O motor `gTTS` é gratuito, mas utiliza síntese antiga do Google Tradutor. Para obter voz humana natural:
     - Na interface Web (`python src/main.py ui`), escolha a opção **"✨ Voz Neural Natural"** no seletor (usa as vozes neurais de estúdio do Windows/Edge/Chrome com zero latência e sem gastar créditos).
     - Ou configure a API oficial da OpenAI com `TTS_ENGINE=openai` e `OPENAI_TTS_VOICE=nova`.

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Siga os passos:

1. Faça um Fork do projeto
2. Crie uma branch para a sua feature (`git checkout -b feature/minha-melhoria`)
3. Adicione testes para o novo recurso em `tests/`
4. Garanta que todos os testes passem (`python -m unittest discover tests`)
5. Faça o commit (`git commit -m 'feat: adiciona novo suporte a motor de áudio'`)
6. Envie para o branch remoto (`git push origin feature/minha-melhoria`)
7. Abra um Pull Request detalhado

---

## 📜 Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.
