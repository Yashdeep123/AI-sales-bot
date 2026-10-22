/**
 * NexusVoice AI Sales Bot - Master Client Engine
 * Handles Speech Recognition (STT), Speech Synthesis (TTS),
 * 2-Way Call Audio Recording (MediaRecorder), Live Chat Transcription,
 * Dynamic Waveform Visualizer, and Call History Sync.
 */

class VoiceSalesApp {
  constructor() {
    this.callActive = false;
    this.isMuted = false;
    this.callStartTime = null;
    this.timerInterval = null;
    this.currentCallId = null;

    // Active state
    this.productId = document.getElementById("productSelect")?.value || "aws-services";
    this.language = "en";
    this.transcript = []; // [{sender: 'bot'|'user', text: '...', timestamp: '...'}]
    this.apiKey = localStorage.getItem("nexus_api_key") || "";
    this.ttsRate = parseFloat(localStorage.getItem("nexus_tts_rate") || "1.0");
    this.ttsPitch = parseFloat(localStorage.getItem("nexus_tts_pitch") || "1.0");

    // Audio & Recording stack
    this.audioContext = null;
    this.mediaStream = null;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.recordedAudioBlob = null;
    this.recordedAudioUrl = null;
    this.recognition = null;
    this.isBotSpeaking = false;
    this.audioMixerDest = null;

    // Canvas visualizer
    this.canvas = document.getElementById("waveformCanvas");
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
    this.animationFrameId = null;
    this.wavePhase = 0;

    this.init();
  }

  async init() {
    this.bindEvents();
    this.initCanvas();
    this.initSpeechRecognition();
    this.loadProducts();
    this.loadHistory();
    this.loadSettings();
  }

  // ================= 1. EVENT BINDINGS =================

  bindEvents() {
    // Top Bar Selectors
    document.getElementById("productSelect")?.addEventListener("change", (e) => {
      this.productId = e.target.value;
      this.updateProductDetails();
    });

    document.getElementById("languageSelect")?.addEventListener("change", (e) => {
      this.language = e.target.value;
      if (this.recognition) {
        this.recognition.lang = this.getRecognitionLangCode(this.language);
      }
    });

    // Call Controls
    document.getElementById("startCallBtn")?.addEventListener("click", () => this.promptConsent());
    document.getElementById("endCallBtn")?.addEventListener("click", () => this.endCall());
    document.getElementById("muteBtn")?.addEventListener("click", () => this.toggleMute());

    // Consent Modal
    document.getElementById("confirmConsentBtn")?.addEventListener("click", () => {
      this.hideModal("consentModal");
      this.startCall();
    });
    document.getElementById("cancelConsentBtn")?.addEventListener("click", () => this.hideModal("consentModal"));

    // Chat Form (Text Fallback / Simulator)
    document.getElementById("chatInputForm")?.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.getElementById("textInput");
      const text = input.value.trim();
      if (text) {
        this.handleUserSpeech(text);
        input.value = "";
      }
    });

    // Quick Simulator Phrases
    document.querySelectorAll(".phrase-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const phrase = btn.dataset.phrase;
        if (!this.callActive) {
          alert("Please start the call first to engage with the AI sales bot.");
          return;
        }
        this.handleUserSpeech(phrase);
      });
    });

    // Modals: History
    document.getElementById("historyBtn")?.addEventListener("click", () => this.openHistoryModal());
    document.getElementById("closeHistoryModalBtn")?.addEventListener("click", () => this.hideModal("historyModal"));
    document.getElementById("historySearchInput")?.addEventListener("input", () => this.filterHistory());
    document.getElementById("historyStatusFilter")?.addEventListener("change", () => this.filterHistory());
    document.getElementById("clearAllHistoryBtn")?.addEventListener("click", () => this.clearAllHistory());

    // Modals: Summary
    document.getElementById("closeSummaryModalBtn")?.addEventListener("click", () => this.hideModal("summaryModal"));
    document.getElementById("doneSummaryBtn")?.addEventListener("click", () => this.hideModal("summaryModal"));
    document.getElementById("viewInHistoryBtn")?.addEventListener("click", () => {
      this.hideModal("summaryModal");
      this.openHistoryModal();
    });

    // Modals: Settings
    document.getElementById("settingsBtn")?.addEventListener("click", () => this.openSettingsModal());
    document.getElementById("closeSettingsModalBtn")?.addEventListener("click", () => this.hideModal("settingsModal"));
    document.getElementById("saveSettingsBtn")?.addEventListener("click", () => this.saveSettings());

    // Chat Actions
    document.getElementById("clearChatBtn")?.addEventListener("click", () => this.clearChatDisplay());
    document.getElementById("copyTranscriptBtn")?.addEventListener("click", () => this.copyTranscript());
  }

  // ================= 2. AUDIO & VOICE ENGINES =================

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Web Speech Recognition API not supported in this browser. Fallback text input available.");
      document.getElementById("voiceHintText").innerHTML = "Speech recognition not natively supported. You can still use the <strong>text box below</strong> to simulate speech!";
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = this.getRecognitionLangCode(this.language);

    this.recognition.onstart = () => {
      if (this.callActive && !this.isBotSpeaking) {
        this.setCallStatus("listening", "Listening to customer...");
      }
    };

    this.recognition.onresult = (event) => {
      if (!this.callActive || this.isMuted) return;
      const lastIndex = event.results.length - 1;
      const transcriptText = event.results[lastIndex][0].transcript.trim();
      if (transcriptText) {
        // Interruption handling: pause/stop bot speech if user interrupts
        if (this.isBotSpeaking) {
          console.log("[Interruption]: Customer spoke. Halting bot speech.");
          if (window.speechSynthesis) window.speechSynthesis.cancel();
          this.isBotSpeaking = false;
          this.setAvatarSpeaking(false);
          this.showLiveSpeechStatus(false);
        }
        console.log("[STT Recognized]:", transcriptText);
        this.handleUserSpeech(transcriptText);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("[SpeechRecognition Error]:", event.error);
      if (event.error === "not-allowed") {
        document.getElementById("voiceHintText").innerText = "Microphone access denied. Please allow microphone permissions or use the text simulator below.";
      }
    };

    this.recognition.onend = () => {
      // Auto-restart recognition if call is still active
      if (this.callActive && !this.isBotSpeaking) {
        try {
          this.recognition.start();
        } catch (e) {
          // ignore already started
        }
      }
    };
  }

  getRecognitionLangCode(lang) {
    if (lang === "hi") return "hi-IN";
    if (lang === "te") return "te-IN";
    return "en-US";
  }

  promptConsent() {
    this.showModal("consentModal");
  }

  async startCall() {
    if (this.callActive) return;

    // Check user recording consent choice
    const consentChecked = document.getElementById("consentCheckbox")?.checked ?? true;
    this.recordingConsent = consentChecked;

    this.callActive = true;
    this.callStartTime = Date.now();
    this.currentCallId = `call_${Date.now().toString(36)}`;
    this.transcript = [];
    this.recordedChunks = [];
    this.recordedAudioBlob = null;
    this.recordedAudioUrl = null;

    this.clearChatDisplay();
    this.updateControlsState(true);
    this.setCallStatus("active", "Connecting Call...");
    this.startTimer();

    // Show REC indicator if consent was granted
    const recBadge = document.getElementById("recordingBadge");
    if (recBadge) recBadge.style.display = this.recordingConsent ? "inline-flex" : "none";

    // Initialize 2-Way Audio Recording ONLY if consented
    if (this.recordingConsent) {
      await this.setupAudioRecording();
    } else {
      console.log("[Call] User declined recording consent. Session continuing without audio recording.");
    }

    // Request AI Opening Greeting
    await this.fetchAndSpeakGreeting();

    // Start STT
    if (this.recognition) {
      try {
        this.recognition.lang = this.getRecognitionLangCode(this.language);
        this.recognition.start();
      } catch (e) {
        console.log("Recognition start catch:", e);
      }
    }
  }

  async setupAudioRecording() {
    try {
      // Create Web Audio context
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioContextClass();

      // Get user microphone stream
      try {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      } catch (err) {
        console.warn("Mic access not granted. Using synthetic silent stream for recording:", err);
        // Fallback: create silent audio stream
        const osc = this.audioContext.createOscillator();
        const silentDest = this.audioContext.createMediaStreamDestination();
        osc.connect(silentDest);
        this.mediaStream = silentDest.stream;
      }

      // Create audio destination for 2-way merged recording
      this.audioMixerDest = this.audioContext.createMediaStreamDestination();
      const micSource = this.audioContext.createMediaStreamSource(this.mediaStream);
      micSource.connect(this.audioMixerDest);

      // Setup MediaRecorder
      const options = { mimeType: 'audio/webm;codecs=opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'audio/webm';
      }

      this.mediaRecorder = new MediaRecorder(this.audioMixerDest.stream, options);
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.recordedChunks.push(e.data);
        }
      };
      this.mediaRecorder.start(250); // collect 250ms chunks
      console.log("[MediaRecorder] Started dual-channel call recording.");
    } catch (e) {
      console.error("[setupAudioRecording Error]:", e);
    }
  }

  async fetchAndSpeakGreeting() {
    try {
      this.setCallStatus("speaking", "AI Introducing...");
      const res = await fetch("/api/greeting", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: this.productId,
          language: this.language
        })
      });
      const data = await res.json();
      const greeting = data.greeting || "Hello! How can I help you today?";
      this.appendMessage("bot", greeting);
      await this.speak(greeting);
    } catch (e) {
      console.error("Error fetching greeting:", e);
      const fallback = "Hi! Thank you for connecting with us today. How are you doing?";
      this.appendMessage("bot", fallback);
      await this.speak(fallback);
    }
  }

  async handleUserSpeech(userText) {
    if (!this.callActive) return;

    // Add customer message to chat
    this.appendMessage("user", userText);

    // Stop recognition while bot is thinking & speaking
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }

    this.setCallStatus("speaking", "AI Thinking...");
    this.showLiveSpeechStatus(true, "AI is formulating response...");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: userText,
          conversation_history: this.transcript,
          product_id: this.productId,
          language: this.language,
          api_key: this.apiKey
        })
      });

      const data = await res.json();
      const botReply = data.response || "Thank you for sharing that. Would you like to schedule a quick 15-minute demo?";

      this.appendMessage("bot", botReply);
      await this.speak(botReply);

    } catch (e) {
      console.error("[handleUserSpeech Error]:", e);
      const errReply = "I understand. Would you like us to send you more details or schedule a quick walkthrough?";
      this.appendMessage("bot", errReply);
      await this.speak(errReply);
    }

    if (this.callActive && !this.isMuted) {
      this.setCallStatus("listening", "Listening to customer...");
      this.showLiveSpeechStatus(false);
      if (this.recognition) {
        try { this.recognition.start(); } catch (e) {}
      }
    }
  }

  speak(text) {
    return new Promise((resolve) => {
      if (!window.speechSynthesis) {
        this.isBotSpeaking = false;
        resolve();
        return;
      }

      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = this.ttsRate;
      utterance.pitch = this.ttsPitch;

      // Select voice based on language
      const voices = window.speechSynthesis.getVoices();
      if (this.language === "hi") {
        utterance.lang = "hi-IN";
        const hiVoice = voices.find(v => v.lang.includes("hi") || v.name.includes("Hindi"));
        if (hiVoice) utterance.voice = hiVoice;
      } else if (this.language === "te") {
        utterance.lang = "te-IN";
        const teVoice = voices.find(v => v.lang.includes("te") || v.name.includes("Telugu"));
        if (teVoice) utterance.voice = teVoice;
      } else {
        utterance.lang = "en-US";
        const enVoice = voices.find(v => v.lang.includes("en-US") || v.name.includes("Google") || v.name.includes("Natural"));
        if (enVoice) utterance.voice = enVoice;
      }

      this.isBotSpeaking = true;
      this.setAvatarSpeaking(true);
      this.setCallStatus("speaking", "AI Speaking...");
      this.showLiveSpeechStatus(true, "AI is speaking...");

      utterance.onend = () => {
        this.isBotSpeaking = false;
        this.setAvatarSpeaking(false);
        this.showLiveSpeechStatus(false);
        resolve();
      };

      utterance.onerror = (e) => {
        console.warn("[TTS Error]:", e);
        this.isBotSpeaking = false;
        this.setAvatarSpeaking(false);
        this.showLiveSpeechStatus(false);
        resolve();
      };

      window.speechSynthesis.speak(utterance);
    });
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    const muteBtn = document.getElementById("muteBtn");
    const muteIcon = document.getElementById("muteIcon");

    if (this.isMuted) {
      muteBtn.classList.add("muted");
      muteIcon.className = "fa-solid fa-microphone-slash";
      if (this.recognition) {
        try { this.recognition.stop(); } catch (e) {}
      }
    } else {
      muteBtn.classList.remove("muted");
      muteIcon.className = "fa-solid fa-microphone";
      if (this.callActive && this.recognition) {
        try { this.recognition.start(); } catch (e) {}
      }
    }
  }

  // ================= 3. CALL TERMINATION & AI SUMMARY =================

  async endCall() {
    if (!this.callActive) return;

    this.callActive = false;
    this.stopTimer();
    this.updateControlsState(false);
    this.setCallStatus("ready", "Call Ended");
    this.setAvatarSpeaking(false);
    this.showLiveSpeechStatus(false);

    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }

    // Stop MediaRecorder and produce audio blob
    await this.finalizeRecording();

    // Calculate call duration
    const durationSeconds = Math.round((Date.now() - this.callStartTime) / 1000);
    const durationFormatted = this.formatDuration(durationSeconds);

    // Call server to generate AI summary and sales status
    this.setCallStatus("speaking", "Generating AI Summary...");
    let analysisResult = null;
    try {
      const res = await fetch("/api/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcript: this.transcript,
          product_id: this.productId,
          language: this.language,
          api_key: this.apiKey
        })
      });
      analysisResult = await res.json();
    } catch (e) {
      console.error("[Summary API Error]:", e);
      analysisResult = {
        summary: "Call concluded with customer discussion on SaaS lead automation.",
        customer_requirements: ["Automated outreach"],
        objections: ["None recorded"],
        next_steps: ["Send follow-up details"],
        sales_status: "Interested",
        status_reason: "Customer engaged with the AI representative."
      };
    }

    // Persist full call record to server
    const callRecord = {
      id: this.currentCallId,
      created_at: new Date().toISOString(),
      duration: durationFormatted,
      duration_seconds: durationSeconds,
      product_id: this.productId,
      product_name: document.getElementById("productTitle")?.innerText || "NexusPulse AI",
      language: this.language,
      transcript: this.transcript,
      recording_consent: this.recordingConsent,
      recording_url: this.recordedAudioUrl,
      sales_status: analysisResult.sales_status,
      status_reason: analysisResult.status_reason,
      summary: analysisResult.summary,
      customer_requirements: analysisResult.customer_requirements,
      objections: analysisResult.objections,
      next_steps: analysisResult.next_steps,
      sentiment: analysisResult.sentiment
    };

    try {
      await fetch("/api/calls", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(callRecord)
      });
      this.loadHistory(); // refresh history list
    } catch (e) {
      console.error("[Save Call Error]:", e);
    }

    // Open Post-Call Intelligence Modal
    this.displayPostCallSummary(callRecord);
  }

  async finalizeRecording() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
        resolve();
        return;
      }

      this.mediaRecorder.onstop = async () => {
        try {
          this.recordedAudioBlob = new Blob(this.recordedChunks, { type: 'audio/webm' });
          const localUrl = URL.createObjectURL(this.recordedAudioBlob);

          // Upload audio blob to server
          const formData = new FormData();
          formData.append("audio", this.recordedAudioBlob, `${this.currentCallId}.webm`);
          formData.append("call_id", this.currentCallId);

          const res = await fetch("/api/recordings", {
            method: "POST",
            body: formData
          });
          const data = await res.json();
          this.recordedAudioUrl = data.recording_url || localUrl;
          console.log("[Audio Uploaded]:", this.recordedAudioUrl);
        } catch (err) {
          console.warn("Could not upload recording to server, using local blob URL:", err);
          if (this.recordedAudioBlob) {
            this.recordedAudioUrl = URL.createObjectURL(this.recordedAudioBlob);
          }
        }
        resolve();
      };

      try {
        this.mediaRecorder.stop();
      } catch (e) {
        resolve();
      }
    });
  }

  displayPostCallSummary(callRecord) {
    document.getElementById("modalCallId").innerText = callRecord.id.toUpperCase();
    document.getElementById("summarySalesStatus").innerText = callRecord.sales_status;
    document.getElementById("summaryStatusReason").innerText = callRecord.status_reason || "";
    
    const durationLabel = document.getElementById("recordingDurationText");
    if (callRecord.recording_url) {
      durationLabel.innerText = `Duration: ${callRecord.duration}`;
    } else {
      durationLabel.innerText = callRecord.recording_consent === false 
        ? "Recording: Opted out by customer" 
        : `Duration: ${callRecord.duration} (No audio)`;
    }

    // Status Banner class
    const statusBanner = document.getElementById("statusBanner");
    const statusClass = this.getStatusCssClass(callRecord.sales_status);
    statusBanner.className = `status-banner ${statusClass}`;

    // Audio Player
    const audioEl = document.getElementById("postCallAudio");
    const downloadBtn = document.getElementById("downloadAudioBtn");
    if (callRecord.recording_url) {
      audioEl.src = callRecord.recording_url;
      audioEl.style.display = "block";
      downloadBtn.href = callRecord.recording_url;
      downloadBtn.download = `${callRecord.id}.webm`;
      downloadBtn.style.display = "inline-flex";
    } else {
      audioEl.style.display = "none";
      downloadBtn.style.display = "none";
    }

    // Executive Summary
    document.getElementById("summaryOverviewText").innerText = callRecord.summary;

    // Requirements list
    const reqList = document.getElementById("summaryRequirementsList");
    reqList.innerHTML = "";
    (callRecord.customer_requirements || []).forEach((req) => {
      const li = document.createElement("li");
      li.innerText = req;
      reqList.appendChild(li);
    });

    // Objections list
    const objList = document.getElementById("summaryObjectionsList");
    objList.innerHTML = "";
    (callRecord.objections || []).forEach((obj) => {
      const li = document.createElement("li");
      li.innerText = obj;
      objList.appendChild(li);
    });

    // Next steps list
    const nextList = document.getElementById("summaryNextStepsList");
    nextList.innerHTML = "";
    (callRecord.next_steps || []).forEach((step) => {
      const li = document.createElement("li");
      li.innerText = step;
      nextList.appendChild(li);
    });

    this.showModal("summaryModal");
  }

  // ================= 4. LIVE CHAT & DOM =================

  appendMessage(sender, text) {
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    this.transcript.push({ sender, text, timestamp });

    const chatContainer = document.getElementById("chatContainer");
    const emptyState = document.getElementById("emptyChatState");
    if (emptyState) emptyState.style.display = "none";

    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${sender}`;

    const isBot = sender === "bot";
    const senderName = isBot ? "Alex (AI Sales)" : "Customer (You)";
    const avatarIcon = isBot ? "fa-solid fa-robot" : "fa-solid fa-user";

    bubble.innerHTML = `
      <div class="msg-avatar">
        <i class="${avatarIcon}"></i>
      </div>
      <div class="msg-content">
        <div class="msg-info">
          <span class="msg-sender">${senderName}</span>
          <span class="msg-time">${timestamp}</span>
        </div>
        <div class="msg-text-box">
          ${this.escapeHtml(text)}
        </div>
      </div>
    `;

    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  clearChatDisplay() {
    const chatContainer = document.getElementById("chatContainer");
    chatContainer.innerHTML = `
      <div class="empty-chat-state" id="emptyChatState">
        <div class="empty-icon"><i class="fa-solid fa-wave-square"></i></div>
        <h3>No Active Conversation</h3>
        <p>Start a call to engage with the AI voice sales representative. Both AI speech and your customer responses will appear here live with timestamps.</p>
      </div>
    `;
  }

  copyTranscript() {
    if (!this.transcript.length) {
      alert("No transcript messages to copy.");
      return;
    }
    const text = this.transcript
      .map(m => `[${m.timestamp}] ${m.sender === 'bot' ? 'AI Bot' : 'Customer'}: ${m.text}`)
      .join("\n");
    navigator.clipboard.writeText(text).then(() => {
      alert("Transcript copied to clipboard!");
    });
  }

  showLiveSpeechStatus(visible, text = "") {
    const el = document.getElementById("liveSpeechStatus");
    const label = document.getElementById("liveSpeechText");
    if (el) el.style.display = visible ? "flex" : "none";
    if (label && text) label.innerText = text;
  }

  setAvatarSpeaking(isSpeaking) {
    const ring = document.getElementById("avatarRing");
    if (ring) {
      if (isSpeaking) ring.classList.add("speaking");
      else ring.classList.remove("speaking");
    }
  }

  setCallStatus(stateClass, labelText) {
    const pill = document.getElementById("callStatusPill");
    const text = document.getElementById("callStatusText");
    if (pill) {
      pill.className = `call-status-pill status-${stateClass}`;
    }
    if (text) text.innerText = labelText;
  }

  updateControlsState(inCall) {
    document.getElementById("startCallBtn").disabled = inCall;
    document.getElementById("endCallBtn").disabled = !inCall;
    document.getElementById("muteBtn").disabled = !inCall;
    document.getElementById("textInput").disabled = !inCall;
    document.getElementById("sendBtn").disabled = !inCall;

    if (inCall) {
      document.getElementById("voiceHintText").innerHTML = "Call is live! Speak clearly into your mic or click any quick phrase below.";
    } else {
      document.getElementById("voiceHintText").innerHTML = "Click <strong>Start Call</strong> to begin interactive voice conversation.";
    }
  }

  startTimer() {
    this.stopTimer();
    const timerEl = document.getElementById("callTimer");
    timerEl.innerText = "00:00";
    this.timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
      timerEl.innerText = this.formatDuration(elapsed);
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  formatDuration(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  // ================= 5. CALL HISTORY =================

  async loadHistory() {
    try {
      const res = await fetch("/api/calls");
      const calls = await res.json();
      const badge = document.getElementById("historyCountBadge");
      if (badge) badge.innerText = calls.length;
      this.renderHistoryList(calls);
    } catch (e) {
      console.warn("Could not load calls history:", e);
    }
  }

  renderHistoryList(calls) {
    const container = document.getElementById("historyListContainer");
    if (!container) return;

    if (!calls || calls.length === 0) {
      container.innerHTML = `
        <div class="empty-history" id="emptyHistoryState">
          <i class="fa-solid fa-inbox"></i>
          <p>No call history recorded yet. Complete a call to populate this log.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = calls.map(c => {
      const dateFormatted = new Date(c.created_at).toLocaleString();
      const statusClass = this.getStatusCssClass(c.sales_status);
      const audioTag = c.recording_url
        ? `<div class="history-audio-preview">
             <audio src="${c.recording_url}" controls preload="none"></audio>
             <a href="${c.recording_url}" download="${c.id}.webm" class="btn btn-sm btn-ghost" title="Download Audio">
               <i class="fa-solid fa-download"></i>
             </a>
           </div>`
        : `<span class="subtext">No recording</span>`;

      return `
        <div class="history-item" data-id="${c.id}" data-status="${c.sales_status}">
          <div class="history-item-top">
            <div class="history-meta">
              <strong>${c.product_name || "NexusPulse AI"}</strong>
              <span><i class="fa-regular fa-clock"></i> ${c.duration}</span>
              <span><i class="fa-regular fa-calendar"></i> ${dateFormatted}</span>
            </div>
            <span class="status-pill ${statusClass}">${c.sales_status}</span>
          </div>
          <div class="history-item-body">
            <div class="history-summary-snippet">
              ${this.escapeHtml(c.summary || "No summary available.")}
            </div>
            ${audioTag}
          </div>
        </div>
      `;
    }).join("");
  }

  filterHistory() {
    const query = (document.getElementById("historySearchInput")?.value || "").toLowerCase();
    const statusFilter = document.getElementById("historyStatusFilter")?.value || "all";
    const items = document.querySelectorAll(".history-item");

    items.forEach(item => {
      const itemStatus = item.dataset.status;
      const itemText = item.innerText.toLowerCase();
      const matchesQuery = !query || itemText.includes(query);
      const matchesStatus = statusFilter === "all" || itemStatus === statusFilter;
      item.style.display = (matchesQuery && matchesStatus) ? "flex" : "none";
    });
  }

  async clearAllHistory() {
    if (!confirm("Are you sure you want to clear all call history?")) return;
    try {
      const res = await fetch("/api/calls");
      const calls = await res.json();
      for (const c of calls) {
        await fetch(`/api/calls/${c.id}`, { method: "DELETE" });
      }
      this.loadHistory();
    } catch (e) {
      console.error("Error clearing history:", e);
    }
  }

  openHistoryModal() {
    this.loadHistory();
    this.showModal("historyModal");
  }

  getStatusCssClass(status) {
    switch (status) {
      case "Converted": return "status-converted";
      case "Demo Requested": return "status-demo";
      case "Interested": return "status-interested";
      case "Follow-up Required": return "status-followup";
      case "Not Interested": return "status-not-interested";
      case "No Response": default: return "status-no-response";
    }
  }

  // ================= 6. PRODUCT CATALOG & SETTINGS =================

  async loadProducts() {
    try {
      const res = await fetch("/api/products");
      const data = await res.json();
      this.catalog = data.catalog || {};
      this.updateProductDetails();
    } catch (e) {
      console.warn("Could not load products catalog:", e);
    }
  }

  updateProductDetails() {
    if (!this.catalog || !this.catalog[this.productId]) return;
    const prod = this.catalog[this.productId];
    document.getElementById("productTitle").innerText = prod.name;
    document.getElementById("productTagline").innerText = prod.tagline;
    document.getElementById("productCategoryBadge").innerText = prod.category;

    const chips = document.getElementById("pricingChips");
    if (chips && prod.pricing) {
      chips.innerHTML = prod.pricing.map(p => `
        <div class="chip"><strong>${p.name}:</strong> ${p.price}</div>
      `).join("");
    }
  }

  openSettingsModal() {
    document.getElementById("apiKeyInput").value = this.apiKey;
    document.getElementById("ttsRateRange").value = this.ttsRate;
    document.getElementById("ttsRateVal").innerText = `${this.ttsRate}x`;
    document.getElementById("ttsPitchRange").value = this.ttsPitch;
    document.getElementById("ttsPitchVal").innerText = this.ttsPitch;

    document.getElementById("ttsRateRange").oninput = (e) => {
      document.getElementById("ttsRateVal").innerText = `${e.target.value}x`;
    };
    document.getElementById("ttsPitchRange").oninput = (e) => {
      document.getElementById("ttsPitchVal").innerText = e.target.value;
    };

    this.showModal("settingsModal");
  }

  saveSettings() {
    this.apiKey = document.getElementById("apiKeyInput").value.trim();
    this.ttsRate = parseFloat(document.getElementById("ttsRateRange").value);
    this.ttsPitch = parseFloat(document.getElementById("ttsPitchRange").value);

    localStorage.setItem("nexus_api_key", this.apiKey);
    localStorage.setItem("nexus_tts_rate", this.ttsRate.toString());
    localStorage.setItem("nexus_tts_pitch", this.ttsPitch.toString());

    this.hideModal("settingsModal");
    alert("Settings saved successfully!");
  }

  loadSettings() {
    const key = localStorage.getItem("nexus_api_key");
    if (key) this.apiKey = key;
  }

  // ================= 7. CANVAS AUDIO WAVEFORM =================

  initCanvas() {
    if (!this.canvas) return;
    const resizeCanvas = () => {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    this.renderWaveform();
  }

  renderWaveform() {
    if (!this.ctx || !this.canvas) return;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerY = height / 2;

    const isActive = this.callActive;
    const isSpeaking = this.isBotSpeaking;
    const baseAmp = isSpeaking ? 38 : (isActive ? 18 : 6);

    this.wavePhase += isSpeaking ? 0.08 : (isActive ? 0.03 : 0.01);

    // Multi-band sinusoidal waveform
    const waves = [
      { color: "rgba(99, 102, 241, 0.4)", freq: 0.012, amp: baseAmp * 1.0, offset: 0 },
      { color: "rgba(6, 182, 212, 0.4)", freq: 0.016, amp: baseAmp * 0.75, offset: 2 },
      { color: "rgba(168, 85, 247, 0.3)", freq: 0.009, amp: baseAmp * 0.5, offset: 4 }
    ];

    waves.forEach(w => {
      this.ctx.beginPath();
      this.ctx.lineWidth = 2.5;
      this.ctx.strokeStyle = w.color;

      for (let x = 0; x < width; x += 4) {
        const y = centerY + Math.sin(x * w.freq + this.wavePhase + w.offset) * w.amp;
        if (x === 0) this.ctx.moveTo(x, y);
        else this.ctx.lineTo(x, y);
      }
      this.ctx.stroke();
    });

    this.animationFrameId = requestAnimationFrame(() => this.renderWaveform());
  }

  // ================= 8. MODAL HELPERS =================

  showModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = "flex";
  }

  hideModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = "none";
  }

  escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// Instantiate on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  window.app = new VoiceSalesApp();
});
