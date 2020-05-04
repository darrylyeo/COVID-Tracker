# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# covidTracker - Analytical tool for tracking COVID spread in the US


import argparse
from configConverter import *
from htmlGenerator import *


# Function that handles MongoDB auth, given auth file
def authenticate(auth_file):
	pass


# Function that takes data from Covid Tracking API & NY Times Dataset, 
# and puts it in MongoDB collections: covid & states
def insert_data():
	pass


def main(auth_file, config_file):
	authenticate(auth_file)
	insert_data()


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

	main(args.auth, args.config)
