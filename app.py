from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)  # 'bot', 'domain', or 'website'
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

# Create tables
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@ntandomods.com'
        )
        db.session.add(admin)
        db.session.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Products data
WHATSAPP_BOTS = [
    {
        'id': 'basic',
        'name': 'Basic Bot',
        'price': 15,
        'features': [
            'Auto-reply messages',
            'Basic commands',
            'Message scheduling',
            'Up to 100 contacts',
            '24/7 Support'
        ]
    },
    {
        'id': 'advanced',
        'name': 'Advanced Bot',
        'price': 30,
        'features': [
            'All Basic features',
            'Custom commands',
            'Media support (images, videos)',
            'Up to 500 contacts',
            'Analytics dashboard',
            'Priority support'
        ],
        'popular': True
    },
    {
        'id': 'premium',
        'name': 'Premium Bot',
        'price': 45,
        'features': [
            'All Advanced features',
            'AI-powered responses',
            'Unlimited contacts',
            'API integration',
            'Multi-device support',
            'Custom branding',
            'Dedicated support'
        ]
    }
]

DOMAINS = [
    {
        'id': 'com',
        'name': '.com',
        'price': 30,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ],
        'popular': True
    },
    {
        'id': 'net',
        'name': '.net',
        'price': 30,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ]
    },
    {
        'id': 'zw',
        'name': '.zw',
        'price': 30,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ]
    },
    {
        'id': 'id',
        'name': '.id',
        'price': 30,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ]
    },
    {
        'id': 'business',
        'name': '.business',
        'price': 30,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ]
    },
    {
        'id': 'zone-id',
        'name': '.zone.id',
        'price': 25,
        'features': [
            '1 year registration',
            'Free DNS management',
            'Free email forwarding',
            'Privacy protection',
            'Easy domain management'
        ]
    }
]

WEBSITES = [
    {
        'id': 'landing',
        'name': 'Landing Page',
        'price': 45,
        'features': [
            'Single page design',
            'Responsive layout',
            'Contact form integration',
            'SEO optimization',
            'Fast loading speed',
            '1 month free support'
        ]
    },
    {
        'id': 'business',
        'name': 'Business Website',
        'price': 50,
        'features': [
            'Up to 5 pages',
            'Custom design',
            'Mobile responsive',
            'Contact forms',
            'SEO optimization',
            'Social media integration',
            'Google Analytics',
            '3 months free support'
        ],
        'popular': True
    },
    {
        'id': 'ecommerce',
        'name': 'E-Commerce Website',
        'price': 150,
        'features': [
            'Full e-commerce functionality',
            'Product management system',
            'Shopping cart',
            'Payment gateway integration',
            'Order management',
            'Customer accounts',
            'Inventory tracking',
            'Mobile responsive',
            'SEO optimization',
            '6 months free support'
        ]
    },
    {
        'id': 'custom',
        'name': 'Custom Website',
        'price': 200,
        'features': [
            'Unlimited pages',
            'Custom functionality',
            'Database integration',
            'Admin dashboard',
            'API development',
            'Advanced features',
            'Complete customization',
            'Mobile responsive',
            'SEO optimization',
            '1 year free support'
        ]
    }
]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/whatsapp-bots')
def whatsapp_bots():
    return render_template('whatsapp-bots.html', bots=WHATSAPP_BOTS)

@app.route('/domains')
def domains():
    return render_template('domains.html', domains=DOMAINS)

@app.route('/websites')
def websites():
    return render_template('websites.html', websites=WEBSITES)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form['subject'],
            message=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/order/<product_type>/<product_id>')
def order(product_type, product_id):
    product = None
    if product_type == 'bot':
        product = next((bot for bot in WHATSAPP_BOTS if bot['id'] == product_id), None)
    elif product_type == 'domain':
        product = next((domain for domain in DOMAINS if domain['id'] == product_id), None)
    elif product_type == 'website':
        product = next((website for website in WEBSITES if website['id'] == product_id), None)
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template('order.html', product=product, product_type=product_type)

@app.route('/submit-order', methods=['POST'])
def submit_order():
    order = Order(
        customer_name=request.form['name'],
        email=request.form['email'],
        phone=request.form['phone'],
        product_type=request.form['product_type'],
        product_name=request.form['product_name'],
        price=float(request.form['price']),
        notes=request.form.get('notes', '')
    )
    db.session.add(order)
    db.session.commit()
    flash('Order submitted successfully! We will contact you soon.', 'success')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    
    stats = {
        'total_orders': Order.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'completed_orders': Order.query.filter_by(status='completed').count(),
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(read=False).count()
    }
    
    return render_template('admin/dashboard.html', orders=orders, messages=messages, stats=stats)

@app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/message/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/order/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
