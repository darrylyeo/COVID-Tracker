# Lab 4 - CSC 369 Spring 2020
# Darryl Yeo (dayeo@calpoly.edu) and Quinn Coleman (qcoleman@calpoly.edu)
# htmlGenerator: produces HTML report containing tables & graphs for analytics


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


def graph(data, config):
	return ''


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
