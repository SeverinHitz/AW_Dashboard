# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

AW_Dashboard is a Plotly Dash web application for analyzing flight club (Albis Wings VS) data exported from AirManager. Users upload export files (flightlog, instructorlog, reservationlog, member data) and the app provides interactive analytics across dedicated pages.

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

The app runs at `http://127.0.0.1:8050` by default. `debug=False` is set in `app.py` — set it to `True` during development for hot-reloading and the Dash debugger.

For production deployment, use gunicorn with the `server` object exported from `app.py`:
```bash
gunicorn app:server
```

## Architecture

### Data Flow

1. **Import page** (`pages/import.py`): Users upload `.xls` (direct AirManager HTML export) or `.xlsx` files. Each dataset is parsed, cleaned, and stored in Dash `dcc.Store` components with `storage_type='session'` — data lives in the browser's Web Storage, not on the server.

2. **Data stores** (defined in `app.py` layout): `flightlog-store`, `instructorlog-store`, `reservationlog-store`, `member-store`, `finance-store` — each paired with a `-date` store holding the file's last-modified date.

3. **Page callbacks** read from these stores by calling `dp.reload_*_dataframe_from_dict()` functions at the start of each callback. The global date picker range (`date-picker-range` in the navbar) filters all data.

4. **Trend comparison**: Most pages support year-over-year comparison. Callbacks call `reload_*_dataframe_from_dict()` twice — once for the selected range, once with `offset=1` (one year prior) — and pass both to `trend_calculation.py`.

### Module Responsibilities

- **`app.py`**: App entry point, navbar with global date picker, `dcc.Store` definitions, page container.
- **`globals.py`**: Single `init()` function that sets all global styling variables (Bootstrap theme, Plotly template, colors, responsive column widths). Call `globals.init()` at the top of every page file.
- **`data_preparation.py`**: All data loading, cleaning, and aggregation. Raw AirManager column names are in German; `data_cleanup_*` functions rename them to English. Aggregation functions produce standardized DataFrames consumed by page callbacks.
- **`plot.py`**: Reusable Plotly figure functions (Sankey diagram, member charts, `not_data_figure()` for empty state).
- **`trend_calculation.py`**: KPI extraction functions per page/data source, plus `trend_calculation()` for computing percent change vs. prior period.
- **`string_func.py`**: String formatting helpers, including `trend_string()` for formatting trend indicators.
- **`pages/`**: One file per dashboard page, each calls `dash.register_page(__name__, ...)`. Pages are self-contained with their own layout and callbacks.

### Responsive Layout

Use the `globals.adaptiv_width_*` dicts (1–12) as `**globals.adaptiv_width_N` kwargs on `dbc.Col` components. These define breakpoint-specific column widths for xs/sm/md/lg/xl screen sizes.

### Adding a New Page

1. Create `pages/mypage.py`
2. Call `globals.init()` at the top
3. Register with `dash.register_page(__name__, path='/mypage', name='MyPage')`
4. Add a `NavItem` in `app.py`'s navbar
5. Read data from stores via `dp.reload_*_dataframe_from_dict()` in callbacks, passing `start_date`/`end_date` from the date picker

### Data Format

Input files must be direct AirManager exports. The `.xls` format is actually an HTML table — `parse_contents()` in `pages/import.py` handles both formats. Required German column names per dataset are documented in `pages/import.py` and shown to users on the Import page.

### Debugging

The project uses `icecream` (`ic()`) for debug printing throughout. These are left in production code and serve as lightweight logging.
