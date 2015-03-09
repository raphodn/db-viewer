'use strict';

dbapp.factory('dbFactory', ['$http', function($http) {
        
	var dbFactory = {};



	var dbUrlBase = '/database/';


	dbFactory.getDatabases = function () {
    	return $http({
	      	url: dbUrlBase,
	      	method: 'GET'
    	});
	};

	dbFactory.postDatabase = function(db_file) {

	   	return $http({
			url: dbUrlBase,
			method: 'POST',
			headers: {'Content-Type': undefined},
			transformRequest: function (data) {
				var fd = new FormData();
				fd.append("db", db_file);
   				return fd;
   			}
   		});
	};




	dbFactory.getDatabaseTables = function (db_name) {
    	return $http({
	      	url: dbUrlBase + db_name + '/',
	      	method: 'GET'
    	});
	};





	dbFactory.getDatabaseTableColumns = function (db_name, table_name) {
    	return $http({
	      	url: dbUrlBase + db_name + '/' + table_name + '/',
	      	method: 'GET'
    	});
	};


	
	dbFactory.getColumnData = function (db_name, table_name, col_name) {
    	return $http({
	      	url: dbUrlBase + db_name + '/' + table_name + '/' + col_name + '/',
	      	method: 'GET'
    	});
	};




    return dbFactory;

}]);//end of dbFactory