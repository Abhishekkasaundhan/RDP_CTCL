import dash
from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from threading import Timer
import webbrowser

groups = {}
with open('groups.txt', 'r') as file:
    for line in file:
        group, password = line.strip().split(',')
        groups[group] = password

df1 = pd.read_excel("ctcl_data.xlsx")
df2 = pd.read_excel("rdp_data.xlsx")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("CTCL & RDP DATA"),
    dcc.Input(
        id='group-name-filter',
        type='text',
        placeholder='ENTER YOUR GROUP NAME',
        style={'width': '50%', 'height': '40px'}
    ),
    dcc.Input(
        id='password-filter',
        type='password',
        placeholder='ENTER YOUR PASSWORD',
        style={'width': '50%', 'height': '40px'}
    ),
    html.Button('Login', id='login-button', n_clicks=0, style={'margin': '30px','height': '40px', 'width': '100px'}),
    html.Div(id='login-output', style={'color': 'red'}),

    html.Div(id='data-section', children=[
        dcc.Dropdown(
            id='ctcl-filter',
            options=[{'label': col, 'value': col} for col in df1.columns],
            multi=True,
            placeholder="Select columns to filter CTCL data"
        ),
        dcc.Dropdown(
            id='rdp-filter',
            options=[{'label': col, 'value': col} for col in df2.columns],
            multi=True,
            placeholder="Select columns to filter RDP data"
        ),
        html.Div([
            html.Button('Select All CTCL Columns', id='select-all-ctcl', n_clicks=0, style={'margin': '10px'}),
            html.Button('Select All RDP Columns', id='select-all-rdp', n_clicks=0, style={'margin': '10px'}),
        ]),
        html.Div([
            html.Div([
                html.H2("CTCL DATA TABLE", style={'text-align': 'center'}),
                dash_table.DataTable(
                    id='ctcl-table',
                    columns=[{"name": i, "id": i} for i in df1.columns],
                    data=[],
                    sort_action="native",
                    page_size=10,
                    style_table={'height': '400px', 'overflowY': 'auto'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-right': '20px'}),
            html.Div([
                html.H2("RDP DATA TABLE", style={'text-align': 'center'}),
                dash_table.DataTable(
                    id='rdp-table',
                    columns=[{"name": i, "id": i} for i in df2.columns],
                    data=[],
                    sort_action="native",
                    page_size=10,
                    style_table={'height': '400px', 'overflowY': 'auto'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'})
        ])
    ], style={'display': 'none'}) 
])

@app.callback(
    Output('data-section', 'style'),
    Output('login-output', 'children'),
    Input('login-button', 'n_clicks'),
    State('group-name-filter', 'value'),
    State('password-filter', 'value')
)
def authenticate(n_clicks, group_name, password):
    if n_clicks > 0:
        if group_name in groups and groups[group_name] == password:
            return {'display': 'block'}, ''
        else:
            return {'display': 'none'}, 'INVALID GROUP NAME OR PASSWORD.'
    return {'display': 'none'}, ''

@app.callback(
    Output('ctcl-filter', 'value'),
    Input('select-all-ctcl', 'n_clicks'),
    State('ctcl-filter', 'options')
)
def select_all_ctcl_columns(n_clicks, options):
    if n_clicks > 0:
        return [option['value'] for option in options]
    else:
        return []

@app.callback(
    Output('rdp-filter', 'value'),
    Input('select-all-rdp', 'n_clicks'),
    State('rdp-filter', 'options')
)
def select_all_rdp_columns(n_clicks, options):
    if n_clicks > 0:
        return [option['value'] for option in options]
    else:
        return []

def update_table(selected_columns, group_filter, df):
    if not selected_columns:
        return [], []

    filtered_df = df[selected_columns]

    if group_filter:
        filtered_df = filtered_df[filtered_df.apply(lambda row: group_filter.lower() in row.astype(str).str.lower().values, axis=1)]
    else:
        filtered_df = pd.DataFrame(columns=selected_columns)

    columns = [{"name": col, "id": col} for col in filtered_df.columns]
    return columns, filtered_df.to_dict('records')

@app.callback(
    Output('ctcl-table', 'columns'),
    Output('ctcl-table', 'data'),
    [Input('ctcl-filter', 'value'),
     Input('group-name-filter', 'value'),
     State('group-name-filter', 'value'),
     State('password-filter', 'value')]
)
def update_ctcl_table(selected_columns, group_filter, group_name, password):
    if group_name in groups and groups[group_name] == password:
        return update_table(selected_columns, group_filter, df1)
    else:
        return [], []

@app.callback(
    Output('rdp-table', 'columns'),
    Output('rdp-table', 'data'),
    [Input('rdp-filter', 'value'),
     Input('group-name-filter', 'value'),
     State('group-name-filter', 'value'),
     State('password-filter', 'value')]
)
def update_rdp_table(selected_columns, group_filter, group_name, password):
    if group_name in groups and groups[group_name] == password:
        return update_table(selected_columns, group_filter, df2)
    else:
        return [], []

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True)
