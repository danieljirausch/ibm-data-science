# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import math
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = ['CCAFS LC-40','CCAFS SLC-40','KSC LC-39A','VAFB SLC-4E']   

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36','font-size': 40}
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        html.Div(dcc.Graph(id='booster-bar-chart')),
        html.Br(),

        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        #dcc.RangeSlider(id='payload-slider',...)
        dcc.RangeSlider(
            id='payload-slider',
            min=0, 
            max=10000, 
            step=1000,
            value=[min_payload, max_payload]
        ),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),

    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        all_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            all_df,
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site',
            category_orders={"Launch Site": launch_sites}
        )
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site']==entered_site]
        class_counts = site_df['class'].value_counts()
        counts_df = pd.DataFrame({'class': class_counts.index, 'count': class_counts.values})
        fig = px.pie(
            counts_df, 
            values='count', 
            names='class', 
            title=f'Total Success Launches for site {entered_site}',
        )
        # return the outcomes piechart for a selected site
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'), 
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    if entered_site == 'ALL':
        scatter_df = filtered_df
        title = 'Correlation between Payload and Success for all Sites'
    else:
        scatter_df = filtered_df[filtered_df['Launch Site']==entered_site]
        title = f'Correlation between Payload and Success for site {entered_site}'
    fig = px.scatter(
        scatter_df,
        x='Payload Mass (kg)', 
        y='class',
        color="Booster Version Category",
        title=title
    )
    return fig

@app.callback(
    Output(component_id='booster-bar-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'), 
)
def get_bar_chart(entered_site):
    if entered_site == 'ALL':
        bar_df = spacex_df.groupby(['Launch Site', 'Booster Version Category'])['class'].sum().reset_index()
        title = 'Successful Launches by Booster Version'
    else:
        bar_df = spacex_df[spacex_df['Launch Site']==entered_site].groupby(['Launch Site', 'Booster Version Category'])['class'].sum().reset_index()
        title = f'Correlation between Payload and Success for site {entered_site}'

    bar_df = bar_df.rename(columns={'class': 'Successful Launches'})
    fig = px.bar(
        bar_df,
        x='Booster Version Category',
        y='Successful Launches',
        color='Launch Site',
        title=title,
        category_orders={"Launch Site": launch_sites}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
