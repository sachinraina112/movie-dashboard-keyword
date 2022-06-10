from moviedashboard import app

import json, plotly
from flask import render_template, request
from scripts.GetDataForPlots import return_figures

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():


	# Parse the POST request countries list
	if (request.method == 'POST') and request.form:
		keyword_dict = request.form
		keyword = keyword_dict.to_dict(flat=False)['keywords'][0]
		keyword = keyword.replace(" ","")
		figures = return_figures(keyword)
	
	# GET request returns all countries for initial page load
	else:
		figures = return_figures('hero')


	# plot ids for the html id tag
	ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

	# Convert the plotly figures to JSON for javascript in html template
	figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('index.html', ids=ids,
		figuresJSON=figuresJSON)