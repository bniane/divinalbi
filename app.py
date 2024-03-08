from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Code, Progression, UserCode, Account
from config import config
import time
hashed_password = generate_password_hash('your_plain_password')

import os
import uuid
import hashlib
import yaml
import MySQLdb.cursors
import re
import random
import string

app = Flask(__name__)
migrate = Migrate(app, db)

# Configuration de la base de données:
db_config = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db_config['mysql_host']
app.config['MYSQL_USER'] = db_config['mysql_user']
app.config['MYSQL_PASSWORD'] = db_config['mysql_password']
app.config['MYSQL_DB'] = db_config['mysql_db']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = config['database']['uri']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + db_config['mysql_user'] + ':' + db_config['mysql_password'] + '@' + db_config['mysql_host'] + '/' + db_config['mysql_db']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

mysql = MySQL(app)

app.secret_key = 'bibi'


# Fonction d'insertion dans la bd:
def insert_user_progress(etape):
    if 'username' in session:  # Supposons que le nom d'utilisateur est stocké dans la session
        username = session['username']
        new_user = Progression(username=username, etape=etape)
        db.session.add(new_user)
        db.session.commit()
    else:
        print("Faut te connecter bg")

### route page accueil:
@app.route('/')
def home():
    print(time.time())
    return render_template('home.html')

### route inscription:
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Hacher le mot de passe avant de l'insérer dans la base de données
        hashed_password = generate_password_hash(password)
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, hashed_password, email))
        mysql.connection.commit()
        cursor.close()
        
        session['loggedin'] = True
        session['username'] = username
        return redirect(url_for('step_one'))
    return render_template('register.html')




### route connection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Incrémentation de la bd:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # Assurez-vous que l'index est correct pour le mot de passe haché dans votre base de données
        if account and check_password_hash(account[1], password):  
            session['loggedin'] = True
            session['user_id'] = account[3]  # Assurez-vous que l'index est correct pour l'ID de l'utilisateur
            session['username'] = account[0]  # Assurez-vous que l'index est correct pour le username

            return redirect(url_for('step_one'))
        else:
            return 'Identifiant ou mot de passe incorrect! Fais un effort.'
    
    return render_template('login.html')


### route pour les règles du jeu:
@app.route('/regles', methods=['GET', 'POST'])
def regles():
    print(time.time())
    return render_template('regles.html')

###route indice:
@app.route('/indice')
def  indice():
    return render_template('indice.html')

### route pour les cadeaux à gagner:
@app.route('/gains', methods=['GET', 'POST'])
def gains():
    return render_template('gains.html')

# Route pour entrer le code de la premiere etape:
@app.route('/step_one', methods=['GET', 'POST'])
def step_one():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Accédez aux données du formulaire uniquement si la méthode est POST
        user_code = request.form.get('user_code')  # Utilisez .get() pour éviter les erreurs si la clé n'existe pas
        correct_code = "1664" 

        if user_code == correct_code:
            insert_user_progress(1)  # Insérer la progression dans la bd
            # Si le code est correct, redirigez vers une nouvelle page ou affichez un succès
            return render_template('success_one.html') 
        else:
            # Si le code est incorrect, redirigez l'utilisateur vers step_one avec un message d'erreur
            flash('Code incorrect, veuillez réessayer.')  
            return redirect(url_for('step_one'))
    else:
        # Pour les requêtes GET, affichez simplement le formulaire ou la page
        return render_template('step_one.html')  
    
###route premier indice:
@app.route('/indice1')
def  indice1():
    return render_template('indice1.html')

###La route pour entrer le code de la deuxiéme etape:
@app.route('/step_two', methods=['GET', 'POST'])
def step_two():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Accédez aux données du formulaire uniquement si la méthode est POST
        user_code = request.form.get('user_code')  
        correct_code = "1820" 
        if user_code == correct_code:
            insert_user_progress(2)  
            # Si le code est correct, redirigez vers une nouvelle page ou affichez un succès
            return render_template('success_two.html') 
        else:
            # Si le code est incorrect, redirigez l'utilisateur vers step_one avec un message d'erreur
            flash('Code incorrect, veuillez réessayer.')  
            return redirect(url_for('step_two'))
    else:
        # Pour les requêtes GET, affichez simplement le formulaire ou la page
        return render_template('step_two.html') 
    
###route deuxiéme indice:
@app.route('/indice2')
def  indice2():
    return render_template('indice2.html')

###Route pour entrer le code de la troisiéme etape:
@app.route('/step_three', methods=['GET', 'POST'])
def step_three():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Traitement de la signification du code soumis par l'utilisateur
        meaning = request.form.get('meaning')
        if meaning == "allo'byrinthe":
            # Si le code est correct, enregistrez la progression, affichez un message de succès, etc.
            flash('Félicitations ! Code correct.')
            insert_user_progress(3)  # Assurez-vous que cette fonction fait ce que vous attendez
            return render_template('success_three.html')
        else:
            # Si le code est incorrect, informez l'utilisateur
            flash('Code incorrect. Veuillez réessayer.')
            # Vous pouvez choisir de rediriger l'utilisateur vers la même page pour réessayer
            return redirect(url_for('step_three'))
    
    return render_template('step_three.html')

###route
@app.route('/success_three', methods=['GET', 'POST'])
def success_three():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Accédez aux données du formulaire uniquement si la méthode est POST
        user_code = request.form.get('user_code')  # Utilisez .get() pour éviter les erreurs si la clé n'existe pas
        correct_code = "j'adore les fraises" 
        if user_code == correct_code:
            insert_user_progress(4)
            return render_template('step_five.html')

        else:
            # Si le code est incorrect, redirigez l'utilisateur vers step_one avec un message d'erreur
            flash('Code incorrect, veuillez réessayer.')  
            return redirect(url_for('success_three'))
    else:
        # Pour les requêtes GET, affichez simplement le formulaire ou la page
        return render_template('step_five.html') 
    
###route 4e étape
@app.route('/step_four')
def  step_four():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))
    return render_template('step_four.html')

###route indice:
@app.route('/indice4')
def  indice4():
    return render_template('indice4.html')

###route etape 5
@app.route('/step_five', methods=['GET', 'POST'])
def step_five():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Accédez aux données du formulaire uniquement si la méthode est POST
        user_code = request.form.get('user_code')  # Utilisez .get() pour éviter les erreurs si la clé n'existe pas
        correct_code = "bde divin'albi" 
        if user_code == correct_code:
            insert_user_progress(5)
            return render_template('step_four.html')

        else:
            # Si le code est incorrect, redirigez l'utilisateur vers step_one avec un message d'erreur
            flash('Code incorrect, veuillez réessayer.')  
            return redirect(url_for('step_five'))
    else:
        # Pour les requêtes GET, affichez simplement le formulaire ou la page
        return render_template('step_five.html') 

###route :
@app.route('/success_five')
def  success_five():
    return render_template('success_five.html')

###route etape 6
@app.route('/step_six', methods=['GET', 'POST'])
def step_six():
    if 'loggedin' not in session:
        # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Accédez aux données du formulaire uniquement si la méthode est POST
        user_code = request.form.get('user_code')  # Utilisez .get() pour éviter les erreurs si la clé n'existe pas
        correct_code = "sncf" 
        if user_code == correct_code:
            insert_user_progress(6)
            
            return redirect(url_for('generate_code'))

        else:
            # Si le code est incorrect, redirigez l'utilisateur vers step_one avec un message d'erreur
            flash('Code incorrect, veuillez réessayer.')  
            return redirect(url_for('step_six'))
    else:
        # Pour les requêtes GET, affichez simplement le formulaire ou la page
        return render_template('step_six.html') 

###route dernier indice   
@app.route('/indice5')
def  indice5():
    return render_template('indice5.html')

###Route pour générer un code et l'afficher
@app.route('/generate_code')
def generate_code():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    
    if not username:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    # Vérifiez si l'utilisateur a déjà un code
    cursor.execute('SELECT code FROM code WHERE username = %s', (username,))
    user_code = cursor.fetchone()
    
    if user_code:
        code = user_code[0]
    else:
        unique = False
        while not unique:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            cursor.execute('SELECT EXISTS(SELECT 1 FROM code WHERE code = %s)', (code,))
            unique = cursor.fetchone()[0] == 0
        print("Username to insert:", username)

        # Insérez le nouveau code avec le username dans la table code
        cursor.execute('INSERT INTO code (code, username) VALUES (%s, %s)', (code, username))
        mysql.connection.commit()

    return render_template('success_six.html', code=code)


if __name__ == '__main__':
    app.secret_key = 'bibi'
    with app.app_context():
        db.create_all()
    app.run(debug=True)

