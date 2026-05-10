// Backend API URL - Relative path since frontend is served from same domain
const API_BASE_URL = '/api/v1';

class ChatApp {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.loading = document.getElementById('loading');

        this.init();
    }

    init() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Focus on input
        this.userInput.focus();
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        this.userInput.value = '';

        // Show loading
        this.showLoading();

        try {
            // Call backend API (streaming handles message display)
            await this.callAPI(message);

            // Hide loading
            this.hideLoading();

        } catch (error) {
            this.hideLoading();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('API Error:', error);
            console.error('Full error details:', {
                message: error.message,
                status: error.status,
                response: error.response
            });
        }
    }

    async callAPI(question) {
        try {
            console.log('Calling streaming API:', `${API_BASE_URL}/query/stream`);
            const response = await fetch(`${API_BASE_URL}/query/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    user_id: 'anonymous',
                    top_k: 5
                })
            });

            console.log('API Response Status:', response.status, response.statusText);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error Response:', errorText);
                throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';
            let messageDiv = null;
            let contentDiv = null;
            let paragraph = null;

            // Create message container immediately
            messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';
            const icon = document.createElement('i');
            icon.className = 'fas fa-robot';
            avatarDiv.appendChild(icon);

            contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            paragraph = document.createElement('p');
            contentDiv.appendChild(paragraph);

            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(contentDiv);
            this.messagesContainer.appendChild(messageDiv);

            // Scroll to bottom
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            console.log('Stream completed');
                            return fullResponse;
                        } else {
                            fullResponse += data;
                            paragraph.textContent = fullResponse;
                            // Scroll to bottom as text updates
                            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
                        }
                    }
                }
            }

            return fullResponse || 'I received your question but couldn\'t generate a response.';
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';

        const icon = document.createElement('i');
        icon.className = type === 'user' ? 'fas fa-user' : 'fas fa-robot';
        avatarDiv.appendChild(icon);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        contentDiv.appendChild(paragraph);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showLoading() {
        this.loading.style.display = 'flex';
        this.sendButton.disabled = true;
        this.userInput.disabled = true;
    }

    hideLoading() {
        this.loading.style.display = 'none';
        this.sendButton.disabled = false;
        this.userInput.disabled = false;
        this.userInput.focus();
    }
}

// Quick question function
function askQuestion(question) {
    const userInput = document.getElementById('user-input');
    userInput.value = question;
    userInput.focus();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});