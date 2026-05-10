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
            // Call backend API
            const response = await this.callAPI(message);

            // Hide loading
            this.hideLoading();

            // Add bot response
            this.addMessage(response, 'bot');

        } catch (error) {
            this.hideLoading();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('API Error:', error);
        }
    }

    async callAPI(question) {
        const response = await fetch(`${API_BASE_URL}/query`, {
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

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();
        return data.answer || 'I received your question but couldn\'t generate a response.';
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