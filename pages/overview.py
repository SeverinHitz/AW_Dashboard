"""
Overview page — one subsection per loaded dataset.
Each section shows only when its store is loaded and contains:
  • KPI cards (H4 value + H6 trend) with year-over-year comparison when period ≤ 1 year
  • Left plot:  historical time series
  • Right plot: aggregated/analytical view (dataset-specific)
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

import data_preparation as dp
import trend_calculation as tc
import string_func as sf
import globals
import plot as plt_mod

globals.init()
dash.register_page(__name__, path='/overview', name='Overview')

TEAL      = 'rgba(0,203,233,255)'
TEAL_FILL = 'rgba(79,144,166,0.25)'
_GREY     = {'color': 'grey'}
_NO_TREND = ('—', _GREY)


# ─── layout helpers ───────────────────────────────────────────────────────────

def _kpi(header, val_id, trend_id=None):
    """KPI card — tall style matching the original dashboard look."""
    body = [html.H4('—', id=val_id)]
    if trend_id:
        body.append(html.H6('—', id=trend_id, style=_GREY))
    return dbc.Card([dbc.CardHeader(header), dbc.CardBody(body)])


def _section_divider(label):
    return html.Div([
        html.Hr(style={'borderColor': '#3a718d', 'margin': '16px 0 4px 0'}),
        html.Span(label, style={'color': '#62a5b4', 'fontWeight': '600', 'fontSize': '0.9rem'}),
    ])


def _plot_card(title, graph_id, extra_header=None):
    hdr = [title] + ([extra_header] if extra_header else [])
    return dbc.Card([
        dbc.CardHeader(hdr),
        dbc.CardBody(dcc.Loading(
            dcc.Graph(id=graph_id, config={'displayModeBar': False}), type='dot')),
    ])


def _row2(left_id, left_title, right_id, right_title, right_extra=None):
    return dbc.Row([
        dbc.Col(_plot_card(left_title, left_id),  **globals.adaptiv_width_6),
        dbc.Col(_plot_card(right_title, right_id, right_extra), **globals.adaptiv_width_6),
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


def _ts_bar(df, x, y, color):
    """Stacked bar + 7-day rolling mean."""
    fig = px.bar(df, x=x, y=y, color=color,
                 color_discrete_sequence=globals.discrete_teal,
                 template='none')
    daily = df.groupby(x)[y].sum()
    ma = daily.rolling(7, center=True, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=daily.index, y=ma, mode='lines', name='7-day avg',
                             line=dict(color=TEAL, width=3, shape='spline', smoothing=1.0)))
    return _apply_theme(fig)


def _agg_profile(df, date_col, value_col, mode, hour_col=None):
    """Return (x_labels, means, stds) for week or intraday profile."""
    df = df.copy()
    if mode == 'week':
        df['_g'] = df[date_col].dt.dayofweek
        x_range, x_labels = range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    else:
        if not hour_col or hour_col not in df.columns:
            return None, None, None
        df['_g'] = pd.to_numeric(df[hour_col], errors='coerce')
        df = df.dropna(subset=['_g']); df['_g'] = df['_g'].astype(int)
        x_range, x_labels = range(24), [f'{h:02d}:00' for h in range(24)]
    per_day = df.groupby([date_col, '_g'])[value_col].sum()
    agg = per_day.groupby('_g').agg(['mean', 'std']).reindex(x_range, fill_value=0)
    agg['std'] = agg['std'].fillna(0)
    return x_labels, agg['mean'].values, agg['std'].values


def _ci_fig(x_labels, means, stds):
    upper = np.clip(means + stds, 0, None)
    lower = np.clip(means - stds, 0, None)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(x_labels) + list(x_labels)[::-1],
        y=upper.tolist() + lower.tolist()[::-1],
        fill='toself', fillcolor=TEAL_FILL,
        line=dict(color='rgba(0,0,0,0)'), name='±1σ', hoverinfo='skip'))
    fig.add_trace(go.Scatter(
        x=list(x_labels), y=means, mode='lines+markers', name='Mean',
        line=dict(color=TEAL, width=2, shape='spline', smoothing=0.7),
        marker=dict(size=5)))
    return _apply_theme(fig)


def _no_data():
    return plt_mod.not_data_figure()


def _fmt_h(minutes):
    h, m = int(minutes // 60), int(minutes % 60)
    return f'{h:02d}:{m:02d} h'


def _do_trend(now, then):
    """Return (text, style) for a single KPI comparison."""
    try:
        if then == 0: raise ZeroDivisionError
        pct = (now / then - 1) * 100
        if pct > 1e-6:  return f'↗ {pct:.1f}%', {'color': 'lightgreen'}
        if pct < -1e-6: return f'↘ {pct:.1f}%', {'color': 'salmon'}
        return '→ 0.0%', {'color': 'yellow'}
    except Exception:
        return '—', _GREY


def _can_trend(start, end):
    """True when the selected period is ≤ 1 year."""
    return (pd.Timestamp(end) - pd.Timestamp(start)).days <= 365


# ─── Layout ───────────────────────────────────────────────────────────────────

layout = html.Div([

    # ── Flightlog ─────────────────────────────────────────────────────────────
    html.Div(id='ovw-fl-section', style={'display': 'none'}, children=[
        _section_divider('✈  Flightlog'),
        dbc.Row([
            dbc.Col(_kpi('Flight Hours',  'ovw-fl-hours',   'ovw-fl-hours-t'),   **globals.adaptiv_width_2),
            dbc.Col(_kpi('Flights',       'ovw-fl-flights', 'ovw-fl-flights-t'), **globals.adaptiv_width_2),
            dbc.Col(_kpi('Landings',      'ovw-fl-ldg',     'ovw-fl-ldg-t'),     **globals.adaptiv_width_2),
            dbc.Col(_kpi('Fuel',          'ovw-fl-fuel',    'ovw-fl-fuel-t'),    **globals.adaptiv_width_2),
            dbc.Col(_kpi('Avg / Week',    'ovw-fl-wk'),                          **globals.adaptiv_width_2),
            dbc.Col(_kpi('Avg / Day',     'ovw-fl-day'),                         **globals.adaptiv_width_2),
        ], className='g-1 mt-1'),
        _row2('ovw-fl-ts',  'Flight Time over Period',
              'ovw-fl-agg', 'Average Profile',
              right_extra=dbc.RadioItems(
                  id='ovw-fl-mode',
                  options=[{'label': ' Week', 'value': 'week'},
                           {'label': ' Intraday', 'value': 'intraday'}],
                  value='week', inline=True,
                  style={'display': 'inline-block', 'fontSize': '0.78rem', 'marginLeft': '12px'})),
    ]),

    # ── Instructorlog ─────────────────────────────────────────────────────────
    html.Div(id='ovw-il-section', style={'display': 'none'}, children=[
        _section_divider('🎓  Instructorlog'),
        dbc.Row([
            dbc.Col(_kpi('Instruction Hours', 'ovw-il-hours',    'ovw-il-hours-t'),    **globals.adaptiv_width_3),
            dbc.Col(_kpi('Sessions',          'ovw-il-sessions', 'ovw-il-sessions-t'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Trainees',          'ovw-il-trainees', 'ovw-il-trainees-t'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Avg / Week',        'ovw-il-wk'),                            **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        _row2('ovw-il-ts',  'Instruction Time over Period',
              'ovw-il-agg', 'Avg Week Profile (day-of-week) ±1σ'),
    ]),

    # ── Reservationlog ────────────────────────────────────────────────────────
    html.Div(id='ovw-rl-section', style={'display': 'none'}, children=[
        _section_divider('📅  Reservationlog'),
        dbc.Row([
            dbc.Col(_kpi('Reservations',  'ovw-rl-total',     'ovw-rl-total-t'),     **globals.adaptiv_width_3),
            dbc.Col(_kpi('Cancellations', 'ovw-rl-cancelled', 'ovw-rl-cancelled-t'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Cancel Rate',   'ovw-rl-rate'),                            **globals.adaptiv_width_3),
            dbc.Col(_kpi('Avg / Week',    'ovw-rl-wk'),                              **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        _row2('ovw-rl-left',  'Reserved vs Flown Hours per Week',
              'ovw-rl-right', 'Active vs Cancelled Reservations over Time'),
    ]),

    # ── Finance ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-fi-section', style={'display': 'none'}, children=[
        _section_divider('💰  Finance'),
        dbc.Row([
            dbc.Col(_kpi('Revenue (CHF)', 'ovw-fi-revenue',  'ovw-fi-revenue-t'),  **globals.adaptiv_width_4),
            dbc.Col(_kpi('Invoices',      'ovw-fi-invoices', 'ovw-fi-invoices-t'), **globals.adaptiv_width_4),
            dbc.Col(_kpi('Avg / Invoice', 'ovw-fi-avg'),                           **globals.adaptiv_width_4),
        ], className='g-1 mt-1'),
        _row2('ovw-fi-left',  'Revenue by Aircraft (Charter vs Training)',
              'ovw-fi-right', 'Days from Invoice to Payment'),
    ]),

    # ── Members ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-mb-section', style={'display': 'none'}, children=[
        _section_divider('👥  Members'),
        dbc.Row([
            dbc.Col(_kpi('Total Members', 'ovw-mb-total'),   **globals.adaptiv_width_4),
            dbc.Col(_kpi('Active',        'ovw-mb-active'),  **globals.adaptiv_width_4),
            dbc.Col(_kpi('Passive',       'ovw-mb-passive'), **globals.adaptiv_width_4),
        ], className='g-1 mt-1'),
        _row2('ovw-mb-last',  'Days Since Last Flight (members)',
              'ovw-mb-type',  'Membership Type Breakdown'),
    ]),

    # ── Techlog ───────────────────────────────────────────────────────────────
    html.Div(id='ovw-tl-section', style={'display': 'none'}, children=[
        _section_divider('🔧  Techlog'),
        dbc.Row([
            dbc.Col(_kpi('Total Entries', 'ovw-tl-total',    'ovw-tl-total-t'),    **globals.adaptiv_width_3),
            dbc.Col(_kpi('Open',          'ovw-tl-open',     'ovw-tl-open-t'),     **globals.adaptiv_width_3),
            dbc.Col(_kpi('Deferred',      'ovw-tl-deferred', 'ovw-tl-deferred-t'), **globals.adaptiv_width_3),
            dbc.Col(_kpi('Closed',        'ovw-tl-closed'),                        **globals.adaptiv_width_3),
        ], className='g-1 mt-1'),
        dbc.Row([
            dbc.Col(_plot_card('Entries per Aircraft by Status', 'ovw-tl-chart'),
                    **globals.adaptiv_width_12),
        ], className='g-1 mt-1'),
    ]),

    html.Div(style={'height': '24px'}),
])


# ─── Visibility ───────────────────────────────────────────────────────────────

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


# ─── Flightlog ────────────────────────────────────────────────────────────────

@callback(
    Output('ovw-fl-hours',    'children'), Output('ovw-fl-hours-t',   'children'), Output('ovw-fl-hours-t',   'style'),
    Output('ovw-fl-flights',  'children'), Output('ovw-fl-flights-t', 'children'), Output('ovw-fl-flights-t', 'style'),
    Output('ovw-fl-ldg',      'children'), Output('ovw-fl-ldg-t',     'children'), Output('ovw-fl-ldg-t',     'style'),
    Output('ovw-fl-fuel',     'children'), Output('ovw-fl-fuel-t',    'children'), Output('ovw-fl-fuel-t',    'style'),
    Output('ovw-fl-wk',       'children'),
    Output('ovw-fl-day',      'children'),
    Input('flightlog-store',  'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fl_kpi(data, start, end):
    na = ('—',) * 14
    if not data: return na
    df   = dp.reload_flightlog_dataframe_from_dict(data, start, end)
    mins = df['Flight Time'].sum().total_seconds() / 60
    n_fl = len(df)
    n_ld = df['Landings'].sum()
    fuel = df['Fuel'].sum()
    days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)

    v_hrs  = _fmt_h(mins)
    v_fl   = f'{n_fl} #'
    v_ld   = f'{n_ld:.0f} #'
    v_fuel = f'{fuel:.0f} L'
    v_wk   = f'{mins/60/(days/7):.2f} h/wk'
    v_day  = f'{mins/60/days:.3f} h/day'

    try:
        if not _can_trend(start, end): raise ValueError
        dft = dp.reload_flightlog_dataframe_from_dict(data, start, end, offset=1)
        if len(dft) < 1: raise ValueError
        t_hrs  = _do_trend(mins, dft['Flight Time'].sum().total_seconds()/60)
        t_fl   = _do_trend(n_fl, len(dft))
        t_ld   = _do_trend(n_ld, dft['Landings'].sum())
        t_fuel = _do_trend(fuel, dft['Fuel'].sum())
    except Exception:
        t_hrs = t_fl = t_ld = t_fuel = _NO_TREND

    return (v_hrs,  t_hrs[0],  t_hrs[1],
            v_fl,   t_fl[0],   t_fl[1],
            v_ld,   t_ld[0],   t_ld[1],
            v_fuel, t_fuel[0], t_fuel[1],
            v_wk, v_day)


@callback(
    Output('ovw-fl-ts', 'figure'),
    Input('flightlog-store',  'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fl_ts(data, start, end):
    if not data: return _no_data()
    df = dp.reload_flightlog_dataframe_from_dict(data, start, end)
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
    if not data: return _no_data()
    df = dp.reload_flightlog_dataframe_from_dict(data, start, end)
    df['Flight Hours'] = df['Flight Time'].dt.total_seconds() / 3600
    hour_col = 'Departure Hour' if (mode == 'intraday' and 'Departure Hour' in df.columns) else None
    if mode == 'intraday' and hour_col is None: mode = 'week'
    x, means, stds = _agg_profile(df, 'Date', 'Flight Hours', mode, hour_col)
    return _ci_fig(x, means, stds) if x is not None else _no_data()


# ─── Instructorlog ────────────────────────────────────────────────────────────

@callback(
    Output('ovw-il-hours',    'children'), Output('ovw-il-hours-t',    'children'), Output('ovw-il-hours-t',    'style'),
    Output('ovw-il-sessions', 'children'), Output('ovw-il-sessions-t', 'children'), Output('ovw-il-sessions-t', 'style'),
    Output('ovw-il-trainees', 'children'), Output('ovw-il-trainees-t', 'children'), Output('ovw-il-trainees-t', 'style'),
    Output('ovw-il-wk',       'children'),
    Input('instructorlog-store','data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def il_kpi(data, start, end):
    na = ('—',) * 10
    if not data: return na
    df   = dp.reload_instructor_dataframe_from_dict(data, start, end)
    mins = df['Duration'].sum().total_seconds() / 60
    n_s  = len(df)
    n_t  = df['Pilot'].nunique()
    days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)

    try:
        if not _can_trend(start, end): raise ValueError
        dft = dp.reload_instructor_dataframe_from_dict(data, start, end, offset=1)
        if len(dft) < 1: raise ValueError
        t_h = _do_trend(mins, dft['Duration'].sum().total_seconds()/60)
        t_s = _do_trend(n_s, len(dft))
        t_t = _do_trend(n_t, dft['Pilot'].nunique())
    except Exception:
        t_h = t_s = t_t = _NO_TREND

    return (_fmt_h(mins), t_h[0], t_h[1],
            f'{n_s} #',  t_s[0], t_s[1],
            f'{n_t} #',  t_t[0], t_t[1],
            f'{mins/60/(days/7):.2f} h/wk')


@callback(
    Output('ovw-il-ts', 'figure'),
    Input('instructorlog-store','data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def il_ts(data, start, end):
    if not data: return _no_data()
    df = dp.reload_instructor_dataframe_from_dict(data, start, end)
    filled = dp.agg_by_Day(df, 'Date', 'Instructor', 'Duration', 'Daily_IT')
    return _ts_bar(filled, 'Date', 'Daily_IT', 'Instructor')


@callback(
    Output('ovw-il-agg', 'figure'),
    Input('instructorlog-store','data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def il_agg(data, start, end):
    if not data: return _no_data()
    df = dp.reload_instructor_dataframe_from_dict(data, start, end)
    df['Instruction Hours'] = df['Duration'].dt.total_seconds() / 3600
    x, means, stds = _agg_profile(df, 'Date', 'Instruction Hours', 'week')
    return _ci_fig(x, means, stds)


# ─── Reservationlog ───────────────────────────────────────────────────────────

@callback(
    Output('ovw-rl-total',     'children'), Output('ovw-rl-total-t',     'children'), Output('ovw-rl-total-t',     'style'),
    Output('ovw-rl-cancelled', 'children'), Output('ovw-rl-cancelled-t', 'children'), Output('ovw-rl-cancelled-t', 'style'),
    Output('ovw-rl-rate',      'children'),
    Output('ovw-rl-wk',        'children'),
    Input('reservationlog-store','data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def rl_kpi(data, start, end):
    na = ('—',) * 8
    if not data: return na
    df    = dp.reload_reservation_dataframe_from_dict(data, start, end)
    total = len(df)
    canc  = int(df['Deleted'].sum())
    rate  = canc / total * 100 if total > 0 else 0
    days  = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)

    try:
        if not _can_trend(start, end): raise ValueError
        dft = dp.reload_reservation_dataframe_from_dict(data, start, end, offset=1)
        if len(dft) < 1: raise ValueError
        t_tot  = _do_trend(total, len(dft))
        t_canc = _do_trend(canc, int(dft['Deleted'].sum()))
    except Exception:
        t_tot = t_canc = _NO_TREND

    return (f'{total} #', t_tot[0],  t_tot[1],
            f'{canc} #',  t_canc[0], t_canc[1],
            f'{rate:.1f} %',
            f'{total/(days/7):.1f} /wk')


@callback(
    Output('ovw-rl-left', 'figure'),
    Input('reservationlog-store','data'),
    Input('flightlog-store',    'data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def rl_left(rl_data, fl_data, start, end):
    """Reserved vs flown hours per week."""
    if not rl_data: return _no_data()
    rl = dp.reload_reservation_dataframe_from_dict(rl_data, start, end)
    rl_active = rl[~rl['Deleted']].copy()
    rl_active['Week'] = rl_active['From'].dt.strftime('%y-W%W')
    weekly_res = (rl_active.groupby('Week')['Duration']
                  .sum().dt.total_seconds().div(3600).rename('Reserved h'))

    series = [weekly_res]
    if fl_data:
        fl = dp.reload_flightlog_dataframe_from_dict(fl_data, start, end)
        fl['Week'] = fl['Date'].dt.strftime('%y-W%W')
        weekly_fl = (fl.groupby('Week')['Flight Time']
                     .sum().dt.total_seconds().div(3600).rename('Flown h'))
        series.append(weekly_fl)

    combined = pd.concat(series, axis=1).fillna(0).reset_index()
    combined = combined.melt(id_vars='Week', var_name='Type', value_name='Hours')

    fig = px.bar(combined, x='Week', y='Hours', color='Type', barmode='group',
                 color_discrete_sequence=globals.discrete_teal, template='none')
    return _apply_theme(fig)


@callback(
    Output('ovw-rl-right', 'figure'),
    Input('reservationlog-store','data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def rl_right(data, start, end):
    """Active vs Cancelled reservations over time (weekly stacked bar)."""
    if not data: return _no_data()
    df = dp.reload_reservation_dataframe_from_dict(data, start, end)
    df['Week'] = df['From'].dt.strftime('%y-W%W')
    weekly = (df.groupby(['Week', 'Deleted']).size()
                .unstack(fill_value=0)
                .rename(columns={False: 'Active', True: 'Cancelled'}))
    if 'Active'    not in weekly.columns: weekly['Active']    = 0
    if 'Cancelled' not in weekly.columns: weekly['Cancelled'] = 0
    weekly = weekly.reset_index().melt(id_vars='Week', var_name='Status', value_name='Count')

    fig = px.bar(weekly, x='Week', y='Count', color='Status', barmode='stack',
                 color_discrete_map={'Active': globals.discrete_teal[0],
                                     'Cancelled': globals.discrete_teal[4]},
                 template='none')
    return _apply_theme(fig)


# ─── Finance ──────────────────────────────────────────────────────────────────

@callback(
    Output('ovw-fi-revenue',  'children'), Output('ovw-fi-revenue-t',  'children'), Output('ovw-fi-revenue-t',  'style'),
    Output('ovw-fi-invoices', 'children'), Output('ovw-fi-invoices-t', 'children'), Output('ovw-fi-invoices-t', 'style'),
    Output('ovw-fi-avg',      'children'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_kpi(data, start, end):
    na = ('—',) * 7
    if not data: return na
    df  = dp.reload_finance_dataframe_from_dict(data, start, end)
    rev = df['Amount'].sum()
    n   = len(df)
    avg = rev / n if n > 0 else 0

    try:
        if not _can_trend(start, end): raise ValueError
        dft = dp.reload_finance_dataframe_from_dict(data, start, end, offset=1)
        if len(dft) < 1: raise ValueError
        t_rev = _do_trend(rev, dft['Amount'].sum())
        t_n   = _do_trend(n,   len(dft))
    except Exception:
        t_rev = t_n = _NO_TREND

    return (f'CHF {rev:,.0f}', t_rev[0], t_rev[1],
            f'{n} #',           t_n[0],   t_n[1],
            f'CHF {avg:,.0f}')


@callback(
    Output('ovw-fi-left', 'figure'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_left(data, start, end):
    """Revenue split by aircraft (Charter vs Training), horizontal grouped bar."""
    if not data: return _no_data()
    df = dp.reload_finance_dataframe_from_dict(data, start, end)

    # Filter to aircraft rows only
    ac = df[df['cost_centre'].str.startswith('Aircraft', na=False)].copy()
    if ac.empty: return _no_data()

    agg = (ac.groupby(['ac_reg', 'flight_type'])['Amount']
             .sum().unstack(fill_value=0).round(0))

    plot_types = [c for c in ['Charter', 'Training'] if c in agg.columns]
    agg = agg[plot_types].reset_index().sort_values(
        plot_types[0] if plot_types else 'ac_reg', ascending=True)

    agg_melt = agg.melt(id_vars='ac_reg', var_name='Type', value_name='CHF')
    fig = px.bar(agg_melt, x='CHF', y='ac_reg', color='Type', barmode='group',
                 orientation='h', color_discrete_sequence=globals.discrete_teal,
                 labels={'ac_reg': 'Aircraft', 'CHF': 'CHF incl. VAT'},
                 template='none')
    return _apply_theme(fig)


@callback(
    Output('ovw-fi-right', 'figure'),
    Input('finance-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def fi_right(data, start, end):
    """Histogram of days from invoice date to payment date."""
    if not data: return _no_data()
    df = dp.reload_finance_dataframe_from_dict(data, start, end)
    if 'Days to Payment' not in df.columns: return _no_data()

    dtp = df['Days to Payment'].dropna()
    dtp = dtp[dtp.between(-60, 400)]   # trim outliers
    if dtp.empty: return _no_data()

    fig = px.histogram(dtp, nbins=60,
                       color_discrete_sequence=[globals.discrete_teal[2]],
                       labels={'value': 'Days (Invoice → Payment)', 'count': 'Invoices'},
                       template='none')
    fig.add_vline(x=0,    line_dash='dash', line_color='grey',  annotation_text='Same day')
    fig.add_vline(x=dtp.median(), line_dash='dot', line_color=TEAL,
                  annotation_text=f'Median {dtp.median():.0f}d')
    return _apply_theme(fig)


# ─── Members ──────────────────────────────────────────────────────────────────

@callback(
    Output('ovw-mb-total',  'children'),
    Output('ovw-mb-active', 'children'),
    Output('ovw-mb-passive','children'),
    Input('member-store', 'data'),
)
def mb_kpi(data):
    if not data: return '—', '—', '—'
    df      = dp.reload_member_dataframe_from_dict(data)
    total   = len(df)
    active  = df['Membership'].str.contains('ktiv|ctive', case=False, na=False).sum()
    passive = df['Membership'].str.contains('assiv|assive', case=False, na=False).sum()
    return f'{total} #', f'{active} #', f'{passive} #'


@callback(
    Output('ovw-mb-last', 'figure'),
    Input('member-store',     'data'),
    Input('flightlog-store',  'data'),
)
def mb_last(mb_data, fl_data):
    """Histogram: days since each member last flew (as of today)."""
    if not mb_data or not fl_data: return _no_data()

    mb = dp.reload_member_dataframe_from_dict(mb_data)

    # Load full flightlog (all time) to find last flight per pilot
    fl_full = dp.reload_flightlog_dataframe_from_dict(
        fl_data, '2000-01-01', '2099-12-31')
    last_flight = fl_full.groupby('Pilot')['Date'].max().rename('Last Flight')

    today = pd.Timestamp.today().normalize()
    merged = mb.join(last_flight, on='Pilot' if 'Pilot' in mb.columns else None, how='left')
    if 'Last Flight' not in merged.columns:
        # join by constructing Pilot from member names
        mb['Pilot'] = mb.get('First Name', mb.get('Vorname', '')).str.strip() + \
                      ' ' + mb.get('Last Name', mb.get('Name', '')).str.strip()
        merged = mb.merge(last_flight.reset_index(), on='Pilot', how='left')

    merged['Days Since Last Flight'] = (today - merged['Last Flight']).dt.days
    valid = merged['Days Since Last Flight'].dropna()
    if valid.empty: return _no_data()

    fig = px.histogram(valid, nbins=40,
                       color_discrete_sequence=[globals.discrete_teal[1]],
                       labels={'value': 'Days since last flight', 'count': 'Members'},
                       template='none')
    med = valid.median()
    fig.add_vline(x=med, line_dash='dot', line_color=TEAL,
                  annotation_text=f'Median {med:.0f}d')
    return _apply_theme(fig)


@callback(
    Output('ovw-mb-type', 'figure'),
    Input('member-store', 'data'),
)
def mb_type(data):
    if not data: return _no_data()
    df   = dp.reload_member_dataframe_from_dict(data)
    by_t = df['Membership'].value_counts().reset_index()
    by_t.columns = ['Membership', 'Count']
    fig  = px.pie(by_t, names='Membership', values='Count',
                  color_discrete_sequence=globals.discrete_teal, hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return _apply_theme(fig)


# ─── Techlog ──────────────────────────────────────────────────────────────────

@callback(
    Output('ovw-tl-total',    'children'), Output('ovw-tl-total-t',    'children'), Output('ovw-tl-total-t',    'style'),
    Output('ovw-tl-open',     'children'), Output('ovw-tl-open-t',     'children'), Output('ovw-tl-open-t',     'style'),
    Output('ovw-tl-deferred', 'children'), Output('ovw-tl-deferred-t', 'children'), Output('ovw-tl-deferred-t', 'style'),
    Output('ovw-tl-closed',   'children'),
    Input('techlog-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def tl_kpi(data, start, end):
    na = ('—',) * 10
    if not data: return na
    df = dp.reload_techlog_dataframe_from_dict(data, start, end)
    sg = df['Status Group'].value_counts() if 'Status Group' in df.columns else pd.Series(dtype=int)
    total, n_open, n_def = len(df), sg.get('Open', 0), sg.get('Deferred', 0)
    n_cls = sg.get('Closed', 0)

    try:
        if not _can_trend(start, end): raise ValueError
        dft = dp.reload_techlog_dataframe_from_dict(data, start, end, offset=1)
        if len(dft) < 1: raise ValueError
        sgt = dft['Status Group'].value_counts() if 'Status Group' in dft.columns else pd.Series(dtype=int)
        t_tot = _do_trend(total,  len(dft))
        t_opn = _do_trend(n_open, sgt.get('Open', 0))
        t_def = _do_trend(n_def,  sgt.get('Deferred', 0))
    except Exception:
        t_tot = t_opn = t_def = _NO_TREND

    return (f'{total} #',  t_tot[0], t_tot[1],
            f'{n_open} #', t_opn[0], t_opn[1],
            f'{n_def} #',  t_def[0], t_def[1],
            f'{n_cls} #')


@callback(
    Output('ovw-tl-chart', 'figure'),
    Input('techlog-store',    'data'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date'),
)
def tl_chart(data, start, end):
    """Stacked bar: entries per aircraft by status group."""
    if not data: return _no_data()
    df = dp.reload_techlog_dataframe_from_dict(data, start, end)
    agg = (df.groupby(['Aircraft', 'Status Group']).size()
             .reset_index(name='Count')
             .sort_values('Count', ascending=False))
    fig = px.bar(agg, x='Aircraft', y='Count', color='Status Group',
                 color_discrete_sequence=globals.discrete_teal,
                 barmode='stack', template='none')
    return _apply_theme(fig)
