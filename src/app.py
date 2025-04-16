import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the country data
world = px.data.gapminder().query("year==2007")

# Create the layout for the app
app.layout = html.Div([
    html.H1("Interactive World Map Dashboard", style={'textAlign': 'center', 'color': '#333', 'padding': '20px'}),
    
    # Map container
    html.Div([
        dcc.Graph(id='world-map', style={'height': '70vh'}),
    ], style={'width': '100%', 'padding': '10px'}),
    
    # Info box for country details
    html.Div(id='country-details', style={
        'width': '80%',
        'margin': '0 auto',
        'padding': '20px',
        'backgroundColor': '#f9f9f9',
        'borderRadius': '5px',
        'boxShadow': '0px 0px 5px #ccc',
        'minHeight': '100px'
    })
])

# Create the choropleth map
@app.callback(
    Output('world-map', 'figure'),
    Input('world-map', 'clickData')
)
def update_map(click_data):
    fig = px.choropleth(
        world,
        locations="iso_alpha",
        color="gdpPercap",
        hover_name="country",
        color_continuous_scale=px.colors.sequential.Plasma,
        projection="natural earth"
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar={
            'title': 'GDP per Capita',
            'thickness': 15,
            'len': 0.5,
            'y': 0.5,
        }
    )
    
    # Make layout more appealing
    fig.update_geos(
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="lightgray",
        countrycolor="white",
        coastlinecolor="white",
        projection_type="natural earth"
    )
    
    return fig

# Fetch additional country data from API
def get_country_details(country_code):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/alpha/{country_code}")
        if response.status_code == 200:
            return response.json()[0]
        else:
            return None
    except:
        return None

# Update the country details when a country is clicked
@app.callback(
    Output('country-details', 'children'),
    Input('world-map', 'clickData')
)
def display_country_info(click_data):
    if click_data is None:
        return html.Div([
            html.H3("Country Information"),
            html.P("Click on a country to see detailed information.")
        ])
    
    # Get country name from click data
    country_name = click_data['points'][0]['hovertext']
    country_code = click_data['points'][0]['location']
    
    # Get country data from our dataset
    country_data = world[world['iso_alpha'] == country_code].iloc[0]
    
    # Try to get additional info from REST Countries API
    detailed_info = get_country_details(country_code)
    
    if detailed_info:
        # Extract relevant information
        capital = detailed_info.get('capital', ['Unknown'])[0]
        population = detailed_info.get('population', 'Unknown')
        languages = ', '.join(list(detailed_info.get('languages', {}).values()))
        currencies = ', '.join([f"{v.get('name', 'Unknown')} ({v.get('symbol', 'Unknown')})" 
                              for v in detailed_info.get('currencies', {}).values()])
        region = f"{detailed_info.get('region', 'Unknown')} ({detailed_info.get('subregion', 'Unknown')})"
        
        flag_emoji = detailed_info.get('flag', '')
        
        return html.Div([
            html.H2(f"{flag_emoji} {country_name}", style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.H3("Geographic Information"),
                    html.P(f"Capital: {capital}"),
                    html.P(f"Region: {region}"),
                    html.P(f"Area: {detailed_info.get('area', 'Unknown'):,} sq km"),
                ], style={'flex': '1', 'padding': '10px'}),
                
                html.Div([
                    html.H3("Demographic Information"),
                    html.P(f"Population: {population:,}"),
                    html.P(f"Languages: {languages}"),
                    html.P(f"Currencies: {currencies}"),
                ], style={'flex': '1', 'padding': '10px'}),
                
                html.Div([
                    html.H3("Economic Information"),
                    html.P(f"GDP per Capita: ${country_data['gdpPercap']:,.2f}"),
                    html.P(f"Life Expectancy: {country_data['lifeExp']:.1f} years"),
                ], style={'flex': '1', 'padding': '10px'})
            ], style={'display': 'flex', 'flexWrap': 'wrap'})
        ])
    else:
        # Fallback to basic info if API request fails
        return html.Div([
            html.H2(country_name, style={'textAlign': 'center'}),
            html.Div([
                html.H3("Basic Information"),
                html.P(f"Population: {country_data['pop']:,}"),
                html.P(f"GDP per Capita: ${country_data['gdpPercap']:,.2f}"),
                html.P(f"Life Expectancy: {country_data['lifeExp']:.1f} years"),
                html.P("Click another country to see its details.")
            ])
        ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)