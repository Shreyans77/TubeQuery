const API_BASE = "/api";

async function processVideo() {
    const urlInput = document.getElementById('video-url');
    const processBtn = document.getElementById('process-btn');
    const statusMsg = document.getElementById('status-message');
    const loader = processBtn.querySelector('.loader');
    const btnText = processBtn.querySelector('.btn-text');

    const url = urlInput.value.trim();
    if (!url) {
        showStatus("Please enter a valid YouTube URL", "error");
        return;
    }

    // UI Loading State
    urlInput.disabled = true;
    processBtn.disabled = true;
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    showStatus("Processing transcript and embedding... This may take a moment.", "");

    try {
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to process video");
        }

        // Success State
        showStatus("Success! Ready to chat.", "success");
        setTimeout(() => {
            document.getElementById('input-section').classList.add('hidden');
            document.getElementById('chat-section').classList.remove('hidden');
            document.getElementById('chat-section').classList.add('fade-in');
        }, 1000);

    } catch (error) {
        showStatus(`Error: ${error.message}`, "error");
        // Reset UI
        urlInput.disabled = false;
        processBtn.disabled = false;
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

async function askQuestion() {
    const questionInput = document.getElementById('user-question');
    const chatHistory = document.getElementById('chat-history');
    const question = questionInput.value.trim();

    if (!question) return;

    // Add User Message
    addMessage(question, 'user');
    questionInput.value = '';

    // Loading indicator for bot
    const paramId = 'loading-' + Date.now();
    addMessage('Thinking...', 'bot', paramId);

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        // Remove loading and add real message
        const loadingMsg = document.getElementById(paramId);
        if (loadingMsg) loadingMsg.remove();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to get answer");
        }

        addMessage(data.answer, 'bot');

    } catch (error) {
        const loadingMsg = document.getElementById(paramId);
        if (loadingMsg) loadingMsg.remove();
        addMessage(`Error: ${error.message}`, 'bot');
    }
}

function addMessage(text, sender, id = null) {
    const chatHistory = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', `${sender}-message`);
    msgDiv.textContent = text;
    if (id) msgDiv.id = id;

    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function showStatus(msg, type) {
    const el = document.getElementById('status-message');
    el.textContent = msg;
    el.className = 'status ' + type;
}

function resetApp() {
    // Reload to plain state
    location.reload();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}
