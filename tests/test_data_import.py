"""
Tests for data import pipeline (data_preparation.py).

Run with:
    C:/Users/sevih/miniconda3/envs/aw_dashboard/python.exe -m pytest tests/ -v
"""

import sys, os, io, types
import pytest
import pandas as pd
import numpy as np

# ── stub icecream so the module loads without it ──────────────────────────────
ic_mod = types.ModuleType('icecream')
ic_mod.ic = lambda *a, **kw: None
sys.modules.setdefault('icecream', ic_mod)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import data_preparation as dp

# ── locate data directory ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

def _load_xls(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f'Data file not found: {filename}')
    with open(path, 'rb') as f:
        raw = io.BytesIO(f.read())
    dfs = pd.read_html(raw, header=0)
    df = dfs[0]
    return dp.xls_format_cleanup(df)


# ═══════════════════════════════════════════════════════════════════════════════
# detect_dataset_type
# ═══════════════════════════════════════════════════════════════════════════════

class TestDetectDatasetType:
    def test_flightlog(self):
        df = _load_xls('260408_Flightlog.xls')
        assert dp.detect_dataset_type(df) == 'flightlog'

    def test_instructorlog(self):
        df = _load_xls('260408_Instructorlog.xls')
        assert dp.detect_dataset_type(df) == 'instructorlog'

    def test_reservationlog(self):
        df = _load_xls('260408_Reservationlog.xls')
        assert dp.detect_dataset_type(df) == 'reservationlog'

    def test_members(self):
        df = _load_xls('260408_Members.xls')
        assert dp.detect_dataset_type(df) == 'member'

    def test_finance(self):
        df = _load_xls('260408_Financelog.xls')
        assert dp.detect_dataset_type(df) == 'finance'

    def test_techlog(self):
        df = _load_xls('260408_Techlog.xls')
        assert dp.detect_dataset_type(df) == 'techlog'

    def test_unknown_returns_unknown(self):
        df = pd.DataFrame({'Foo': [1], 'Bar': [2]})
        assert dp.detect_dataset_type(df) == 'unknown'

    def test_empty_df_returns_unknown(self):
        df = pd.DataFrame()
        assert dp.detect_dataset_type(df) == 'unknown'


# ═══════════════════════════════════════════════════════════════════════════════
# Flightlog cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestFlightlogCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Flightlog.xls')
        return dp.data_cleanup_flightlog(raw)

    def test_required_columns_present(self, df):
        for col in ['Date', 'Pilot', 'Aircraft', 'Flight Time', 'Landings', 'Fuel']:
            assert col in df.columns, f'Missing column: {col}'

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_date_is_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df['Date']), 'Date not datetime'

    def test_no_null_dates(self, df):
        assert df['Date'].isna().sum() == 0, 'Null dates found'

    def test_flight_time_is_timedelta(self, df):
        assert pd.api.types.is_timedelta64_dtype(df['Flight Time']), \
            'Flight Time not timedelta'

    def test_flight_time_non_negative(self, df):
        assert (df['Flight Time'] >= pd.Timedelta(0)).all(), \
            'Negative flight times found'

    def test_landings_numeric_non_negative(self, df):
        assert pd.api.types.is_numeric_dtype(df['Landings'])
        assert (df['Landings'] >= 0).all()

    def test_fuel_numeric(self, df):
        assert pd.api.types.is_numeric_dtype(df['Fuel'])

    def test_pilot_non_empty_strings(self, df):
        assert df['Pilot'].notna().all()
        assert (df['Pilot'].str.strip() != '').all()

    def test_roundtrip_to_dict_and_back(self, df):
        records = df.to_dict('records')
        df2 = dp.reload_flightlog_dataframe_from_dict(records, '2000-01-01', '2099-12-31')
        assert len(df2) == len(df)
        assert list(df2.columns) == list(df.columns)


# ═══════════════════════════════════════════════════════════════════════════════
# Instructorlog cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestInstructorlogCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Instructorlog.xls')
        return dp.data_cleanup_instructorlog(raw)

    def test_required_columns(self, df):
        for col in ['Date', 'Pilot', 'Instructor', 'Duration']:
            assert col in df.columns, f'Missing column: {col}'

    def test_date_is_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df['Date'])

    def test_duration_is_timedelta(self, df):
        assert pd.api.types.is_timedelta64_dtype(df['Duration'])

    def test_duration_non_negative(self, df):
        assert (df['Duration'] >= pd.Timedelta(0)).all()

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_roundtrip(self, df):
        records = df.to_dict('records')
        df2 = dp.reload_instructor_dataframe_from_dict(records, '2000-01-01', '2099-12-31')
        assert len(df2) == len(df)


# ═══════════════════════════════════════════════════════════════════════════════
# Reservationlog cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestReservationlogCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Reservationlog.xls')
        return dp.data_cleanup_reservation(raw)

    def test_required_columns(self, df):
        for col in ['From', 'To', 'Pilot', 'Aircraft', 'Deleted']:
            assert col in df.columns, f'Missing column: {col}'

    def test_from_is_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df['From'])

    def test_to_is_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df['To'])

    def test_deleted_is_bool(self, df):
        assert df['Deleted'].dtype == bool

    def test_to_after_from(self, df):
        # Most reservations: To >= From
        valid = df['To'] >= df['From']
        assert valid.mean() > 0.95, f'Too many To < From: {(~valid).sum()}'

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_roundtrip(self, df):
        records = df.to_dict('records')
        df2 = dp.reload_reservation_dataframe_from_dict(records, '2000-01-01', '2099-12-31')
        assert len(df2) == len(df)


# ═══════════════════════════════════════════════════════════════════════════════
# Finance cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestFinanceCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Financelog.xls')
        return dp.data_cleanup_finance(raw)

    def test_required_columns(self, df):
        for col in ['Invoice Date', 'Payment Date', 'Amount', 'cost_centre', 'ac_reg', 'flight_type']:
            assert col in df.columns, f'Missing column: {col}'

    def test_amount_numeric(self, df):
        assert pd.api.types.is_numeric_dtype(df['Amount'])

    def test_cost_centre_no_nan(self, df):
        assert df['cost_centre'].notna().all(), 'cost_centre has NaN'

    def test_cost_centre_known_values(self, df):
        known = {
            'Aircraft HB-CQW', 'Aircraft HB-DHP', 'Aircraft HB-POD',
            'Aircraft HB-POX', 'Aircraft HB-SFS', 'Aircraft HB-SFU',
            'Aircraft HB-SGZ', 'Intro/Rundflug vouchers',
            'Flight Instructor (FI)', 'Deposits & packages',
            'Intro/Rundflug flights', 'Landing fees',
            'Customs & fuel refunds', 'Membership fees', 'Other',
        }
        unexpected = set(df['cost_centre'].unique()) - known
        assert not unexpected, f'Unexpected cost_centre values: {unexpected}'

    def test_ac_reg_format(self, df):
        non_null = df['ac_reg'].dropna()
        assert non_null.str.match(r'^HB-[A-Z]{3}$').all(), \
            'ac_reg has malformed registrations'

    def test_flight_type_values(self, df):
        valid = {'Charter', 'Training', 'Other'}
        unexpected = set(df['flight_type'].unique()) - valid
        assert not unexpected, f'Unexpected flight_type values: {unexpected}'

    def test_days_to_payment_reasonable(self, df):
        dtp = df['Days to Payment'].dropna()
        # Should be between -30 and 730 days for 99% of records
        pct_in_range = dtp.between(-30, 730).mean()
        assert pct_in_range > 0.99, f'Unusual Days to Payment: {pct_in_range:.1%} in range'

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_roundtrip(self, df):
        records = df.to_dict('records')
        df2 = dp.reload_finance_dataframe_from_dict(records, '2000-01-01', '2099-12-31')
        # Rows where both dates are NaT are legitimately dropped by the date filter
        null_date_rows = df[['Payment Date', 'Invoice Date']].isna().all(axis=1).sum()
        assert len(df2) >= len(df) - null_date_rows


# ═══════════════════════════════════════════════════════════════════════════════
# Member cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemberCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Members.xls')
        return dp.data_cleanup_member(raw)

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_no_email_or_iban(self, df):
        sensitive = {'Email', 'email', 'IBAN', 'iban', 'Phone', 'phone', 'Telefon'}
        present = sensitive & set(df.columns)
        assert not present, f'Sensitive columns not stripped: {present}'


# ═══════════════════════════════════════════════════════════════════════════════
# Techlog cleanup
# ═══════════════════════════════════════════════════════════════════════════════

class TestTechlogCleanup:
    @pytest.fixture(scope='class')
    def df(self):
        raw = _load_xls('260408_Techlog.xls')
        return dp.data_cleanup_techlog(raw)

    def test_required_columns(self, df):
        for col in ['Date', 'Aircraft', 'Status', 'Status Group']:
            assert col in df.columns, f'Missing column: {col}'

    def test_date_is_datetime(self, df):
        assert pd.api.types.is_datetime64_any_dtype(df['Date'])

    def test_status_group_known_values(self, df):
        known = {'Open', 'Deferred', 'Closed', 'Info', 'Other', 'Not Airworthy'}
        unexpected = set(df['Status Group'].unique()) - known
        assert not unexpected, f'Unknown Status Group values: {unexpected}'

    def test_no_empty_rows(self, df):
        assert len(df) > 0

    def test_roundtrip(self, df):
        records = df.to_dict('records')
        df2 = dp.reload_techlog_dataframe_from_dict(records, '2000-01-01', '2099-12-31')
        assert len(df2) == len(df)


# ═══════════════════════════════════════════════════════════════════════════════
# Finance classification helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestClassifyFinanceArtikel:
    def test_aircraft_ranges(self):
        assert dp._classify_finance_artikel(2100) == 'Aircraft HB-CQW'
        assert dp._classify_finance_artikel(2199) == 'Aircraft HB-CQW'
        assert dp._classify_finance_artikel(2200) == 'Aircraft HB-DHP'
        assert dp._classify_finance_artikel(3000) == 'Flight Instructor (FI)'
        assert dp._classify_finance_artikel(3099) == 'Flight Instructor (FI)'
        assert dp._classify_finance_artikel(6000) == 'Membership fees'
        assert dp._classify_finance_artikel(6199) == 'Membership fees'

    def test_unmapped_returns_other(self):
        assert dp._classify_finance_artikel(9999) == 'Other'
        assert dp._classify_finance_artikel(0)    == 'Other'

    def test_nan_returns_other(self):
        assert dp._classify_finance_artikel(float('nan')) == 'Other'
        assert dp._classify_finance_artikel(None) == 'Other'

    def test_string_number_coerced(self):
        # Artikel numbers sometimes come as strings from Excel
        assert dp._classify_finance_artikel('2300') == 'Aircraft HB-POD'
