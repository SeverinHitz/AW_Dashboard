"""
Import page — single multi-file drop zone.
Files are auto-detected from their column structure; no need to drop into
separate boxes per dataset.
"""

from icecream import ic
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import base64
import io

import data_preparation as dp
import globals

globals.init()

dash.register_page(__name__, path='/', name='Import')

# ── Dataset registry: type → (label, cleanup_fn, store_id, date_store_id) ──
DATASETS = {
    'flightlog':      ('Flightlog',      dp.data_cleanup_flightlog,      'flightlog-store',      'flightlog-store-date'),
    'instructorlog':  ('Instructorlog',  dp.data_cleanup_instructorlog,  'instructorlog-store',  'instructorlog-store-date'),
    'reservationlog': ('Reservationlog', dp.data_cleanup_reservation,    'reservationlog-store', 'reservationlog-store-date'),
    'member':         ('Members',        dp.data_cleanup_member,         'member-store',         'member-store-date'),
    'finance':        ('Finance',        dp.data_cleanup_finance,        'finance-store',        'finance-store-date'),
    'techlog':        ('Techlog',        dp.data_cleanup_techlog,        'techlog-store',        'techlog-store-date'),
}

# ── Info tables ──────────────────────────────────────────────────────────────
_data_req = [
    ["Flightlog",      "x", "x", "x", "x", "",  "",  "(x)"],
    ["Instructorlog",  "x", "",  "",  "x", "",  "",  "(x)"],
    ["Reservationlog", "",  "x", "",  "",  "",  "",  "(x)"],
    ["Member",         "",  "",  "",  "",  "x", "",  "(x)"],
    ["Finance",        "",  "",  "",  "",  "",  "x", "(x)"],
    ["Techlog",        "x", "",  "x", "",  "",  "",  "(x)"],
]

requirement_table = dbc.Table(
    [html.Thead(html.Tr([html.Th(h) for h in
                         ["Dataset", "Overview", "Pilot", "Aircraft", "School", "Member", "Finance", "Analytics"]]))] +
    [html.Tbody([html.Tr([html.Td(c) for c in row]) for row in _data_req])],
    bordered=True, style={'font-size': 'smaller'}
)

_data_fmt = [
    ["Flightlog",      "Datum, Vorname, Name, Abflugort, Ankunftsort, Flugzeit, Block Zeit, Benzin, Öl, Landungen, Flugart, Flugzeug"],
    ["Instructorlog",  "Datum, Pilot Vorname, Pilot Name, Fluglehrer Vorname, Fluglehrer Name, Dauer"],
    ["Reservationlog", "Von, Bis, Vorname, Name, Flugzeug, Typ, Gelöscht, Löschgrund"],
    ["Members",        "AirManager ID, PLZ, Geburtsdatum, Mitgliedschaft, Eintrittsdatum"],
    ["Finance",        "Rechnungsnummer, Artikel, Artikelnummer, Betrag inkl. MWST, Zahlungsdatum"],
    ["Techlog",        "ID, Datum, Vorname, Name, Flugzeug, Description, Status, Timestamp"],
]

format_table = dbc.Table(
    [html.Thead(html.Tr([html.Th("Dataset"), html.Th("Required Columns")]))] +
    [html.Tbody([html.Tr([html.Td(c) for c in row]) for row in _data_fmt])],
    bordered=True, style={'font-size': 'smaller'}
)

# ── Layout ───────────────────────────────────────────────────────────────────
layout = html.Div([

    # ── Drop zone ─────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Import — Drop all AirManager exports here"),
                dbc.CardBody([
                    dcc.Upload(
                        id='multi-upload',
                        children=html.Div([
                            html.B('Drag & Drop'),
                            ' or ',
                            html.A('Select Files'),
                            html.Br(),
                            html.Small(
                                'Flightlog · Instructorlog · Reservationlog · Members · Finance · Techlog',
                                style={'color': '#aaa'}
                            ),
                            html.Br(),
                            html.Small(
                                'Files are auto-detected from their column structure.',
                                style={'color': '#aaa'}
                            ),
                        ]),
                        style={
                            'width': '100%',
                            'minHeight': '100px',
                            'lineHeight': '60px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '8px',
                            'textAlign': 'center',
                            'padding': '20px',
                        },
                        multiple=True,
                    ),
                ]),
                dbc.CardFooter(
                    dcc.Loading(id='upload-results-loading', type='dot',
                                children=html.Div(id='upload-results'))
                ),
            ])
        ], **globals.adaptiv_width_12),
    ], className="g-0"),

    # ── Data status ───────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Data Status"),
                dbc.CardBody(html.Div(id='data-status')),
            ])
        ], **globals.adaptiv_width_12),
    ], className="g-0 mt-2"),

    # ── Info cards ────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Pages × Data"),
                dbc.CardBody(requirement_table),
            ])
        ], **globals.adaptiv_width_6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Data Security / Privacy"),
                dbc.CardBody([
                    html.P(
                        "Data is not retained on the server. It lives only in your browser's "
                        "Web Storage during the session. Personal fields kept: first name, "
                        "surname, postcode, date of birth. Email, phone, IBAN are discarded "
                        "at import. All transfers use HTTPS."
                    ),
                    html.P("No liability accepted. Operate within your organisation's privacy policy."),
                    html.A("AirManager", href="https://airmanager.ch/"),
                ]),
            ])
        ], **globals.adaptiv_width_6),
    ], className="g-0 mt-2"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Required Data Format"),
                dbc.CardBody([
                    html.P([html.B("Format: "), "Direct AirManager export (.xls HTML table) or Excel (.xlsx)"]),
                    format_table,
                ]),
            ])
        ], **globals.adaptiv_width_12),
    ], className="g-0 mt-2"),
])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_file(contents, filename):
    """Decode a dcc.Upload payload → (ok, df, message)."""
    if not contents:
        return False, None, 'No content'

    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        return False, None, f'Unsupported file type: {filename}'

    _type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        else:  # .xls — AirManager HTML export
            dfs = pd.read_html(io.BytesIO(decoded), header=0)
            df = dfs[0]
            df = dp.xls_format_cleanup(df)
    except Exception as e:
        ic(e)
        return False, None, f'Could not read file: {e}'

    return True, df, 'Parsed OK'


def _status_badge(label, filename, rows, ok):
    color = '#4caf50' if ok else '#f44336'
    icon = '✅' if ok else '❌'
    text = f'{rows:,} rows loaded' if ok else filename
    return html.Div(
        f'{icon} {label}  —  {text}',
        style={'color': color, 'marginBottom': '4px'}
    )


# ── Single callback: process all uploaded files ───────────────────────────────

@callback(
    # Stores (data + date) for all 6 datasets
    Output('flightlog-store',      'data'),
    Output('flightlog-store-date', 'data'),
    Output('instructorlog-store',      'data'),
    Output('instructorlog-store-date', 'data'),
    Output('reservationlog-store',      'data'),
    Output('reservationlog-store-date', 'data'),
    Output('member-store',      'data'),
    Output('member-store-date', 'data'),
    Output('finance-store',      'data'),
    Output('finance-store-date', 'data'),
    Output('techlog-store',      'data'),
    Output('techlog-store-date', 'data'),
    # UI feedback
    Output('upload-results', 'children'),
    Output('data-status',    'children'),
    # Inputs
    Input('multi-upload', 'contents'),
    State('multi-upload', 'filename'),
    State('multi-upload', 'last_modified'),
    # Current store values (kept if a file isn't re-uploaded)
    State('flightlog-store',      'data'), State('flightlog-store-date', 'data'),
    State('instructorlog-store',  'data'), State('instructorlog-store-date', 'data'),
    State('reservationlog-store', 'data'), State('reservationlog-store-date', 'data'),
    State('member-store',         'data'), State('member-store-date', 'data'),
    State('finance-store',        'data'), State('finance-store-date', 'data'),
    State('techlog-store',        'data'), State('techlog-store-date', 'data'),
)
def handle_upload(
    contents_list, filenames, last_modified_list,
    fl_data, fl_date, il_data, il_date, rl_data, rl_date,
    mb_data, mb_date, fi_data, fi_date, tl_data, tl_date,
):
    # Start from whatever is already in the stores
    stores = {
        'flightlog':      [fl_data, fl_date],
        'instructorlog':  [il_data, il_date],
        'reservationlog': [rl_data, rl_date],
        'member':         [mb_data, mb_date],
        'finance':        [fi_data, fi_date],
        'techlog':        [tl_data, tl_date],
    }

    result_badges = []

    if contents_list:
        for contents, filename, last_mod in zip(contents_list, filenames, last_modified_list):
            ok, df_raw, msg = _parse_file(contents, filename)
            if not ok:
                result_badges.append(_status_badge('Unknown', filename, 0, False))
                ic(msg)
                continue

            ds_type = dp.detect_dataset_type(df_raw)
            if ds_type == 'unknown':
                result_badges.append(
                    _status_badge(f'Unknown ({filename})', filename, 0, False)
                )
                continue

            label, cleanup_fn, _store_id, _date_id = DATASETS[ds_type]
            try:
                df_clean = cleanup_fn(df_raw)
            except Exception as e:
                ic(e)
                result_badges.append(_status_badge(label, filename, 0, False))
                continue

            timestamp = datetime.fromtimestamp(last_mod).strftime('%d.%m.%Y')
            stores[ds_type] = [df_clean.to_dict('records'), timestamp]
            result_badges.append(_status_badge(label, filename, len(df_clean), True))

    # Build status panel
    status_items = []
    for ds_type, (label, _, _, _) in DATASETS.items():
        data, date = stores[ds_type]
        if data is not None:
            rows = len(data)
            status_items.append(
                html.Span(
                    f'✅ {label}  {date}  ({rows:,} rows)',
                    style={'color': '#4caf50', 'marginRight': '20px'}
                )
            )
        else:
            status_items.append(
                html.Span(
                    f'❌ {label}',
                    style={'color': '#888', 'marginRight': '20px'}
                )
            )

    return (
        stores['flightlog'][0],      stores['flightlog'][1],
        stores['instructorlog'][0],  stores['instructorlog'][1],
        stores['reservationlog'][0], stores['reservationlog'][1],
        stores['member'][0],         stores['member'][1],
        stores['finance'][0],        stores['finance'][1],
        stores['techlog'][0],        stores['techlog'][1],
        result_badges or html.Span('Drop files above to import.', style={'color': '#aaa'}),
        html.Div(status_items),
    )
