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


def single_graph(file_name, graph_config, graph_data, labels):
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

	plt.savefig(file_name)

	return f'<img src="${file_name}">'


# Produces a graph and outputs it as a picture file in cwd, if applicable
def graph(config, task_config, graph_config, data):
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
				obs for obs in data
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
				obs for obs in data
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
			[obs[task_config["track"]] for obs in data]
				if has_track else
			[obs["the_ratio"] for obs in data]
		)
		labels.append(
			task_config["track"]
				if has_track else
			"ratio"
		)

	# Make graph

	# Construct one graph per <level of aggregation>
	if graph_config["combo"] == "split":
		return ''.join([
			single_graph("graph" + str(i), graph_config, [data], [labels[i]])
			for i, data in enumerate(graph_data)
		])

	# Construct one graph per <level of aggregation>
	elif graph_config["combo"] == "separate":
		return ''.join([
			single_graph("graph" + str(i), graph_config, [data], [labels[i]])
			for i, data in enumerate(graph_data)
		])
	
	# Combine
	elif graph_config["combo"] == "combine":
		return single_graph("graph", graph_config, graph_data, labels)


# Takes in query result JSON and creates an HTML document
def results_to_html(config, data):
	sections = '\n'.join([
		f'''
			<section>
				{
					graph(config, analysis["task"], analysis["output"]["graph"], data)
						if "graph" in analysis["output"] else
					''
				}">
				{
					table(config, analysis["task"], analysis["output"]["table"], data)
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
