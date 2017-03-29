from flask import Flask, render_template, json, request
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zI0R378CjfTF0sljMvOgzrFXJwSlhPbH1Fe'
app.config['MYSQL_DATABASE_DB'] = 'nfldb'
app.config['MYSQL_DATABASE_HOST'] = 'nfldb.cvfrpuoosleq.us-east-1.rds.amazonaws.com:3306'
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
	# Read posted values from user interface
	username = request.form['inputUsername']
	password = request.form['inputPassword']

	# Validation
	if username and password:
		return json.dumps({'html':'<span>Creating account...</span>'})
	else:
		return json.dumps({'html':'<span>Error: enter a username and password.</span>'})

if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)
	
