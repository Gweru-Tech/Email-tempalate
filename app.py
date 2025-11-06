from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folders if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'music'), exist_ok=True)

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
    product_type = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
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

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_path = db.Column(db.String(200))
    background_music_path = db.Column(db.String(200))
    music_enabled = db.Column(db.Boolean, default=False)
    site_name = db.Column(db.String(100), default='Ntando Mods')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='fa-star')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_position = db.Column(db.Integer, default=0)

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
    
    # Create default site settings if not exists
    if not SiteSettings.query.first():
        settings = SiteSettings()
        db.session.add(settings)
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
        'price': 150,
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
        'price': 350,
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
        'price': 650,
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
        'price': 1000,
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

HOSTING = [
    {
        'id': 'monthly',
        'name': 'Monthly Hosting',
        'price': 5,
        'period': '/month',
        'features': [
            '10 GB SSD Storage',
            'Unlimited Bandwidth',
            '1 Website',
            'Free SSL Certificate',
            'Daily Backups',
            'Email Accounts',
            '99.9% Uptime Guarantee',
            '24/7 Support'
        ]
    },
    {
        'id': 'quarterly',
        'name': '3-Month Hosting',
        'price': 15,
        'period': '/3 months',
        'features': [
            '20 GB SSD Storage',
            'Unlimited Bandwidth',
            '3 Websites',
            'Free SSL Certificate',
            'Daily Backups',
            'Unlimited Email Accounts',
            '99.9% Uptime Guarantee',
            'Priority Support',
            'Save 10%'
        ],
        'popular': True
    },
    {
        'id': 'biannual',
        'name': '6-Month Hosting',
        'price': 25,
        'period': '/6 months',
        'features': [
            '50 GB SSD Storage',
            'Unlimited Bandwidth',
            'Unlimited Websites',
            'Free SSL Certificate',
            'Daily Backups',
            'Unlimited Email Accounts',
            'Free Domain (.com)',
            '99.9% Uptime Guarantee',
            'Priority Support',
            'Save 20%'
        ]
    },
    {
        'id': 'annual',
        'name': 'Annual Hosting',
        'price': 45,
        'period': '/year',
        'features': [
            '100 GB SSD Storage',
            'Unlimited Bandwidth',
            'Unlimited Websites',
            'Free SSL Certificate',
            'Daily Backups',
            'Unlimited Email Accounts',
            'Free Domain (.com)',
            'Free Website Migration',
            '99.9% Uptime Guarantee',
            'Dedicated Support',
            'Save 30%'
        ]
    }
]

PREMIUM_APPS = [
    {
        'id': 'netflix',
        'name': 'Netflix Premium Mod',
        'price': 10,
        'icon': 'fab fa-netflix',
        'color': '#E50914',
        'features': [
            'Unlimited streaming',
            '4K Ultra HD quality',
            'Download content offline',
            'No ads',
            'Multiple profiles',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ],
        'popular': True
    },
    {
        'id': 'spotify',
        'name': 'Spotify Premium Mod',
        'price': 10,
        'icon': 'fab fa-spotify',
        'color': '#1DB954',
        'features': [
            'Unlimited skips',
            'No ads',
            'Offline mode',
            'High quality audio',
            'Access to all songs',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'photoshop',
        'name': 'Adobe Photoshop Mod',
        'price': 10,
        'icon': 'fas fa-image',
        'color': '#31A8FF',
        'features': [
            'Full version unlocked',
            'All premium features',
            'Professional photo editing',
            'Advanced filters',
            'Cloud integration',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation guide'
        ]
    },
    {
        'id': 'youtube-premium',
        'name': 'YouTube Premium Mod',
        'price': 10,
        'icon': 'fab fa-youtube',
        'color': '#FF0000',
        'features': [
            'Ad-free videos',
            'Background playback',
            'Download videos',
            'YouTube Music Premium',
            'Picture-in-picture',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'canva-pro',
        'name': 'Canva Pro Mod',
        'price': 10,
        'icon': 'fas fa-palette',
        'color': '#00C4CC',
        'features': [
            'Premium templates',
            'Brand kit access',
            'Background remover',
            'Unlimited storage',
            'Team collaboration',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'microsoft-office',
        'name': 'Microsoft Office 365 Mod',
        'price': 10,
        'icon': 'fab fa-microsoft',
        'color': '#D83B01',
        'features': [
            'Word, Excel, PowerPoint',
            'OneDrive storage',
            'Outlook email',
            'Teams access',
            'All premium features',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation guide'
        ]
    },
    {
        'id': 'lightroom',
        'name': 'Adobe Lightroom Mod',
        'price': 10,
        'icon': 'fas fa-camera-retro',
        'color': '#31A8FF',
        'features': [
            'Professional photo editing',
            'Premium presets',
            'Cloud sync',
            'Advanced filters',
            'RAW editing',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'duolingo-plus',
        'name': 'Duolingo Plus Mod',
        'price': 10,
        'icon': 'fas fa-language',
        'color': '#58CC02',
        'features': [
            'Ad-free learning',
            'Unlimited hearts',
            'Offline lessons',
            'Progress tracking',
            'All languages unlocked',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'picsart',
        'name': 'PicsArt Gold Mod',
        'price': 10,
        'icon': 'fas fa-paint-brush',
        'color': '#F84A81',
        'features': [
            'Premium filters',
            'Ad-free experience',
            'Advanced editing tools',
            'Unlimited stickers',
            'HD export',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'winrar',
        'name': 'WinRAR Premium Mod',
        'price': 10,
        'icon': 'fas fa-file-archive',
        'color': '#0066CC',
        'features': [
            'Unlimited compression',
            'Password protection',
            'Multi-format support',
            'Fast extraction',
            'No trial limitations',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation guide'
        ]
    },
    {
        'id': 'zoom-pro',
        'name': 'Zoom Pro Mod',
        'price': 10,
        'icon': 'fas fa-video',
        'color': '#2D8CFF',
        'features': [
            'Unlimited meeting time',
            'Screen sharing',
            'Recording features',
            'Virtual backgrounds',
            'Up to 300 participants',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    },
    {
        'id': 'grammarly',
        'name': 'Grammarly Premium Mod',
        'price': 10,
        'icon': 'fas fa-spell-check',
        'color': '#15C39A',
        'features': [
            'Advanced grammar checks',
            'Plagiarism detector',
            'Style suggestions',
            'Vocabulary enhancement',
            'Tone detector',
            'Modded by Ntando Mods',
            'Lifetime updates',
            'Installation support'
        ]
    }
]

# Context processor to inject site settings and custom features
@app.context_processor
def inject_site_settings():
    settings = SiteSettings.query.first()
    custom_features = CustomFeature.query.filter_by(active=True).order_by(CustomFeature.order_position).all()
    return dict(site_settings=settings, custom_features=custom_features)

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

@app.route('/hosting')
def hosting():
    return render_template('hosting.html', hosting_plans=HOSTING)

@app.route('/premium-apps')
def premium_apps():
    return render_template('premium_apps.html', apps=PREMIUM_APPS)

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
    elif product_type == 'hosting':
        product = next((host for host in HOSTING if host['id'] == product_id), None)
    elif product_type == 'app':
        product = next((app for app in PREMIUM_APPS if app['id'] == product_id), None)
    
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

@app.route('/admin/order/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/message/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = SiteSettings.query.first()
    
    if request.method == 'POST':
        settings.site_name = request.form.get('site_name', 'Ntando Mods')
        settings.music_enabled = 'music_enabled' in request.form
        
        # Handle logo upload
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo and logo.filename:
                filename = secure_filename(logo.filename)
                logo_path = os.path.join('uploads', 'logos', filename)
                logo.save(os.path.join('static', logo_path))
                settings.logo_path = logo_path
        
        # Handle music upload
        if 'background_music' in request.files:
            music = request.files['background_music']
            if music and music.filename:
                filename = secure_filename(music.filename)
                music_path = os.path.join('uploads', 'music', filename)
                music.save(os.path.join('static', music_path))
                settings.background_music_path = music_path
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', settings=settings)

if __name__ == '__main__':
    app.run(debug=True)
