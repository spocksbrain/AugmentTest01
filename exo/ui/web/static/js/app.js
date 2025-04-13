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

// Function to auto-scroll to the bottom of the messages container
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Settings Modal Functionality
const settingsButton = document.getElementById('settings-button');
const settingsModal = document.getElementById('settings-modal');
const closeButton = document.querySelector('.close-button');
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// LLM Settings Elements
const defaultProvider = document.getElementById('default-provider');
const defaultModel = document.getElementById('default-model');
const openaiApiKey = document.getElementById('openai-api-key');
const anthropicApiKey = document.getElementById('anthropic-api-key');
const googleApiKey = document.getElementById('google-api-key');
const openrouterApiKey = document.getElementById('openrouter-api-key');
const ollamaHost = document.getElementById('ollama-host');
const saveLlmSettingsButton = document.getElementById('save-llm-settings');

// MCP Server Elements
const mcpServersList = document.getElementById('mcp-servers-list');
const addMcpServerButton = document.getElementById('add-mcp-server');
const mcpServerForm = document.getElementById('mcp-server-form');
const mcpFormTitle = document.getElementById('mcp-form-title');
const mcpServerId = document.getElementById('mcp-server-id');
const mcpServerName = document.getElementById('mcp-server-name');
const mcpServerUrl = document.getElementById('mcp-server-url');
const mcpServerApiKey = document.getElementById('mcp-server-api-key');
const saveMcpServerButton = document.getElementById('save-mcp-server');
const cancelMcpServerButton = document.getElementById('cancel-mcp-server');

// General Settings Elements
const themeSelect = document.getElementById('theme-select');
const autoScroll = document.getElementById('auto-scroll');
const saveGeneralSettingsButton = document.getElementById('save-general-settings');

// Model options by provider
const modelOptions = {
    openai: [
        { value: 'gpt-4o', label: 'GPT-4o' },
        { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
        { value: 'gpt-4', label: 'GPT-4' },
        { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
        { value: 'o3-mini', label: 'o3-mini (Claude 3 Opus)' }
    ],
    anthropic: [
        { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
        { value: 'claude-3-sonnet-20240229', label: 'Claude 3 Sonnet' },
        { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
        { value: 'claude-2.1', label: 'Claude 2.1' },
        { value: 'claude-2.0', label: 'Claude 2.0' },
        { value: 'claude-instant-1.2', label: 'Claude Instant 1.2' }
    ],
    google: [
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' },
        { value: 'gemini-1.0-pro', label: 'Gemini 1.0 Pro' },
        { value: 'gemini-1.0-ultra', label: 'Gemini 1.0 Ultra' }
    ],
    openrouter: [
        { value: 'openai/gpt-4o', label: 'GPT-4o (OpenAI)' },
        { value: 'anthropic/claude-3-opus', label: 'Claude 3 Opus (Anthropic)' },
        { value: 'google/gemini-1.5-pro', label: 'Gemini 1.5 Pro (Google)' },
        { value: 'meta-llama/llama-3-70b-instruct', label: 'Llama 3 70B (Meta)' }
    ],
    ollama: [
        { value: 'llama3', label: 'Llama 3' },
        { value: 'llama3:8b', label: 'Llama 3 8B' },
        { value: 'llama3:70b', label: 'Llama 3 70B' },
        { value: 'mistral', label: 'Mistral' },
        { value: 'mixtral', label: 'Mixtral' },
        { value: 'codellama', label: 'CodeLlama' }
    ]
};

// Open settings modal
settingsButton.addEventListener('click', () => {
    settingsModal.classList.add('active');
    loadSettings();
});

// Close settings modal
closeButton.addEventListener('click', () => {
    settingsModal.classList.remove('active');
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    if (event.target === settingsModal) {
        settingsModal.classList.remove('active');
    }
});

// Tab switching
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Update model options based on selected provider
defaultProvider.addEventListener('change', () => {
    const provider = defaultProvider.value;

    // Show loading state
    defaultModel.innerHTML = '<option value="">Loading models...</option>';

    // Fetch models from the API
    fetch(`/api/models/${provider}`)
        .then(response => response.json())
        .then(data => {
            if (data.models && data.models.length > 0) {
                // Clear existing options
                defaultModel.innerHTML = '';

                // Add new options
                data.models.forEach(model => {
                    const optionElement = document.createElement('option');
                    optionElement.value = model.value;
                    optionElement.textContent = model.label;
                    defaultModel.appendChild(optionElement);
                });
            } else {
                // No models found, use fallback
                updateModelOptionsFromStatic();
            }
        })
        .catch(error => {
            console.error(`Error fetching ${provider} models:`, error);
            // Use fallback on error
            updateModelOptionsFromStatic();
        });
});

// Toggle password visibility
document.querySelectorAll('.toggle-visibility').forEach(button => {
    button.addEventListener('click', () => {
        const input = button.previousElementSibling;
        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = 'Hide';
        } else {
            input.type = 'password';
            button.textContent = 'Show';
        }
    });
});

// Save LLM settings
saveLlmSettingsButton.addEventListener('click', () => {
    const settings = {
        default_provider: defaultProvider.value,
        default_model: defaultModel.value,
        api_keys: {
            openai: openaiApiKey.value,
            anthropic: anthropicApiKey.value,
            google: googleApiKey.value,
            openrouter: openrouterApiKey.value
        },
        ollama_host: ollamaHost.value
    };

    saveLlmSettings(settings);
});

// Add MCP server button
addMcpServerButton.addEventListener('click', () => {
    mcpFormTitle.textContent = 'Add MCP Server';
    mcpServerId.value = '';
    mcpServerName.value = '';
    mcpServerUrl.value = '';
    mcpServerApiKey.value = '';
    mcpServerForm.classList.remove('hidden');
});

// Cancel MCP server form
cancelMcpServerButton.addEventListener('click', () => {
    mcpServerForm.classList.add('hidden');
});

// Save MCP server
saveMcpServerButton.addEventListener('click', () => {
    const server = {
        id: mcpServerId.value,
        name: mcpServerName.value,
        url: mcpServerUrl.value,
        api_key: mcpServerApiKey.value
    };

    saveMcpServer(server);
});

// Save general settings
saveGeneralSettingsButton.addEventListener('click', () => {
    const settings = {
        theme: themeSelect.value,
        auto_scroll: autoScroll.checked
    };

    saveGeneralSettings(settings);
});

// Load settings from server
function loadSettings() {
    // Load LLM settings
    fetch('/api/settings/llm')
        .then(response => response.json())
        .then(data => {
            defaultProvider.value = data.default_provider || 'openai';

            // Fetch models for the selected provider
            const provider = defaultProvider.value;

            // Show loading state
            defaultModel.innerHTML = '<option value="">Loading models...</option>';

            // Fetch models from the API
            fetch(`/api/models/${provider}`)
                .then(response => response.json())
                .then(modelData => {
                    if (modelData.models && modelData.models.length > 0) {
                        // Clear existing options
                        defaultModel.innerHTML = '';

                        // Add new options
                        modelData.models.forEach(model => {
                            const optionElement = document.createElement('option');
                            optionElement.value = model.value;
                            optionElement.textContent = model.label;
                            defaultModel.appendChild(optionElement);
                        });

                        // Set the selected model
                        defaultModel.value = data.default_model || '';
                    } else {
                        // No models found, use fallback
                        updateModelOptionsFromStatic();
                        defaultModel.value = data.default_model || '';
                    }
                })
                .catch(error => {
                    console.error(`Error fetching ${provider} models:`, error);
                    // Use fallback on error
                    updateModelOptionsFromStatic();
                    defaultModel.value = data.default_model || '';
                });

            if (data.api_keys) {
                openaiApiKey.value = data.api_keys.openai || '';
                anthropicApiKey.value = data.api_keys.anthropic || '';
                googleApiKey.value = data.api_keys.google || '';
                openrouterApiKey.value = data.api_keys.openrouter || '';
            }

            ollamaHost.value = data.ollama_host || 'http://localhost:11434';
        })
        .catch(error => {
            console.error('Error loading LLM settings:', error);
        });

    // Load MCP servers
    fetch('/api/settings/mcp-servers')
        .then(response => response.json())
        .then(data => {
            renderMcpServersList(data.servers || []);
        })
        .catch(error => {
            console.error('Error loading MCP servers:', error);
        });

    // Load general settings
    fetch('/api/settings/general')
        .then(response => response.json())
        .then(data => {
            themeSelect.value = data.theme || 'system';
            autoScroll.checked = data.auto_scroll !== false; // Default to true
        })
        .catch(error => {
            console.error('Error loading general settings:', error);
        });
}

// Update model options from static list (fallback)
function updateModelOptionsFromStatic() {
    const provider = defaultProvider.value;
    const options = modelOptions[provider] || [];

    // Clear existing options
    defaultModel.innerHTML = '';

    // Add new options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        defaultModel.appendChild(optionElement);
    });
}

// Render MCP servers list
function renderMcpServersList(servers) {
    if (servers.length === 0) {
        mcpServersList.innerHTML = '<div class="empty-state">No MCP servers configured</div>';
        return;
    }

    mcpServersList.innerHTML = '';

    servers.forEach(server => {
        const serverItem = document.createElement('div');
        serverItem.className = 'server-item';
        serverItem.innerHTML = `
            <div class="server-info">
                <div class="server-name">${server.name}</div>
                <div class="server-url">${server.url}</div>
            </div>
            <div class="server-actions">
                <button class="edit-button" data-id="${server.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </button>
                <button class="delete-button" data-id="${server.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            </div>
        `;

        mcpServersList.appendChild(serverItem);
    });

    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', () => {
            const serverId = button.getAttribute('data-id');
            editMcpServer(serverId, servers);
        });
    });

    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', () => {
            const serverId = button.getAttribute('data-id');
            deleteMcpServer(serverId);
        });
    });
}

// Edit MCP server
function editMcpServer(serverId, servers) {
    const server = servers.find(s => s.id === serverId);
    if (!server) return;

    mcpFormTitle.textContent = 'Edit MCP Server';
    mcpServerId.value = server.id;
    mcpServerName.value = server.name;
    mcpServerUrl.value = server.url;
    mcpServerApiKey.value = server.api_key || '';
    mcpServerForm.classList.remove('hidden');
}

// Delete MCP server
function deleteMcpServer(serverId) {
    if (!confirm('Are you sure you want to delete this MCP server?')) return;

    fetch(`/api/settings/mcp-servers/${serverId}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadSettings(); // Reload the servers list
            } else {
                alert('Failed to delete MCP server: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting MCP server:', error);
            alert('Failed to delete MCP server: ' + error.message);
        });
}

// Save LLM settings
function saveLlmSettings(settings) {
    fetch('/api/settings/llm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('LLM settings saved successfully!');
            } else {
                alert('Failed to save LLM settings: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error saving LLM settings:', error);
            alert('Failed to save LLM settings: ' + error.message);
        });
}

// Save MCP server
function saveMcpServer(server) {
    const isNew = !server.id;
    const method = isNew ? 'POST' : 'PUT';
    const url = isNew ? '/api/settings/mcp-servers' : `/api/settings/mcp-servers/${server.id}`;

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(server)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mcpServerForm.classList.add('hidden');
                loadSettings(); // Reload the servers list
            } else {
                alert('Failed to save MCP server: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error saving MCP server:', error);
            alert('Failed to save MCP server: ' + error.message);
        });
}

// Save general settings
function saveGeneralSettings(settings) {
    fetch('/api/settings/general', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('General settings saved successfully!');
                applyTheme(settings.theme);
            } else {
                alert('Failed to save general settings: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error saving general settings:', error);
            alert('Failed to save general settings: ' + error.message);
        });
}

// Apply theme
function applyTheme(theme) {
    if (theme === 'system') {
        // Use system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        } else {
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        }
    } else if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
    } else if (theme === 'light') {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
    }
}
