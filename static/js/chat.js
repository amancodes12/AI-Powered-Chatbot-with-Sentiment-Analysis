/**
 * Chat.js - Handles chatbot interaction and real-time messaging
 * Manages user input, API calls, message display, and sentiment visualization
 */

$(document).ready(function() {
    const chatContainer = $('#chatContainer');
    const chatForm = $('#chatForm');
    const messageInput = $('#messageInput');
    const sendButton = $('#sendButton');

    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.animate({
            scrollTop: chatContainer[0].scrollHeight
        }, 500);
    }

    // Get sentiment badge HTML
    function getSentimentBadge(sentiment) {
        const badges = {
            'positive': '<span class="sentiment-badge sentiment-positive"><i class="bi bi-emoji-smile me-1"></i>Positive</span>',
            'negative': '<span class="sentiment-badge sentiment-negative"><i class="bi bi-emoji-frown me-1"></i>Negative</span>',
            'neutral': '<span class="sentiment-badge sentiment-neutral"><i class="bi bi-emoji-neutral me-1"></i>Neutral</span>'
        };
        return badges[sentiment] || badges['neutral'];
    }

    // Get current time string
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    // Display user message
    function displayUserMessage(message) {
        const messageHtml = `
            <div class="user-message mb-3">
                <div class="d-flex justify-content-end">
                    <div class="message-content">
                        <div class="message-bubble user-bubble">
                            <strong>You</strong>
                            <p class="mb-1">${escapeHtml(message)}</p>
                            <small class="text-white-50">${getCurrentTime()}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatContainer.append(messageHtml);
        scrollToBottom();
    }

    // Display bot message
    function displayBotMessage(response, sentiment, sentimentScore) {
        const messageHtml = `
            <div class="bot-message mb-3">
                <div class="d-flex">
                    <div class="bot-avatar me-3">
                        <i class="bi bi-robot text-primary" style="font-size: 2rem;"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-bubble bot-bubble">
                            <strong>AI Bot</strong>
                            <p class="mb-1">${escapeHtml(response)}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-white-50">${getCurrentTime()}</small>
                                ${getSentimentBadge(sentiment)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatContainer.append(messageHtml);
        scrollToBottom();
    }

    // Display typing indicator
    function showTypingIndicator() {
        const typingHtml = `
            <div class="bot-message mb-3 typing-message">
                <div class="d-flex">
                    <div class="bot-avatar me-3">
                        <i class="bi bi-robot text-primary" style="font-size: 2rem;"></i>
                    </div>
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        chatContainer.append(typingHtml);
        scrollToBottom();
    }

    // Remove typing indicator
    function hideTypingIndicator() {
        $('.typing-message').remove();
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Display error message
    function displayError(message) {
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        chatContainer.append(errorHtml);
        scrollToBottom();
    }

    // Send message to API
    async function sendMessage(message) {
        try {
            // Disable input while processing
            messageInput.prop('disabled', true);
            sendButton.prop('disabled', true);

            // Display user message
            displayUserMessage(message);

            // Show typing indicator
            showTypingIndicator();

            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            // Hide typing indicator
            hideTypingIndicator();

            if (!response.ok) {
                throw new Error('Failed to get response from server');
            }

            const data = await response.json();

            if (data.success) {
                // Display bot response
                displayBotMessage(
                    data.response,
                    data.sentiment,
                    data.sentiment_score
                );
            } else {
                displayError(data.error || 'An error occurred');
            }

        } catch (error) {
            hideTypingIndicator();
            console.error('Error:', error);
            displayError('Failed to send message. Please try again.');
        } finally {
            // Re-enable input
            messageInput.prop('disabled', false);
            sendButton.prop('disabled', false);
            messageInput.focus();
        }
    }

    // Load chat history on page load
    async function loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history');
            const data = await response.json();

            if (data.success && data.messages.length > 0) {
                // Display last 10 messages
                data.messages.slice(-10).forEach(msg => {
                    displayUserMessage(msg.message);
                    displayBotMessage(msg.response, msg.sentiment, msg.sentiment_score);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // Handle form submission
    chatForm.on('submit', function(e) {
        e.preventDefault();

        const message = messageInput.val().trim();

        if (message === '') {
            return;
        }

        // Clear input
        messageInput.val('');

        // Send message
        sendMessage(message);
    });

    // Load chat history on page load
    loadChatHistory();

    // Focus on input field
    messageInput.focus();

    // Handle Enter key (without shift)
    messageInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.submit();
        }
    });
});