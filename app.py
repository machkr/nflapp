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

			# Log in user
			cursor.callproc('login', (username,))

			# Commit changes to database
			database.commit()

			# Set current session user
			session['user'] = username

			# Set current session admin status
			session['admin'] = False

			# Redirect user to home page
			return redirect('/home')

		else: # Error

			# Render register page again, with error
			return render_template('register.html', 
				error = 'Username already exists.')

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

				# Log in user
				cursor.callproc('login', (username,))

				# Retrieve data from procedure
				data = cursor.fetchone()

				# Set current session user
				session['user'] = username

				print("Login (Admin):", data[0])

				if data[0] == 1: # User is administrator

					# Set current session admin status
					session['admin'] = True

					# Redirect user to homepage
					return redirect('/admin')

				elif data[0] == 0: # User is not an administrator

					# Set current session admin status
					session['admin'] = False

					# Redirect user to homepage
					return redirect('/home')

				else: # User is neither admin nor regular

					# Render log in page again, display error
					return render_template('login.html', 
						error = 'Something went wrong.')

			else: # Password hashes don't match

				# Render log in page again, display error
				return render_template('login.html', 
					error = 'Incorrect password.')

		elif data[0] == 'FALSE': # User does not exist

			# Render log in page again, display error
			return render_template('login.html', 
				error = 'User does not exist.')

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

		if session.get('admin'): # User is administrator

			# Render the admin home page
			return render_template('home.html', 
				home = '/admin')

		else: # User is not administrator

			# Render the user home page
			return render_template('home.html', 
				home = '/home')

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
	return render_template('error.html', 
		error = message)

# BACKEND: Log Out Method
@app.route('/logout')
def logout():

	# Remove stored username from cookie
	session.pop('user', None)
	session.pop('admin', False)

	# Redirect to home page
	return redirect('/')

# HTML: Coaches Page
@app.route('/database/coaches')
def render_coaches():

	# Connect to the database
	database = mysql.connect()
	cursor = database.cursor()

	# Query the database for headers
	cursor.callproc('get_headers', ('coaches',))

	headers = cursor.fetchall()

	# Query database -- will be stored procedure eventually
	cursor.execute("SELECT * FROM coaches LIMIT 100")

	# Retrieve data from procedure
	data = cursor.fetchall()

	if session.get('admin'): # User is administrator

		# Render the coaches page as admin
		return render_template('coaches.html', 
			home = '/admin', headers = headers, data = data)

	else: # User is not administrator

		# Render the coaches page as user
		return render_template('coaches.html', 
			home = '/home', headers = headers, data = data)

# BACKEND: Query Coaches Method
@app.route('/database/coaches', methods = ['POST'])
def query_coaches():
	try:
		# Read posted values from user interface
		if request.form['limit']: # Limit checkbox checked
			entries = request.form['entries']


	except Exception as exception:

		# Store error message in session cookie
		session['error'] = str(exception)

		# Redirect to error page
		return redirect('/error')

# HTML: Players Page
@app.route('/database/players')
def render_players():

	if session.get('admin'): # User is administrator

		# Render the admin home page
		return render_template('players.html', 
			home = '/admin')

	else: # User is not administrator

		# Render the user home page
		return render_template('players.html', 
			home = '/home')
	
# HTML: Games Page
@app.route('/database/games')
def render_games():

	if session.get('admin'): # User is administrator

		# Render the games page as admin
		return render_template('games.html', 
			home = '/admin')

	else: # User is not administrator

		# Render the games page as user
		return render_template('games.html', 
			home = '/home')

# HTML: Super Bowls Page
@app.route('/database/superbowls')
def render_superbowls():

	if session.get('admin'): # User is administrator

		# Render the super bowls page as admin
		return render_template('superbowls.html', 
			home = '/admin')

	else: # User is not administrator

		# Render the super bowls page as user
		return render_template('superbowls.html', 
			home = '/home')

# HTML: Franchises Page
@app.route('/database/franchises')
def render_franchises():

	if session.get('admin'): # User is administrator

		# Render the franchises page as admin
		return render_template('franchises.html', 
			home = '/admin')

	else: # User is not administrator

		# Render the franchises page as user
		return render_template('franchises.html', 
			home = '/home')

# HTML: Teams Page
@app.route('/database/teams')
def render_teams():

	if session.get('admin'): # User is administrator

		# Render the teams page as admin
		return render_template('teams.html', 
			home = '/admin')

	else: # User is not administrator

		# Render the teams page as user
		return render_template('teams.html', 
			home = '/home')

# HTML: Admin Page
@app.route('/admin')
def render_admin():

	# If the user's admin status is 'True'
	if session.get('admin'): # User is admin

		# Render the admin page
		return render_template('admin.html')

	else:

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

if __name__ == "__main__":
	app.run(debug = True, use_reloader = True)
