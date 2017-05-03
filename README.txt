Ensure all of the following packages are installed by executing `pip install [PACKAGENAME]`:

	flask
	flask-MySQL
	bcrypt

Execute 

	python app.py

in the 'local' directory to run the application back-end locally. Once running, view the application at 'http://localhost:5000/'.

Alternatively, the application is currently being hosted on an Amazon Web Services Elastic Beanstalk Instance where it is publicly accessible from the internet at the url 'http://www.nfldb.me/'. The version currently being hosted can be found in the 'aws' folder, with previous versions located in 'aws-versions'

This web application was developed using Flask, a Python-based web application framework. It features an Bootstrap-based HTML front-end that, through the Flask interface, connects to a MySQL 5.6.27 database instance hosted through Amazon's Relational Database Service (RDS). This instance features 20 gigabytes of SSD storage, 1 gigabyte of memory, and a single virtual Intel Xeon CPU. By developing the application in this way, the web application can be transported from machine to machine and - so long as the Python dependencies are installed - function flawlessly without the need for reconfiguring the database.
