from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from bcrypt import hashpw, checkpw, gensalt

mysql = MySQL()
app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zI0R378CjfTF0sljMvOgzrFXJwSlhPbH1Fe'
app.config['MYSQL_DATABASE_DB'] = 'nfldb'
app.config['MYSQL_DATABASE_HOST'] = 'nfldb.cvfrpuoosleq.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

# HTML: Home Page
@app.route('/')
def main():
	return render_template('index.html')

# HTML: Register Page
@app.route('/register')
def render_register():
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

		# Render an error page
		return render_template('error.html', error = str(exception))

# HTML: Log In Page
@app.route('/login')
def render_login():
	return render_template('login.html')

# BACKEND: Log In Method
@app.route('/login', methods = ['POST'])
def login():
	try:
		# Read posted values from user interface
		username = request.form['inputUsername']
		password = request.form['inputPassword']

		print("Username: ", username)

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

		# Render an error page
		return render_template('error.html', error = str(exception))

@app.route('/home')
def home():
	return render_template('home.html')

if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)
	
