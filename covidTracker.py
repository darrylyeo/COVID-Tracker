# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# covidTracker: an analytical tool for tracking COVID spread in the US

import argparse, csv, json
from pymongo import MongoClient

from covidQuery import *
from htmlGenerator import *


# Function that gives MongoDB db and handles auth, given auth config
def authenticate_db(auth):
	server = auth.get("server", "localhost")	# localhost is default
	# TODO: Handle password not given, or -1
	return MongoClient(
		server,
		username=auth["username"],
		password=auth["password"],
		authSource=auth["authDB"],
		authMechanism="SCRAM-SHA-1"
	)[auth["db"]]


def json_from_csv(csv_file):
	return [
		{
			"deaths": int(obj["deaths"]),
			"county": obj["county"],
			"state": obj["state"],
			"fips": obj["fips"],
			"date": int(obj["date"].replace('-', '')),
			"cases": int(obj["cases"])
		}
		for obj in list(csv.DictReader(csv_file))
	]


# Function that takes data from Covid Tracking API & NY Times Dataset,
# and imports into MongoDB collections if necessary: covid & states
def load_data(db, collection, data_file, refresh=False):
	if refresh:
		db[collection].remove({})

	if db[collection].find().count() == 0 or refresh:
		with open(data_file, 'r') as data:
			db[collection].insert_many(
				json.load(data)
					if ".json" in data_file else
				json_from_csv(data)
			)


def main(auth_file, config_file, covid_data_file, states_data_file):
	with open(auth_file, 'r') as auth:
		db = authenticate_db(json.load(auth))

		with open(config_file, 'r') as config_json:
			config = json.load(config_json)

			# Load data if necessary
			load_data(db, "covid", covid_data_file, refresh=config["refresh"])
			load_data(db, "states", states_data_file, refresh=config["refresh"])

			# Results is a list of query results
			# where each query result is a list of json objects
			results = query_from_config(db, config)

			# Print results
			for i, result in enumerate(results):
				print('Query', i, 'Results:', result, '\n')

			# Make graphs of results if applicable
			graph(results, config)


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
