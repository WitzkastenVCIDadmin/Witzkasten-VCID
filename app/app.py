from flask import Flask, flash, redirect, url_for, render_template, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_httpauth import HTTPBasicAuth
import hashlib
import mysql.connector

app = Flask(__name__)

# Geheimen Schlüssel für Flask setzen
auth = HTTPBasicAuth()
app.secret_key = '4bUQZ0fKOO441pPSgDU67Y5WlXnmAkTB'
# Flask-Login starten
login_manager = LoginManager(app)
login_manager.login_view = 'loginseite'

# Mit Datenbank verbinden

conn = mysql.connector.connect(
    database="VCID_app",
    host="mysql-db",
    user="vcid",
    password="IchBinDeinSicheresPasswort69"
    )

# Benutzermodell definieren oder verwenden
class User(UserMixin):
    def __init__(self, user_id, username, email, name):
        self.id = user_id
        self.username = username
        self.email = email
        self.name = name


@login_manager.user_loader
def load_user(user_id):
    if not conn:
        return None


    local_cursor = conn.cursor(buffered=True)  # change here
    local_cursor.execute("SELECT id, username, email, name FROM users WHERE id = %s", (user_id,))
    user_data = local_cursor.fetchone()
    local_cursor.close()
    if user_data:
        user_id, username, email, name = user_data
        user = User(user_id, username, email, name)
        return user
    return None  # Return None, falls kein Eintrag vorhanden ist


@app.route("/")
def startseite():

    greeting = "Willkommen beim VCID Witzkasten!"
    local_cursor = conn.cursor(buffered=True)  # change here

    if current_user.is_authenticated:
        greeting = f"Hallo {current_user.username}!"

    local_cursor.execute(
        "SELECT p.titel, p.author_username, p.inhalt, p.created_at FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC")
    all_posts = local_cursor.fetchall()
    local_cursor.close()

    return render_template('home.html', posts=all_posts, greeting=greeting)

# Route für den Benutzerlogin
@app.route("/login", methods=['GET', 'POST'])
def loginseite():
    if not conn:
        return "Verbindung zur Datenbank fehlgschlagen.", 500

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

                                      
                                                                 

        local_cursor = conn.cursor(buffered=True)  # change here
        local_cursor.execute(
            "SELECT id, username, email, name FROM users WHERE username = %s AND password = MD5(%s)", (username, password))
        user_data = local_cursor.fetchone()
        local_cursor.close()

        if user_data:
            user_id, username, email, name = user_data
            user = User(user_id, username, email, name)
                                    
            login_user(user)

            flash('Erfolgreich angemeldet', 'success')
            return redirect(url_for('startseite'))

        flash('Anmeldung nicht erfolgreich. Bitte Zugangsdaten erneut prüfen.', 'danger')

    return render_template('login.html')

# Route um Einträge zu erfassen
@app.route("/entry", methods=['GET', 'POST'])
@login_required
def add_blog():

    local_cursor = conn.cursor(buffered=True)  # change here

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('inhalt')
        user_id = current_user.id

                                                                                            
        if title and content and title.strip() and content.strip():
            insert_query = "INSERT INTO posts (titel, inhalt, user_id, author_username) VALUES (%s, %s, %s, %s)"
            local_cursor.execute(insert_query, (title, content, user_id, current_user.username))
            conn.commit()

                                                          
             
                                                                        

    local_cursor.execute(
        "SELECT p.titel, p.author_username, p.inhalt, p.created_at FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC")
    all_posts = local_cursor.fetchall()
    local_cursor.close()

    return render_template('entry.html', posts=all_posts)


@app.route('/register', methods=['GET', 'POST'])
def register():

    local_cursor = conn.cursor(buffered=True)  # change here

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')


        insert_query = "INSERT INTO users (username, email, password, name) VALUES (%s, %s, MD5(%s), %s)"
        local_cursor.execute(insert_query, (username, email, password, name))
        conn.commit()
        local_cursor.close()

        flash('Erfolgreich registriert.', 'success')
        return redirect(url_for('loginseite'))

    return render_template('signup.html')

# Route für Benutzer logout
@app.route('/logout')
@login_required
def logout():
    logout_user()

    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('startseite'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@auth.verify_password
def verify_password(username, password):
    if not conn:
        return False

    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    password = md5.hexdigest()
    local_cursor = conn.cursor(buffered=True)
    local_cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    user_data = local_cursor.fetchone()
    local_cursor.close()

    if user_data is not None:
        stored_password = user_data[0]
        if password == stored_password:
            return username


@app.route('/api/user/<int:user_id>')
@auth.login_required
def get_user(user_id):
    if not conn:
        return "Verbindung zur Datenbank fehlgschlagen.", 500

    local_cursor = conn.cursor(buffered=True)
    local_cursor.execute("SELECT id, username, email, name FROM users WHERE id = %s", (user_id,))
    user_data = local_cursor.fetchone()
    local_cursor.close()

    if user_data:
        user_id, username, email, name = user_data
        response = {
            "id": user_id,
            "username": username,
            "email": email,
            "name": name
        }
        return jsonify(response), 200

    return "Benutzer nicht gefunden.", 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
