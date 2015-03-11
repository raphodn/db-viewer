'use strict';

var dbapp = angular.module("dbApp", ['angularFileUpload', 'ngActivityIndicator']);


dbapp.config(['$interpolateProvider', function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
}]);


dbapp.controller("MainController", ['$scope', 'dbFactory', '$activityIndicator',
	function($scope, dbFactory, $activityIndicator) {

	$scope.spinner = {};

	//our databases names
	$scope.databases = [];
	//object we are working on
	$scope.workingData = {};
	// tables of the database we are working on
	$scope.working_database_tables = null;
	//columns of the table of the database we are working on
	$scope.working_database_table_columns = null;
	//show final table
	$scope.showTable = false;

	
	/*
	 * initialization
	 * Get existing database files in the database folder
	 *
	*/

	dbFactory.getDatabases()
    .success(function(data) {
    	$scope.databases = data['databases'];
    })
    .error(function(error) {
    	alert(error['message']);
    	console.log(error);
    })




    /*
	 * STEP 1
	 * Select a database to work with
	 * OR
	 * upload a new database
	*/

	$scope.databaseSelected = function() {

		if ($scope.workingData.database != undefined) {
			dbFactory.getDatabaseTables($scope.workingData.database)
	    	.success(function(data) {
	    		$scope.working_database_tables = data['tables'];
	    	})
	    	.error(function(error) {
	    		alert(error['message']);
	    		console.log(error);
	    	})
	    }
	    else {}
    };


	$scope.uploadDatabase = function() {

		if ($scope.files != undefined) {
			
			$activityIndicator.startAnimating();

			dbFactory.postDatabase($scope.files[0]) //multi-upload possible
			.success(function(data) {
				$activityIndicator.stopAnimating();
				$scope.databases = data['databases'];
				$scope.files = null;
			})
			.error(function(error) {
				$activityIndicator.stopAnimating();
				$scope.files = null;
				alert(error['message']);
				console.log(error);
			});
		}
		else {}
	};


	$scope.removeFile = function() {
		$scope.files = null;
	};





	/*
	 * STEP 2
	 * Select a table to work with
	*/


	$scope.tableSelected = function() {

    	if ($scope.workingData.table != undefined) {
			dbFactory.getDatabaseTableColumns($scope.workingData.database, $scope.workingData.table)
	    	.success(function(data) {
	    		$scope.working_database_table_columns = data['columns'];
	    	})
	    	.error(function(error) {
	    		alert(error['message']);
	    		console.log(error);
	    	})
	    }
	    else {}
    };
	




    /*
	 * STEP 3
	 * Select a column to work with
	*/

	//store for each column variable the column value, value count & average age
	$scope.columnData = [];
	//the total number of values & rows for this column
	$scope.columnValuesFullLength = 0;
	$scope.columnValuesFullRows = 0;
	//the number of clipped rows if any
	$scope.columnValuesMissingRows = 0;


    $scope.columnSelected = function() {
    	$scope.showTable = false;

    	if ($scope.workingData.column != undefined) {
    		$activityIndicator.startAnimating();
			dbFactory.getColumnData($scope.workingData.database, $scope.workingData.table, $scope.workingData.column)
	    	.success(function(data) {
	    		$scope.columnValues = data['values']['index'];
	    		$scope.columnData = data['values']['data'];
	    		$scope.columnValuesFullLength = data['values_length'];
	    		$scope.columnValuesFullRows = data['rows_length'];
	    		$scope.columnValuesMissingRows = data['missing_rows'];
	    		$activityIndicator.stopAnimating();
	    		$scope.showTable = true;
	    	})
	    	.error(function(error) {
	    		$activityIndicator.stopAnimating();
	    		alert(error['message']);
	    		console.log(error);
	    	})
	    }
	    else {}
    };






	$scope.reset = function() {
		$scope.workingData = {};
		$scope.showTable = false;
	};




}]); //end of MainController