from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="374145Orugi$",
    database="simple_site"
)

@app.route('/')
def home():
    if 'user_id' in session:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
        return render_template('index.html', user=user)
    return render_template('index.html', user=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        try:
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
                db.commit()
        except mysql.connector.Error as err:
            return f"Error: {err}"
        
        return redirect(url_for('login'))
    
    return render_template('index.html', user=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        
        return 'Login failed'
    
    return render_template('index.html', user=None)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/tasks')
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT points FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
    
    return render_template('tasks.html', points=user['points'])

@app.route('/complete_task', methods=['POST'])
def complete_task():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not logged in"), 403
    
    data = request.get_json()
    task_id = data.get('task_id')
    
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO tasks (user_id, task_id) VALUES (%s, %s)", (session['user_id'], task_id))
            cursor.execute("UPDATE users SET points = points + 10 WHERE id = %s", (session['user_id'],))
            db.commit()
            cursor.execute("SELECT points FROM users WHERE id = %s", (session['user_id'],))
            points = cursor.fetchone()[0]
    except mysql.connector.Error as err:
        return jsonify(success=False, message=f"Error: {err}")
    
    return jsonify(success=True, points=points)

if __name__ == '__main__':
    app.run(debug=True)
