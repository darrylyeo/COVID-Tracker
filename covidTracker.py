# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# covidTracker: an analytical tool for tracking COVID spread in the US


import argparse
import json
from pymongo import MongoClient

from configConverter import *
from htmlGenerator import *


# Function that handles MongoDB auth, given auth config
def authenticate(auth):
	pass


# Function that takes data from Covid Tracking API & NY Times Dataset, 
# and puts it in MongoDB collections: covid & states
def insert_data(db, data):
	db.covid.insertMany(data)
	# db.states.insertMany(data)


def main(auth_file, config_file, input_file):
	with open(auth_file, 'r') as auth:
		authenticate(json.load(auth))

		db = MongoClient().covidTracker
		with open(input_file, 'r') as input_data:
			insert_data(db, json.load(input_data))

		with open(config_file, 'r') as config:
			result = query_from_config(db, json.load(config))
			print(result)


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

	main(args.auth, args.config, "daily.json")
