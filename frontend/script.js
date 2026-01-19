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

// Send message to API with streaming support
async function sendMessageStream(message, onChunk) {
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

        // Check if the response is streaming (Server-Sent Events or plain text stream)
        const contentType = response.headers.get('content-type');

        if (contentType && (contentType.includes('text/event-stream') || contentType.includes('text/plain'))) {
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                // Decode the chunk
                buffer += decoder.decode(value, { stream: true });

                // Process complete lines/chunks
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.trim()) {
                        // Handle SSE format
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data !== '[DONE]') {
                                onChunk(data);
                            }
                        } else {
                            // Handle plain text chunks
                            onChunk(line);
                        }
                    }
                }
            }

            // Process any remaining data in buffer
            if (buffer.trim()) {
                if (buffer.startsWith('data: ')) {
                    const data = buffer.slice(6);
                    if (data !== '[DONE]') {
                        onChunk(data);
                    }
                } else {
                    onChunk(buffer);
                }
            }
        } else {
            // Handle non-streaming JSON response (fallback)
            const data = await response.json();
            const result = typeof data.result === 'string'
                ? data.result
                : JSON.stringify(data.result, null, 2);
            onChunk(result);
        }
    } catch (error) {
        throw error;
    }
}

// Handle form submission with streaming
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

    // Create assistant message container for streaming
    let assistantMessageDiv = null;
    let assistantContentDiv = null;
    let accumulatedContent = '';

    try {
        // Send message to API with streaming
        await sendMessageStream(message, (chunk) => {
            // Remove loading indicator on first chunk
            if (loadingIndicator.parentNode) {
                loadingIndicator.remove();
            }

            // Create message element on first chunk
            if (!assistantMessageDiv) {
                assistantMessageDiv = document.createElement('div');
                assistantMessageDiv.className = 'message assistant';

                const labelDiv = document.createElement('div');
                labelDiv.className = 'message-label';
                labelDiv.textContent = 'Assistant';

                assistantContentDiv = document.createElement('div');
                assistantContentDiv.className = 'message-content';

                assistantMessageDiv.appendChild(labelDiv);
                assistantMessageDiv.appendChild(assistantContentDiv);
                chatMessages.appendChild(assistantMessageDiv);
            }

            // Append chunk to content
            accumulatedContent += chunk;
            assistantContentDiv.textContent = accumulatedContent;
            scrollToBottom();
        });

        // If no chunks were received, remove loading indicator
        if (loadingIndicator.parentNode) {
            loadingIndicator.remove();
        }

        // If no message was created, create an empty one
        if (!assistantMessageDiv) {
            const assistantMessage = createMessageElement('No response received', 'assistant');
            chatMessages.appendChild(assistantMessage);
        }

    } catch (error) {
        // Remove loading indicator
        if (loadingIndicator.parentNode) {
            loadingIndicator.remove();
        }

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
