# Darryl Yeo, Quinn Coleman
# dayeo@calpoly.edu, qcoleman@calpoly.edu
# Lab 4 - CSC 369 Spring 2020
# configConverter: converts input config file into a MongoDB query


import datetime
from pymongo import MongoClient


# Format date to match integer format in the dataset
# e.g. April 1, 2020 -> 20200401
def format_date(date):
	if type(date) == datetime.date:
		date = int(str(date.year) + str(date.month) + str(date.day))
	return date

# TODO: (Case 2) Both collections present, but refresh flag True in config file
def refresh_collections(db, covid_file, states_file):
	with open(covid_file, 'r') as input_data:
		db.covid.insert_many(json.load(input_data))

	with open(states_file, 'r') as input_data:
		db.states.insert_many(json.load(input_data))


# Function that given a config file, returns all query results
def get_results(db, config, covid_data_file, states_data_file):
	result = []

	# Refresh check
	if config["refresh"] == 'true':
		refresh_collections(db, covid_data_file, states_data_file)

	# Aggregation checks
	if (config["collection"] == "states" and
		(config["aggregation"] == "usa" or
		 config["aggregation"] == "fiftyStates")):
		print("Cannot aggregate over \'usa\' or \'fiftyStates\' if collection is '\states\'")
		exit(1)
	elif (config["collection"] == "covid" and
		 config["aggregation"] == "county"):
		print("Cannot aggregate over \'county\' if collection is '\covid\'")
		exit(1)

	today = datetime.date.today()

	# Perform each query as specified in Analysis attribute
	for i in range(len(config["analysis"])):
		result.append(list(query_from_config(db, config, i)))

	return result


# Function that takes in config file JSON, and converts it into query
def query_from_config(db, config, query_index):
	# Construct grouping dictionary
	if config["aggregation"] == "fiftyStates" or config["aggregation"] == "usa":
		group_dict = {
			"_id": "$date" if config["aggregation"] == "usa" else 1,
			(
				"s" + config["analysis"][query_index]["task"]["track"]
					if config["analysis"][query_index]["task"].keys()[0] == "track" else
				config["analysis"][query_index]["task"].keys()[0]
			): {
				"$sum": config["analysis"][query_index]["task"]["track"]
			}
		}
	else:
		group_dict = {
			"$group": {
				"_id": (
					config["aggregation"]
						if (config["aggregation"] == "state" and config["target"] is list) else
					"$date"
						if config["aggregation"] == "usa" else
					config["target"] # If config["aggregation"] == "state"
				),
				# Aggregate fields are hardcoded - may contain garbage if not applicable
				"array": {
					"$push": (
						config["analysis"][query_index]["task"]["track"]
							if config["analysis"][query_index]["task"].keys()[0] == "track" else
						config["analysis"][query_index]["task"].keys()[0]
					)
				},
				"dateArray": {"$push": "$date"},
			# Example - attributes can be made by:
			# json1['analysis'][0]['task'].keys()[0] + 'shmee'
			}
		}
	if config["analysis"][query_index]["task"].keys()[0] == "stats":
		# Load dictionary with items with number that can't be predetermined
		for stat in config["analysis"][query_index]["task"]["stats"]:
			group_dict["$group"]["avg" + stat] = {"$avg": stat}
			group_dict["$group"]["std" + stat] = {"$stdDevPop": stat}

	# Construct projection dictionary
	if config["analysis"][query_index]["task"].keys()[0] == "track":
		project_dict = {
			"$project": {
				"_id": 0,
				config["analysis"][query_index]["task"]["track"]: 1,
				"date": 1,
				"state": 1
			}
		}
	else:
		project_dict = {
			"$project": {
				"_id": 0,
				config["analysis"][query_index]["task"].keys()[0]:
				{"$divide": [
					config["analysis"][query_index]["task"]["ratio"]["numerator"],
					config["analysis"][query_index]["task"]["ratio"]["denominator"]
				]},
				"date": 1,
				"state": 1
			}
		}

	# Construct & return MongoDB query
	return db.config["collection"].aggregate([
		# Filter by target
		{ "$match": {
			config["aggregation"]:
				{ "$in": config["target"] }
					if type(config["target"]) is list else
				config["target"]
		} }
			if "target" in config else
		{},

		# Filter by counties
		{ "$match": {
			config["aggregation"]:
				{ "$in": config["counties"] }
					if type(config["counties"]) is list else
				config["counties"]
		} }
			if "counties" in config and config["collection"] == "states" else
		{},

		# Filter by only states
		{ "$match": {
			"state": {"$nin": ["AS", "GM", "GU", "MH", "FM", "MP", "PW", "PR", "VI"]}
		} }
			if config["aggregation"] == "fiftyStates" else
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
		project_dict
			if config["analysis"][query_index]["task"].keys()[0] != "stats" else
		{},

		# Sort
		{ "$sort": ({ "date": 1 } if
			(config["aggregation"] != "state" or config["target"] is not list) else
			{ "county": 1, "date": 1} if
			config["aggregation"] == "county" else
			{ "state": 1, "date": 1} )
		}
			if config["aggregation"] != "fiftyStates" else
		{},

		# Group for analysis
		group_dict,

		# Sort
		{ "$sort": ({ "date": 1 } if
			(config["aggregation"] != "state" or config["target"] is not list) else
			{ "county": 1, "date": 1} if
			config["aggregation"] == "county" else
			{ "state": 1, "date": 1 })
		}
			if config["aggregation"] != "fiftyStates" else
		{}

		# Optional? Project step at end for cosmetics
	])
