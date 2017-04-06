from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from bcrypt import hashpw, checkpw, gensalt
from binascii import hexlify
from os import urandom

mysql = MySQL() # Initialize database
app = Flask(__name__) # Shorten application object
app.secret_key = hexlify(urandom(32)) # Generate session key

# MySQL Configuration
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zI0R378CjfTF0sljMvOgzrFXJwSlhPbH1Fe'
app.config['MYSQL_DATABASE_DB'] = 'nfldb'
app.config['MYSQL_DATABASE_HOST'] = 'nfldb.cvfrpuoosleq.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

# HTML: Home Page
@app.route('/')
def main():

	# Render home page
	return render_template('index.html')

# HTML: Register Page
@app.route('/register')
def render_register():

	# Render user registration page
	return render_template('register.html')

# BACKEND: Register Method
@app.route('/register', methods = ['POST'])
def register():
	try:
		# Read posted values from user interface
		username = request.form['inputUsername']
		password = request.form['inputPassword']

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Generate password hash
		hash = hashpw(password.encode('utf-8'), gensalt())

		# Create user using stored procedure
		cursor.callproc('create_user', (username, hash))

		# Retrieve data from procedure
		data = cursor.fetchone()

		if data[0] == 'TRUE': # Success
			
			# Commit changes to database
			database.commit()

			# Print success message to console
			return render_template('home.html')

		else: # Error

			# Render register page again, with error
			return render_template('register.html', error = "Username already exists.")

		# Disconnect from database
		cursor.close
		database.close

	except Exception as exception:

		# Store error message in session cookie
		session['error'] = str(exception)

		# Redirect to error page
		return redirect('/error')

# HTML: Log In Page
@app.route('/login')
def render_login():

	# Render the login page
	return render_template('login.html')

# BACKEND: Log In Method
@app.route('/login', methods = ['POST'])
def login():
	try:
		# Read posted values from user interface
		username = request.form['inputUsername']
		password = request.form['inputPassword']

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Check if user exists
		cursor.callproc('check_user', (username,))

		# Retrieve data from procedure
		data = cursor.fetchone()

		if data[0] == 'TRUE': # User exists
			
			# Get corresponding password hash
			cursor.callproc('get_password', (username,))

			# Retrieve data from procedure
			data = cursor.fetchone()

			# Check password against password hash
			if checkpw(password.encode('utf-8'), data[0]):

				# Set current session user
				session['user'] = username

				# Redirect user to homepage
				return redirect('/home')

			else: # Password hashes don't match

				# Render log in page again, display error
				return render_template('login.html', error = 'Incorrect password.')

		elif data[0] == 'FALSE': # User does not exist

			# Render log in page again, display error
			return render_template('login.html', error = 'User does not exist.')

		# Disconnect from database
		cursor.close
		database.close

	except Exception as exception:

		# Store error message in session cookie
		session['error'] = str(exception)

		# Redirect to error page
		return redirect('/error')

# HTML: User Home Page
@app.route('/home')
def render_home():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Render the user home page
		return render_template('home.html')

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Error Page
@app.route('/error')
def render_error():

	# Retrieve error messages stored in session cookie
	message = session['error']

	# Render an error page with the error message
	return render_template('error.html', error = message)

# BACKEND: Log Out Method
@app.route('/logout')
def logout():

	# Remove stored username from cookie
	session.pop('user', None)

	# Redirect to home page
	return redirect('/')

# HTML: Coaches Page
@app.route('/database/coaches')
def render_coaches():

	# Render the coaches page
	return render_template('coaches.html')

if __name__ == "__main__":
	app.run(debug = True, use_reloader = True)
