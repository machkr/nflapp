from flask import Flask, render_template, json, request
app = Flask(__name__)

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
	