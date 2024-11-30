# Импортируем необходимые модули из Flask и Flask-Login
from flask import Flask, render_template, redirect, url_for, request, flash  # Flask и его функции для работы с маршрутами, шаблонами, запросами и выводом сообщений
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  # Для авторизации и управления пользователями
from werkzeug.security import generate_password_hash, check_password_hash  # Для работы с безопасным хэшированием паролей

# Создаем объект Flask для нашего приложения
app = Flask(__name__)
app.secret_key = '113'  # Устанавливаем секретный ключ для сессий и защиты от подделки данных (например, для авторизации)

# Настраиваем LoginManager для управления авторизацией
login_manager = LoginManager(app)  # Привязываем менеджер авторизации к нашему приложению
login_manager.login_view = 'login'  # Указываем маршрут, куда перенаправлять неавторизованных пользователей

# Словарь для хранения пользователей
users = {}  # Пустой словарь, который будет использоваться как база данных пользователей

# Класс пользователя, представляющий каждого зарегистрированного пользователя
class User(UserMixin):  # Наследуемся от UserMixin, чтобы интегрировать стандартные функции Flask-Login
    def __init__(self, id, name, email, password):
        self.id = id  # Уникальный идентификатор пользователя
        self.name = name  # Имя пользователя
        self.email = email  # Электронная почта пользователя
        self.password = password  # Хэшированный пароль пользователя

# Добавляем тестового пользователя в словарь users
users['1'] = User(id='1', name='Test User', email='test@example.com', password=generate_password_hash('testpassword'))  # Генерация хэшированного пароля

# Функция для загрузки пользователя по его id
@login_manager.user_loader
def load_user(user_id):  # Flask-Login вызывает эту функцию при авторизации
    return users.get(user_id)  # Возвращаем пользователя из словаря users по id

# Главная страница приложения
@app.route('/')
def index():
    if current_user.is_authenticated:  # Проверяем, авторизован ли пользователь
        return render_template(
            'index.html',  # Отдаем HTML-шаблон с информацией
            lab_name="Лабораторная работа 5",  # Название лабораторной работы
            lab_description="Страница index лабораторной работы 5",  # Описание
            logout_url=url_for('logout'),  # URL для выхода
            name=current_user.name  # Имя текущего пользователя
        )
    else:
        return redirect(url_for('login'))  # Перенаправляем на страницу входа, если пользователь не авторизован

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Если пользователь уже вошел, отправляем его на главную
        return redirect(url_for('index'))

    if request.method == 'POST':  # Если запрос POST (форма отправлена)
        email = request.form['email']  # Получаем email из формы
        password = request.form['password']  # Получаем пароль из формы

        # Поиск пользователя в словаре users по email
        user = next((user for user in users.values() if user.email == email), None)
        if user is None:
            flash('Пользователь не найден!', 'error')  # Сообщение об ошибке, если пользователь не найден
        elif not check_password_hash(user.password, password):  # Проверяем пароль
            flash('Неверный пароль!', 'error')  # Сообщение об ошибке, если пароль неверный
        else:
            login_user(user)  # Авторизуем пользователя
            return redirect(url_for('index'))  # Перенаправляем на главную страницу

    return render_template('login.html')  # Отображаем страницу входа, если метод GET

# Страница регистрации
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:  # Если пользователь уже вошел, отправляем его на главную
        return redirect(url_for('index'))

    if request.method == 'POST':  # Если запрос POST (форма отправлена)
        name = request.form['name']  # Получаем имя из формы
        email = request.form['email']  # Получаем email из формы
        password = request.form['password']  # Получаем пароль из формы

        # Проверяем, существует ли пользователь с таким email
        if email in [user.email for user in users.values()]:
            flash('Пользователь с таким email уже существует!', 'error')  # Выводим ошибку
        else:
            # Создаем нового пользователя и добавляем его в словарь users
            user_id = str(len(users) + 1)  # Уникальный id для нового пользователя
            hashed_password = generate_password_hash(password)  # Хэшируем пароль
            new_user = User(user_id, name, email, hashed_password)  # Создаем объект пользователя
            users[user_id] = new_user  # Добавляем пользователя в словарь
            flash('Вы успешно зарегистрированы! Пожалуйста, войдите.', 'success')  # Сообщение об успехе
            return redirect(url_for('login'))  # Перенаправляем на страницу входа

    return render_template('signup.html')  # Отображаем страницу регистрации, если метод GET

# Страница выхода
@app.route('/logout')
@login_required  # Ограничиваем доступ только для авторизованных пользователей
def logout():
    logout_user()  # Завершаем сессию текущего пользователя
    return redirect(url_for('login'))  # Перенаправляем на страницу входа

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)  # Включаем режим отладки для удобства разработки
