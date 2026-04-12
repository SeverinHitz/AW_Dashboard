"""
Overview — high-level club health at a glance.

Zone 1: 5 headline KPIs  (cross-dataset where possible) + YoY trend
Zone 2: Charter vs School per aircraft (left) | weekly activity timeline (right)
Zone 3: 4 operational status signals
Zone 4: Navigation cards → sub-pages

Every element degrades gracefully when data is missing.
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

globals.init()
dash.register_page(__name__, path='/overview', name='Overview')

TEAL  = 'rgba(0,203,233,255)'
_GREY = {'color': 'grey'}

# Flight type classification from the 'Flight Type' column (Flugart)
_TYPE_CHARTER = r'Charter|Schnupper|Rund'
_TYPE_SCHOOL  = r'Schulung'

_TYPE_COLORS = {
    'Charter':     globals.discrete_teal[1],
    'School':      globals.discrete_teal[5],
    'Maintenance': '#555555',
    'Other':       '#444444',
}


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _classify_type(series):
    """Map Flight Type strings → 'Charter' | 'School' | 'Maintenance' | 'Other'."""
    s = series.astype(str)
    result = pd.Series('Other', index=series.index)
    result[s.str.contains(_TYPE_CHARTER, case=False, na=False)] = 'Charter'
    result[s.str.contains(_TYPE_SCHOOL,  case=False, na=False)] = 'School'
    result[s.str.contains('Maintenance', case=False, na=False)] = 'Maintenance'
    return result


def _can_trend(start, end):
    return (pd.Timestamp(end) - pd.Timestamp(start)).days <= 365


def _do_trend(now, then):
    try:
        if then == 0:
            raise ZeroDivisionError
        pct = (now / then - 1) * 100
        if pct > 0.05:
            return f'↗ {pct:.1f}%', {'color': 'lightgreen'}
        if pct < -0.05:
            return f'↘ {abs(pct):.1f}%', {'color': 'salmon'}
        return '→ 0.0%', {'color': 'yellow'}
    except Exception:
        return '—', _GREY


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


def _no_data_fig(msg='No data — upload a file on the Import page'):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref='paper', yref='paper',
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color='grey', size=13))
    fig.update_layout(template=globals.plot_template,
                      margin=globals.plot_margin,
                      paper_bgcolor=globals.paper_bgcolor,
                      plot_bgcolor=globals.paper_bgcolor)
    return fig


def _kpi(header, val_id, trend_id=None):
    """Tall KPI card: H4 value + optional H6 trend."""
    body = [html.H4('—', id=val_id)]
    if trend_id:
        body.append(html.H6('—', id=trend_id, style=_GREY))
    return dbc.Card([dbc.CardHeader(header), dbc.CardBody(body)])


def _stat_card(label, value, sub=None, color='white'):
    """Compact status card: coloured value + small sub-label."""
    children = [
        html.Div(label, style={'fontSize': '0.75rem', 'color': '#aaa', 'marginBottom': '2px'}),
        html.Div(value, style={'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': color}),
    ]
    if sub:
        children.append(html.Div(sub, style={'fontSize': '0.75rem', 'color': '#888',
                                              'marginTop': '2px'}))
    return dbc.Card(dbc.CardBody(children),
                    style={'textAlign': 'center', 'minHeight': '90px'})


def _stat_missing(label, hint):
    return _stat_card(label, '—', hint, color='grey')


def _nav_card(name, href, desc):
    return dbc.Card([
        dbc.CardHeader(name, style={'fontWeight': '600'}),
        dbc.CardBody([
            html.P(desc, style={'fontSize': '0.78rem', 'color': '#aaa', 'marginBottom': '10px'}),
            html.A('Explore', href=href,
                   style={'color': TEAL, 'fontSize': '0.85rem', 'fontWeight': '600',
                          'textDecoration': 'none'}),
        ]),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# Layout
# ═══════════════════════════════════════════════════════════════════════════════

_NAV_PAGES = [
    ('Pilot',     '/pilot',     'Flight hours, landings & trends per pilot'),
    ('Aircraft',  '/aircraft',  'Fleet utilization, fuel & maintenance'),
    ('School',    '/school',    'Instruction hours, trainees & instructors'),
    ('Finance',   '/finance',   'Revenue by aircraft, category & timing'),
    ('Member',    '/member',    'Roster, demographics & activity'),
    ('Analytics', '/analytics', 'Cross-dataset deep-dive analytics'),
]

layout = html.Div([

    # ── Zone 1: Headline KPIs ─────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(_kpi('Flight Hours',   'ovw-kpi-hours',   'ovw-kpi-hours-trend'),   **globals.adaptiv_width_2),
        dbc.Col(_kpi('Active Pilots',  'ovw-kpi-pilots',  'ovw-kpi-pilots-trend'),  **globals.adaptiv_width_2),
        dbc.Col(_kpi('Utilization',    'ovw-kpi-util',    'ovw-kpi-util-trend'),    **globals.adaptiv_width_2),
        dbc.Col(_kpi('Revenue',        'ovw-kpi-revenue', 'ovw-kpi-revenue-trend'), **globals.adaptiv_width_2),
        dbc.Col(_kpi('Open Tech Items','ovw-kpi-tech'),                             **globals.adaptiv_width_2),
    ], className='g-1 mt-1'),

    # ── Zone 2: Main charts ───────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader('Charter vs School — flight hours by aircraft'),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id='ovw-chart-split', config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
        dbc.Col(dbc.Card([
            dbc.CardHeader('Activity — weekly flight hours'),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id='ovw-chart-timeline', config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
    ], className='g-1 mt-1'),

    # ── Zone 3: Status row ────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(html.Div(id='ovw-stat-cancel',  children=_stat_missing('Reservation Cancel Rate', 'Upload Reservationlog')), **globals.adaptiv_width_3),
        dbc.Col(html.Div(id='ovw-stat-fleet',   children=_stat_missing('Fleet Availability',       'Upload Techlog')),        **globals.adaptiv_width_3),
        dbc.Col(html.Div(id='ovw-stat-school',  children=_stat_missing('Instruction Hours',        'Upload Instructorlog')),  **globals.adaptiv_width_3),
        dbc.Col(html.Div(id='ovw-stat-members', children=_stat_missing('Roster Size',              'Upload Member data')),    **globals.adaptiv_width_3),
    ], className='g-1 mt-1'),

    # ── Zone 4: Navigate deeper ───────────────────────────────────────────────
    html.Div([
        html.Hr(style={'borderColor': '#3a718d', 'margin': '20px 0 6px 0'}),
        html.Span('Explore in detail', style={'color': '#62a5b4', 'fontWeight': '600',
                                              'fontSize': '0.9rem'}),
    ]),
    dbc.Row([
        dbc.Col(_nav_card(name, href, desc), **globals.adaptiv_width_2)
        for name, href, desc in _NAV_PAGES
    ], className='g-1 mt-1 mb-3'),

])


# ═══════════════════════════════════════════════════════════════════════════════
# Zone 1 — KPI callbacks
# ═══════════════════════════════════════════════════════════════════════════════

@callback(
    Output('ovw-kpi-hours',        'children'),
    Output('ovw-kpi-hours-trend',  'children'),
    Output('ovw-kpi-hours-trend',  'style'),
    Output('ovw-kpi-pilots',       'children'),
    Output('ovw-kpi-pilots-trend', 'children'),
    Output('ovw-kpi-pilots-trend', 'style'),
    Input('flightlog-store',    'data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def kpi_flightlog(data, start, end):
    _no = ('—', '—', _GREY, '—', '—', _GREY)
    if not data:
        return _no
    try:
        fl     = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        hours  = fl['Flight Time'].dt.total_seconds().sum() / 3600
        pilots = fl['Pilot'].nunique()

        h_trend, h_style = '—', _GREY
        p_trend, p_style = '—', _GREY
        if _can_trend(start, end):
            try:
                fl_t    = dp.reload_flightlog_dataframe_from_dict(data, start, end, offset=1)
                hours_t = fl_t['Flight Time'].dt.total_seconds().sum() / 3600
                pilots_t= fl_t['Pilot'].nunique()
                h_trend, h_style = _do_trend(hours,  hours_t)
                p_trend, p_style = _do_trend(pilots, pilots_t)
            except Exception:
                pass

        return f'{hours:.0f} h', h_trend, h_style, f'{pilots} #', p_trend, p_style
    except Exception:
        return _no


@callback(
    Output('ovw-kpi-revenue',       'children'),
    Output('ovw-kpi-revenue-trend', 'children'),
    Output('ovw-kpi-revenue-trend', 'style'),
    Input('finance-store',      'data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def kpi_finance(data, start, end):
    if not data:
        return '—', '—', _GREY
    try:
        df  = dp.reload_finance_dataframe_from_dict(data, start, end)
        rev = df['Amount'].sum()

        trend, style = '—', _GREY
        if _can_trend(start, end):
            try:
                df_t  = dp.reload_finance_dataframe_from_dict(data, start, end, offset=1)
                rev_t = df_t['Amount'].sum()
                trend, style = _do_trend(rev, rev_t)
            except Exception:
                pass

        return f'CHF {rev:,.0f}', trend, style
    except Exception:
        return '—', '—', _GREY


@callback(
    Output('ovw-kpi-util',       'children'),
    Output('ovw-kpi-util-trend', 'children'),
    Output('ovw-kpi-util-trend', 'style'),
    Input('flightlog-store',      'data'),
    Input('reservationlog-store', 'data'),
    Input('date-picker-range',    'start_date'),
    Input('date-picker-range',    'end_date'),
)
def kpi_utilization(fl_data, rl_data, start, end):
    if not fl_data:
        return '—', '—', _GREY
    try:
        fl      = dp.reload_flightlog_dataframe_from_dict(fl_data, start, end)
        flown_h = fl['Flight Time'].dt.total_seconds().sum() / 3600

        trend, style = '—', _GREY

        if rl_data:
            rl    = dp.reload_reservation_dataframe_from_dict(rl_data, start, end)
            res_h = rl[~rl['Deleted']]['Duration'].dt.total_seconds().sum() / 3600
            util  = (flown_h / res_h * 100) if res_h > 0 else 0
            val   = f'{util:.0f}%'

            if _can_trend(start, end):
                try:
                    fl_t    = dp.reload_flightlog_dataframe_from_dict(fl_data, start, end, offset=1)
                    rl_t    = dp.reload_reservation_dataframe_from_dict(rl_data, start, end, offset=1)
                    flown_t = fl_t['Flight Time'].dt.total_seconds().sum() / 3600
                    res_t   = rl_t[~rl_t['Deleted']]['Duration'].dt.total_seconds().sum() / 3600
                    util_t  = (flown_t / res_t * 100) if res_t > 0 else 0
                    trend, style = _do_trend(util, util_t)
                except Exception:
                    pass
        else:
            # Fallback: flights per week when no reservationlog
            days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)
            val  = f'{len(fl) / (days / 7):.1f} flt/wk'

        return val, trend, style
    except Exception:
        return '—', '—', _GREY


@callback(
    Output('ovw-kpi-tech',  'children'),
    Output('ovw-kpi-tech',  'style'),
    Input('techlog-store', 'data'),
)
def kpi_tech(data):
    if not data:
        return '—', {}
    try:
        tl   = pd.DataFrame.from_dict(data)
        open_n = tl['Status Group'].isin(['Open', 'Not Airworthy']).sum() \
                 if 'Status Group' in tl.columns else 0
        color = 'salmon' if open_n > 0 else 'lightgreen'
        return str(open_n), {'color': color, 'fontWeight': 'bold'}
    except Exception:
        return '—', {}


# ═══════════════════════════════════════════════════════════════════════════════
# Zone 2 — Main charts
# ═══════════════════════════════════════════════════════════════════════════════

@callback(
    Output('ovw-chart-split', 'figure'),
    Input('flightlog-store',   'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def chart_split(data, start, end):
    """Horizontal stacked bar: flight hours per aircraft, coloured by purpose."""
    if not data:
        return _no_data_fig('Upload Flightlog to see Charter vs School breakdown')
    try:
        fl = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        if fl.empty:
            return _no_data_fig('No flights in selected period')

        fl['Hours'] = fl['Flight Time'].dt.total_seconds() / 3600
        fl['Type']  = _classify_type(
            fl['Flight Type'] if 'Flight Type' in fl.columns
            else pd.Series('', index=fl.index))

        agg   = fl.groupby(['Aircraft', 'Type'])['Hours'].sum().reset_index()
        order = (fl.groupby('Aircraft')['Hours'].sum()
                   .sort_values(ascending=True).index.tolist())

        # Only keep types that are present
        present_types = agg['Type'].unique().tolist()
        color_map = {t: _TYPE_COLORS.get(t, '#777') for t in present_types}

        fig = px.bar(agg, x='Hours', y='Aircraft', color='Type', barmode='stack',
                     orientation='h', template='none',
                     color_discrete_map=color_map,
                     category_orders={'Aircraft': order,
                                      'Type': ['Charter', 'School', 'Maintenance', 'Other']},
                     labels={'Hours': 'Flight Hours', 'Aircraft': ''})

        # Fleet average line
        fleet_avg = fl.groupby('Aircraft')['Hours'].sum().mean()
        fig.add_vline(x=fleet_avg, line_dash='dot', line_color='grey',
                      annotation_text=f'avg {fleet_avg:.0f}h',
                      annotation_font_color='grey',
                      annotation_position='top right')

        fig = _apply_theme(fig)
        fig.update_layout(legend_title_text='')
        return fig
    except Exception as e:
        return _no_data_fig(f'Error rendering chart: {e}')


@callback(
    Output('ovw-chart-timeline', 'figure'),
    Input('flightlog-store',    'data'),
    Input('date-picker-range',  'start_date'),
    Input('date-picker-range',  'end_date'),
)
def chart_timeline(data, start, end):
    """Stacked bar of weekly hours by type + fleet average hline."""
    if not data:
        return _no_data_fig('Upload Flightlog to see activity timeline')
    try:
        fl = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        if fl.empty:
            return _no_data_fig('No flights in selected period')

        fl['Hours'] = fl['Flight Time'].dt.total_seconds() / 3600
        fl['Week']  = fl['Date'].dt.strftime('%y-W%W')
        fl['Type']  = _classify_type(
            fl['Flight Type'] if 'Flight Type' in fl.columns
            else pd.Series('', index=fl.index))

        weekly = fl.groupby(['Week', 'Type'])['Hours'].sum().reset_index()
        present_types = weekly['Type'].unique().tolist()
        color_map = {t: _TYPE_COLORS.get(t, '#777') for t in present_types}

        fig = px.bar(weekly, x='Week', y='Hours', color='Type', barmode='stack',
                     template='none', color_discrete_map=color_map,
                     category_orders={'Type': ['Charter', 'School', 'Maintenance', 'Other']},
                     labels={'Hours': 'Flight Hours', 'Week': ''})

        # Average weekly hours reference line
        avg_h = fl.groupby('Week')['Hours'].sum().mean()
        fig.add_hline(y=avg_h, line_dash='dot', line_color='grey',
                      annotation_text=f'avg {avg_h:.0f}h/wk',
                      annotation_font_color='grey',
                      annotation_position='top right')

        fig = _apply_theme(fig)
        fig.update_layout(legend_title_text='', xaxis_tickangle=-45)
        return fig
    except Exception as e:
        return _no_data_fig(f'Error rendering chart: {e}')


# ═══════════════════════════════════════════════════════════════════════════════
# Zone 3 — Status cards
# ═══════════════════════════════════════════════════════════════════════════════

@callback(
    Output('ovw-stat-cancel',  'children'),
    Output('ovw-stat-fleet',   'children'),
    Output('ovw-stat-school',  'children'),
    Output('ovw-stat-members', 'children'),
    Input('reservationlog-store', 'data'),
    Input('techlog-store',        'data'),
    Input('instructorlog-store',  'data'),
    Input('member-store',         'data'),
    Input('date-picker-range',    'start_date'),
    Input('date-picker-range',    'end_date'),
)
def status_cards(rl_data, tl_data, il_data, mb_data, start, end):

    # ── 1. Reservation cancel rate ────────────────────────────────────────────
    if rl_data:
        try:
            rl    = dp.reload_reservation_dataframe_from_dict(rl_data, start, end)
            total = len(rl)
            canc  = int(rl['Deleted'].sum()) if 'Deleted' in rl.columns else 0
            rate  = canc / total * 100 if total > 0 else 0
            color = 'lightgreen' if rate < 10 else ('orange' if rate < 20 else 'salmon')
            cancel_card = _stat_card('Reservation Cancel Rate',
                                     f'{rate:.0f}%',
                                     f'{canc} of {total} reservations',
                                     color)
        except Exception:
            cancel_card = _stat_missing('Reservation Cancel Rate', 'Error loading data')
    else:
        cancel_card = _stat_missing('Reservation Cancel Rate', 'Upload Reservationlog')

    # ── 2. Fleet availability (current open items — not date-filtered) ────────
    if tl_data:
        try:
            tl    = pd.DataFrame.from_dict(tl_data)
            if 'Status Group' in tl.columns and 'Aircraft' in tl.columns:
                all_ac  = tl['Aircraft'].dropna().unique()
                blocked = tl[tl['Status Group'].isin(['Open', 'Not Airworthy'])][
                              'Aircraft'].dropna().unique()
                avail   = len(set(all_ac) - set(blocked))
                total_n = len(all_ac)
                pct     = avail / total_n * 100 if total_n > 0 else 100
                color   = 'lightgreen' if pct == 100 else ('orange' if pct >= 75 else 'salmon')
                fleet_card = _stat_card('Fleet Availability',
                                        f'{avail}/{total_n}',
                                        f'{len(blocked)} aircraft with open items',
                                        color)
            else:
                fleet_card = _stat_missing('Fleet Availability', 'Unexpected Techlog format')
        except Exception:
            fleet_card = _stat_missing('Fleet Availability', 'Error loading data')
    else:
        fleet_card = _stat_missing('Fleet Availability', 'Upload Techlog')

    # ── 3. Instruction hours ──────────────────────────────────────────────────
    if il_data:
        try:
            il       = dp.reload_instructor_dataframe_from_dict(il_data, start, end)
            instr_h  = il['Duration'].dt.total_seconds().sum() / 3600
            trainees = il['Pilot'].nunique()
            instrs   = il['Instructor'].nunique() if 'Instructor' in il.columns else 0
            school_card = _stat_card('Instruction Hours',
                                     f'{instr_h:.0f} h',
                                     f'{trainees} trainees, {instrs} instructors',
                                     'white')
        except Exception:
            school_card = _stat_missing('Instruction Hours', 'Error loading data')
    else:
        school_card = _stat_missing('Instruction Hours', 'Upload Instructorlog')

    # ── 4. Roster size ────────────────────────────────────────────────────────
    if mb_data:
        try:
            mb    = dp.reload_member_dataframe_from_dict(mb_data)
            total = len(mb)
            # Count active (Aktiv) vs passive members if column present
            if 'Membership' in mb.columns:
                aktiv   = mb['Membership'].str.contains('ktiv|ctive', case=False, na=False).sum()
                passiv  = total - aktiv
                sub     = f'{aktiv} active, {passiv} passive'
            else:
                sub = f'{total} members total'
            member_card = _stat_card('Roster Size', f'{total}', sub, 'white')
        except Exception:
            member_card = _stat_missing('Roster Size', 'Error loading data')
    else:
        member_card = _stat_missing('Roster Size', 'Upload Member data')

    return cancel_card, fleet_card, school_card, member_card
