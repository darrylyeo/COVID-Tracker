# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# covidQuery: converts input config file into a MongoDB query


import datetime, json
from pymongo import MongoClient


# Format date to match integer format in the dataset
# e.g. April 1, 2020 -> 20200401
def format_date(date):
	if type(date) == datetime.date:
		date = int(str(date.year) + str(date.month) + str(date.day))
	return date


# Function that given a config file, returns all query results
def query_from_config(db, config):
	# Aggregation checks
	if (
		config["collection"] == "states" and
		(config["aggregation"] == "usa" or config["aggregation"] == "fiftyStates")
	):
		print("Cannot aggregate over 'usa' or 'fiftyStates' if collection is 'states'")
		exit(1)

	if config["collection"] == "covid" and config["aggregation"] == "county":
		print("Cannot aggregate over 'county' if collection is 'covid'")
		exit(1)


	# Perform each query as specified in Analysis attribute
	return [
		list(query_task(db, config, task["task"]))
		for task in config["analysis"]
	]


# Function that takes in config file JSON, and converts it into query
def query_task(db, config, task):
	today = datetime.date.today()

	# Construct grouping dictionary
	if config["aggregation"] == "fiftyStates" or config["aggregation"] == "usa":
		group_stage = {
			"_id": "$date" if config["aggregation"] == "usa" else 1,
			(
				"s" + task["track"]
					if "track" in task else
				list(task.values())[0]
			): {
				"$sum": task["track"]
			}
		}
	else:
		group_stage = {
			"_id":
				config["aggregation"]
					if config["aggregation"] == "state" and config["target"] is list else
				"$date"
					if config["aggregation"] == "usa" else
				config["target"], # If config["aggregation"] == "state"
			# Aggregate fields are hardcoded - may contain garbage if not applicable
			"array": {
				"$push":
					task["track"]
						if "track" in task else
					list(task.values())[0]
			},
			"dateArray": {"$push": "$date"},
			# Example - attributes can be made by:
			# json1['analysis'][0]['task'].keys()[0] + 'shmee'
		}
	if "stats" in task:
		# Load dictionary with items with number that can't be predetermined
		group_stage.update({
			"avg" + stat: {"$avg": stat}
			for stat in task["stats"]
		})
		group_stage.update({
			"std" + stat: {"$stdDevPop": stat}
			for stat in task["stats"]
		})

	# Construct projection dictionary
	project_stage = {
		"_id": 0,
		"date": 1,
		"state": 1
	}
	task_key = list(task.keys())[0]
	project_stage.update({
		task["track"]: 1
	} if "track" in task else {
		"the_ratio": {
			"$divide": [
				"$" + task[task_key]["numerator"],
				"$" + task[task_key]["denominator"]
			]
		}
	} if "ratio" in task else {	# Stats case
		item: 1 for item in task[task_key]
	})
	if config["aggregation"] == "county":
		project_stage["county"] = 1

	# Initialize empty pipeline - begin constructing query
	pipeline = []

	# Filter by target
	if "target" in config:
		pipeline.append({
			"$match": {
				config["aggregation"]:
					{ "$in": config["target"] }
						if type(config["target"]) is list else
					config["target"]
			}
		})

	# Filter by counties
	if "counties" in config and config["collection"] == "states":
		pipeline.append({
			"$match": {
				config["aggregation"]:
					{ "$in": config["counties"] }
						if type(config["counties"]) is list else
					config["counties"]
			}
		})

	# Filter by only states
	if config["aggregation"] == "fiftyStates":
		pipeline.append({
			"$match": {
				"state": { "$nin": ["AS", "GM", "GU", "MH", "FM", "MP", "PW", "PR", "VI"] }
			}
		})

	# Filter by date range
	if "time" in config:
		pipeline.append({ "$match": { "date": {
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
		} } })

	# Project
	if "stats" not in task:
		pipeline.append({ "$project": project_stage })

	# Sort
	if config["aggregation"] != "fiftyStates":
		pipeline.append({
			"$sort":
				{ "county": 1, "date": 1 }
					if config["aggregation"] == "county" and config["target"] is list else
				{ "state": 1, "date": 1 }
					if config["aggregation"] == "state" and config["target"] is list else
				{ "date": 1 }
		})

	# Group for analysis
	pipeline.append({ "$group": group_stage })

	# Sort
	if config["aggregation"] != "fiftyStates":
		pipeline.append({
			"$sort":
				{ "county": 1, "date": 1 }
					if config["aggregation"] == "county" and config["target"] is list else
				{ "state": 1, "date": 1 }
					if config["aggregation"] == "state" and config["target"] is list else
				{ "date": 1 }
		})

	# Optional? Project step at end for cosmetics

	# Construct & return MongoDB query
	return db[config["collection"]].aggregate(pipeline)

