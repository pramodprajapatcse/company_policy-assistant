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
            let sources = [];
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

            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                buffer += chunk;
                const lines = buffer.split('\n');

                // Keep the last incomplete line in the buffer
                buffer = lines[lines.length - 1];

                for (let i = 0; i < lines.length - 1; i++) {
                    const line = lines[i];
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            console.log('Stream completed');
                            // Add sources button if sources exist
                            if (sources.length > 0) {
                                this.addSourcesButton(messageDiv, sources);
                            }
                            return fullResponse;
                        } else if (data === '[DONE_ANSWER]') {
                            console.log('Answer streaming complete, waiting for sources');
                            // Answer is complete, paragraph content is final
                        } else if (data.startsWith('[SOURCES]') && data.endsWith('[/SOURCES]')) {
                            console.log('Received sources data');
                            const sourcesJson = data.slice(9, -10); // Remove [SOURCES] and [/SOURCES]
                            try {
                                sources = JSON.parse(sourcesJson);
                                console.log('Parsed sources:', sources);
                            } catch (e) {
                                console.error('Failed to parse sources:', e);
                            }
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

    addSourcesButton(messageDiv, sources) {
        const contentDiv = messageDiv.querySelector('.message-content');
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'sources-button-container';
        
        const sourcesButton = document.createElement('button');
        sourcesButton.className = 'sources-button';
        sourcesButton.innerHTML = '<i class="fas fa-book"></i> Sources (' + sources.length + ')';
        
        sourcesButton.addEventListener('click', () => {
            this.showSourcesModal(sources);
        });
        
        buttonContainer.appendChild(sourcesButton);
        contentDiv.appendChild(buttonContainer);
    }

    showSourcesModal(sources) {
        let modal = document.getElementById('sources-modal');
        if (!modal) {
            // Create modal if it doesn't exist
            modal = document.createElement('div');
            modal.id = 'sources-modal';
            modal.className = 'modal';
            document.body.appendChild(modal);
        }

        const sourcesList = sources.map((source, index) => `
            <div class="source-item">
                <div class="source-header">
                    <span class="source-number">${index + 1}</span>
                    <span class="source-document">${source.document_name}</span>
                    ${source.section ? `<span class="source-section">${source.section}</span>` : ''}
                </div>
                <div class="source-content">
                    ${source.content.substring(0, 300)}${source.content.length > 300 ? '...' : ''}
                </div>
                ${source.relevance_score ? `<div class="source-score">Relevance: ${(source.relevance_score * 100).toFixed(0)}%</div>` : ''}
            </div>
        `).join('');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Sources</h2>
                    <button class="modal-close" onclick="document.getElementById('sources-modal').style.display='none'">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${sourcesList}
                </div>
            </div>
        `;

        modal.style.display = 'flex';

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
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