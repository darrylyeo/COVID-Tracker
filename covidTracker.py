# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# covidTracker: an analytical tool for tracking COVID spread in the US

import argparse
import json
import pymongo as pm
from pymongo import MongoClient

from configConverter import *
from htmlGenerator import *

# Function that gives MongoDB db and handles auth, given auth config
def authenticate_db(auth):
        server = auth.get("server", "localhost")    # localhost is default
        # TODO: Handle password not given, or -1
        return MongoClient(server,
                           username=auth["username"],
                           password=auth["password"],
                           authSource=auth["authDB"],
                           authMechanism="SCRAM-SHA-1").auth["db"]


# Function that takes data from Covid Tracking API & NY Times Dataset, 
# and puts it in MongoDB collections: covid & states
def insert_data(db, data_file):
        with open(data_file, 'r') as input_data:
            if data_file == "daily.json":
                db.covid.insertMany(json.load(input_data))
            else:
                db.states.insertMany(json.load(input_data))


def main(auth_file, config_file, input_file, input_file2):
	with open(auth_file, 'r') as auth:
		db = authenticate_db(json.load(auth))
                
                # TODO: (Case 1) Check to see if collections exist, fill if not
                insert_data(db, input_file)
                insert_data(db, input_file2)
                
                with open(config_file, 'r') as config:
			# Results is a list of query results
                        # where each query result is a list of json objects
                        results = get_results(db, json.load(config))
                        for i in range(len(results)):
                                print('Query', i, 'Results:')
                                print(result[i], '\n')


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='COVID Tracker: Analytical tool for tracking COVID spread in the US'
	)
	parser.add_argument(
		'-auth',
		default='credentials.json', 
		help='file for MongoDB access (default: credentials.json)'
	)
	parser.add_argument(
		'-config',
		default='trackerConfig.json',
		help='file to convey your request (default: trackerConfig.json)'
	)
	args = parser.parse_args()

	main(args.auth, args.config, "../datasets/daily.json", "../datasets/us-counties.csv")
