from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for authentication.
    Inherits from UserMixin to get Flask-Login functionality.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One user can have many chat messages
    messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ChatMessage(db.Model):
    """
    Chat message model to store all conversation history.
    Each message is linked to a user and contains sentiment analysis results.
    """
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)  # positive, negative, neutral
    sentiment_score = db.Column(db.Float, nullable=False)  # Polarity score from -1 to 1
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.sentiment}>'
    
    def to_dict(self):
        """Convert message to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }