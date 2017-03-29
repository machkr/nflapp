# nflapp
### A MySQL-backed, Flask-based web application
Ensure all of the following packages are installed by executing `pip install [PACKAGENAME]`:
```
flask
flask-MySQL
bcrypt
```

---

Execute `python app.py` to run the application back-end. Once running, view the application at `http://localhost:5000/`.

---

The application will detect any changes made in `app.py` and automatically reload. When modifying front-end files, refresh the web page to display those changes.

---

### TO-DO
#### BACKEND
- database queries

#### FRONT END
- page for running queries
  - general (omni-table) query page
  - player query page
  - coach query page
  - game query page
  - etc.
- page for viewing tables
  - single page
  - select table
  - displays formatted table
  - sorting?
  - filtering?
  
  ---
  
### ABOUT
This web application was developed using Flask, a Python-based web application framework. It features an Bootstrap-based HTML front-end that, through the Flask interface, connects to a MySQL 5.6.27 database instance hosted through Amazon's Relational Database Service (RDS). This instance features 20 gigabytes of SSD storage, 1 gigabyte of memory, and a single virtual Intel Xeon CPU. By developing the application in this way, the web application can be transported from machine to machine and - so long as the Python dependencies are installed - function flawlessly without the need for reconfiguring the database.
