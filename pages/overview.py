"""
Overview — high-level club health at a glance.

Zone 1: 6 headline KPIs  (Flights, Hours, Landings, Active Pilots, Instruction Time, Revenue)
         + YoY trend for each
Zone 2: GitHub-style activity heatmap (full width)
Zone 3: Flight-type pie (left)  |  Aircraft flight-count bar (right)
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
_TYPE_CHARTER  = r'Charter|Schnupper|Rund'
_TYPE_SCHOOL   = r'Schulung'

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
    result[s.str.contains(_TYPE_CHARTER,   case=False, na=False)] = 'Charter'
    result[s.str.contains(_TYPE_SCHOOL,    case=False, na=False)] = 'School'
    result[s.str.contains('Maintenance',   case=False, na=False)] = 'Maintenance'
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


def _kpi_card(header, val_id, trend_id):
    """KPI card with value + trend line."""
    return dbc.Card([
        dbc.CardHeader(header, style={'fontSize': '0.78rem', 'padding': '6px 10px'}),
        dbc.CardBody([
            html.H4('—', id=val_id, style={'marginBottom': '2px'}),
            html.Div('—', id=trend_id, style={**_GREY, 'fontSize': '0.82rem'}),
        ], style={'padding': '8px 10px'}),
    ])


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

    # ── Zone 1: 6 KPIs ────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(_kpi_card('Flights',          'ovw-kpi-flights',   'ovw-kpi-flights-trend'),   **globals.adaptiv_width_2),
        dbc.Col(_kpi_card('Flight Hours',     'ovw-kpi-hours',     'ovw-kpi-hours-trend'),     **globals.adaptiv_width_2),
        dbc.Col(_kpi_card('Landings',         'ovw-kpi-landings',  'ovw-kpi-landings-trend'),  **globals.adaptiv_width_2),
        dbc.Col(_kpi_card('Active Pilots',    'ovw-kpi-pilots',    'ovw-kpi-pilots-trend'),    **globals.adaptiv_width_2),
        dbc.Col(_kpi_card('Instruction Time', 'ovw-kpi-instrtime', 'ovw-kpi-instrtime-trend'), **globals.adaptiv_width_2),
        dbc.Col(_kpi_card('Revenue',          'ovw-kpi-revenue',   'ovw-kpi-revenue-trend'),   **globals.adaptiv_width_2),
    ], className='g-1 mt-1'),

    # ── Zone 2: Activity heatmap (full width) ─────────────────────────────────
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader('Daily Flight Activity'),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id='ovw-chart-heatmap', config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_12),
    ], className='g-1 mt-1'),

    # ── Zone 3: Pie + Aircraft count ──────────────────────────────────────────
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader('Flight Type Breakdown'),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id='ovw-chart-typepie', config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
        dbc.Col(dbc.Card([
            dbc.CardHeader('Flights per Aircraft'),
            dbc.CardBody(dcc.Loading(
                dcc.Graph(id='ovw-chart-aircraftcount', config={'displayModeBar': False}),
                type='dot')),
        ]), **globals.adaptiv_width_6),
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
    Output('ovw-kpi-flights',       'children'),
    Output('ovw-kpi-flights-trend', 'children'),
    Output('ovw-kpi-flights-trend', 'style'),
    Output('ovw-kpi-hours',         'children'),
    Output('ovw-kpi-hours-trend',   'children'),
    Output('ovw-kpi-hours-trend',   'style'),
    Output('ovw-kpi-landings',      'children'),
    Output('ovw-kpi-landings-trend','children'),
    Output('ovw-kpi-landings-trend','style'),
    Output('ovw-kpi-pilots',        'children'),
    Output('ovw-kpi-pilots-trend',  'children'),
    Output('ovw-kpi-pilots-trend',  'style'),
    Input('flightlog-store',   'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def kpi_flightlog(data, start, end):
    _no = ('—', '—', _GREY) * 4
    if not data:
        return _no
    try:
        fl      = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        flights = len(fl)
        hours   = fl['Flight Time'].dt.total_seconds().sum() / 3600
        landings= int(fl['Landings'].sum()) if 'Landings' in fl.columns else 0
        pilots  = fl['Pilot'].nunique()

        f_trend, f_style = '—', _GREY
        h_trend, h_style = '—', _GREY
        l_trend, l_style = '—', _GREY
        p_trend, p_style = '—', _GREY

        if _can_trend(start, end):
            try:
                fl_t     = dp.reload_flightlog_dataframe_from_dict(data, start, end, offset=1)
                flights_t= len(fl_t)
                hours_t  = fl_t['Flight Time'].dt.total_seconds().sum() / 3600
                landings_t = int(fl_t['Landings'].sum()) if 'Landings' in fl_t.columns else 0
                pilots_t = fl_t['Pilot'].nunique()
                f_trend, f_style = _do_trend(flights,  flights_t)
                h_trend, h_style = _do_trend(hours,    hours_t)
                l_trend, l_style = _do_trend(landings, landings_t)
                p_trend, p_style = _do_trend(pilots,   pilots_t)
            except Exception:
                pass

        return (
            f'{flights}',      f_trend, f_style,
            f'{hours:.0f} h',  h_trend, h_style,
            f'{landings}',     l_trend, l_style,
            f'{pilots}',       p_trend, p_style,
        )
    except Exception:
        return _no


@callback(
    Output('ovw-kpi-instrtime',       'children'),
    Output('ovw-kpi-instrtime-trend', 'children'),
    Output('ovw-kpi-instrtime-trend', 'style'),
    Input('instructorlog-store', 'data'),
    Input('date-picker-range',   'start_date'),
    Input('date-picker-range',   'end_date'),
)
def kpi_instrtime(data, start, end):
    if not data:
        return '—', '—', _GREY
    try:
        il     = dp.reload_instructor_dataframe_from_dict(data, start, end)
        instr_h = il['Duration'].dt.total_seconds().sum() / 3600

        trend, style = '—', _GREY
        if _can_trend(start, end):
            try:
                il_t     = dp.reload_instructor_dataframe_from_dict(data, start, end, offset=1)
                instr_h_t = il_t['Duration'].dt.total_seconds().sum() / 3600
                trend, style = _do_trend(instr_h, instr_h_t)
            except Exception:
                pass

        return f'{instr_h:.0f} h', trend, style
    except Exception:
        return '—', '—', _GREY


@callback(
    Output('ovw-kpi-revenue',       'children'),
    Output('ovw-kpi-revenue-trend', 'children'),
    Output('ovw-kpi-revenue-trend', 'style'),
    Input('finance-store',     'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
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


# ═══════════════════════════════════════════════════════════════════════════════
# Zone 2 — GitHub-style activity heatmap
# ═══════════════════════════════════════════════════════════════════════════════

@callback(
    Output('ovw-chart-heatmap', 'figure'),
    Input('flightlog-store',   'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def chart_heatmap(data, start, end):
    """GitHub contribution-style calendar heatmap of daily flight hours."""
    if not data:
        return _no_data_fig('Upload Flightlog to see activity heatmap')
    try:
        fl = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        if fl.empty:
            return _no_data_fig('No flights in selected period')

        # Sum flight hours per calendar day using date strings as key to avoid
        # any timezone / dtype mismatch in the merge
        fl['_day'] = fl['Date'].dt.strftime('%Y-%m-%d')
        fl['Hours'] = fl['Flight Time'].dt.total_seconds() / 3600
        daily = fl.groupby('_day')['Hours'].sum().reset_index()
        daily.columns = ['_day', 'Hours']

        # Full date range as strings
        date_range = pd.date_range(
            start=pd.Timestamp(start).normalize(),
            end=pd.Timestamp(end).normalize(),
            freq='D')
        full = pd.DataFrame({'Date': date_range})
        full['_day'] = full['Date'].dt.strftime('%Y-%m-%d')
        full = full.merge(daily, on='_day', how='left')
        # Keep NaN (and treat 0) as "no activity" → transparent cell
        full['Hours'] = full['Hours'].replace(0.0, np.nan)

        # Week index (column) and day-of-week (row, 0=Mon … 6=Sun)
        start_dt = full['Date'].min()
        offset_days = int(start_dt.dayofweek)      # align grid to Monday
        full['Week'] = (full['Date'] - (start_dt - pd.Timedelta(days=offset_days))).dt.days // 7
        full['DOW']  = full['Date'].dt.dayofweek   # 0=Mon, 6=Sun

        n_weeks = int(full['Week'].max()) + 1
        # Build z matrix: rows=DOW (0..6), cols=week — NaN = transparent
        z    = np.full((7, n_weeks), np.nan)
        text = np.full((7, n_weeks), '', dtype=object)

        for _, row in full.iterrows():
            w, d = int(row['Week']), int(row['DOW'])
            h = row['Hours']  # may be NaN
            z[d, w] = h
            if pd.isna(h):
                text[d, w] = row['Date'].strftime('%d %b %Y')
            else:
                text[d, w] = f"{row['Date'].strftime('%d %b %Y')}<br>{h:.1f} h"

        # X-axis: show month name at first week of each month
        week_starts = (full.groupby('Week')['Date'].min()
                           .reindex(range(n_weeks), fill_value=pd.NaT))
        x_labels, prev_month = [], None
        for dt in week_starts:
            if pd.isna(dt):
                x_labels.append('')
                continue
            m = dt.strftime('%b')
            if m != prev_month:
                x_labels.append(m)
                prev_month = m
            else:
                x_labels.append('')

        day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        fig = go.Figure(go.Heatmap(
            z=z,
            x=list(range(n_weeks)),
            y=day_labels,
            text=text,
            hovertemplate='%{text}<extra></extra>',
            colorscale=globals.color_scale,
            showscale=True,
            colorbar=dict(
                title='Hours',
                thickness=10,
                len=0.6,
                tickfont=dict(color='grey', size=10),
                titlefont=dict(color='grey', size=10),
            ),
            xgap=3,
            ygap=3,
        ))

        fig.update_layout(
            template=globals.plot_template,
            paper_bgcolor=globals.paper_bgcolor,
            plot_bgcolor=globals.paper_bgcolor,
            margin=dict(l=40, r=60, t=10, b=30),
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(n_weeks)),
                ticktext=x_labels,
                tickfont=dict(color='grey', size=10),
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                tickfont=dict(color='grey', size=10),
                showgrid=False,
                autorange='reversed',
            ),
            height=190,
        )
        return fig

    except Exception as e:
        return _no_data_fig(f'Error rendering heatmap: {e}')


# ═══════════════════════════════════════════════════════════════════════════════
# Zone 3 — Pie + Aircraft count
# ═══════════════════════════════════════════════════════════════════════════════

@callback(
    Output('ovw-chart-typepie', 'figure'),
    Input('flightlog-store',   'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def chart_typepie(data, start, end):
    """Pie chart: share of each flight type by hours."""
    if not data:
        return _no_data_fig('Upload Flightlog to see flight type breakdown')
    try:
        fl = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        if fl.empty:
            return _no_data_fig('No flights in selected period')

        fl['Hours'] = fl['Flight Time'].dt.total_seconds() / 3600

        hours = (fl.groupby('Flight Type')['Hours'].sum()
                   .reset_index()
                   .sort_values('Hours', ascending=False))

        fig = px.pie(
            hours,
            names='Flight Type',
            values='Hours',
            template=globals.plot_template,
            color_discrete_sequence=globals.discrete_teal,
        )
        fig.update_layout(
            margin=globals.plot_margin,
            paper_bgcolor=globals.paper_bgcolor,
            plot_bgcolor=globals.paper_bgcolor,
            legend=globals.legend,
        )
        return fig

    except Exception as e:
        return _no_data_fig(f'Error rendering pie: {e}')


@callback(
    Output('ovw-chart-aircraftcount', 'figure'),
    Input('flightlog-store',   'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
)
def chart_aircraftcount(data, start, end):
    """Horizontal bar chart: flight hours per aircraft, colored by hours (teal cmap)."""
    if not data:
        return _no_data_fig('Upload Flightlog to see aircraft activity')
    try:
        fl = dp.reload_flightlog_dataframe_from_dict(data, start, end)
        if fl.empty:
            return _no_data_fig('No flights in selected period')

        fl['Hours'] = fl['Flight Time'].dt.total_seconds() / 3600
        ac = (fl.groupby('Aircraft')['Hours'].sum()
                .reset_index()
                .sort_values('Hours', ascending=True))

        fig = go.Figure(go.Bar(
            x=ac['Hours'],
            y=ac['Aircraft'],
            orientation='h',
            marker=dict(
                color=ac['Hours'],
                colorscale=globals.color_scale,
                showscale=False,
            ),
            hovertemplate='<b>%{y}</b><br>%{x:.1f} h<extra></extra>',
            text=ac['Hours'].map(lambda h: f'{h:.1f} h'),
            textposition='outside',
            textfont=dict(color='grey', size=11),
        ))

        # Fleet average
        avg = ac['Hours'].mean()
        fig.add_vline(x=avg, line_dash='dot', line_color='grey',
                      annotation_text=f'avg {avg:.1f} h',
                      annotation_font_color='grey',
                      annotation_position='top right')

        fig = _apply_theme(fig)
        fig.update_layout(
            xaxis_title='Flight Hours',
            yaxis_title='',
            showlegend=False,
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.07)')
        return fig

    except Exception as e:
        return _no_data_fig(f'Error rendering aircraft chart: {e}')
