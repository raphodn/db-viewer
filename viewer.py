import os
import sqlite3
from os import listdir
from os.path import isfile, join
from flask import Flask, g, request, render_template, Response
from flask.json import jsonify
from werkzeug import secure_filename
from datetime import datetime
import numpy as np
import pandas as pd



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

try:
	databases_list.remove('_store_databases_here.txt')
except:
	pass

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
		# query database
		value_query = query_db(db_name, "SELECT [" + col_name + "], [age] FROM " + table_name)

		# put the query result in a pandas DataFrame
		df = pd.DataFrame(value_query, columns=list('xy'))

		# clean data (remove NULL rows)
		df_cleaned = df.dropna(how='all')

		# group by x (selected col_name)
		df_grouped = df_cleaned.groupby('x').agg({"x": np.size, "y": np.mean})

		# sort by x (selected col_name), descending
		df_sorted = df_grouped.sort('x', ascending=False)

		# total number of different values for the selected column
		length = len(df_sorted.index)

		# total number of different rows for the selected column
		total_rows = df_sorted['x'].sum()

		# if length > 100, then send to the client only the 100 top values, and calculate the number of clipped rows
		missing_rows = 0
		if (length > 100):
			#missing_data = df_sorted.iloc[100:]
			missing_rows = df_sorted.iloc[100:]['x'].sum()

		return jsonify({'values_length': length, 'rows_length': int(total_rows), 'missing_rows': int(missing_rows), 'values': df_sorted.iloc[:100].to_dict(orient='split')})



if __name__ == '__main__':
    app.run(debug=True)