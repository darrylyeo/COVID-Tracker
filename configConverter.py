# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# configConverter: converts input config file into a MongoDB query


import datetime
from pymongo import MongoClient


# Format date to match integer format in the dataset
# e.g. April 1, 2020 -> 20200401
def format_date(date) -> int:
	if type(date) == datetime.date:
		date = int(str(date.year) + str(date.month) + str(date.day))
	return date


# Function that takes in config file JSON, and converts it into query
def query_from_config(db, config):
	today = datetime.date.today()

	return db[config["collection"]].aggregate(
		# Filter by target
		{ "$match": {
			config["aggregation"]:
				{ "$in": config["target"] }
					if type(config["target"]) is list else
				config["target"]
		} }
			if "target" in config else
		{},

		# Filter by date range
		{ "$match": { "date": {
			"$gte": format_date(
				config["time"]["start"] if "start" in config["time"] else
				datetime.date(today.year, 1, 1) if config["time"] == "year" else
				datetime.date(today.year, today.month, 1) if config["time"] == "month" else
				today - datetime.timedelta(days=today.weekday()) if config["time"] == "week" else
				0
			),
			
			"$lte": format_date(
				config["time"]["end"] if "end" in config["time"] else
				today if config["time"] == "year" else
				today if config["time"] == "month" else
				today if config["time"] == "week" else
				30000101
			)
		} } }
			if "time" in config else
		{},

		# Project
		{ "$project": { "_id": 0, "positive": 1, "date": 1 } },
		
		# Sort
		{ "$sort": { "date": 1 } }

		# Group for analysis
		# { "$group": {
		# 	"_id": config["analysis"].
		# } }
	)
