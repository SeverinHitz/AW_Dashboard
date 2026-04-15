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

### Page Layouts (current state)

**Overview (`pages/overview.py`)**
- Zone 1: 6 KPIs with YoY trend — Flights, Flight Hours, Landings, Active Pilots, Instruction Time, Revenue
- Zone 2: GitHub-style activity heatmap (daily flight hours, teal colorscale, NaN = transparent)
- Zone 3: Flight-type pie (raw `Flight Type` values, hours) | Aircraft flight hours bar (teal cmap by bar length)
- Zone 4: Navigation cards to sub-pages

**Pilot (`pages/pilot.py`)**
- KPI Row 1 (width_2 each): Pilot · Flight Time · Block Time · Flt./Blckt. · Flights · Landings
- KPI Row 2 (width_3 each): Flt/Res · Reservations · Cancelled · Canc. Ratio
- Plots: Flight Time bar | Cancellation Reason pie | Custom Bar Plot | **Day-of-Week flight hours bar**

**Aircraft (`pages/aircraft.py`)**
- KPI Row 1 (width_2 each): Aircraft · Flight Time · Flights · ⌀ Flt Time · Landings · Airports
- KPI Row 2 (width_3 each): Fuel p.h. · Oil p.h. · Inst. Ratio · # Pilots
- Plot Row 1: Flight Time bar | Flight Type pie | Destinations map
- Plot Row 2: **Techlog Status stacked bar** (per aircraft, teal status colors) | **Day-of-Week flight hours bar**
- Destinations map: density glow background + route lines (width ∝ flights) + scatter circles

### Plotly Chart Patterns

**Critical:** Never pass `template=globals.plot_template` directly to `px.bar()` when also using `color=<numeric_column>` (continuous color). This triggers a Plotly internal crash. Instead:
```python
fig = px.bar(..., template='none', color='MyCol', color_continuous_scale=globals.color_scale)
fig.update_layout(..., template=globals.plot_template)  # apply template here
```

**Hover text:** Always set `hovertemplate` explicitly. Use `<extra></extra>` to suppress the trace-name box. Example: `'<b>%{x}</b><br>%{y:.1f} h<extra></extra>'`. For bars use `%{y:g}` when the column can be either int or float.

**Colorscale:** Use `globals.color_scale` (`'teal'`) for continuous scales and `globals.discrete_teal` (list of 9 teal hex values) for categorical. Both are set in `globals.py`.

### Techlog Status Groups

`data_cleanup_techlog()` in `data_preparation.py` maps raw German status strings to these groups (stored in `Status Group` column):

| Raw Status | Group |
|---|---|
| Open - Not Flight Relevant | Open |
| DD - Not Flight Relevant / DD - Restriction | Deferred |
| Not Airworthy | Not Airworthy |
| CRS / CRS - Check / Close | Closed |
| For information only | Info |
| (anything else) | Other |

Colors used on aircraft page: Not Airworthy → `discrete_teal[7]`, Open → `[5]`, Deferred → `[3]`, Info → `[1]`, Closed → `[0]`, Other → `#444444`.

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
