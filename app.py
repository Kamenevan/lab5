from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '113'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модели и хранилище пользователей
users = {}

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Главная страница
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', name=current_user.name)
    else:
        return redirect(url_for('login'))

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = next((user for user in users.values() if user.email == email), None)
        if user is None:
            flash('Пользователь не найден!', 'error')
        elif not check_password_hash(user.password, password):
            flash('Неверный пароль!', 'error')
        else:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

# Страница регистрации
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if email in [user.email for user in users.values()]:
            flash('Пользователь с таким email уже существует!', 'error')
        else:
            user_id = str(len(users) + 1)
            hashed_password = generate_password_hash(password)
            new_user = User(user_id, name, email, hashed_password)
            users[user_id] = new_user
            flash('Вы успешно зарегистрированы! Пожалуйста, войдите.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

#Страница выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
