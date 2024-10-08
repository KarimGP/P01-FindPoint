import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash
from Choosing_fl import choosin
from New_points_fl import delete_place, add_place
from Valoraciones_con_media_fl import value_med
from db_utils import create_users_table, get_db_connection
from user_management import User

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'es', 'ca']
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Necesario para usar sesiones

babel = Babel(app)

@babel.localeselector
def get_locale():
    return session.get('lang', 'en')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Ruta para cambiar el idioma
@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.before_request
def before_request():
    g.current_lang = session.get('lang', 'en')

# Registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        birth_year = request.form['birth_year']
        country = request.form['country']
        email = request.form['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password, birth_year, country, email) VALUES (?, ?, ?, ?, ?)', 
                (username, hashed_password, birth_year, country, email)
            )
            conn.commit()
            flash(_('You have successfully registered! Please log in.'))
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash(_('Username or email already exists!'))
            return render_template('register.html')
        finally:
            conn.close()
    
    # Cargar los países desde el archivo JSON
    try:
        with open('countries.json') as f:
            countries = json.load(f)
    except json.JSONDecodeError as e:
        flash(_("Error loading country list: {}").format(e))
        countries = []
    except FileNotFoundError:
        flash(_("Country list file not found"))
        countries = []

    return render_template('register.html', countries=countries)

# Iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            flash(_('You were successfully logged in!'))
            return redirect(url_for('index_b'))
        else:
            flash(_('Login failed. Check your credentials and try again.'))
    
    return render_template('login.html')

# Nueva ruta para el panel principal del usuario
@app.route('/index_b')
@login_required
def index_b():
    return render_template('index_b.html')

# Nueva ruta para el dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    city = session.get('selected_city')
    image_url = url_for('static', filename=f'images/{city}_main.jpg')
    if not city:
        flash(_('Please select a city first.'))
        return redirect(url_for('index_b'))
    return render_template('dashboard.html', city=city, image_url=image_url)

# Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        birth_year = request.form.get('birth_year')
        country = request.form.get('country')
        password = request.form.get('password')

        # Actualizar los datos del usuario
        conn = get_db_connection()
        if password:  # Si se proporciona una nueva contraseña, actualízala
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            conn.execute('UPDATE users SET username = ?, email = ?, birth_year = ?, country = ?, password = ? WHERE id = ?',
                         (username, email, birth_year, country, hashed_password, current_user.id))
        else:  # Si no se proporciona una nueva contraseña, no la cambies
            conn.execute('UPDATE users SET username = ?, email = ?, birth_year = ?, country = ? WHERE id = ?',
                         (username, email, birth_year, country, current_user.id))
        
        conn.commit()
        conn.close()
        
        flash(_('Your profile has been updated!'))
        return redirect(url_for('dashboard'))
    
    # Cargar los países desde el archivo JSON
    try:
        with open('countries.json') as f:
            countries = json.load(f)
    except json.JSONDecodeError as e:
        flash(_("Error loading country list: {}").format(e))
        countries = []
    except FileNotFoundError:
        flash(_("Country list file not found"))
        countries = []

    return render_template('edit_profile.html', countries=countries)

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user_id = current_user.id
        
        # Conectar a la base de datos y eliminar el usuario
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        # Cerrar la sesión después de eliminar la cuenta
        logout_user()
        flash(_('Your account has been deleted successfully.'))
        return redirect(url_for('index'))

    return render_template('delete_account.html')

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/choose_city', methods=['POST'])
def choose_city():
    city = request.form.get('city')
    if city:
        session['selected_city'] = city
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('choose_category'))
    else:
        flash(_('Please select a valid city.'))
        return redirect(url_for('index_b'))

@app.route('/choose_category', methods=['GET', 'POST'])
def choose_category():
    return render_template('choose_category.html')

@app.route('/choose_category_d', methods=['GET', 'POST'])
@login_required
def choose_category_d():
    return render_template('choose_category_d.html')

@app.route('/visit', methods=['GET', 'POST'])
def visit():
    if request.method == 'POST':
        choosen_type = request.form.get('category')
        city = session.get('selected_city')
        file_name = f'ratings_{city}.json'

        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        if choosen_type in data:
            interesting_point = choosin(choosen_type, data)
            if interesting_point:
                coordinates = data[choosen_type][interesting_point]['coordinates']
                ratings = data[choosen_type][interesting_point].get('rating', [])
                if ratings:
                    average_rating = sum(ratings) / len(ratings)
                    rating_text = _("Rate by the users: {:.2f}").format(average_rating)
                else:
                    rating_text = _("{} has not been rated yet.").format(interesting_point)
                
                return render_template('visit_result.html', point_1=_("You should visit {}").format(interesting_point.upper()),
                                       latitude=coordinates['lat'], longitude=coordinates['lng'],
                                       rating_text=rating_text)
            else:
                flash(_("No points available for the selected category: {}.").format(choosen_type))
        else:
            flash(_("Category '{}' does not exist in the selected city.").format(choosen_type))
        return redirect(url_for('choose_category'))

    return render_template('choose_category.html')

@app.route('/visit_d', methods=['GET', 'POST'])
def visit_b():
    if request.method == 'POST':
        city = session.get('selected_city')
        choosen_type = request.form.get('category')
        file_name = f'ratings_{city}.json'

        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        interesting_point = choosin(choosen_type, data)
        
        if interesting_point and choosen_type in data and interesting_point in data[choosen_type]:
            coordinates = data[choosen_type][interesting_point]['coordinates']
            ratings = data[choosen_type][interesting_point].get('rating', [])
            if ratings:
                average_rating = sum(ratings) / len(ratings)
                rating_text = _("Rate by the users: {:.2f}").format(average_rating)
            else:
                rating_text = _("{} has not been rated yet.").format(interesting_point)
            return render_template('visit_dashboard.html', point_1=_("You should visit {}").format(interesting_point.upper()),
                                   latitude=coordinates['lat'], longitude=coordinates['lng'],
                                   rating_text=rating_text)
        else:
            return redirect(url_for('dashboard'))
    
    return render_template('choose_category_d.html')

# Ruta para coger lugares que se usarán para el rate
@app.route('/get_places')
def get_places():
    category = request.args.get('category')
    city = session.get('selected_city')
    
    if not city:
        return {"places": []}  # Si no hay ciudad seleccionada, devolver una lista vacía

    file_name = f'ratings_{city}.json'
    
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
        places = list(data.get(category, {}).keys())
    else:
        places = []
    
    return {"places": places}

# Ruta para valorar un lugar
@app.route('/rate', methods=['GET', 'POST'])
@login_required
def rate():
    if request.method == 'POST':
        city = session.get('selected_city')
        category = request.form.get('category').strip().lower()
        place = request.form.get('place').strip().title()

        file_name = f'ratings_{city}.json'
        
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        if category in data and place in data[category]:
            try:
                new_rating = int(request.form.get('rating'))
                if 1 <= new_rating <= 5:
                    data[category][place]["rating"].append(new_rating)
                    average_rating = sum(data[category][place]["rating"]) / len(data[category][place]["rating"])
                    result = _('Thank you! The new average rating for {} in {} is {:.2f}.').format(place, city, average_rating)
                else:
                    result = _("Rating must be between 1 and 5.")
            except ValueError:
                result = _("Please enter a valid number for rating.")
        else:
            result = _('The place "{}" does not exist in {} under the category "{}".').format(place, city, category)

        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

        return render_template('result.html', result=result)

    return render_template('rate_place.html')

# Ruta para agregar un lugar
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        city = session.get('selected_city')
        new_point = request.form.get('new_point').strip().title()
        specify = request.form.get('category').strip().lower()
        latitude = float(request.form.get('latitude').strip())
        longitude = float(request.form.get('longitude').strip())
        
        file_name = f'ratings_{city}.json'
        
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        if specify in data:
            if new_point in data[specify]:
                flash(_('The point "{}" already exists in {}.').format(new_point, city))
                return render_template('result.html', result=_('The point "{}" already exists in {}.').format(new_point, city))
        else:
            data[specify] = {}
        
        # Add the new point with the user ID
        data[specify][new_point] = {
            "rating": [],
            "coordinates": {
                "lat": latitude,
                "lng": longitude
            },
            "user_id": current_user.id  # Store the user ID who added this point
        }
        
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
        
        flash(_('Place added successfully in {}!').format(city))
        return render_template('result.html', result=_('{} added successfully in {}!').format(new_point, city))
    
    return render_template('add_place.html')

# Ruta para eliminar un lugar
@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        city = session.get('selected_city')
        delete_point = request.form.get('delete_point').strip().title()
        specify = request.form.get('category').strip().lower()

        file_name = f'ratings_{city}.json'
        
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Check if the place exists and if the current user is the one who added it
        if specify in data and delete_point in data[specify]:
            if data[specify][delete_point].get('user_id') == current_user.id:
                del data[specify][delete_point]
                
                if not data[specify]:
                    del data[specify]
                
                result = _('The point "{}" was successfully deleted from {}.').format(delete_point, city)
            else:
                result = _('You do not have permission to delete the point "{}".').format(delete_point)
        else:
            result = _('The point "{}" does not exist in {} under the category "{}".').format(delete_point, city, specify)
        
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

        return render_template('result.html', result=result)
    
    return render_template('delete_place.html')

# Crear la tabla de usuarios al iniciar la app
if __name__ == "__main__":
    create_users_table()
    app.run(host="0.0.0.0", port=5000, debug=True)