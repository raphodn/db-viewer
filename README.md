# Basic database viewer

## Goal

Display data from a database.

The user selects a column from the database. The app displays the 100 most common values of this variable (the column), in decreasing order. For each value, the row count and the average age is shown.


## The App

### Stack chosen

Backend: Python (Flask, NumPy)

Frontend: AngularJS, Bootstrap


### Dependencies

- Python
	- Flask
	- NumPy


### Functionnalities

- On launch, the app will go through the /database folder and get existing files (make sure they are legit db files)
- A user can also upload his own database via the web interface
- Query's can be made on any of the database, tables and columns available
- No internet connection needed, all needed dependencies are in the /static folder
- API-like communication between the client and the server
	- GET /database/
		- returns list of available database
	- POST /database/
		- returns list of available database
	- GET /database/<db_name>/
		- returns list of tables in the database
	- GET /database/<db_name>/<table_name>/
		- returns list of columns in the database
	- GET /database/<db_name>/<table_name>/<col_name>/
		- returns column data



## Run

- run the Python server

		python viewer.py

- Launch the browser

		http://localhost:8000

- Step 1: select an existing database, or upload a new one (will go in the folder /databases)

- Step 2: select a table from the database

- Step 3: select a column from the table

- Step 4: displays the data regarding the column