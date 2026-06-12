/**
 * AI Lab Assistant — Frontend Application
 * Handles text chat, voice recording, audio playback, and WebSocket communication.
 */

(function () {
    "use strict";

    // ── Configuration ───────────────────────────────────────
    const API_BASE = window.location.origin;
    const MAX_RECORDING_MS = 30000; // 30 seconds max recording
    const SAMPLE_RATE = 16000; // 16kHz for ASR

    // ── DOM Elements ────────────────────────────────────────
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const btnSend = document.getElementById("btn-send");
    const btnVoice = document.getElementById("btn-voice");
    const statusIndicator = document.getElementById("status-indicator");
    const statusText = statusIndicator.querySelector(".status-text");
    const recordingStatus = document.getElementById("recording-status");
    const charCount = document.getElementById("char-count");
    const audioPlayer = document.getElementById("audio-player");

    // ── State ───────────────────────────────────────────────
    let isRecording = false;
    let audioContext = null;
    let mediaStream = null;
    let scriptProcessor = null;
    let audioChunks = [];
    let recordingTimer = null;
    let conversationId = generateId();

    // ── Initialization ──────────────────────────────────────
    function init() {
        // Event listeners
        btnSend.addEventListener("click", sendTextMessage);
        btnVoice.addEventListener("click", toggleRecording);
        messageInput.addEventListener("keydown", handleKeyDown);
        messageInput.addEventListener("input", handleInput);

        // Auto-resize textarea
        messageInput.addEventListener("input", autoResize);

        // Check backend health
        checkHealth();

        // Focus input
        messageInput.focus();
    }

    // ── Health Check ────────────────────────────────────────
    async function checkHealth() {
        try {
            const resp = await fetch(`${API_BASE}/health`);
            if (resp.ok) {
                const data = await resp.json();
                setStatus("connected", "Đã kết nối");
            } else {
                setStatus("error", "Lỗi kết nối");
            }
        } catch (e) {
            setStatus("error", "Không thể kết nối server");
            console.error("Health check failed:", e);
        }
    }

    function setStatus(state, text) {
        statusIndicator.className = `status-indicator ${state}`;
        statusText.textContent = text;
    }

    // ── Text Chat ───────────────────────────────────────────
    async function sendTextMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Add user message to UI
        addMessage("user", text);
        messageInput.value = "";
        messageInput.style.height = "auto";
        charCount.classList.remove("visible");
        btnSend.disabled = true;

        // Show typing indicator
        const typingEl = showTyping();

        try {
            const resp = await fetch(`${API_BASE}/chat/text`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    conversation_id: conversationId,
                }),
            });

            removeTyping(typingEl);

            if (resp.ok) {
                const data = await resp.json();
                addMessage("assistant", data.reply, {
                    latency: `${data.latency_ms.toFixed(0)}ms`,
                    model: data.model,
                });
            } else {
                const err = await resp.json().catch(() => ({}));
                addMessage("assistant", `❌ Lỗi: ${err.error || "Không thể xử lý yêu cầu"}`, {
                    isError: true,
                });
            }
        } catch (e) {
            removeTyping(typingEl);
            addMessage("assistant", "❌ Không thể kết nối đến server. Vui lòng thử lại.", {
                isError: true,
            });
            console.error("Chat error:", e);
        }

        btnSend.disabled = false;
        messageInput.focus();
    }

    // ── Voice Recording (Web Audio API → WAV) ───────────────
    async function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    async function startRecording() {
        try {
            // Request microphone access
            mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });

            // Create AudioContext at 16kHz for direct ASR-compatible recording
            audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: SAMPLE_RATE,
            });

            const source = audioContext.createMediaStreamSource(mediaStream);

            // Use ScriptProcessorNode to capture raw PCM data
            // Buffer size 4096 gives ~256ms chunks at 16kHz
            scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
            audioChunks = [];

            scriptProcessor.onaudioprocess = (event) => {
                const channelData = event.inputBuffer.getChannelData(0);
                // Clone the Float32Array data (buffer gets reused)
                audioChunks.push(new Float32Array(channelData));
            };

            source.connect(scriptProcessor);
            scriptProcessor.connect(audioContext.destination);

            isRecording = true;
            updateRecordingUI(true);
            console.log(`Recording started: ${audioContext.sampleRate}Hz, mono`);

            // Auto-stop after max duration
            recordingTimer = setTimeout(() => {
                if (isRecording) stopRecording();
            }, MAX_RECORDING_MS);

        } catch (e) {
            console.error("Microphone access error:", e);
            addMessage("assistant", "❌ Không thể truy cập microphone. Vui lòng kiểm tra quyền truy cập.", {
                isError: true,
            });
        }
    }

    function stopRecording() {
        isRecording = false;
        clearTimeout(recordingTimer);
        updateRecordingUI(false);

        // Disconnect audio nodes
        if (scriptProcessor) {
            scriptProcessor.disconnect();
            scriptProcessor = null;
        }

        // Stop media stream
        if (mediaStream) {
            mediaStream.getTracks().forEach((track) => track.stop());
            mediaStream = null;
        }

        // Close audio context
        if (audioContext) {
            audioContext.close();
            audioContext = null;
        }

        // Process recorded audio
        if (audioChunks.length > 0) {
            const wavBlob = encodeWAV(audioChunks, SAMPLE_RATE);
            console.log(`Recording stopped: ${audioChunks.length} chunks, WAV size: ${wavBlob.size} bytes`);
            sendVoiceMessage(wavBlob);
        }
    }

    /**
     * Encode Float32Array PCM chunks into a WAV file Blob.
     * WAV format: 16-bit PCM, mono, specified sample rate.
     */
    function encodeWAV(chunks, sampleRate) {
        // Merge all chunks into one Float32Array
        let totalLength = 0;
        for (const chunk of chunks) {
            totalLength += chunk.length;
        }

        const merged = new Float32Array(totalLength);
        let offset = 0;
        for (const chunk of chunks) {
            merged.set(chunk, offset);
            offset += chunk.length;
        }

        // Convert Float32 [-1.0, 1.0] to Int16 [-32768, 32767]
        const int16 = new Int16Array(merged.length);
        for (let i = 0; i < merged.length; i++) {
            const s = Math.max(-1, Math.min(1, merged[i]));
            int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Build WAV file
        const wavBuffer = new ArrayBuffer(44 + int16.length * 2);
        const view = new DataView(wavBuffer);

        // RIFF header
        writeString(view, 0, "RIFF");
        view.setUint32(4, 36 + int16.length * 2, true);
        writeString(view, 8, "WAVE");

        // fmt chunk
        writeString(view, 12, "fmt ");
        view.setUint32(16, 16, true);         // chunk size
        view.setUint16(20, 1, true);           // PCM format
        view.setUint16(22, 1, true);           // mono
        view.setUint32(24, sampleRate, true);   // sample rate
        view.setUint32(28, sampleRate * 2, true); // byte rate (16-bit mono)
        view.setUint16(32, 2, true);           // block align
        view.setUint16(34, 16, true);          // bits per sample

        // data chunk
        writeString(view, 36, "data");
        view.setUint32(40, int16.length * 2, true);

        // Write PCM samples
        const dataView = new Uint8Array(wavBuffer, 44);
        const int16Bytes = new Uint8Array(int16.buffer);
        dataView.set(int16Bytes);

        return new Blob([wavBuffer], { type: "audio/wav" });
    }

    function writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    function updateRecordingUI(recording) {
        const micIcon = btnVoice.querySelector(".mic-icon");
        const stopIcon = btnVoice.querySelector(".stop-icon");

        if (recording) {
            btnVoice.classList.add("recording");
            micIcon.classList.add("hidden");
            stopIcon.classList.remove("hidden");
            recordingStatus.classList.remove("hidden");
        } else {
            btnVoice.classList.remove("recording");
            micIcon.classList.remove("hidden");
            stopIcon.classList.add("hidden");
            recordingStatus.classList.add("hidden");
        }
    }

    async function sendVoiceMessage(audioBlob) {
        // Show recording sent indicator
        addMessage("user", "🎤 Tin nhắn thoại", { isVoice: true });

        const typingEl = showTyping();

        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "recording.wav");

            const resp = await fetch(`${API_BASE}/chat/voice`, {
                method: "POST",
                body: formData,
            });

            removeTyping(typingEl);

            if (resp.ok) {
                const data = await resp.json();

                // Update user message with transcript
                if (data.transcript) {
                    updateLastUserMessage(data.transcript);
                }

                // Add assistant response
                const latencyParts = [];
                if (data.latency.asr_ms) latencyParts.push(`ASR: ${data.latency.asr_ms.toFixed(0)}ms`);
                if (data.latency.llm_ms) latencyParts.push(`LLM: ${data.latency.llm_ms.toFixed(0)}ms`);
                if (data.latency.tts_ms) latencyParts.push(`TTS: ${data.latency.tts_ms.toFixed(0)}ms`);
                if (data.latency.total_ms) latencyParts.push(`Tổng: ${data.latency.total_ms.toFixed(0)}ms`);

                addMessage("assistant", data.reply, {
                    latency: latencyParts.join(" | "),
                    model: data.model,
                    audioBase64: data.audio_url,
                });

                // Auto-play response audio
                if (data.audio_url) {
                    playAudioBase64(data.audio_url);
                }
            } else {
                const err = await resp.json().catch(() => ({}));
                addMessage("assistant", `❌ Lỗi: ${err.error || "Voice pipeline error"}`, {
                    isError: true,
                });
            }
        } catch (e) {
            removeTyping(typingEl);
            addMessage("assistant", "❌ Không thể xử lý giọng nói. Vui lòng thử lại.", {
                isError: true,
            });
            console.error("Voice chat error:", e);
        }
    }

    // ── Audio Playback ──────────────────────────────────────
    function playAudioBase64(base64Data) {
        try {
            const audioSrc = `data:audio/mp3;base64,${base64Data}`;
            audioPlayer.src = audioSrc;
            audioPlayer.play().catch((e) => {
                console.warn("Auto-play blocked:", e);
            });
        } catch (e) {
            console.error("Audio playback error:", e);
        }
    }

    // ── Message UI ──────────────────────────────────────────
    function addMessage(role, text, options = {}) {
        const messageEl = document.createElement("div");
        messageEl.className = `message ${role}-message`;

        let avatarHtml = "";
        if (role === "assistant") {
            avatarHtml = `
                <div class="message-avatar">
                    <svg viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" fill="url(#msgGrad)"/>
                        <path d="M8 10C8 9.44772 8.44772 9 9 9H15C15.5523 9 16 9.44772 16 10V14C16 14.5523 15.5523 15 15 15H13.5L12 17L10.5 15H9C8.44772 15 8 14.5523 8 14V10Z" fill="white"/>
                        <defs>
                            <linearGradient id="msgGrad" x1="2" y1="2" x2="22" y2="22">
                                <stop offset="0%" stop-color="#6366f1"/>
                                <stop offset="100%" stop-color="#8b5cf6"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>`;
        } else {
            avatarHtml = `
                <div class="message-avatar">
                    <svg viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.5" fill="none"/>
                        <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
                        <path d="M6 19.5C6 16.5 8.5 14.5 12 14.5C15.5 14.5 18 16.5 18 19.5" stroke="currentColor" stroke-width="1.5" fill="none"/>
                    </svg>
                </div>`;
        }

        // Build bubble content
        let bubbleContent = `<p>${escapeHtml(text)}</p>`;

        if (options.isError) {
            messageEl.classList.add("error-message");
        }

        // Add audio play button
        if (options.audioBase64) {
            bubbleContent += `
                <button class="audio-play-btn" onclick="document.getElementById('audio-player').src='data:audio/mp3;base64,${options.audioBase64}';document.getElementById('audio-player').play()">
                    <svg viewBox="0 0 24 24" fill="none">
                        <polygon points="5,3 19,12 5,21" fill="currentColor"/>
                    </svg>
                    Phát lại
                </button>`;
        }

        // Add latency badge
        if (options.latency) {
            bubbleContent += `
                <div class="latency-badge">
                    <svg viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M12 7V12L15 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                    ${options.latency}
                </div>`;
        }

        messageEl.innerHTML = `
            ${avatarHtml}
            <div class="message-content">
                <div class="message-bubble">${bubbleContent}</div>
            </div>`;

        chatMessages.appendChild(messageEl);
        scrollToBottom();
    }

    function updateLastUserMessage(transcript) {
        const userMessages = chatMessages.querySelectorAll(".user-message");
        const lastUserMsg = userMessages[userMessages.length - 1];
        if (lastUserMsg) {
            const bubble = lastUserMsg.querySelector(".message-bubble p");
            if (bubble) {
                bubble.textContent = transcript;
            }
        }
    }

    function showTyping() {
        const el = document.createElement("div");
        el.className = "message assistant-message typing";
        el.innerHTML = `
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" fill="url(#msgGrad)"/>
                    <path d="M8 10C8 9.44772 8.44772 9 9 9H15C15.5523 9 16 9.44772 16 10V14C16 14.5523 15.5523 15 15 15H13.5L12 17L10.5 15H9C8.44772 15 8 14.5523 8 14V10Z" fill="white"/>
                    <defs>
                        <linearGradient id="msgGrad" x1="2" y1="2" x2="22" y2="22">
                            <stop offset="0%" stop-color="#6366f1"/>
                            <stop offset="100%" stop-color="#8b5cf6"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>`;
        chatMessages.appendChild(el);
        scrollToBottom();
        return el;
    }

    function removeTyping(el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }

    // ── Input Handling ──────────────────────────────────────
    function handleKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendTextMessage();
        }
    }

    function handleInput() {
        const len = messageInput.value.length;
        if (len > 0) {
            charCount.textContent = `${len}/5000`;
            charCount.classList.add("visible");
        } else {
            charCount.classList.remove("visible");
        }
    }

    function autoResize() {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    }

    // ── Utilities ───────────────────────────────────────────
    function scrollToBottom() {
        const chatArea = document.getElementById("chat-area");
        requestAnimationFrame(() => {
            chatArea.scrollTop = chatArea.scrollHeight;
        });
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function generateId() {
        return "conv_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    }

    // ── Start ───────────────────────────────────────────────
    document.addEventListener("DOMContentLoaded", init);
})();
