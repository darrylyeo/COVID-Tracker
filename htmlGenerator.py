# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# htmlGenerator: produces HTML report containing tables & graphs for analytics


import matplotlib.pyplot as plt


def table(data, config, task_config, table_config):
	rows = ''.join([
		f'''
		<div>
			<dt>{row["date"]}</dt><dd>{row["date"]}</dd>
		</div>
		'''
		for row in data
	])

	return f'''
		<h1>{config["table"]}</h1>
		<dl>
			{rows}
		</dl>
	'''


def single_graph(graph_data, labels, graph_config, name):
	for i, data in enumerate(graph_data):
		if graph_config["type"] == "line":
			plt.plot(range(len(data)), data, label=labels[i])
		elif graph_config["type"] == "bar":
			plt.bar(range(len(data)), data, label=labels[i])
		elif graph_config["type"] == "scatter":
			plt.scatter(range(len(data)), data, label=labels[i])

	if "legend" in graph_config and graph_config["legend"] == "on":
		plt.legend()
	if "title" in graph_config:
		plt.title(graph_config["title"])

	plt.savefig(name)


# Produces a graph and outputs it as a picture file in cwd, if applicable
def graph(data, config, task_config, graph_config):
	graph_data = []
	labels = []

	has_track = list(task_config.keys())[0] == "track"

	# Create graph data & labels - separate data sources if applicable
	if (
		config["aggregation"] == "state" and
		"target" in config and config["target"] is list
	):
		for state in config["target"]:
			filtered_data = [
				obs for obs in data[i]
				if obs["state"] == state
			]
			graph_data.append(
				[obs[task_config["track"]] for obs in filtered_data]
					if has_track else
				[obs["the_ratio"] for obs in filtered_data]
			)
			labels.append(state)

	elif (
		config["aggregation"] == "county" and
		"counties" in config and config["counties"] is list
	):
		for county in config["counties"]:
			filtered_data = [
				obs for obs in data[i]
				if obs["county"] == county
			]
			graph_data.append(
				[obs[task_config["track"]] for obs in filtered_data]
					if has_track else
				[obs["the_ratio"] for obs in filtered_data]
			)
			labels.append(county)

	else:
		graph_data.append(
			[obs[task_config["track"]] for obs in data[i]]
				if has_track else
			[obs["the_ratio"] for obs in data[i]]
		)
		labels.append(
			task_config["track"]
				if has_track else
			"ratio"
		)

	# Make graph

	# Construct one graph per <level of aggregation>
	if graph_config["combo"] == "split":
		for i, data in enumerate(graph_data):
			single_graph([data], [labels[i]], graph_config, "graph" + str(i))

	# Construct one graph per <level of aggregation>
	elif graph_config["combo"] == "separate":
		for i, data in enumerate(graph_data):
			single_graph([data], [labels[i]], graph_config, "graph" + str(i))

	# Combine
	elif graph_config["combo"] == "combine":
		single_graph(graph_data, labels, graph_config, "graph")


# Takes in query result JSON, and creates an HTML doc from this?
def results_to_html(data, config):
	sections = '\n'.join([
		f'''
			<section>
				{
					graph(data, config, analysis["task"], analysis["output"]["graph"])
						if "graph" in analysis["output"] else
					''
				}
				{
					table(data, config, analysis["task"], analysis["output"]["table"])
						if "table" in analysis["output"] else
					''
				}
			</section>
		'''
		for analysis in config["analysis"]
	])

	css = '''
		* {
			margin: 0;
		}

		:root {
			font-family: sans-serif;
		}

		section {
			padding: 1rem;
		}

		dl {
			display: grid;
		}
	'''

	return f'''
		<head>
			<title>COVID Tracker</title>
			<style>{css}</style>
		</head>
		<body>
			<h1>COVID Tracker</h1>
			{sections}
		</body>
	'''
