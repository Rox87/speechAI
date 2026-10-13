/**
 * SpeechAI Studio - Interactive Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  initTabs();

  // Assistant Logic
  initAssistant();

  // TTS Studio Logic
  initTTS();

  // STT Studio Logic
  initSTT();

  // Settings & Diagnostics
  initSettings();
});

/* =====================================================================
   1. Tab Navigation
   ===================================================================== */
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');

      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });
}

/* =====================================================================
   2. Voice Assistant (Live Interaction)
   ===================================================================== */
function initAssistant() {
  const micOrb = document.getElementById('btn-mic-toggle');
  const micContainer = document.querySelector('.mic-orb-container');
  const statusTitle = document.getElementById('assistant-status-title');
  const statusDesc = document.getElementById('assistant-status-desc');
  const chipMode = document.getElementById('chip-mode');
  const chatContainer = document.getElementById('chat-messages-container');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-text-input');
  const historyCounter = document.getElementById('history-counter');
  const btnClearChat = document.getElementById('btn-clear-chat');
  const btnBrowserRecord = document.getElementById('btn-browser-record');

  let interactionCount = 0;
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];

  // Update status UI helper
  function setAssistantStatus(state, title, desc) {
    statusTitle.textContent = title;
    statusDesc.textContent = desc;

    if (state === 'listening') {
      micContainer.classList.add('active');
      micOrb.classList.add('recording');
      chipMode.textContent = 'Ouvindo...';
      chipMode.style.color = '#f43f5e';
    } else if (state === 'thinking') {
      micContainer.classList.remove('active');
      micOrb.classList.remove('recording');
      chipMode.textContent = 'Processando...';
      chipMode.style.color = '#f59e0b';
    } else if (state === 'speaking') {
      micContainer.classList.add('active');
      micOrb.classList.remove('recording');
      chipMode.textContent = 'Falando...';
      chipMode.style.color = '#10b981';
    } else {
      micContainer.classList.remove('active');
      micOrb.classList.remove('recording');
      chipMode.textContent = 'Pronto';
      chipMode.style.color = '#06b6d4';
    }
  }

  // Append chat bubble
  function addBubble(role, text) {
    const emptyState = document.getElementById('chat-empty-state');
    if (emptyState) emptyState.remove();

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    const textElem = document.createElement('p');
    textElem.textContent = text;
    bubble.appendChild(textElem);

    const meta = document.createElement('div');
    meta.className = 'bubble-meta';
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    meta.textContent = role === 'user' ? `Você • ${now}` : `Assistente • ${now}`;
    bubble.appendChild(meta);

    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    interactionCount++;
    historyCounter.textContent = `${interactionCount} interações`;
  }

  // Play audio in-browser helper
  function playSpeechAudio(audioUrl) {
    const audio = new Audio(audioUrl);
    setAssistantStatus('speaking', 'Assistente falando...', 'Reproduzindo resposta gerada pelo modelo.');
    audio.play().catch(e => console.warn('Autoplay bloqueado:', e));
    audio.onended = () => {
      setAssistantStatus('idle', 'Clique no microfone para falar', 'O assistente está pronto para ouvir sua próxima fala.');
    };
  }

  // Trigger server hardware mic turn
  async function runServerVoiceTurn() {
    setAssistantStatus('listening', 'Gravando pelo microfone do computador (5s)...', 'Fale agora com o microfone...');
    try {
      const res = await fetch('/api/voice-turn', { method: 'POST' });
      const data = await res.json();

      if (data.error) {
        setAssistantStatus('idle', 'Erro na gravação', data.error);
        return;
      }

      if (data.user_text) {
        addBubble('user', data.user_text);
      }
      if (data.assistant_text) {
        addBubble('assistant', data.assistant_text);
        const synthUrl = `/api/synthesize?text=${encodeURIComponent(data.assistant_text)}&engine=gtts`;
        playSpeechAudio(synthUrl);
      } else {
        setAssistantStatus('idle', 'Nenhuma fala detectada', 'Tente falar mais próximo ao microfone.');
      }
    } catch (err) {
      setAssistantStatus('idle', 'Erro na conexão', err.message);
    }
  }

  // Browser MediaRecorder fallback
  async function toggleBrowserRecording() {
    if (isRecording) {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        isRecording = false;
        stream.getTracks().forEach(t => t.stop());
        setAssistantStatus('thinking', 'Transcrevendo áudio via Whisper...', 'Enviando gravação para transcrição...');

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = async () => {
          const base64Audio = reader.result;

          // 1. Transcribe
          try {
            const trRes = await fetch('/api/transcribe', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: jsonStringify({ audio_base64: base64Audio })
            });
            const trData = await trRes.json();
            const transcript = trData.transcript;

            if (!transcript) {
              setAssistantStatus('idle', 'Nenhuma fala detectada', 'Tente novamente falando mais alto.');
              return;
            }

            addBubble('user', transcript);
            setAssistantStatus('thinking', 'Gerando resposta...', 'Consultando modelo no OpenRouter...');

            // 2. Chat completion
            const chatRes = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: jsonStringify({ message: transcript })
            });
            const chatData = await chatRes.json();
            const reply = chatData.reply || 'Sem resposta.';

            addBubble('assistant', reply);

            // 3. Synthesize & Speak
            const synthUrl = `/api/synthesize?text=${encodeURIComponent(reply)}&engine=gtts`;
            playSpeechAudio(synthUrl);

          } catch (e) {
            setAssistantStatus('idle', 'Erro no processamento', e.message);
          }
        };
      };

      mediaRecorder.start();
      isRecording = true;
      setAssistantStatus('listening', 'Gravando pelo navegador...', 'Fale agora! Clique novamente no botão para enviar.');
    } catch (e) {
      alert('Permissão de microfone negada ou indisponível no navegador: ' + e.message);
    }
  }

  // Click on central mic orb
  micOrb.addEventListener('click', () => {
    runServerVoiceTurn();
  });

  // Browser record button
  btnBrowserRecord.addEventListener('click', () => {
    toggleBrowserRecording();
  });

  // Clear chat
  btnClearChat.addEventListener('click', () => {
    chatContainer.innerHTML = `
      <div class="chat-empty-state" id="chat-empty-state">
        <div class="empty-icon">💬</div>
        <p>Conversa limpa.</p>
        <span>Fale pelo microfone ou digite uma mensagem abaixo.</span>
      </div>
    `;
    interactionCount = 0;
    historyCounter.textContent = '0 interações';
  });

  // Text Form Submission
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    addBubble('user', text);
    setAssistantStatus('thinking', 'Gerando resposta...', 'Consultando modelo...');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({ message: text })
      });
      const data = await res.json();
      const reply = data.reply || 'Desculpe, ocorreu um erro.';
      addBubble('assistant', reply);

      const synthUrl = `/api/synthesize?text=${encodeURIComponent(reply)}&engine=gtts`;
      playSpeechAudio(synthUrl);
    } catch (err) {
      setAssistantStatus('idle', 'Erro no chat', err.message);
    }
  });
}

/* =====================================================================
   3. TTS Studio (Synthesis)
   ===================================================================== */
function initTTS() {
  const textInput = document.getElementById('tts-text-input');
  const charCounter = document.getElementById('tts-char-counter');
  const engineSelect = document.getElementById('tts-engine-select');
  const btnSynthesize = document.getElementById('btn-synthesize');
  const audioPlayer = document.getElementById('tts-audio-player');
  const btnDownload = document.getElementById('btn-download-audio');
  const visualizer = document.getElementById('tts-visualizer-bars');
  const playerStatus = document.getElementById('tts-player-status');
  const presetButtons = document.querySelectorAll('.preset-btn');

  function updateCharCount() {
    charCounter.textContent = `${textInput.value.length} caracteres`;
  }

  textInput.addEventListener('input', updateCharCount);
  updateCharCount();

  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      textInput.value = btn.getAttribute('data-text');
      updateCharCount();
    });
  });

  // Synthesize button
  btnSynthesize.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
      alert('Digite algum texto para sintetizar.');
      return;
    }

    const engine = engineSelect.value;
    btnSynthesize.disabled = true;
    btnSynthesize.innerHTML = '<span class="btn-icon">⏳</span><span>Sintetizando...</span>';
    playerStatus.textContent = 'Gerando áudio...';

    try {
      const res = await fetch('/api/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify({ text: text, engine: engine })
      });
      const data = await res.json();

      if (data.error) {
        alert('Erro ao sintetizar áudio: ' + data.error);
        playerStatus.textContent = 'Erro';
        return;
      }

      audioPlayer.src = data.audio_base64;
      audioPlayer.play();
      btnDownload.href = data.audio_base64;
      btnDownload.classList.remove('disabled');
      playerStatus.textContent = 'Reproduzindo';
      visualizer.classList.add('animating');

    } catch (e) {
      alert('Falha na comunicação com o servidor: ' + e.message);
      playerStatus.textContent = 'Falha';
    } finally {
      btnSynthesize.disabled = false;
      btnSynthesize.innerHTML = '<span class="btn-icon">⚡</span><span>Sintetizar & Ouvir</span>';
    }
  });

  audioPlayer.onplay = () => {
    visualizer.classList.add('animating');
    playerStatus.textContent = 'Reproduzindo';
  };
  audioPlayer.onpause = () => {
    visualizer.classList.remove('animating');
    playerStatus.textContent = 'Pausado';
  };
  audioPlayer.onended = () => {
    visualizer.classList.remove('animating');
    playerStatus.textContent = 'Concluído';
  };
}

/* =====================================================================
   4. STT Studio (Transcription)
   ===================================================================== */
function initSTT() {
  const dropzone = document.getElementById('stt-dropzone');
  const fileInput = document.getElementById('stt-file-input');
  const btnRecord = document.getElementById('btn-stt-record');
  const btnRecordText = document.getElementById('btn-stt-record-text');
  const outputBox = document.getElementById('stt-transcript-output');
  const btnCopy = document.getElementById('btn-copy-transcript');
  const latencyTag = document.getElementById('stt-latency-tag');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--primary)';
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
    if (e.dataTransfer.files.length > 0) {
      processAudioFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      processAudioFile(fileInput.files[0]);
    }
  });

  async function processAudioFile(file) {
    outputBox.innerHTML = '<p class="placeholder-text">Transcrevendo áudio com Whisper no OpenRouter...</p>';
    const startTime = performance.now();

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = async () => {
      try {
        const res = await fetch('/api/transcribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: jsonStringify({ audio_base64: reader.result, engine: 'openai' })
        });
        const data = await res.json();
        const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
        latencyTag.textContent = `Latência: ${elapsed}s`;

        if (data.transcript) {
          outputBox.textContent = data.transcript;
        } else {
          outputBox.innerHTML = `<p class="placeholder-text">${data.error || 'Nenhum texto detectado.'}</p>`;
        }
      } catch (e) {
        outputBox.innerHTML = `<p class="placeholder-text">Erro: ${e.message}</p>`;
      }
    };
  }

  // 5s Record from browser
  btnRecord.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      btnRecord.disabled = true;
      btnRecordText.textContent = 'Gravando (fale agora)...';
      outputBox.innerHTML = '<p class="placeholder-text">Gravando áudio do microfone...</p>';

      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        btnRecord.disabled = false;
        btnRecordText.textContent = 'Gravar do Microfone (5s)';
        const blob = new Blob(chunks, { type: 'audio/wav' });
        processAudioFile(blob);
      };

      recorder.start();
      setTimeout(() => recorder.stop(), 5000);
    } catch (e) {
      alert('Erro ao acessar microfone: ' + e.message);
      btnRecord.disabled = false;
      btnRecordText.textContent = 'Gravar do Microfone (5s)';
    }
  });

  // Copy text
  btnCopy.addEventListener('click', () => {
    const text = outputBox.textContent;
    if (text && !text.includes('aparecerá aqui')) {
      navigator.clipboard.writeText(text);
      const prev = btnCopy.textContent;
      btnCopy.textContent = '✅ Copiado!';
      setTimeout(() => btnCopy.textContent = prev, 1800);
    }
  });
}

/* =====================================================================
   5. Settings & Diagnostics
   ===================================================================== */
function initSettings() {
  const form = document.getElementById('settings-form');
  const baseUrlInput = document.getElementById('cfg-base-url');
  const chatModelInput = document.getElementById('cfg-chat-model');
  const whisperModelInput = document.getElementById('cfg-whisper-model');
  const ttsEngineSelect = document.getElementById('cfg-tts-engine');
  const ttsModelInput = document.getElementById('cfg-tts-model');
  const btnReload = document.getElementById('btn-reload-config');
  const btnDiagnostics = document.getElementById('btn-run-diagnostics');
  const diagContainer = document.getElementById('diagnostic-results-container');
  const badgeModelText = document.getElementById('badge-model-text');
  const badgeConnectionText = document.getElementById('badge-connection-text');

  async function loadConfig() {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();

      baseUrlInput.value = data.openai_base_url || '';
      chatModelInput.value = data.chat_model || '';
      whisperModelInput.value = data.openai_whisper_model || '';
      ttsEngineSelect.value = data.tts_engine || 'gtts';
      ttsModelInput.value = data.openai_tts_model || '';

      if (data.openai_whisper_model) {
        badgeModelText.textContent = data.openai_whisper_model;
      }
      if (data.openai_base_url && data.openai_base_url.includes('openrouter')) {
        badgeConnectionText.textContent = 'OpenRouter Conectado';
      } else {
        badgeConnectionText.textContent = 'OpenAI Conectado';
      }
    } catch (e) {
      console.error('Falha ao carregar configurações:', e);
    }
  }

  loadConfig();

  btnReload.addEventListener('click', loadConfig);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      openai_base_url: baseUrlInput.value.trim(),
      openai_chat_model: chatModelInput.value.trim(),
      openai_whisper_model: whisperModelInput.value.trim(),
      tts_engine: ttsEngineSelect.value,
      openai_tts_model: ttsModelInput.value.trim(),
    };

    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStringify(payload)
      });
      const data = await res.json();
      if (data.status === 'saved') {
        alert('Configurações salvas no .env com sucesso!');
        loadConfig();
      }
    } catch (err) {
      alert('Erro ao salvar configurações: ' + err.message);
    }
  });

  // Diagnostics
  async function runDiagnostics() {
    diagContainer.innerHTML = '<div class="loading-state">Executando diagnósticos do ambiente...</div>';
    try {
      const res = await fetch('/api/diagnostics');
      const data = await res.json();

      diagContainer.innerHTML = '';
      data.checks.forEach(check => {
        const item = document.createElement('div');
        item.className = `diagnostic-item ${check.status}`;
        item.innerHTML = `
          <div>
            <div class="diag-title">${check.name}</div>
            <div class="diag-msg">${check.message}</div>
          </div>
          <span class="chip">${check.status.toUpperCase()}</span>
        `;
        diagContainer.appendChild(item);
      });
    } catch (err) {
      diagContainer.innerHTML = `<div class="diagnostic-item error">Erro ao rodar diagnóstico: ${err.message}</div>`;
    }
  }

  btnDiagnostics.addEventListener('click', runDiagnostics);
  // Run once on load
  runDiagnostics();
}

// Utility
function jsonStringify(obj) {
  return JSON.stringify(obj);
}
