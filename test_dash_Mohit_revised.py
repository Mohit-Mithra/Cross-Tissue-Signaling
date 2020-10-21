#!/usr/bin/env python
# coding: utf-8

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

cols_to_use = ['Hormone', 'Gene', 'SVM score', 'SVM probability']
df_gene = pd.read_csv('./protein_coding_genes_novel_predictions.csv', usecols = cols_to_use)
df_lncrna = pd.read_csv('./lncRNA_novel_predictions.csv', usecols = cols_to_use)
with open('./hgv1_hormone_src_tgt_genes.json') as json_file:
    hormone_src_tgt_genes = json.load(json_file)

hormone_lst = ['aldosterone', 'angiotensin', 'calcitonin', 'cholecystokinin', 'cortisol', 'erythropoietin', 'estrogen', 'glucagon', 'insulin', 'leptin', 'melatonin', 'peptide yy', 'progesterone', 'prolactin', 'prostaglandins', 'relaxin', 'somatostatin', 'testosterone', 'adrenocorticotropin', 'thyrotropin-releasing hormone', 'gonadotropin-releasing hormone', 'vascular endothelial growth factor', 'norepinephrine', 'adiponectin', 'a-type natriuretic peptide', 'adrenaline/epinephrine', 'estradiol/oestradiol', 'somatotrophin/growth hormone', 'parathyroid hormone/parathyrin', 'serotonin/5-hydroxytryptamine', 'vitamin d/calciferol', 'follicle-stimulating hormone/follitropin', 'antidiuretic hormone/vasopressin', 'thymosin']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



df_new = df_gene[df_gene['Hormone'].str.match('aldosterone')]
print(len(df_new))
to_load = 50
tablebreak = 12

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
max_rows=10
app.layout = html.Div([
    dcc.Tabs([
        
        dcc.Tab(label="Explore HGv1 dataset", children =[
            html.H4("HGv1 Dataset"),
            html.Div([dcc.Dropdown(id="hormone-input",
                                       options=[
                                           {'label': hor, 'value': hor} for hor in list(hormone_src_tgt_genes.keys())
                                       ],
                                       placeholder="Select a hormone",
                                      )  
                         ]),
            html.H2("Source Genes"),
            html.Div(id='src_table'),
            html.H2("Target Genes"),
            html.Div(id='tar_table')
        ]),
        
        dcc.Tab(label="Browse predictions", children = [
            html.Div(children=[
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
                                             {'label': 'Show associated genes', 'value': 'gene'},
                                             {'label': 'Show associated lncRNAs', 'value': 'lncrna'},
                                         ],
                                         value='gene'
                                        ) 
                         ]),
                html.Div(
                          
                          dash_table.DataTable(
                                  id='my-table',
                                  columns=[
                                            {'name': name, 'id': name} for name in df_new.columns
                                        ],
                                  data=df_new.nlargest(10,['SVM score','SVM probability']).to_dict('records'),
                                  sort_action="native",
                                  sort_mode="multi",
                                  page_size= 10,
                                  tooltip={'Hormone': {'type': 'text', 'value': 'Tooplit'},
                                  		   'Gene': {'type': 'text', 'value': 'Tooplit'},
                                  		   'SVM scores': {'type': 'text', 'value': 'Tooplit'},
                                  		   'SVM probability' : {'type': 'text', 'value': 'Tooplit'}}

								)
								  # tooltip_conditional=[{'if': {'column_id': 'SVM score'}},
										# 				{'value': "My tooltip"},
										# 			    {'type': 'text'}]),
                  )
            ])
        ]),
        
        dcc.Tab(label="Downloads", children = [
            #html.A('Download all hormone-gene predictions', id='hg-link',href="./bioembeds_nonsmote_pos_preds.csv")
            html.Div([html.Button("Download all hormone-gene predictions", id="hg-btn"), Download(id="hg-download")]),
            html.Div([html.Button("Download predictions for protein coding genes", id="pc-btn"), Download(id="pc-download")]),
            html.Div([html.Button("Download predictions for lncrna genes", id="lncrna-btn"), Download(id="lncrna-download")])
        ])
    ])
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
    print(val1)
    if val1 != None:
        if val2 == "gene":
            df1 = df_gene[df_gene['Hormone'].str.match(val1)]
        elif val2 == "lncrna":
            df1 = df_lncrna[df_lncrna['Hormone'].str.match(val1)]

        #return df1.nlargest(10,['SVM score','SVM probability']).to_dict('records')
        return df1.nlargest(to_load,['SVM score','SVM probability']).to_dict('records')

        # return html.Div(dash_table.DataTable(
        # id='table',
        # columns=[
        #     [{"name": col, "id": col, "selectable": True} for col in df1.columns]
        # ],
        # data=df1.to_dict('records'),
        # filter_action="native",
        # sort_action="native",
        # sort_mode="multi",
        # column_selectable="single",
        # row_selectable="multi",
        # selected_columns=[],
        # selected_rows=[],
        # page_action="native",
        # page_current= 0,
        # page_size= 10))


@app.callback(Output("hg-download", "data"), [Input("hg-btn", "n_clicks")])
def func(n_clicks):
    return send_file("./bioembeds_nonsmote_pos_preds.csv", filename = 'bioembed preds.csv')

@app.callback(Output("pc-download", "data"), [Input("pc-btn", "n_clicks")])
def func(n_clicks):
    return send_file("./protein_coding_genes_novel_predictions.csv", filename='protein coding.csv')

@app.callback(Output("lncrna-download", "data"), [Input("lncrna-btn", "n_clicks")])
def func(n_clicks):
    return send_file("./lncRNA_novel_predictions.csv", filename = 'lncRNA.csv')


if __name__ == '__main__':	
    app.run_server(debug=False,port=8051,host='0.0.0.0')
