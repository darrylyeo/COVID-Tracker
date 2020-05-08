# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# covidTracker: an analytical tool for tracking COVID spread in the US

import argparse
import json
import csv
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
                           authMechanism="SCRAM-SHA-1")[auth["db"]]


def prep_csv(csv_fp):
        data = list(csv.DictReader(csv_fp))
        data = [{u"deaths": int(obj["deaths"]), 
                 u"county": unicode(obj["county"], "utf-8"),
                 u"state": unicode(obj["state"], "utf-8"),
                 u"fips": unicode(obj["fips"], "utf-8"),
                 u"date": int(obj["date"].replace('-', '')),
                 u"cases": int(obj["cases"])} for obj in data]
        return data


# Function that takes data from Covid Tracking API & NY Times Dataset, 
# and puts it in MongoDB collections if necessary: covid & states
def data_fill_check(db, covid_data_file, states_data_file):
        if db.covid.find().count() == 0:
                with open(covid_data_file, 'r') as input_data:
                        db.covid.insert_many(json.load(input_data))
   
        if db.states.find().count() == 0:
                with open(states_data_file, 'r') as input_data:
                        db.states.insert_many(prep_csv(input_data))


def main(auth_file, config_file, covid_data_file, states_data_file):
	with open(auth_file, 'r') as auth:
		db = authenticate_db(json.load(auth))
                
                # Check to see if collections exist, fill if not
                data_fill_check(db, covid_data_file, states_data_file)
                
                with open(config_file, 'r') as config:
			# Results is a list of query results
                        # where each query result is a list of json objects
                        results = get_results(db, json.load(config), covid_data_file, states_data_file)
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
