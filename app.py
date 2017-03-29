from flask import Flask, render_template, json, request
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

# HTML: Sign Up
@app.route('/showsignup')
def showsignup():
	return render_template('signup.html')

# BACKEND: Sign Up Method
@app.route('/signup', methods=['POST'])
def signup():
	try:
		# Read posted values from user interface
		username = request.form['inputUsername']
		password = request.form['inputPassword']

		# Validation
		if username and password:

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
				return json.dumps({'message':'User created successfully.'})

			else: # Error

				# Print error message to console
				return json.dumps({'error':'Username already exists.'})

			# Disconnect from database
			cursor.close
			database.close

		else: # One or both of the fields were empty

			# Print error message to console
			return json.dumps({'error':'<span>Error: enter a username and password.</span>'})

	except Exception as exception:

		# Print error message to console
		return json.dumps({'error': str(exception)})

if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)
	
