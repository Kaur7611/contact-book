from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///contactbook.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a strong secret in production

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        new_contact = Contact(name=name, phone=phone, user_id=current_user.id)
        db.session.add(new_contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        flash("You don't have permission to edit this contact.", "danger")
        return redirect(url_for('index'))
    if request.method == 'POST':
        contact.name = request.form['name']
        contact.phone = request.form['phone']
        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>')
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        flash("You don't have permission to delete this contact.", "danger")
        return redirect(url_for('index'))
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('index'))

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
