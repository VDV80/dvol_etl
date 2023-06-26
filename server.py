import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


# Assume you have a function to query the database and return a DataFrame with time series data
def query_database(start_date, end_date):
    db_user = "airflow"
    db_password = "airflow"
    db_host = "air-pg-datastore-1"
    db_port = 5432 #5439
    db_name = "postgres"
    from sqlalchemy import create_engine
    # Create the SQLAlchemy engine
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    query = f"""SELECT * FROM public.hist_data WHERE dates BETWEEN '{start_date}' AND '{end_date}'"""
    result = pd.read_sql(query, engine)
    res = result[['dates', 'mid_price']]
    res.columns = ['date', 'value']
    return res

    # # Placeholder implementation with random data for demonstration purposes
    # data = pd.DataFrame({
    #     'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
    #     'value': [x % 100 for x in range(365)]
    # })
    # return data


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Time Series Data Visualization (data only available for approx Oct-Dec 2016)'),
    html.Div([
        html.Label('Start Date as YYYY-MM-DD   '),
        dcc.DatePickerSingle(
            id='start-date-picker',
            display_format='YYYY-MM-DD',
            date='2011-01-01'  # Set default start date here
        )
    ]),
    html.Div([
        html.Label('End Date as YYYY-MM-DD    '),
        dcc.DatePickerSingle(
            id='end-date-picker',
            display_format='YYYY-MM-DD',
            date='2017-01-01'  # Set default end date here
        )
    ]),
    dcc.Graph(id='time-series-chart')
])


@app.callback(
    Output('time-series-chart', 'figure'),
    Input('start-date-picker', 'date'),
    Input('end-date-picker', 'date')
)
def update_chart(start_date, end_date):
    # Query the database with the selected start and end dates
    data = query_database(start_date, end_date)

    # Create the Plotly figure
    fig = px.line(data, x='date', y='value')

    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8081)
