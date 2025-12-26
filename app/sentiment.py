from textblob import TextBlob
import random

class SentimentAnalyzer:
    """
    Sentiment Analysis Engine using TextBlob.
    Analyzes text sentiment and generates appropriate responses.
    """
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Analyze the sentiment of the given text.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            tuple: (sentiment_label, polarity_score)
                - sentiment_label: 'positive', 'negative', or 'neutral'
                - polarity_score: Float between -1 (negative) and 1 (positive)
        """
        # Create TextBlob object and get polarity
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment based on polarity score
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, round(polarity, 4)
    
    @staticmethod
    def generate_response(message, sentiment):
        """
        Generate a context-aware response based on detected sentiment.
        
        Args:
            message (str): User's message
            sentiment (str): Detected sentiment ('positive', 'negative', 'neutral')
            
        Returns:
            str: Generated response
        """
        # Response templates based on sentiment
        responses = {
            'positive': [
                "That's wonderful! I'm glad you're feeling positive! 😊",
                "I love your enthusiasm! How can I help you further?",
                "Great to hear such positivity! What else can I do for you?",
                "Your positive energy is contagious! What's on your mind?",
                "That's fantastic! I'm here to keep that good mood going!"
            ],
            'negative': [
                "I'm sorry to hear that. I'm here to help you feel better. 💙",
                "I understand this might be difficult. Let's work through it together.",
                "I hear you. Sometimes things can be tough. How can I assist you?",
                "I'm here for you. Would you like to talk more about it?",
                "I appreciate you sharing that with me. Let's find a way to help."
            ],
            'neutral': [
                "I understand. How can I assist you today?",
                "Got it! What would you like to know?",
                "I'm listening. Please tell me more.",
                "Alright! What can I help you with?",
                "I see. What's your next question?"
            ]
        }
        
        # Select a random response from the appropriate sentiment category
        response_list = responses.get(sentiment, responses['neutral'])
        base_response = random.choice(response_list)
        
        # Add contextual responses for specific keywords
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['help', 'support', 'assist']):
            base_response += " I'm here to assist you with any questions or concerns you may have."
        
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            base_response = "You're very welcome! It's my pleasure to help you. 😊"
        
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            base_response = "Goodbye! Feel free to return anytime. Have a great day! 👋"
        
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            base_response = "Hello! Nice to meet you! How can I brighten your day? 😊"
        
        return base_response


class SentimentStats:
    """
    Calculate sentiment statistics for dashboard analytics.
    """
    
    @staticmethod
    def calculate_statistics(messages):
        """
        Calculate sentiment distribution from chat messages.
        
        Args:
            messages (list): List of ChatMessage objects
            
        Returns:
            dict: Statistics including counts and percentages
        """
        if not messages:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'positive_percent': 0,
                'negative_percent': 0,
                'neutral_percent': 0
            }
        
        total = len(messages)
        positive = sum(1 for msg in messages if msg.sentiment == 'positive')
        negative = sum(1 for msg in messages if msg.sentiment == 'negative')
        neutral = sum(1 for msg in messages if msg.sentiment == 'neutral')
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_percent': round((positive / total) * 100, 1),
            'negative_percent': round((negative / total) * 100, 1),
            'neutral_percent': round((neutral / total) * 100, 1)
        }