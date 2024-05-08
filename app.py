from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask( __name__ )

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="arya bhavan",
    database="flask_users"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('userlogin.html')

@app.route('/userlogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user is an admin
        cursor.execute('SELECT * FROM tbl_admin WHERE username = %s AND password = %s', (username, password))
        admin = cursor.fetchone()

        # Check if user is a regular user
        cursor.execute('SELECT * FROM tbl_users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if admin:
            # Login successful
            return redirect(url_for('admindash'))
        elif user:
            # Login successful
            return redirect(url_for('userdash'))
        else:
            # Login failed
            return render_template('userlogin.html', error='Invalid username or password')

    return render_template('userlogin.html')

@app.route('/userdash')
def userdash():
    return render_template('userdash.html')

@app.route('/admindash')
def admindash():
    # Fetch all users from the database
    cursor.execute('SELECT id, username, email FROM tbl_users')
    users = cursor.fetchall()

    # Convert the list of tuples to a list of lists
    users = [list(user) for user in users]

    return render_template('admindash.html', users=users)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    # Delete the user with the given ID from the database
    cursor.execute('DELETE FROM tbl_users WHERE id = %s', (id,))
    db.commit()

    # Redirect to the admin dashboard
    return redirect(url_for('admindash'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        # handle signup form submission
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Insert the new user into the database
        cursor.execute('INSERT INTO tbl_users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
        db.commit()

        # Redirect to the login page
        return redirect(url_for('index'))

    return render_template('signup.html')
@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(port=8000, debug=True)