# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# htmlGenerator: produces HTML report containing tables & graphs for analytics

import matplotlib.pyplot as plt


def table(data, config):
	rows = ''.join([
		f'''
		<div>
			<dt>{row['date']}</dt><dd>{row['date']}</dd>
		</div>
		'''
		for row in data
	])

	return f'''
		<h1>{config['table']}</h1>
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
		else:	# Scatter plot case
			plt.scatter(range(len(data)), data, label=labels[i])
		
	if "legend" in graph_config and graph_config["legend"] == "on":
		plt.legend()
	if "title" in graph_config:
		plt.title(graph_config["title"])
	plt.savefig(name)


# Produces a graph and outputs it as a picture file in cwd, if applicable
def graph(data, config):
	for i, query in enumerate(config["analysis"]):
		if "graph" in query["output"]:
			graph_config = query["output"]["graph"]
			graph_data, labels = [], []
			
			# Create graph data & labels - separate data sources if applicable
			if (config["aggregation"] == "state" and "target" in config and 
				config["target"] is list):
				for state in config["target"]:
					filtered_data = [obs for obs in data[i] 
									 if obs["state"] == state]
					graph_data.append(
						[obs[query["task"]["track"]] for obs in filtered_data]
							if list(query["task"].keys())[0] == "track" else
						[obs["the_ratio"] for obs in filtered_data]
					)	
					labels.append(state)

			elif (config["aggregation"] == "county" and "counties" in config and 
				  config["counties"] is list):
				for county in config["counties"]:
					filtered_data = [obs for obs in data[i] 
									 if obs["county"] == county]
					graph_data.append(
						[obs[query["task"]["track"]] for obs in filtered_data]
							if list(query["task"].keys())[0] == "track" else
						[obs["the_ratio"] for obs in filtered_data]
					)	
					labels.append(county)

			else:
				graph_data.append(
					[obs[query["task"]["track"]] for obs in data[i]]
						if list(query["task"].keys())[0] == "track" else
					[obs["the_ratio"] for obs in data[i]]
				)
				labels.append(query["task"]["track"]
					if list(query["task"].keys())[0] == "track" else
					"ratio")	
			
			# Make graph
			if graph_config["combo"] == "split":
				# Construct one graph per <level of aggregation>
				for i, data in enumerate(graph_data):
					single_graph([data], [labels[i]], graph_config, "graph" + str(i))

			elif graph_config["combo"] == "separate":
				# Construct one graph per <level of aggregation>
				for i, data in enumerate(graph_data):
					single_graph([data], [labels[i]], graph_config, "graph" + str(i))

			else:	# Combine	
				single_graph(graph_data, labels, graph_config, "graph")


# Takes in query result JSON, and creates an HTML doc from this?
def results_to_html(data, config):
	sections = '\n'.join([
		f'''
			<section>
				{
					graph(data, output['graph'])
						if 'graph' in output else
					table(data, output['table'])
						if 'table' in output else
					''
				}
			</section>
		'''
		for output in [analysis['output']]
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
			<title>COVID Tracker</title>
			{sections}
		</body>
	'''
