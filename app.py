import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load datasets
drivers = pd.read_csv('drivers.csv')
vehicles = pd.read_csv('vehicles.csv')
maintenance = pd.read_csv('maintenance.csv')
routes = pd.read_csv('routes.csv')
locations = pd.read_csv('locations.csv')
shipments = pd.read_csv('shipments.csv')

# Enrich shipment data
enriched = (
    shipments
    .merge(drivers, on='driver_id', how='left')
    .merge(vehicles, on='vehicle_id', how='left')
    .merge(routes, on='route_id', how='left')
    .merge(locations, left_on='delivery_location_id', right_on='location_id', how='left')
)
enriched['shipment_date'] = pd.to_datetime(enriched['shipment_date'])

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("📦 Logistics Dashboard", style={'textAlign': 'center'}),
    
    html.Label("Select Driver:"),
    dcc.Dropdown(
        id='driver-dropdown',
        options=[{'label': f"{row['first_name']} {row['last_name']}", 'value': row['last_name']} for _, row in drivers.iterrows()],
        value=drivers['last_name'].iloc[0]
    ),
    
    html.Div([
        dcc.Graph(id='scatter-plot'),
        dcc.Graph(id='box-plot'),
        dcc.Graph(id='bar-plot'),
        dcc.Graph(id='line-plot')
    ])
])

@app.callback(
    [
        Output('scatter-plot', 'figure'),
        Output('box-plot', 'figure'),
        Output('bar-plot', 'figure'),
        Output('line-plot', 'figure')
    ],
    [Input('driver-dropdown', 'value')]
)
def update_plots(selected_driver):
    filtered_df = enriched[enriched['last_name'] == selected_driver]

    scatter_fig = px.scatter(
        filtered_df,
        x='distance_km',
        y='fuel_used_liters',
        color='delivery_status',
        title=f"Distance vs Fuel Used ({selected_driver})",
        labels={'distance_km': 'Distance (km)', 'fuel_used_liters': 'Fuel Used (liters)'}
    )

    box_fig = px.box(
        filtered_df,
        y='delay_minutes',
        color='delivery_status',
        title=f"Delay Minutes Distribution ({selected_driver})"
    )

    bar_fig = px.histogram(
        filtered_df,
        x='delivery_status',
        title=f"Delivery Status Count ({selected_driver})",
        labels={'delivery_status': 'Delivery Status'}
    )

    line_fig = px.line(
        filtered_df.sort_values('shipment_date'),
        x='shipment_date',
        y='delay_minutes',
        title=f"Delay Over Time ({selected_driver})",
        labels={'shipment_date': 'Date', 'delay_minutes': 'Delay (minutes)'}
    )

    return scatter_fig, box_fig, bar_fig, line_fig

if __name__ == '__main__':
    app.run_server(debug=True)
