from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, ChatMessage
from app.sentiment import SentimentAnalyzer, SentimentStats
from sqlalchemy import func
from datetime import datetime, timedelta

# Create Blueprint
main = Blueprint('main', __name__)

# Initialize sentiment analyzer
analyzer = SentimentAnalyzer()


# ============================================
# AUTHENTICATION ROUTES
# ============================================

@main.route('/')
def index():
    """Landing page - redirects to login if not authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('index.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('index.html')


@main.route('/logout')
@login_required
def logout():
    """Logout current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))


# ============================================
# DASHBOARD ROUTE
# ============================================

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with analytics."""
    # Get user's chat statistics
    messages = ChatMessage.query.filter_by(user_id=current_user.id).all()
    stats = SentimentStats.calculate_statistics(messages)
    
    # Get recent messages (last 10)
    recent_messages = ChatMessage.query.filter_by(user_id=current_user.id)\
        .order_by(ChatMessage.timestamp.desc())\
        .limit(10)\
        .all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_messages=recent_messages)


# ============================================
# CHATBOT ROUTES
# ============================================

@main.route('/chat')
@login_required
def chat():
    """Chatbot interface page."""
    return render_template('chat.html')


@main.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """
    API endpoint for chatbot conversation.
    Receives message, analyzes sentiment, generates response, and stores in database.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Analyze sentiment
        sentiment, score = analyzer.analyze_sentiment(user_message)
        
        # Generate response based on sentiment
        bot_response = analyzer.generate_response(user_message, sentiment)
        
        # Save to database
        chat_message = ChatMessage(
            user_id=current_user.id,
            message=user_message,
            response=bot_response,
            sentiment=sentiment,
            sentiment_score=score
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'sentiment': sentiment,
            'sentiment_score': score,
            'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred processing your message'}), 500


@main.route('/api/chat/history')
@login_required
def chat_history():
    """API endpoint to get chat history for current user."""
    try:
        messages = ChatMessage.query.filter_by(user_id=current_user.id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(50)\
            .all()
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in reversed(messages)]
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to load chat history'}), 500


# ============================================
# ANALYTICS API ROUTES
# ============================================

@main.route('/api/analytics/sentiment')
@login_required
def analytics_sentiment():
    """API endpoint for sentiment distribution data."""
    try:
        messages = ChatMessage.query.filter_by(user_id=current_user.id).all()
        stats = SentimentStats.calculate_statistics(messages)
        
        return jsonify({
            'success': True,
            'data': {
                'labels': ['Positive', 'Negative', 'Neutral'],
                'values': [stats['positive'], stats['negative'], stats['neutral']],
                'percentages': [
                    stats['positive_percent'],
                    stats['negative_percent'],
                    stats['neutral_percent']
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to load analytics'}), 500


@main.route('/api/analytics/timeline')
@login_required
def analytics_timeline():
    """API endpoint for sentiment over time (last 7 days)."""
    try:
        # Get date 7 days ago
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Query messages from last 7 days grouped by date
        messages = ChatMessage.query.filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.timestamp >= week_ago
        ).all()
        
        # Group by date
        daily_sentiment = {}
        for msg in messages:
            date_key = msg.timestamp.strftime('%Y-%m-%d')
            if date_key not in daily_sentiment:
                daily_sentiment[date_key] = {'positive': 0, 'negative': 0, 'neutral': 0}
            daily_sentiment[date_key][msg.sentiment] += 1
        
        # Create arrays for last 7 days
        dates = []
        positive_counts = []
        negative_counts = []
        neutral_counts = []
        
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            dates.append(date)
            sentiment_data = daily_sentiment.get(date, {'positive': 0, 'negative': 0, 'neutral': 0})
            positive_counts.append(sentiment_data['positive'])
            negative_counts.append(sentiment_data['negative'])
            neutral_counts.append(sentiment_data['neutral'])
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'positive': positive_counts,
                'negative': negative_counts,
                'neutral': neutral_counts
            }
        })
    
    except Exception as e:
        return jsonify({'error': 'Failed to load timeline data'}), 500