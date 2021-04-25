import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

########### Define your variables
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_table
import json
from dash_extensions import Download
from dash_extensions.snippets import send_file
import os
import base64
import math

cols_to_use = ['Hormone', 'Gene', 'SVM score', 'SVM probability']
df_gene = pd.read_csv('results/protein_coding_genes_novel_predictions_threshold.csv', usecols = cols_to_use)
df_lncrna = pd.read_csv('results/lncRNA_novel_predictions_threshold.csv', usecols = cols_to_use)
with open('./hgv1_hormone_src_tgt_genes.json') as json_file:
	hormone_src_tgt_genes = json.load(json_file)

with open('./source_target_tissue.json') as st_json_file:
	src_tgt_tissue = json.load(st_json_file)
	
hormone_lst = ['aldosterone', 'angiotensin', 'calcitonin', 'cholecystokinin', 'cortisol', 'erythropoietin', 'estrogen', 'glucagon', 'insulin', 'leptin', 'melatonin', 'peptide yy', 'progesterone', 'prolactin', 'prostaglandins', 'relaxin', 'somatostatin', 'testosterone', 'adrenocorticotropin', 'thyrotropin-releasing hormone', 'gonadotropin-releasing hormone', 'vascular endothelial growth factor', 'norepinephrine', 'adiponectin', 'a-type natriuretic peptide', 'adrenaline/epinephrine', 'estradiol/oestradiol', 'somatotrophin/growth hormone', 'parathyroid hormone/parathyrin', 'serotonin/5-hydroxytryptamine', 'vitamin d/calciferol', 'follicle-stimulating hormone/follitropin', 'antidiuretic hormone/vasopressin', 'thymosin']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
trunc = lambda x: math.trunc(10000 * x) / 10000;


df_new = df_gene[df_gene['Hormone'].str.match('aldosterone')]
print(len(df_new))
to_load = 50
tablebreak = 8

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
max_rows=10
image_filename = 'HGV1.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

biomedbed_image_filename = 'bioembedlogo.png'
encoded_bioemned_image = base64.b64encode(open(biomedbed_image_filename, 'rb').read())

server = app.server

app.layout = html.Div([

	html.Div(children = [

		html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width': '220px', 'display': 'block'}), className = 'left'),
		html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_bioemned_image.decode()), style={'width': '220px', 'display': 'block'}), className='right'),
		html.Div(children = "Predicting cross-tissue hormone-gene relations using balanced word embeddings.", className='center'),

		], className = 'banner'),

	dcc.Tabs([
		
	dcc.Tab(label="Explore HGv1 dataset", children =[
		html.H4("HGv1 Dataset"),
		html.Div([
			html.Div([
				html.Div([dcc.Dropdown(id="hormone-input",
										   options=[
											   {'label': hor, 'value': hor} for hor in list(hormone_src_tgt_genes.keys())
										   ],
										   placeholder="Select a hormone",
										  )  
							 ]),


				html.H3(id='hormone'),
				html.H3("Source Tissues"),
				html.Div(id='src_tissue'),
				html.H3("Source Genes"),
				html.Div(id='src_table'),
				html.H3("Target Tissues"),
				html.Div(id='tar_tissue'),
				html.H3("Target Genes"),
				html.Div(id='tar_table')
			], style={'width': '49%', 'display': 'inline-block'}),
			# html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width': '220px', 'display': 'block', 'marginLeft': 'auto', 'marginRight': 'auto'}), style={'width': '49%', 'display': 'inline-block', 'verticalAlign':'top'}),
		])
	]),
		
		dcc.Tab(label="Browse predictions", children = [
			html.Div([
				html.Div(children=[
					# html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_bioemned_image.decode()), style={'width':'220px', 'display': 'block','marginLeft': 'auto', 'marginRight': 'auto', 'paddingTop':'10px'})),
					html.H4(children='BioEmbedS Predictions'),
					html.Div([dcc.Dropdown(id="my-input",
										   options=[
											   {'label': hor, 'value': hor} for hor in hormone_lst
										   ],
										   placeholder="Select a hormone",
										  )  
							 ]),
					html.Div([dcc.RadioItems(id="type",
											 options=[
												 {'label': 'Show associated genes (predictions discussed in BioEmbedS paper)', 'value': 'gene'},
												 {'label': 'Show associated lncRNAs (preliminary/exploratory predictions)', 'value': 'lncrna'},
											 ],
											 value='gene'
											) 
							 ]),
					
					html.Br(),
					html.Div(
							  
							  dash_table.DataTable(
									  id='my-table',
									  columns=[
												{'name': name, 'id': name} for name in df_new.columns
											],
									  data=[{'Hormone': ' ', 'Gene': ' ', 'SVM score': ' ', 'SVM probability': ' '}],
									  sort_action="native",
									  sort_mode="multi",
									  export_format = 'csv',
									  page_size= 10)
													
					  ),
					html.Div(id = 'count'),
				]),
			]),
		]),
		
		dcc.Tab(label="Downloads", children = [
			html.Br(),
			#html.A('Download all hormone-gene predictions', id='hg-link',href="./bioembeds_nonsmote_pos_preds.csv")
			html.A(html.Button('Link to access all hormone-gene predictions file', className = 'downloads'), href='https://drive.google.com/file/d/1mwYZgFU5jP7Kocslwt_QjgKfkKgvMQkL/view?usp=sharing'), html.Br(),  html.Br(),
			html.A(html.Button('Link to access all predictions for protein coding genes', className = 'downloads'), href='https://drive.google.com/file/d/1DGqWXcGLWc9bntlWtl0NB3aJ7WLGb3qi/view?usp=sharing'), html.Br(),  html.Br(),
			html.Div([html.Button("Download top predictions for protein coding genes", id="pc-btn", className = 'downloads'), Download(id="pc-download")]), html.Br(),
			html.Div([html.Button("Download predictions for lncrna genes", id="lncrna-btn", className = 'downloads'), Download(id="lncrna-download")]), html.Br(),
			html.Div([html.Button("Download the HGv1 Gene Dataset", id="hgv1-gene-btn", className = 'downloads'), Download(id="hgv1-gene-download")]), html.Br(),
			html.Div([html.Button("Download the HGv1 Tissue Dataset", id="hgv1-tissue-btn", className = 'downloads'), Download(id="hgv1-tissue-download")]), html.Br(),
		]),

		dcc.Tab(label="About", children = [
			html.Div(children=[
					html.H4(children='Predicting cross-tissue hormone-gene relations using balanced word embeddings.'),
					html.P(children='    - Aditya Jadhav, Tarun Kumar, Mohit Raghavendra, Tamizhini Loganathan and Manikandan Narayanan.'),
					html.A('Code on Github', href="https://github.com/BIRDSgroup/BioEmbedS")
			])
		])
	])
])


@app.callback(
	Output(component_id = 'hormone', component_property='children'), 
	[Input(component_id='hormone-input', component_property='value')]
)
def display_src_tissue(val1):
		return "Hormone Selected - " + val1


@app.callback(
	Output(component_id = 'src_tissue', component_property='children'), 
	[Input(component_id='hormone-input', component_property='value')]
)
def display_src_tissue(val1):
	if val1 != None:
		sourcegenes = list(src_tgt_tissue[str(val1)]['source'])
		targetgenes = list(src_tgt_tissue[str(val1)]['target'])

		if(len(sourcegenes)%tablebreak != 0):
			while(len(sourcegenes)%tablebreak != 0):
				sourcegenes.append(' ')

		return html.Table([
			html.Thead(
				html.Tr([html.Th(' ') for i in range(tablebreak)])),
			html.Tbody([
				html.Tr([html.Td(gene.upper()) for gene in sourcegenes[i*tablebreak:i*tablebreak+tablebreak]]) for i in range(len(sourcegenes)//tablebreak)])
		])
	
@app.callback(
	Output(component_id = 'src_table', component_property='children'), 
	[Input(component_id='hormone-input', component_property='value')]
)
def display_src(val1):
	if val1 != None:
		sourcegenes = list(hormone_src_tgt_genes[str(val1)]['source'])
		targetgenes = list(hormone_src_tgt_genes[str(val1)]['target'])

		if(len(sourcegenes)%tablebreak != 0):
			while(len(sourcegenes)%tablebreak != 0):
				sourcegenes.append(' ')

		return html.Table([
			html.Thead(
				html.Tr([html.Th(' ') for i in range(tablebreak)])),
			html.Tbody([
				html.Tr([html.Td(gene.upper()) for gene in sourcegenes[i*tablebreak:i*tablebreak+tablebreak]]) for i in range(len(sourcegenes)//tablebreak)])
		])

@app.callback(
	Output(component_id = 'tar_tissue', component_property='children'), 
	[Input(component_id='hormone-input', component_property='value')]
)
def display_tar_tissue(val1):
	if val1 != None:
		sourcegenes = list(src_tgt_tissue[str(val1)]['source'])
		targetgenes = list(src_tgt_tissue[str(val1)]['target'])

		if(len(targetgenes)%tablebreak != 0):
			while(len(targetgenes)%tablebreak != 0):
				targetgenes.append(' ')

		return html.Table([
			html.Thead(
				html.Tr([html.Th(' ') for i in range(tablebreak)])),
			html.Tbody([
				html.Tr([html.Td(gene.upper()) for gene in targetgenes[i*tablebreak:i*tablebreak+tablebreak]]) for i in range(len(targetgenes)//tablebreak)])
		])
	
@app.callback(
	Output(component_id = 'tar_table', component_property='children'), 
	[Input(component_id='hormone-input', component_property='value')]
)
def display_tar(val1):
	if val1 != None:
		sourcegenes = list(hormone_src_tgt_genes[str(val1)]['source'])
		targetgenes = list(hormone_src_tgt_genes[str(val1)]['target'])

		if(len(targetgenes)%tablebreak != 0):
			while(len(targetgenes)%tablebreak != 0):
				targetgenes.append(' ')

		return html.Table([
			html.Thead(
				html.Tr([html.Th(' ') for i in range(tablebreak)])),
			html.Tbody([
				html.Tr([html.Td(gene.upper()) for gene in targetgenes[i*tablebreak:i*tablebreak+tablebreak]]) for i in range(len(targetgenes)//tablebreak)])
		])


@app.callback(
	Output(component_id='my-table', component_property='data'),
	[Input(component_id='my-input', component_property='value'),
	Input(component_id='type', component_property='value')],
	[State('my-table', 'data'),
	 State('my-table', 'columns')]
)
def generate_table(val1, val2, rows, columns):
	if(val1 == None):
		val1 = "aldosterone"
	if val1 != None:
		if val2 == "gene":
			df1 = df_gene[df_gene['Hormone'].str.match(val1)]
			df1['SVM probability'] = df1['SVM probability'].apply(trunc)
			df1['SVM score'] = df1['SVM score'].apply(trunc)
		
		elif val2 == "lncrna":
			df1 = df_lncrna[df_lncrna['Hormone'].str.match(val1)]
			df1['SVM probability'] = df1['SVM probability'].apply(trunc)
			df1['SVM score'] = df1['SVM score'].apply(trunc)
					
		return df1.to_dict('records')

@app.callback(
	Output(component_id = 'count', component_property = 'children'),
	[Input(component_id='my-input', component_property='value'),
	Input(component_id='type', component_property='value')]
)
def generate_count(val1, val2):
	print(val1)
	if val1 != None:
		if val2 == "gene":
			df1 = df_gene[df_gene['Hormone'].str.match(val1)]
		elif val2 == "lncrna":
			df1 = df_lncrna[df_lncrna['Hormone'].str.match(val1)]

		return "Discovered " + str(len(df1)) + " " + str(val2) + "s associated with this hormone, with the SVM probability score higher than 0.70"	

@app.callback(Output("pc-download", "data"), [Input("pc-btn", "n_clicks")])
def func(n_clicks):
	return send_file("results/protein_coding_genes_novel_predictions_threshold.csv", filename='protein coding.csv')

@app.callback(Output("lncrna-download", "data"), [Input("lncrna-btn", "n_clicks")])
def func(n_clicks):
	return send_file("results/lncRNA_novel_predictions_threshold.csv", filename = 'lncRNA.csv')

@app.callback(Output("hgv1-gene-download", "data"), [Input("hgv1-gene-btn", "n_clicks")])
def func(n_clicks):
	return send_file("./hgv1_hormone_src_tgt_genes.json", filename = 'HGv1_Gene.json')

@app.callback(Output("hgv1-tissue-download", "data"), [Input("hgv1-tissue-btn", "n_clicks")])
def func(n_clicks):
	return send_file("./source_target_tissue.json", filename = 'HGv1_Tissue.json')

if __name__ == '__main__':
	app.run_server()