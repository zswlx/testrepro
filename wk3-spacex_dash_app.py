# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
#import dash_html_components as html
#import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

OptionList = [{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()]
OptionList.insert(0,{'label': 'All', 'value': 'All'})

# Create a dash application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Create an app layout
app.layout = html.Div(children=
                [html.H1('SpaceX Launch Records Dashboard',
                        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                html.Div([html.Label("Select Statistics:"),
                    dcc.Dropdown(
                        id='site-dropdown',
                        options=OptionList,
                        value='All',
                        placeholder='Select a Launch Site here',
                        searchable=True
                    )
                ]),

                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                html.Div(dcc.Graph(id='success-pie-chart')),
                html.Br(),

                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                html.Div([               
                    dcc.RangeSlider(
                        id='payload-slider',
                        min=min_payload,
                        max=max_payload,
                        step=1000,
                        marks={0:'0', 100:'100'},
                        value=[min_payload,max_payload]
                    )
                ]), 
                #html.Br(),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                ])


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
#@callback(
#    Output('output-slider', 'value'),
#    Input('payload-slider', 'value'))
#def update_output(entered_v):
#    return entered_v

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id="payload-slider", component_property="value")])
def get_graph(entered_site, entered_value):
    s_data_= spacex_df[spacex_df['Payload Mass (kg)'] < entered_value[1]]  
    s_data= s_data_[s_data_['Payload Mass (kg)'] > entered_value[0]]  
    if entered_site == 'All':
        s_1= s_data[['Payload Mass (kg)','class', 'Booster Version Category']]        
        fig = px.scatter(s_1,x='Payload Mass (kg)', y='class',
                        color="Booster Version Category" )
        return fig
    else:
        s_2=s_data[s_data['Launch Site']==entered_site][['Payload Mass (kg)','class', 'Booster Version Category']]
        fig = px.scatter(s_2,x='Payload Mass (kg)', y='class',
                        color="Booster Version Category")
        return fig
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site): 
    if entered_site == 'All':
        filtered_1 = spacex_df[spacex_df['class']==1].groupby('Launch Site')['class'].sum()
        filtered_df1=pd.DataFrame({'Launch Site':filtered_1.index, 'class':filtered_1.values})
        fig = px.pie(filtered_df1,
            values='class', 
            names='Launch Site', 
            title='Total Successful Launches Count for All Sites')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_2= spacex_df[spacex_df['Launch Site']==entered_site]['class'].value_counts(normalize=True)
        filtered_df2=pd.DataFrame({'class':filtered_2.index, 'count':filtered_2.values})
        fig = px.pie(filtered_df2,
            values='count', 
            names='class', 
            title='Success vs. Failed Counts for Site "{}"'.format(entered_site))
        return fig           

# Run the app
if __name__ == '__main__':
    app.run_server()
