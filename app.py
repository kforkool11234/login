from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
mongo = PyMongo(app)




@app.route('/')
def index():
    if 'username' in session:
        # If logged in, redirect to the profile route
        return redirect(url_for('profile'))

    # If not logged in, render the login and signup buttons
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required!'}), 400

        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('profile'))

        return jsonify({'error': 'Invalid username or password!'}), 401

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name= request.form.get('name')
        if not username or not password:
            return jsonify({'error': 'Username and password are required!'}), 400

        if mongo.db.users.find_one({'username': username}):
            return jsonify({'error': 'Username already exists!'}), 400

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': hashed_password, 'name':name})

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        # Get user data from MongoDB
        user = mongo.db.users.find_one({'username': session['username']})
        if user:
            # Render profile template and pass user data
            return render_template('profile.html', user=user)
    return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
