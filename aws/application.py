from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from bcrypt import hashpw, checkpw, gensalt
from binascii import hexlify
from os import urandom, environ

mysql = MySQL() # Initialize database
application = Flask(__name__) # Shorten application object
application.secret_key = hexlify(urandom(32)) # Generate session key

# MySQL Configuration
application.config['MYSQL_DATABASE_USER'] = 'admin'
application.config['MYSQL_DATABASE_PASSWORD'] = 'zI0R378CjfTF0sljMvOgzrFXJwSlhPbH1Fe'
application.config['MYSQL_DATABASE_DB'] = 'nfldb'
application.config['MYSQL_DATABASE_HOST'] = 'nfldb.cvfrpuoosleq.us-east-1.rds.amazonaws.com'
mysql.init_app(application)

# HTML: Home Page
@application.route('/')
def main():

	# Render home page
	return render_template('index.html')

# HTML: Register Page
@application.route('/register')
def render_register():

	# Render user registration page
	return render_template('register.html')

# BACKEND: Register Method
@application.route('/register', methods = ['POST'])
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
@application.route('/login')
def render_login():

	# Render the login page
	return render_template('login.html')

# BACKEND: Log In Method
@application.route('/login', methods = ['POST'])
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

				# Commit changes to database
				database.commit()

				# Set current session user
				session['user'] = username

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
@application.route('/home')
def render_home():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		if session.get('admin'): # User is administrator

			# Render the admin home page
			return render_template('home.html', 
				home = '/admin', username = session['user'])

		else: # User is not administrator

			# Render the user home page
			return render_template('home.html', 
				home = '/home', username = session['user'])

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Error Page
@application.route('/error')
def render_error():

	# Retrieve error messages stored in session cookie
	message = session['error']

	# Render an error page with the error message
	return render_template('error.html', 
		error = message)

# BACKEND: Log Out Method
@application.route('/logout')
def logout():

	# Remove stored username from cookie
	session.pop('user', None)

	# Remove stored admin status from cookie
	session.pop('admin', False)

	# Redirect to home page
	return redirect('/')

# HTML: Coaches Page
@application.route('/database/coaches')
def render_coaches():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('coaches',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('coaches',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the coaches page as admin
			return render_template('coaches.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the coaches page as user
			return render_template('coaches.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Coaches Method
@application.route('/database/coaches', methods = ['POST'])
def query_coaches():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('coaches',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('coaches', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close


			if session.get('admin'): # User is administrator

				# Render the coaches page as admin
				return render_template('coaches.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the coaches page as user
				return render_template('coaches.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the coaches page without data
			return render_template('coaches.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Players Page
@application.route('/database/players')
def render_players():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('players',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('players',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the admin home page
			return render_template('players.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the user home page
			return render_template('players.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Players Method
@application.route('/database/players', methods = ['POST'])
def query_players():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('players',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('players', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close

			if session.get('admin'): # User is administrator

				# Render the players page as admin
				return render_template('players.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the players page as user
				return render_template('players.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the players page without data
			return render_template('players.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Games Page
@application.route('/database/games')
def render_games():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('games',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('games',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the games page as admin
			return render_template('games.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the games page as user
			return render_template('games.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Games Method
@application.route('/database/games', methods = ['POST'])
def query_games():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('games',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('games', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close

			if session.get('admin'): # User is administrator

				# Render the games page as admin
				return render_template('games.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the games page as user
				return render_template('games.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the games page without data
			return render_template('games.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Super Bowls Page
@application.route('/database/superbowls')
def render_superbowls():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('superbowls',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('superbowls',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the super bowls page as admin
			return render_template('superbowls.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the super bowls page as user
			return render_template('superbowls.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Super Bowls Method
@application.route('/database/superbowls', methods = ['POST'])
def query_superbowls():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('superbowls',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('superbowls', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close

			if session.get('admin'): # User is administrator

				# Render the superbowls page as admin
				return render_template('superbowls.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the superbowls page as user
				return render_template('superbowls.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the superbowls page without data
			return render_template('superbowls.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Franchises Page
@application.route('/database/franchises')
def render_franchises():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('franchises',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('franchises',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the franchises page as admin
			return render_template('franchises.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the franchises page as user
			return render_template('franchises.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Franchises Method
@application.route('/database/franchises', methods = ['POST'])
def query_franchises():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('franchises',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('franchises', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close

			if session.get('admin'): # User is administrator

				# Render the franchises page as admin
				return render_template('franchises.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the franchises page as user
				return render_template('franchises.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the franchises page without data
			return render_template('franchises.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Teams Page
@application.route('/database/teams')
def render_teams():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_headers', ('teams',))

		# Retrieve data from procedure
		headers = cursor.fetchall()

		# Query database
		cursor.callproc('preview_table', ('teams',))

		# Retrieve data from procedure
		data = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		if session.get('admin'): # User is administrator

			# Render the teams page as admin
			return render_template('teams.html', 
				home = '/admin', headers = headers, data = data)

		else: # User is not administrator

			# Render the teams page as user
			return render_template('teams.html', 
				home = '/home', headers = headers, data = data)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Teams Method
@application.route('/database/teams', methods = ['POST'])
def query_teams():

	# If there is a username stored in the session coookie
	if session.get('user'): # User logged in

		try:
			# Read posted values from user interface
			attribute = request.form['query_attribute'] # Query attribute
			operator = request.form['query_operator'] # Query operator
			input = request.form['query_input'] # Query input	
			sort_attribute = request.form['sort_attribute'] # Sorting attribute
			sort_type = request.form['sort_type'] # Sorting type
			entries = request.form['limit'] # Limit entries value
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			# Query the database for headers
			cursor.callproc('get_headers', ('teams',))

			# Retrieve data from procedure
			headers = cursor.fetchall()

			# Query database
			cursor.callproc('query', 
				('teams', attribute, operator, input, sort_attribute, sort_type, entries))

			# Retrieve data from procedure
			data = cursor.fetchall()

			# Disconnect from database
			cursor.close
			database.close

			if session.get('admin'): # User is administrator

				# Render the teams page as admin
				return render_template('teams.html', 
					home = '/admin', headers = headers, data = data)

			else: # User is not administrator

				# Render the teams page as user
				return render_template('teams.html', 
					home = '/home', headers = headers, data = data)

		except Exception as exception:

			# Render the teams page without data
			return render_template('teams.html', 
				headers = headers)

	else: # User not logged in

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Admin Page
@application.route('/admin')
def render_admin():

	# If the user's admin status is 'True'
	if session.get('admin'): # User is admin

		# Render the admin page
		return render_template('admin.html', username = session['user'])

	else:

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# HTML: Config Page
@application.route('/admin/config')
def render_config():

	# If the user's admin status is 'True'
	if session.get('admin'): # User is admin

		# Connect to the database
		database = mysql.connect()
		cursor = database.cursor()

		# Query the database for headers
		cursor.callproc('get_users')

		# Retrieve data from procedure
		users = cursor.fetchall()

		# Query database
		cursor.callproc('get_admins')

		# Retrieve data from procedure
		admins = cursor.fetchall()

		# Query database
		cursor.callproc('get_all_usernames')

		# Retrieve data from procedure
		usernames = cursor.fetchall()

		# Disconnect from database
		cursor.close
		database.close

		# Render the admin page
		return render_template('config.html', 
			users = users, admins = admins, usernames = usernames)

	else:

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

# BACKEND: Query Config Page
@application.route('/admin/config', methods = ['POST'])
def query_config():

	# If the user's admin status is 'True'
	if session.get('admin'): # User is admin

		try:
			# Read posted values from user interface
			username = request.form['query_username'] # Query username
			action = request.form['query_action'] # Query action
			
			# Connect to the database
			database = mysql.connect()
			cursor = database.cursor()

			if action == 'promote':

				# Promote the user
				cursor.callproc('set_user', (username, 1,))

			if action == 'demote':

				# Promote the user
				cursor.callproc('set_user', (username, 0,))

			if action == 'delete':

				# Delete the user
				cursor.callproc('delete_user', (username,))

			# Commit changes to database
			database.commit()

			# Disconnect from database
			cursor.close
			database.close

			# Redirect to config page
			return redirect('/admin/config')

		except Exception as exception:

			# Render the teams page without data
			return render_template('teams.html', 
				headers = headers)

	else:

		# Store error message in session cookie
		session['error'] = 'Unauthorized Access'

		# Redirect to error page
		return redirect('/error')

if __name__ == "__main__":
	application.run()
