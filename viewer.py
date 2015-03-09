import os
import sqlite3
from os import listdir
from os.path import isfile, join
from flask import Flask, g, request, render_template
from flask.json import jsonify
from werkzeug import secure_filename
from datetime import datetime
import numpy as np




#
# Constants & initialization
#

DATABASES_FOLDER = 'databases'
ALLOWED_EXTENSIONS = set(['db', 'csv', 'txt'])

app = Flask(__name__)
app.config['DATABASES_FOLDER'] = DATABASES_FOLDER
app.static_url_path = '/static'


# store the available databases
databases_list = []
# get existing databases files in the folder on first run
databases_list = [ f for f in listdir(DATABASES_FOLDER) if isfile(join(DATABASES_FOLDER,f)) ]




# 
# Database manipulation functions
# - connect to the database file
# - query the database
#

def connect_db(db_name):
	db_path = os.path.join(DATABASES_FOLDER, db_name)
	return sqlite3.connect(db_path)

def get_db(db_name):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db(db_name)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(db_name, query, args=()):
    cur = get_db(db_name).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv




#
# Database utils functions
#

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_db_list():
	return databases_list

def check_db_exists(name):
	if (len(databases_list) > 0):
		for db_name in databases_list:
			if db_name == name:
				return True
	return False




#
# Simple error message
#

def make_error(status_code, sub_code, message):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message
    })
    response.status_code = status_code
    return response





@app.route('/')
def main():
	"""
	Main app
	"""
	return render_template('db_viewer.html')



@app.route('/database/', methods=['GET', 'POST'])
def databases():
	"""
	STEP 1
    > list all databases
    > upload a new database
    """
	if request.method == 'POST':
		new_db = request.files['db']
		if new_db and allowed_file(new_db.filename):
			if check_db_exists(new_db.filename):
				return make_error(400, 1, 'database filename already exists')
			new_db.save(os.path.join(app.config['DATABASES_FOLDER'], secure_filename(new_db.filename)))
			key = len(databases_list)
			databases_list.append(new_db.filename)
			return jsonify({'databases': get_db_list()})
		else:
			return make_error(400, 1, 'extension error: only accept .db, .csv and .txt')

    # request.method == 'GET'
	return jsonify({'databases': get_db_list()})



@app.route('/database/<db_name>/', methods=['GET'])
def database_tables(db_name):
	"""
	STEP 2
    > list all tables of the selected database
    """
	if not check_db_exists(db_name):
		return make_error(400, 1, 'database does not exist')
	else:
		# return list of tables in this database
		tables_query = query_db(db_name, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
		return jsonify({'tables': tables_query[0]})



@app.route('/database/<db_name>/<table_name>/', methods=['GET'])
def database_table_columns(db_name, table_name):
	"""
	STEP 3
    > list all columns of the selected table (and database)
    """
	if not check_db_exists(db_name):
		return make_error(400, 1, 'database does not exist')
	else:
		# return list of tables in this database
		columns_query = query_db(db_name, "PRAGMA table_info(" + table_name + ")")
		return jsonify({'columns': columns_query})



@app.route('/database/<db_name>/<table_name>/<col_name>/', methods=['GET'])
def column_data(db_name, table_name, col_name):
	"""
	STEP 4
    > get & process data for the selected column
    """
	if not check_db_exists(db_name):
		return make_error(400, 1, 'database does not exist')
	else:
		print()
		# query database
		value_query = query_db(db_name, "SELECT [" + col_name + "], [age] FROM " + table_name)

		# sort query result by selected column value
		tmp = np.array(value_query)
		a = tmp[np.argsort(tmp[:, 0])]

		# iterate through result
		# - group by value
		# - count value appearance
		# - calculate age average

		# store current column value
		val = a[0][0]

		# store value appearances
		count = 0

		# store the age corresponding to each appearance
		age = []
		age_mean = None

		# 2d array, store data of each distinct column value
		b = []

		for x in range(0, len(a)):
			if (val == a[x][0]):
				count += 1
				if (a[x][1] != None):
					age.append(a[x][1])
			else:
				# we moved to a new column value
				# store data from the previous value
				age_mean = None
				if (len(age) > 0):
					age_mean = np.mean(age)
				b.append([val, int(count), age_mean])
				# re-initialize for the new value
				val = a[x][0]
				count = 1
				if (a[x][1] != None):
					age = []
					age.append(a[x][1])
				else:
					age = []

		# save last column value
		if (len(age) > 0):
			age_mean = np.mean(age)
		b.append([val, int(count), age_mean])


		# sort by value count (ascending by default)
		tmp2 = np.array(b)
		c = tmp2[np.argsort(tmp2[:, 1])]
		# reverse order (descending)
		c = c[::-1]

		# total length of array (number of distinct column values)
		c_length = len(c)

		# calculate the missing rows (if we have to clip the array at 100)
		missing_rows = 0
		if (c_length > 100):
			for x in range(100, c_length):
				missing_rows += c[x][1]

		# get only the top 100 results
		c = c[:100]

		return jsonify({'values_length': c_length, 'missing_rows': missing_rows, 'values': c.tolist()})





if __name__ == '__main__':
    app.run(debug=True)