# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# htmlGenerator: produces HTML report containing tables & graphs for analytics


import matplotlib.pyplot as plt

# <dt>{row["date"]}</dt><dd>{row["date"]}</dd>
# for row in data
# <h1>{config["table"]}</h1>
def table(config, task_config, table_config, data):
	rows = ''
	if table_config["row"] == "time":
		rows = (
			''.join([
				f'''
				<div>
					<dt>{row['_id']}</dt><dd>{row["s" + task_config["track"]]}</dd>
				</div>
				'''
			for row in data])
				if (config["aggregation"] == "fiftyStates" or 
					config["aggregation"] == "usa") else
			''.join([
				f'''
				<div>
					<dt>{data[0]['dateArray'][i]}</dt><dd>{row}</dd>
				</div>
				'''
			for i, row in enumerate(data[0]['array'])])
		)
	else:
		rows = (
			''.join([
				f'''
				<div>
					<dt>{row['_id']}</dt><dd>{row["s" + task_config["track"]]}</dd>
				</div>
				'''
			for row in data])
				if (config["aggregation"] == "fiftyStates" or 
					config["aggregation"] == "usa") else
			''.join([
				f'''
				<div>
					<dt>{data[0]['dateArray'][i]}</dt><dd>{row}</dd>
				</div>
				'''
			for i, row in enumerate(data[0]['array'])])
		)
	return f'''
		<h1>{table_config.get("title", "Table")}</h1>
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

	return f'<img src="{file_name}.png">'


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
				data_point for data_point in query
				if data_point["state"] == state
				for query in data
			]
			graph_data.append(
				[data_point[task_config["track"]] for data_point in filtered_data]
					if has_track else
				[data_point["the_ratio"] for data_point in filtered_data]
			)
			labels.append(state)

	elif (
		config["aggregation"] == "county" and
		"counties" in config and config["counties"] is list
	):
		for county in config["counties"]:
			filtered_data = [
				data_point for data_point in query
				if data_point["county"] == county
				for query in data
			]
			graph_data.append(
				[data_point[task_config["track"]] for data_point in filtered_data]
					if has_track else
				[data_point["the_ratio"] for data_point in filtered_data]
			)
			labels.append(county)

	else:
		graph_data.append(
			[data_point["s" + task_config["track"]] for data_point in data]
				if config["aggregation"] == "fiftyStates" or config["aggregation"] == "usa" else
			data[0]["array"]
		)
		# TODO - consider this
        #if config["aggregation"] == "fiftyStates" or config["aggregation"] == "usa":
		
		#[data_point[task_config["track"]] for data_point in query]
			#	if has_track else
			#[data_point["the_ratio"] for data_point in query]
			#for query in data
		#)
		labels.append(
			task_config["track"]
				if has_track else
			"ratio"
		)

	# Make graph

	# Construct one graph per <level of aggregation>
	if "combo" in graph_config:
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
	else:
		return single_graph("graph", graph_config, graph_data, labels)

# table(config, analysis["task"], analysis["output"]["table"], data)

# Takes in query result JSON and creates an HTML document
def results_to_html(config, data):
	sections = '\n'.join([
		f'''
			<section>
				{
					graph(config, analysis["task"], analysis["output"]["graph"], data[i])
						if "graph" in analysis["output"] else
					''
				}
				{
					table(config, analysis["task"], analysis["output"]["table"], data[i])
						if "table" in analysis["output"] else
					''
				}
			</section>
		'''
		for i, analysis in enumerate(config["analysis"])
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
