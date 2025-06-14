# ───────────────────────────────────────────────
# spacex_dash_app.py  –  complete working code
# IBM DS Capstone  •  Plotly Dash Interactive Dashboard
# ───────────────────────────────────────────────

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ───────────────────────────────────────────────
# 1.  LOAD + CLEAN DATA
# ───────────────────────────────────────────────
df = pd.read_csv("spacex_launch_dash.csv")

# Ensure numeric payload and drop rows with missing critical data
df['Payload Mass (kg)'] = pd.to_numeric(df['Payload Mass (kg)'],
                                        errors='coerce')
df = df.dropna(subset=['Payload Mass (kg)', 'class'])

# Min / Max payload for slider
min_payload = df['Payload Mass (kg)'].min()
max_payload = df['Payload Mass (kg)'].max()

# ───────────────────────────────────────────────
# 2.  DASH APP SET‑UP
# ───────────────────────────────────────────────
app = dash.Dash(__name__)

# Build dropdown options dynamically
site_options = ([{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': s, 'value': s}
                 for s in sorted(df['Launch Site'].unique())])

app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard",
            style={'textAlign': 'center', 'color': '#503D36'}),

    # TASK‑1  •  Dropdown
    dcc.Dropdown(id="site-dropdown",
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),

    # Pie Chart
    dcc.Graph(id="success-pie-chart"),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK‑3  •  Slider
    dcc.RangeSlider(id="payload-slider",
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000',
                           7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),

    # Scatter Plot
    dcc.Graph(id="success-payload-scatter-chart")
])

# ───────────────────────────────────────────────
# 3.  CALLBACK • PIE CHART
# ───────────────────────────────────────────────
@app.callback(Output("success-pie-chart", "figure"),
              Input("site-dropdown", "value"))
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Aggregate successes per site
        grouped = (df.groupby('Launch Site')['class']
                     .sum()
                     .reset_index(name='Successes'))
        fig = px.pie(grouped, values='Successes', names='Launch Site',
                     title="Total Successful Launches by Site")
    else:
        site_df = df[df['Launch Site'] == selected_site]
        outcome = (site_df['class']
                   .value_counts()
                   .rename({1: 'Success', 0: 'Failure'})
                   .reset_index(name='Count')
                   .rename(columns={'index': 'Outcome'}))
        fig = px.pie(outcome, values='Count', names='Outcome',
                     title=f"Success vs Failure for {selected_site}")
    return fig

# ───────────────────────────────────────────────
# 4.  CALLBACK • SCATTER PLOT
# ───────────────────────────────────────────────
@app.callback(Output("success-payload-scatter-chart", "figure"),
              [Input("site-dropdown", "value"),
               Input("payload-slider", "value")])
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = df['Payload Mass (kg)'].between(low, high)
    filtered = df[mask]

    if selected_site != 'ALL':
        filtered = filtered[filtered['Launch Site'] == selected_site]

    title = ("Correlation Between Payload and Success – "
             f"{selected_site if selected_site!='ALL' else 'All Sites'}")

    fig = px.scatter(filtered,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     hover_data=['Flight Number'],
                     title=title,
                     labels={'class': 'Outcome (0=Fail, 1=Success)'})
    # Keep y‑axis visible even if only successes
    fig.update_yaxes(range=[-0.2, 1.2])
    return fig

# ───────────────────────────────────────────────
# 5.  RUN SERVER  (Dash 3 uses app.run)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8060, debug=True)
