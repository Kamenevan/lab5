from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '113'  #для хранения сессий необходимых для авторизации пользователей

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Указание страницы для перенаправления при попытке доступа к защищенным страницам

# Модели и хранилище пользователей
users = {}

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

# Пример тестового пользователя
users['1'] = User(id='1', name='Test User', email='test@example.com', password=generate_password_hash('testpassword'))

# Загрузка пользователя по id
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Главная страница (защищена авторизацией)
@app.route('/')
def index():
    if current_user.is_authenticated:  # Если пользователь авторизован
        return render_template(
            'index.html',
            lab_name="Лабораторная работа 5",
            lab_description="Страница index лабораторной работы 5",
            logout_url=url_for('logout'),
            name=current_user.name
        )
    else:
        return redirect(url_for('login'))  # Перенаправление на страницу входа, если не авторизован

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Если пользователь уже авторизован, перенаправляем на главную страницу
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Поиск пользователя по email
        user = next((user for user in users.values() if user.email == email), None)
        if user is None:
            flash('Пользователь не найден!', 'error')  # Выводим ошибку, если пользователь не найден
        elif not check_password_hash(user.password, password):
            flash('Неверный пароль!', 'error')  # Выводим ошибку, если пароль неверный
        else:
            login_user(user)  # Авторизация пользователя
            return redirect(url_for('index'))  # Перенаправляем на главную страницу

    return render_template('login.html')

# Страница регистрации
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:  # Если пользователь уже авторизован, перенаправляем на главную страницу
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Проверка, если такой email уже существует
        if email in [user.email for user in users.values()]:
            flash('Пользователь с таким email уже существует!', 'error')
        else:
            # Создаем нового пользователя
            user_id = str(len(users) + 1)
            hashed_password = generate_password_hash(password)
            new_user = User(user_id, name, email, hashed_password)
            users[user_id] = new_user
            flash('Вы успешно зарегистрированы! Пожалуйста, войдите.', 'success')
            return redirect(url_for('login'))  # Перенаправляем на страницу входа

    return render_template('signup.html')

# Страница выхода (разлогинивание)
@app.route('/logout')
@login_required  # Требует авторизации для выхода
def logout():
    logout_user()  # Завершаем сессию
    return redirect(url_for('login'))  # Перенаправляем на страницу входа

if __name__ == '__main__':
    app.run(debug=True)
