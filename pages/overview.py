"""
Overview page — one subsection per loaded dataset, each with KPIs +
a historical time-series plot and a toggleable average-profile plot
(week / intraday) with ±1σ confidence interval.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

import data_preparation as dp
import globals
import plot as plt_mod

globals.init()
dash.register_page(__name__, path='/overview', name='Overview')

TEAL      = 'rgba(0,203,233,255)'
TEAL_FILL = 'rgba(79,144,166,0.25)'

# ─── reusable layout helpers ──────────────────────────────────────────────────

def _kpi(header, cid):
    return dbc.Card([
        dbc.CardHeader(header, style={'padding': '3px 8px', 'fontSize': '0.73rem'}),
        dbc.CardBody(html.H5('—', id=cid, style={'margin': 0}),
                     style={'padding': '5px 8px'}),
    ])


def _section_divider(label):
    return html.Div([
        html.Hr(style={'borderColor': '#3a718d', 'margin': '14px 0 3px 0'}),
        html.Span(label, style={'color': '#62a5b4', 'fontWeight': '600', 'fontSize': '0.88rem'}),
    ])


def _two_plots(ts_id, agg_id, ts_title, agg_title, radio_id=None):
    """Returns a dbc.Row with time-series on the left and agg-profile on the right."""
    agg_header_children = agg_title
    if radio_id:
        agg_header_children = [
            agg_title + '  ',
            dbc.RadioItems(
                id=radio_id,
                options=[{'label': ' Week', 'value': 'week'},
                         {'label': ' Intraday', 'value': 'intraday'}],
                value='week', inline=True,
                style={'display': 'inline-block', 'fontSize': '0.78rem'},
            ),
        ]
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(ts_title),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id=ts_id, config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
        dbc.Col(dbc.Card([
            dbc.CardHeader(agg_header_children),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id=agg_id, config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
    ], className='g-1 mt-1')


# ─── plot helpers ─────────────────────────────────────────────────────────────

def _apply_theme(fig):
    fig.update_layout(
        template=globals.plot_template,
        margin=globals.plot_margin,
        paper_bgcolor=globals.paper_bgcolor,
        plot_bgcolor=globals.paper_bgcolor,
        legend=globals.legend,
    )
    fig.update_yaxes(showgrid=False)
    return fig


def _ts_bar(df, date_col, y_col, color_col):
    """Stacked bar + 7-day rolling mean line."""
    fig = px.bar(df, x=date_col, y=y_col, color=color_col,
                 color_discrete_sequence=globals.discrete_teal)
    daily = df.groupby(date_col)[y_col].sum()
    ma = daily.rolling(7, center=True, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=daily.index, y=ma, mode='lines', name='7-day avg',
        line=dict(color=TEAL, width=3, shape='spline', smoothing=1.0),
    ))
    return _apply_theme(fig)


def _agg_profile(df, date_col, value_col, mode, hour_col=None):
    """
    Returns (x_labels, means, stds).
    value_col must be numeric (hours / counts).
    mode: 'week' | 'intraday'
    """
    df = df.copy()
    if mode == 'week':
        df['_g'] = df[date_col].dt.dayofweek
        x_range  = range(7)
        x_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    else:
        if not hour_col or hour_col not in df.columns:
            return None, None, None
        df['_g'] = pd.to_numeric(df[hour_col], errors='coerce')
        df = df.dropna(subset=['_g'])
        df['_g'] = df['_g'].astype(int)
        x_range  = range(24)
        x_labels = [f'{h:02d}:00' for h in range(24)]

    per_day = df.groupby([date_col, '_g'])[value_col].sum()
    agg     = per_day.groupby('_g').agg(['mean', 'std']).reindex(x_range, fill_value=0)
    agg['std'] = agg['std'].fillna(0)
    return x_labels, agg['mean'].values, agg['std'].values


def _ci_fig(x_labels, means, stds):
    """Mean line + ±1σ filled confidence band."""
    upper = np.clip(means + stds, 0, None)
    lower = np.clip(means - stds, 0, None)
    x_rev = list(x_labels)[::-1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(x_labels) + x_rev,
        y=upper.tolist() + lower.tolist()[::-1],
        fill='toself', fillcolor=TEAL_FILL,
        line=dict(color='rgba(0,0,0,0)'), name='±1σ', hoverinfo='skip',
    ))
    fig.add_trace(go.Scatter(
        x=list(x_labels), y=means, mode='lines+markers', name='Mean',
        line=dict(color=TEAL, width=2, shape='spline', smoothing=0.7),
        marker=dict(size=5),
    ))
    return _apply_theme(fig)


def _fmt_h(minutes):
    h, m = int(minutes // 60), int(minutes % 60)
    return f'{h:02d}:{m:02d} h'


def _no_data():
    return plt_mod.not_data_figure()


# ─── Layout ───────────────────────────────────────────────────────────────────

layout = html.Div([

    # ── Flightlog ─────────────────────────────────────────────────────────────
    html.Div(id='ovw-fl-section', style={'display': 'none'}, children=[
        _section_divider('✈  Flightlog'),
        dbc.Row([
            dbc.Col(_kpi('Flight Hours',  'ovw-fl-hours'),    **globals.adaptiv_width_2),
            dbc.Col(_kpi('Flights',       'ovw-fl-flights'),  **globals.adaptiv_width_2),
            dbc.Col(_kpi('Landings',      'ovw-fl-landings'), **globals.adaptiv_width_2),
            dbc.Col(_kpi('Fuel',          'ovw-fl-fuel'),     **globals.adaptiv_width_2),
            dbc.Col(_kpi('Avg / Week',    'ovw-fl-wk'),       **globals.adaptiv_width_2),
            dbc.Col(_kpi('Avg / Day',     'ovw-fl-day'),      **globals.adaptiv_width_2),
        ], className='g-1 mt-1'),
        _two_plots('ovw-fl-ts', 'ovw-fl-agg',
                   'Flight Time over Period',
                   'Average Profile',
                   radio_id='ovw-fl-mode'),
    ]),

    # ── Instructorlog ─────────────────────────────────────────────────────────
    html.Div(id='ovw-il-section', style={'display': 'none'}, children=[
        _section_divider('🎓  Instructorlog'),
        dbc.Row([
            dbc.Col(_kpi('Instruction Hours', 'ovw-il-hours'),    **globals.adaptiv_width_3),
            dbc.Col(_kpi('Sessions',          'ovw-il-sessions'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Trainees',          'ovw-il-trainees'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Avg / Week',        'ovw-il-wk'),       **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        _two_plots('ovw-il-ts', 'ovw-il-agg',
                   'Instruction Time over Period',
                   'Avg Week Profile  (day-of-week)'),
    ]),

    # ── Reservationlog ────────────────────────────────────────────────────────
    html.Div(id='ovw-rl-section', style={'display': 'none'}, children=[
        _section_divider('📅  Reservationlog'),
        dbc.Row([
            dbc.Col(_kpi('Reservations',  'ovw-rl-total'),    **globals.adaptiv_width_3),
            dbc.Col(_kpi('Cancellations', 'ovw-rl-cancelled'),**globals.adaptiv_width_3),
            dbc.Col(_kpi('Cancel Rate',   'ovw-rl-rate'),     **globals.adaptiv_width_3),
            dbc.Col(_kpi('Avg / Week',    'ovw-rl-wk'),       **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        _two_plots('ovw-rl-ts', 'ovw-rl-agg',
                   'Reservations over Period',
                   'Average Profile',
                   radio_id='ovw-rl-mode'),
    ]),

    # ── Finance ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-fi-section', style={'display': 'none'}, children=[
        _section_divider('💰  Finance'),
        dbc.Row([
            dbc.Col(_kpi('Revenue (CHF)', 'ovw-fi-revenue'),  **globals.adaptiv_width_4),
            dbc.Col(_kpi('Invoices',      'ovw-fi-invoices'), **globals.adaptiv_width_4),
            dbc.Col(_kpi('Avg / Invoice', 'ovw-fi-avg'),      **globals.adaptiv_width_4),
        ], className='g-1 mt-1'),
        _two_plots('ovw-fi-ts', 'ovw-fi-agg',
                   'Revenue over Period',
                   'Avg Revenue by Day of Week'),
    ]),

    # ── Members ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-mb-section', style={'display': 'none'}, children=[
        _section_divider('👥  Members'),
        dbc.Row([
            dbc.Col(_kpi('Total Members', 'ovw-mb-total'),   **globals.adaptiv_width_4),
            dbc.Col(_kpi('Active',        'ovw-mb-active'),  **globals.adaptiv_width_4),
            dbc.Col(_kpi('Passive',       'ovw-mb-passive'), **globals.adaptiv_width_4),
        ], className='g-1 mt-1'),
        _two_plots('ovw-mb-ts', 'ovw-mb-type',
                   'Members Joined by Year',
                   'Membership Type Breakdown'),
    ]),

    # ── Techlog ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-tl-section', style={'display': 'none'}, children=[
        _section_divider('🔧  Techlog'),
        dbc.Row([
            dbc.Col(_kpi('Total Entries', 'ovw-tl-total'),    **globals.adaptiv_width_3),
            dbc.Col(_kpi('Open',          'ovw-tl-open'),     **globals.adaptiv_width_3),
            dbc.Col(_kpi('Deferred',      'ovw-tl-deferred'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Closed',        'ovw-tl-closed'),   **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        _two_plots('ovw-tl-ts', 'ovw-tl-agg',
                   'Entries over Period',
                   'Avg Entries by Day of Week'),
    ]),

    html.Div(style={'height': '24px'}),
])


# ─── Visibility callbacks ─────────────────────────────────────────────────────

@callback(Output('ovw-fl-section', 'style'), Input('flightlog-store',      'data'))
def _vis_fl(d): return {} if d else {'display': 'none'}

@callback(Output('ovw-il-section', 'style'), Input('instructorlog-store',  'data'))
def _vis_il(d): return {} if d else {'display': 'none'}

@callback(Output('ovw-rl-section', 'style'), Input('reservationlog-store', 'data'))
def _vis_rl(d): return {} if d else {'display': 'none'}

@callback(Output('ovw-fi-section', 'style'), Input('finance-store',        'data'))
def _vis_fi(d): return {} if d else {'display': 'none'}

@callback(Output('ovw-mb-section', 'style'), Input('member-store',         'data'))
def _vis_mb(d): return {} if d else {'display': 'none'}

@callback(Output('ovw-tl-section', 'style'), Input('techlog-store',        'data'))
def _vis_tl(d): return {} if d else {'display': 'none'}


# ─── Flightlog callbacks ──────────────────────────────────────────────────────

@callback(
    Output('ovw-fl-hours',   'children'),
    Output('ovw-fl-flights', 'children'),
    Output('ovw-fl-landings','children'),
    Output('ovw-fl-fuel',    'children'),
    Output('ovw-fl-wk',      'children'),
    Output('ovw-fl-day',     'children'),
    Input('flightlog-store', 'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fl_kpi(data, start, end):
    if not data:
        return ('—',) * 6
    df   = dp.reload_flightlog_dataframe_from_dict(data, start, end)
    mins = df['Flight Time'].sum().total_seconds() / 60
    days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)
    return (
        _fmt_h(mins),
        f'{len(df)} #',
        f'{df["Landings"].sum():.0f} #',
        f'{df["Fuel"].sum():.0f} L',
        f'{mins/60/(days/7):.2f} h/wk',
        f'{mins/60/days:.3f} h/day',
    )


@callback(
    Output('ovw-fl-ts', 'figure'),
    Input('flightlog-store',  'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fl_ts(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_flightlog_dataframe_from_dict(data, start, end)
    df['Flight Hours'] = df['Flight Time'].dt.total_seconds() / 3600
    filled = dp.agg_by_Day(df, 'Date', 'Aircraft', 'Flight Time', 'Daily_FT')
    return _ts_bar(filled, 'Date', 'Daily_FT', 'Aircraft')


@callback(
    Output('ovw-fl-agg', 'figure'),
    Input('flightlog-store',  'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
    Input('ovw-fl-mode',      'value'),
)
def fl_agg(data, start, end, mode):
    if not data:
        return _no_data()
    df = dp.reload_flightlog_dataframe_from_dict(data, start, end)
    df['Flight Hours'] = df['Flight Time'].dt.total_seconds() / 3600
    # For intraday we need departure hour — derive from the stored date if available
    hour_col = None
    if mode == 'intraday':
        if 'Departure Hour' in df.columns:
            hour_col = 'Departure Hour'
        else:
            # Fall back to week view if departure hour not in old store
            mode = 'week'
    x, means, stds = _agg_profile(df, 'Date', 'Flight Hours', mode, hour_col)
    if x is None:
        return _no_data()
    return _ci_fig(x, means, stds)


# ─── Instructorlog callbacks ──────────────────────────────────────────────────

@callback(
    Output('ovw-il-hours',   'children'),
    Output('ovw-il-sessions','children'),
    Output('ovw-il-trainees','children'),
    Output('ovw-il-wk',      'children'),
    Input('instructorlog-store','data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def il_kpi(data, start, end):
    if not data:
        return ('—',) * 4
    df   = dp.reload_instructor_dataframe_from_dict(data, start, end)
    mins = df['Duration'].sum().total_seconds() / 60
    days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)
    return (
        _fmt_h(mins),
        f'{len(df)} #',
        f'{df["Pilot"].nunique()} #',
        f'{mins/60/(days/7):.2f} h/wk',
    )


@callback(
    Output('ovw-il-ts', 'figure'),
    Input('instructorlog-store','data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def il_ts(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_instructor_dataframe_from_dict(data, start, end)
    filled = dp.agg_by_Day(df, 'Date', 'Instructor', 'Duration', 'Daily_IT')
    return _ts_bar(filled, 'Date', 'Daily_IT', 'Instructor')


@callback(
    Output('ovw-il-agg', 'figure'),
    Input('instructorlog-store','data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def il_agg(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_instructor_dataframe_from_dict(data, start, end)
    df['Instruction Hours'] = df['Duration'].dt.total_seconds() / 3600
    x, means, stds = _agg_profile(df, 'Date', 'Instruction Hours', 'week')
    return _ci_fig(x, means, stds)


# ─── Reservationlog callbacks ─────────────────────────────────────────────────

@callback(
    Output('ovw-rl-total',    'children'),
    Output('ovw-rl-cancelled','children'),
    Output('ovw-rl-rate',     'children'),
    Output('ovw-rl-wk',       'children'),
    Input('reservationlog-store','data'),
    Input('date-picker-range',   'start_date'),
    Input('date-picker-range',   'end_date'),
)
def rl_kpi(data, start, end):
    if not data:
        return ('—',) * 4
    df    = dp.reload_reservation_dataframe_from_dict(data, start, end)
    total = len(df)
    canc  = df['Deleted'].sum()
    days  = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)
    return (
        f'{total} #',
        f'{canc} #',
        f'{canc/total*100:.1f} %' if total else '— %',
        f'{total/(days/7):.1f} /wk',
    )


@callback(
    Output('ovw-rl-ts', 'figure'),
    Input('reservationlog-store','data'),
    Input('date-picker-range',   'start_date'),
    Input('date-picker-range',   'end_date'),
)
def rl_ts(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_reservation_dataframe_from_dict(data, start, end)
    df['Count'] = 1
    daily = (df.groupby(['From', 'Aircraft'])['Count']
               .sum().reset_index()
               .rename(columns={'From': 'Date'}))
    fig = px.bar(daily, x='Date', y='Count', color='Aircraft',
                 color_discrete_sequence=globals.discrete_teal)
    tot = daily.groupby('Date')['Count'].sum()
    ma  = tot.rolling(7, center=True, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=tot.index, y=ma, mode='lines', name='7-day avg',
                             line=dict(color=TEAL, width=3, shape='spline', smoothing=1.0)))
    return _apply_theme(fig)


@callback(
    Output('ovw-rl-agg', 'figure'),
    Input('reservationlog-store','data'),
    Input('date-picker-range',   'start_date'),
    Input('date-picker-range',   'end_date'),
    Input('ovw-rl-mode',         'value'),
)
def rl_agg(data, start, end, mode):
    if not data:
        return _no_data()
    df = dp.reload_reservation_dataframe_from_dict(data, start, end)
    df['Count']    = 1
    df['Date']     = df['From'].dt.normalize()
    hour_col = 'From Hour' if mode == 'intraday' and 'From Hour' in df.columns else None
    x, means, stds = _agg_profile(df, 'Date', 'Count', mode, hour_col)
    if x is None:
        return _no_data()
    return _ci_fig(x, means, stds)


# ─── Finance callbacks ────────────────────────────────────────────────────────

@callback(
    Output('ovw-fi-revenue', 'children'),
    Output('ovw-fi-invoices','children'),
    Output('ovw-fi-avg',     'children'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_kpi(data, start, end):
    if not data:
        return ('—',) * 3
    df  = dp.reload_finance_dataframe_from_dict(data, start, end)
    rev = df['Amount'].sum()
    n   = len(df)
    return (
        f'CHF {rev:,.0f}',
        f'{n} #',
        f'CHF {rev/n:.0f}' if n else '—',
    )


@callback(
    Output('ovw-fi-ts', 'figure'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_ts(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_finance_dataframe_from_dict(data, start, end)
    daily = df.groupby('Payment Date')['Amount'].sum().reset_index()
    ma    = daily['Amount'].rolling(7, center=True, min_periods=1).mean()
    fig   = px.bar(daily, x='Payment Date', y='Amount',
                   color_discrete_sequence=globals.discrete_teal)
    fig.add_trace(go.Scatter(x=daily['Payment Date'], y=ma, mode='lines',
                             name='7-day avg',
                             line=dict(color=TEAL, width=3, shape='spline', smoothing=1.0)))
    return _apply_theme(fig)


@callback(
    Output('ovw-fi-agg', 'figure'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_agg(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_finance_dataframe_from_dict(data, start, end)
    df = df.rename(columns={'Payment Date': 'Date'})
    x, means, stds = _agg_profile(df, 'Date', 'Amount', 'week')
    return _ci_fig(x, means, stds)


# ─── Member callbacks ─────────────────────────────────────────────────────────

@callback(
    Output('ovw-mb-total',  'children'),
    Output('ovw-mb-active', 'children'),
    Output('ovw-mb-passive','children'),
    Input('member-store', 'data'),
)
def mb_kpi(data):
    if not data:
        return ('—',) * 3
    df      = dp.reload_member_dataframe_from_dict(data)
    total   = len(df)
    active  = df['Membership'].str.contains('ktiv|active', case=False, na=False).sum()
    passive = df['Membership'].str.contains('assiv|passive', case=False, na=False).sum()
    return f'{total} #', f'{active} #', f'{passive} #'


@callback(
    Output('ovw-mb-ts', 'figure'),
    Input('member-store', 'data'),
)
def mb_ts(data):
    if not data:
        return _no_data()
    df = dp.reload_member_dataframe_from_dict(data)
    df['Join Date'] = pd.to_datetime(df['Join Date'], errors='coerce')
    df = df.dropna(subset=['Join Date'])
    df['Year'] = df['Join Date'].dt.year
    by_year = df.groupby('Year').size().reset_index(name='New Members')
    fig = px.bar(by_year, x='Year', y='New Members',
                 color_discrete_sequence=globals.discrete_teal)
    return _apply_theme(fig)


@callback(
    Output('ovw-mb-type', 'figure'),
    Input('member-store', 'data'),
)
def mb_type(data):
    if not data:
        return _no_data()
    df   = dp.reload_member_dataframe_from_dict(data)
    by_t = df['Membership'].value_counts().reset_index()
    by_t.columns = ['Membership', 'Count']
    fig  = px.pie(by_t, names='Membership', values='Count',
                  color_discrete_sequence=globals.discrete_teal,
                  hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return _apply_theme(fig)


# ─── Techlog callbacks ────────────────────────────────────────────────────────

@callback(
    Output('ovw-tl-total',   'children'),
    Output('ovw-tl-open',    'children'),
    Output('ovw-tl-deferred','children'),
    Output('ovw-tl-closed',  'children'),
    Input('techlog-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def tl_kpi(data, start, end):
    if not data:
        return ('—',) * 4
    df = dp.reload_techlog_dataframe_from_dict(data, start, end)
    sg = df['Status Group'].value_counts()
    return (
        f'{len(df)} #',
        f'{sg.get("Open", 0)} #',
        f'{sg.get("Deferred", 0)} #',
        f'{sg.get("Closed", 0)} #',
    )


@callback(
    Output('ovw-tl-ts', 'figure'),
    Input('techlog-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def tl_ts(data, start, end):
    if not data:
        return _no_data()
    df    = dp.reload_techlog_dataframe_from_dict(data, start, end)
    daily = df.groupby(['Date', 'Status Group']).size().reset_index(name='Count')
    fig   = px.bar(daily, x='Date', y='Count', color='Status Group',
                   color_discrete_sequence=globals.discrete_teal)
    tot   = daily.groupby('Date')['Count'].sum()
    ma    = tot.rolling(7, center=True, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=tot.index, y=ma, mode='lines', name='7-day avg',
                             line=dict(color=TEAL, width=3, shape='spline', smoothing=1.0)))
    return _apply_theme(fig)


@callback(
    Output('ovw-tl-agg', 'figure'),
    Input('techlog-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def tl_agg(data, start, end):
    if not data:
        return _no_data()
    df = dp.reload_techlog_dataframe_from_dict(data, start, end)
    df['Count'] = 1
    x, means, stds = _agg_profile(df, 'Date', 'Count', 'week')
    return _ci_fig(x, means, stds)
