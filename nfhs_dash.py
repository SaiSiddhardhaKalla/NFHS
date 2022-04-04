#from tkinter import font
#from click import style
import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table

nfhs=pd.read_csv('India_Change.csv',low_memory=False)
state = list(nfhs['State'].unique())
state = sorted(state)
state.insert(0, "All")
geo=gpd.read_file('Districts.geojson')

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
    html.H1("National Family Health Survey")],
                 className='header'),
    html.Div(style={'background-image': 'url("/assets/blue-wave.svg")'},className='bground'),
    # html.Div(style={'background-image': 'url("/assets/blue-wave.svg")'},className='bground_down'),
    html.Div([
    html.Label('Select a Category', style={'fontSize' : '16px'}),
    dcc.Dropdown(id="Category",
                 options= [{"label" : i, "value" : i} for i in nfhs.Category.unique()],
                 placeholder="Select a Category",
                 multi=False,
                 searchable=True,
                 value="Population and Household Profile",
                 clearable=False,
                 style={ 'verticalAlign':"middle",'color':'black'} #'width' : '50%',
                )],className='Cat'),
    html.Div([
    html.Label('Select an Indicator', style={'fontSize' : '16px'}),
    dcc.Dropdown(id="Indicator",
                 options= [],
                 placeholder="Select an Indicator",
                 multi=False,
                 searchable=True,
                 value="Population below age 15 (%)",
                 clearable=False,
                 style={ 'verticalAlign':"middle",'color':'black'}
                )],className='indi'),
    html.Div(id='output_container', children=[],className='output'),
    html.Div([
    html.Label('Select a State', style={'fontSize' : '16px'}),
    dcc.Dropdown(id="State",
                 options= [{"label" : i, "value" : i} for i in state],
                 placeholder= "Select a State",
                 multi=False,
                 searchable=True,
                 value='All',
                 clearable=False,
                )],className='States'),
    html.Div([
    html.Label('Best Performing Districts', style={'fontSize' : '16px','fontWeight':'bold'}),
    html.Div(id="top5_table")],className='top5'),
    html.Div([
    html.Label('Worst Performing Districts', style={'fontSize' : '16px','fontWeight':'bold'}),
    html.Div(id="bot5_table")],className='bot5'),
    html.Div([
    html.Label('Districts with the most change', style={'fontSize' : '16px','fontWeight':'bold'}),
    html.Div(id="chan_table")],className='chan'),
    html.Div([
    html.Label('Districts with the least change', style={'fontSize' : '16px','fontWeight':'bold'}),
    html.Div(id="negchan_table")],className='negchan'),
    html.Div([
    dcc.Graph(id='nfhs5', figure={},style={
                                             "height": "85vh",
                                            #  'width':'70vh',
                                            #  "display": "inline-block",
                                            #  "border": "3px #5c5c5c solid",
                                            #  "overflow": "absolute",
                                            })],className='n5')
],className='wrapper')

@app.callback(
    [Output('Indicator','options'),
     Output('Indicator','value')],
    Input('Category','value')
    )
def update_ac(Categ):
    df1 = nfhs[nfhs['Category']== Categ]
    k =  df1['Indicator'].unique()
    return [{'label' : i, 'value' : i} for i in df1['Indicator'].unique()], k[-2]

@app.callback(
    [Output('output_container', 'children'),
     Output("nfhs5", "figure")],
    [Input("Indicator", "value"),
     Input("State","value")]
     )
def update_figure(mtric_chosen,states):
    df3 = nfhs.copy()
    df4 = df3[df3["Indicator"] == mtric_chosen]
    container = "The indicator chosen by user was: {}".format(mtric_chosen)
    if states == 'All':
        fig4 = px.choropleth_mapbox(
            data_frame = df4,
            geojson = geo,
            featureidkey='properties.DISTRICT', # from geojson
            locations = 'DISTRICT', # from df
            center = {'lon':82.8496, 'lat':22.6944},
            mapbox_style='carto-positron',
            zoom=3.75,
            color='Change',
            range_color=[-50,50],
            color_continuous_scale=px.colors.diverging.RdBu,
            title='Percentage Change between NFHS 4 and NFHS 5 values',
            hover_name='District Name',
            color_continuous_midpoint=0,
            custom_data=[df4['District Name'],df4['State'],
                         df4['NFHS 5'],df4['NFHS 4'],df4['Change']]
            )
        hovertemp = '<i style="color:red;">District :</i> %{customdata[0]}<br>'
        hovertemp += '<i style="color:red;">State :</i> %{customdata[1]}<br>'
        hovertemp += '<i>NFHS 5 :</i> %{customdata[2]:,f}<br>'
        hovertemp += '<i>NFHS 4 :</i> %{customdata[3]:,f}<br>'
        hovertemp += '<i>Change :</i> %{customdata[4]:,f}<br>'
        fig4.update_traces(hovertemplate=hovertemp)
        fig4.update_layout(
                        margin=dict(l=10, r=10, t=50, b=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                        title_font_family='Helvetica',
                        font_family='Helvetica',
                        dragmode='pan',
                      )
        return container, fig4
    else:
        sta4 = df4[df4['State']==states]
        cento = geo[geo['ST_NM']== states]
        cen = cento.centroid
        lon = cen.apply(lambda p: p.x)
        lat = cen.apply(lambda p: p.y)
        fig4 = px.choropleth_mapbox(
            data_frame = sta4,
            geojson = cento,
            featureidkey='properties.DISTRICT', # from geojson
            locations = 'DISTRICT', # from df
            center = {'lon':lon.iloc[0], 'lat':lat.iloc[0]},
            mapbox_style='carto-positron',
            zoom=5.25,
            color='Change',
            # range_color=[-50,50],
            color_continuous_scale=px.colors.diverging.RdBu,
            title='State values',
            color_continuous_midpoint=0,
            custom_data=[sta4['District Name'],sta4['State'],
                         sta4['NFHS 5'],sta4['NFHS 4'],sta4['Change']]
            )
        # I created my own hover template for on hover event
        hovertemp = '<i style="color:red;">District :</i> %{customdata[0]}<br>'
        hovertemp += '<i style="color:red;">State :</i> %{customdata[1]}<br>'
        hovertemp += '<i>NFHS 5 :</i> %{customdata[2]:,f}<br>'
        hovertemp += '<i>NFHS 4 :</i> %{customdata[3]:,f}<br>'
        hovertemp += '<i>Change :</i> %{customdata[4]:,f}<br>'
        fig4.update_traces(hovertemplate=hovertemp)
        fig4.update_layout(
                        margin=dict(l=10, r=10, t=50, b=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                        title_font_family='Helvetica',
                        font_family='Helvetica',
                        dragmode='pan',
                      )
        return container, fig4

@app.callback(
    [Output('top5_table', 'children'),
     Output('bot5_table','children'),
     Output('chan_table','children'),
     Output('negchan_table','children')],
    [Input("Indicator", "value"),
     Input("State","value")]
     )
def update_table(mtric_chose,stat):
    df5 = nfhs[nfhs["Indicator"] == mtric_chose]
    if stat == 'All':
        tdf = df5.sort_values(by = 'NFHS 5',ascending = False)
        tdf = tdf.head(5)
        tdf = tdf[['State','District Name','NFHS 5'	,'NFHS 4']]
        tdf2 = df5.sort_values(by = 'NFHS 5',ascending = True)
        tdf2 = tdf2[tdf2['District Name'] != 'Data Not Available']
        tdf2 = tdf2.head(5)
        tdf2 = tdf2[['State','District Name','NFHS 5'	,'NFHS 4']]
        tdf5 = df5.sort_values(by = 'Change',ascending = False)
        tdf5 = tdf5[tdf5['NFHS 4'] != 0]
        tdf5 = tdf5.head(5)
        tdf5 = tdf5[['State','District Name','NFHS 5','NFHS 4','Change']]
        tdf5.columns=['State','District Name','NFHS 5','NFHS 4','Change (in %)']
        tdf7 = df5.sort_values(by = 'Change',ascending = True)
        tdf7 = tdf7[tdf7['NFHS 4'] != 0]
        tdf7 = tdf7.head(5)
        tdf7 = tdf7[['State','District Name','NFHS 5','NFHS 4','Change']]
        tdf7.columns=['State','District Name','NFHS 5','NFHS 4','Change (in %)']
        # td7= td7.rename(columns={'Change':'Change (in %)'})
        return dash_table.DataTable(data=tdf.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'maxWidth': '35%',
                                                'font-family': 'HelveticaNeue'
                                                },
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_data={'fontWeight':'bold',
                                                        'whiteSpace': 'normal',
                                                        'height': 'auto',
                                                        'backgroundColor': 'transparent' 
                                                        },
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '35%'},
                                        {'if': {'column_id':'State'}, 'width' : '25%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'20%'}
                                        ],
                                    style_as_list_view=True,
                ),dash_table.DataTable(data=tdf2.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_header={'fontWeight':'bold',
                                                            # 'color': '#ffffff',
                                                            'backgroundColor':'#F9E6DD'},
                                    style_data={'fontWeight':'bold',
                                                        'whiteSpace': 'normal',
                                                        'height': 'auto',
                                                        # 'backgroundColor': 'transparent' 
                                                        },
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '35%'},
                                        {'if': {'column_id':'State'}, 'width' : '25%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'20%'}
                                        ],
                                    style_as_list_view=True,
                ),dash_table.DataTable(data=tdf5.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_data={'fontWeight':'bold',
                                                        'whiteSpace': 'normal',
                                                        'height': 'auto',
                                                        'backgroundColor': 'transparent' 
                                                        },
                                    style_header={'fontWeight':'bold',
                                                            # 'color': '#ffffff',
                                                            'backgroundColor':'#F9E6DD'},
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '30%'},
                                        {'if': {'column_id':'State'}, 'width' : '25%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'15%'},
                                        {'if':{'column_id':'NFHS 4'},'width':'15%'}
                                        ],
                                    style_data_conditional=[ 
                                        {'if': {'filter_query': '{Change (in %)} < 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': 'tomato',
                                                'fontWeight': 'bold'},
                                        {'if': {'filter_query': '{Change (in %)} > 0',
                                                'column_id': 'Change (in %)'},
                                                'color': '#006400',
                                                'fontWeight': 'bold'},
                                        ],
                                    style_as_list_view=True,       
                ),dash_table.DataTable(data=tdf7.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_data={'fontWeight':'bold',
                                                        'whiteSpace': 'normal',
                                                        'height': 'auto',
                                                        # 'backgroundColor': 'transparent' 
                                                        },
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '30%'},
                                        {'if': {'column_id':'State'}, 'width' : '25%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'15%'},
                                        {'if':{'column_id':'NFHS 4'},'width':'15%'}
                                        ],
                                    style_data_conditional=[ 
                                        {'if': {'filter_query': '{Change (in %)} < 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': 'tomato',
                                                'fontWeight': 'bold'},         
                                        {'if': {'filter_query': '{Change (in %)} > 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': '#006400',
                                                'fontWeight': 'bold'},                                       
                                        ],
                                    style_as_list_view=True,
                )
    else:
        sta5 = df5[df5['State']==stat]
        tdf3 = sta5.sort_values(by = 'NFHS 5',ascending = False)
        tdf3 = tdf3.head(5)
        tdf3 = tdf3[['District Name','NFHS 5'	,'NFHS 4']]
        tdf4 = sta5.sort_values(by = 'NFHS 5',ascending = True)
        tdf4 = tdf4[tdf4['District Name'] != 'Data Not Available']
        tdf4 = tdf4.head(5)
        tdf4 = tdf4[['District Name','NFHS 5'	,'NFHS 4']]
        tdf6 = sta5.sort_values(by = 'Change',ascending = False)
        tdf6 = tdf6[tdf6['NFHS 4'] != 0]
        tdf6 = tdf6.head(5)
        tdf6 = tdf6[['District Name','NFHS 5','NFHS 4','Change']]
        tdf6.columns=['District Name','NFHS 5','NFHS 4','Change (in %)']
        tdf8 = sta5.sort_values(by = 'Change',ascending = True)
        tdf8 = tdf8[tdf8['NFHS 4'] != 0]
        tdf8 = tdf8.head(5)
        tdf8 = tdf8[['District Name','NFHS 5','NFHS 4','Change']]
        tdf8.columns=['District Name','NFHS 5','NFHS 4','Change (in %)']
        return dash_table.DataTable(data=tdf3.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_data={'whiteSpace': 'normal',
                                                        'fontWeight': 'bold',
                                                        'height': 'auto' },
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '40%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'30%'}
                                        ],
                                    style_as_list_view=True,
                ),dash_table.DataTable(data=tdf4.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_data={'whiteSpace': 'normal',
                                                        'fontWeight': 'bold',                                    
                                                        'height': 'auto' },
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '40%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'30%'}
                                        ],
                                    style_as_list_view=True,
                ),dash_table.DataTable(data=tdf6.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family':'HelveticaNeue'},
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_data={'whiteSpace': 'normal',
                                                        'fontWeight': 'bold',
                                                        'height': 'auto' },
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '40%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'20%'},
                                        {'if':{'column_id':'NFHS 4'},'width':'20%'}
                                        ],
                                    style_data_conditional=[ 
                                        {'if': {'filter_query': '{Change (in %)} < 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': 'tomato',
                                                'fontWeight': 'bold'},
                                        {'if': {'filter_query': '{Change (in %)} > 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': '#006400',
                                                'fontWeight': 'bold'},                                              
                                        ],
                                    style_as_list_view=True,
                ),dash_table.DataTable(data=tdf8.to_dict('records'),
                                    style_cell={'text-align':'left',
                                                'height':'auto',
                                                'fontSize': 10.5,
                                                'font-family': 'HelveticaNeue'},
                                    style_data={'whiteSpace': 'normal',
                                                        'fontWeight': 'bold',
                                                        'height': 'auto' },
                                    style_header={'fontWeight':'bold',
                                                            'color': '#ffffff',
                                                            'backgroundColor':'#052F5F'},
                                    style_cell_conditional=[
                                        {'if': {'column_id':'District Name'}, 'width' : '40%'},
                                        {'if':{'column_id':'NFHS 5'},'width':'20%'},
                                        {'if':{'column_id':'NFHS 4'},'width':'20%'}
                                        ],
                                    style_data_conditional=[ 
                                        {'if': {'filter_query': '{Change (in %)} < 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': 'tomato',
                                                'fontWeight': 'bold'},
                                        {'if': {'filter_query': '{Change (in %)} > 0',
                                                'column_id': 'Change (in %)'},
                                                 'color': '#006400',
                                                'fontWeight': 'bold'},                                              
                                        ],
                                    style_as_list_view=True,
                )
if __name__ == '__main__':
    app.run_server(debug=True)# use_reloader=False")
