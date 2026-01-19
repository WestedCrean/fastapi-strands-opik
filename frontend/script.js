// Configuration
const API_URL = 'http://localhost:8000/llm';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// State
let isLoading = false;

// Create message element
function createMessageElement(content, type = 'assistant') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = type === 'user' ? 'You' : type === 'error' ? 'Error' : 'Assistant';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

// Create loading indicator
function createLoadingElement() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading';
    loadingDiv.id = 'loadingIndicator';

    for (let i = 0; i < 3; i++) {
        const span = document.createElement('span');
        loadingDiv.appendChild(span);
    }

    return loadingDiv;
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to API
async function sendMessage(message) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (isLoading) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';

    // Add user message to chat
    const userMessage = createMessageElement(message, 'user');
    chatMessages.appendChild(userMessage);
    scrollToBottom();

    // Show loading indicator
    isLoading = true;
    sendButton.disabled = true;
    const loadingIndicator = createLoadingElement();
    chatMessages.appendChild(loadingIndicator);
    scrollToBottom();

    try {
        // Send message to API
        const response = await sendMessage(message);

        // Remove loading indicator
        loadingIndicator.remove();

        // Add assistant response to chat
        const assistantMessage = createMessageElement(
            typeof response.result === 'string'
                ? response.result
                : JSON.stringify(response.result, null, 2),
            'assistant'
        );
        chatMessages.appendChild(assistantMessage);

    } catch (error) {
        // Remove loading indicator
        loadingIndicator.remove();

        // Show error message
        const errorMessage = createMessageElement(
            `Failed to get response: ${error.message}`,
            'error'
        );
        chatMessages.appendChild(errorMessage);

        console.error('Error:', error);
    } finally {
        isLoading = false;
        sendButton.disabled = false;
        scrollToBottom();
        messageInput.focus();
    }
});

// Focus input on load
messageInput.focus();
