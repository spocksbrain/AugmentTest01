// DOM Elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const voiceButton = document.getElementById('voice-button');
const statusDot = document.getElementById('status-dot');

// Voice recording variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Connection state
let socketConnected = false;
let websocketConnected = false;

// Initialize Socket.IO
const socket = io(config.socketIoUrl);

// Initialize WebSocket (as a fallback)
let ws = null;
initWebSocket();

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to Socket.IO server');
    socketConnected = true;
    updateConnectionStatus();
});

socket.on('disconnect', () => {
    console.log('Disconnected from Socket.IO server');
    socketConnected = false;
    updateConnectionStatus();
});

socket.on('message', (data) => {
    console.log('Received message from Socket.IO:', data);
    handleMessage(data);
});

// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Voice button event listener
voiceButton.addEventListener('click', toggleVoiceRecording);

// Functions
function initWebSocket() {
    // Only initialize WebSocket if Socket.IO is not connected
    if (socketConnected) return;

    // Close existing WebSocket if any
    if (ws) {
        ws.close();
    }

    // Create new WebSocket
    ws = new WebSocket(config.websocketUrl);

    // WebSocket event handlers
    ws.onopen = () => {
        console.log('Connected to WebSocket server');
        websocketConnected = true;
        updateConnectionStatus();
    };

    ws.onclose = () => {
        console.log('Disconnected from WebSocket server');
        websocketConnected = false;
        updateConnectionStatus();

        // Try to reconnect after a delay
        setTimeout(initWebSocket, 5000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        websocketConnected = false;
        updateConnectionStatus();
    };

    ws.onmessage = (event) => {
        console.log('Received message from WebSocket:', event.data);
        try {
            const data = JSON.parse(event.data);
            handleMessage(data);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };
}

function updateConnectionStatus() {
    if (socketConnected || websocketConnected) {
        statusDot.classList.remove('error');
        statusDot.classList.add('idle');
    } else {
        statusDot.classList.remove('idle');
        statusDot.classList.add('error');

        // Add a system message
        addMessage({
            role: 'system',
            content: 'Connection lost. Trying to reconnect...'
        });
    }
}

function sendMessage() {
    const content = messageInput.value.trim();
    if (!content) return;

    // Create message object
    const message = {
        type: 'message',
        data: {
            role: 'user',
            content: content,
            timestamp: Date.now() / 1000
        }
    };

    // Add message to UI
    addMessage(message.data);

    // Clear input
    messageInput.value = '';

    // Send message
    if (socketConnected) {
        socket.emit('message', message);
    } else if (websocketConnected) {
        ws.send(JSON.stringify(message));
    } else {
        addMessage({
            role: 'system',
            content: 'Not connected to server. Please try again later.'
        });
        return;
    }

    // Update dot state
    statusDot.className = 'dot processing';
}

function handleMessage(data) {
    if (data.type === 'chat_message') {
        addMessage(data.data);
    } else if (data.type === 'dot_state') {
        updateDotState(data.data.state);
    }
}

function addMessage(message) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');

    // Set message type class
    if (message.role === 'user') {
        messageElement.classList.add('user-message');
    } else if (message.role === 'assistant') {
        messageElement.classList.add('assistant-message');
    } else {
        messageElement.classList.add('system-message');
    }

    // Set message content
    messageElement.textContent = message.content;

    // Add message to container
    messagesContainer.appendChild(messageElement);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateDotState(state) {
    // Remove all state classes
    statusDot.className = 'dot';

    // Add the new state class
    statusDot.classList.add(state);
}

// Voice recording functions
async function toggleVoiceRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Create media recorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        // Set up event handlers
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            // Create audio blob
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendVoiceMessage(audioBlob);

            // Reset recording state
            isRecording = false;
            voiceButton.classList.remove('recording');

            // Stop all tracks in the stream
            stream.getTracks().forEach(track => track.stop());
        };

        // Start recording
        mediaRecorder.start();
        isRecording = true;
        voiceButton.classList.add('recording');

        // Add a system message
        addMessage({
            role: 'system',
            content: 'Recording voice message... Click the microphone button again to stop.'
        });

    } catch (error) {
        console.error('Error starting voice recording:', error);
        addMessage({
            role: 'system',
            content: 'Error accessing microphone. Please check your browser permissions.'
        });
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
    }
}

function sendVoiceMessage(audioBlob) {
    // Create a message to show in the UI
    addMessage({
        role: 'user',
        content: '🎤 Voice message sent'
    });

    // Update dot state
    statusDot.className = 'dot processing';

    // Convert blob to base64
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = function() {
        const base64Audio = reader.result.split(',')[1]; // Remove the data URL prefix

        // Create message object
        const message = {
            type: 'voice_message',
            data: {
                audio: base64Audio,
                timestamp: Date.now() / 1000
            }
        };

        // Send message
        if (socketConnected) {
            socket.emit('message', message);
        } else if (websocketConnected) {
            ws.send(JSON.stringify(message));
        } else {
            addMessage({
                role: 'system',
                content: 'Not connected to server. Please try again later.'
            });
            return;
        }
    };
}

// Add welcome message
addMessage({
    role: 'assistant',
    content: 'Welcome to exo! I\'m your personal assistant. How can I help you today?'
});

// Register Service Worker for PWA functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    });

    // Add install prompt for PWA
    let deferredPrompt;
    const installButton = document.createElement('button');
    installButton.style.display = 'none';
    installButton.classList.add('install-button');
    installButton.textContent = 'Install App';
    document.querySelector('.app-header').appendChild(installButton);

    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        // Update UI to notify the user they can add to home screen
        installButton.style.display = 'block';

        installButton.addEventListener('click', () => {
            // Hide our user interface that shows our install button
            installButton.style.display = 'none';
            // Show the install prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                } else {
                    console.log('User dismissed the install prompt');
                }
                deferredPrompt = null;
            });
        });
    });
}
