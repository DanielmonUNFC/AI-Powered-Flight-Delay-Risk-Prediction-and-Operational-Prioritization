# ============================================================
# Databricks catalog and storage configuration
# ============================================================

CATALOG = "workspace"
SCHEMA = "default"
VOLUME = "flight_delay_capstone"

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"


# ============================================================
# Project storage paths
# ============================================================

RAW_PATH = f"{VOLUME_PATH}/raw"
REFERENCE_PATH = f"{VOLUME_PATH}/reference"
EXTERNAL_PATH = f"{VOLUME_PATH}/external"
SAMPLES_PATH = f"{VOLUME_PATH}/samples"

# ============================================================
# Reference files
# ============================================================

AIRLINES_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_UNIQUE_CARRIERS_Reporting_Airline.csv"
)

AIRPORTS_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_AIRPORT_Origin_Dest.csv"
)

CANCELLATION_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_CANCELLATION_CancellationCode.csv"
)

MONTHS_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_MONTHS_Month.csv"
)

QUARTERS_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_QUARTERS_Quarter.csv"
)

WEEKDAYS_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/L_WEEKDAYS_DayOfWeek.csv"
)

YES_NO_REFERENCE_FILE = (
    f"{REFERENCE_PATH}/"
    "L_YESNO_RESP_ArrDel15_DepDel15_Cancelled_Diverted.csv"
)

# ============================================================
# Delta tables
# ============================================================

RAW_TABLE = f"{CATALOG}.{SCHEMA}.flights_raw"
CLEAN_TABLE = f"{CATALOG}.{SCHEMA}.flights_clean"
FEATURES_TABLE = f"{CATALOG}.{SCHEMA}.flights_features"
PREDICTIONS_TABLE = f"{CATALOG}.{SCHEMA}.flight_predictions"
DASHBOARD_TABLE = f"{CATALOG}.{SCHEMA}.flight_dashboard"
AIRLINES_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.airlines_lookup"
AIRPORTS_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.airports_lookup"
CANCELLATION_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.cancellation_codes_lookup"
MONTHS_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.months_lookup"
QUARTERS_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.quarters_lookup"
WEEKDAYS_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.weekdays_lookup"
YES_NO_LOOKUP_TABLE = f"{CATALOG}.{SCHEMA}.yes_no_lookup"

# ============================================================
# Raw data validation
# ============================================================

EXPECTED_FILE_COUNT = 12
EXPECTED_FILE_EXTENSION = ".csv"

# ============================================================
# Reference data validation
# ============================================================

EXPECTED_REFERENCE_FILE_COUNT = 7

EXPECTED_REFERENCE_FILES = [
    "L_AIRPORT_Origin_Dest.csv",
    "L_CANCELLATION_CancellationCode.csv",
    "L_MONTHS_Month.csv",
    "L_QUARTERS_Quarter.csv",
    "L_UNIQUE_CARRIERS_Reporting_Airline.csv",
    "L_WEEKDAYS_DayOfWeek.csv",
    "L_YESNO_RESP_ArrDel15_DepDel15_Cancelled_Diverted.csv",
]

# ============================================================
# Reference dataset mapping
# ============================================================

REFERENCE_DATASETS = {
    "airports": {
        "path": AIRPORTS_REFERENCE_FILE,
        "table": AIRPORTS_LOOKUP_TABLE,
    },
    "cancellation_codes": {
        "path": CANCELLATION_REFERENCE_FILE,
        "table": CANCELLATION_LOOKUP_TABLE,
    },
    "months": {
        "path": MONTHS_REFERENCE_FILE,
        "table": MONTHS_LOOKUP_TABLE,
    },
    "quarters": {
        "path": QUARTERS_REFERENCE_FILE,
        "table": QUARTERS_LOOKUP_TABLE,
    },
    "airlines": {
        "path": AIRLINES_REFERENCE_FILE,
        "table": AIRLINES_LOOKUP_TABLE,
    },
    "weekdays": {
        "path": WEEKDAYS_REFERENCE_FILE,
        "table": WEEKDAYS_LOOKUP_TABLE,
    },
    "yes_no": {
        "path": YES_NO_REFERENCE_FILE,
        "table": YES_NO_LOOKUP_TABLE,
    },
}

# ============================================================
# Core date and time columns
# ============================================================

QUARTER_COLUMN = "QUARTER"
MONTH_COLUMN = "MONTH"
DAY_OF_WEEK_COLUMN = "DAY_OF_WEEK"
FLIGHT_DATE_COLUMN = "FL_DATE"

SCHEDULED_DEPARTURE_COLUMN = "CRS_DEP_TIME"
SCHEDULED_ARRIVAL_COLUMN = "CRS_ARR_TIME"


# ============================================================
# Core flight identification columns
# ============================================================

AIRLINE_COLUMN = "OP_UNIQUE_CARRIER"
FLIGHT_NUMBER_COLUMN = "OP_CARRIER_FL_NUM"

ORIGIN_COLUMN = "ORIGIN"
DESTINATION_COLUMN = "DEST"

ORIGIN_CITY_COLUMN = "ORIGIN_CITY_NAME"
DESTINATION_CITY_COLUMN = "DEST_CITY_NAME"


# ============================================================
# Flight status columns
# ============================================================

CANCELLED_COLUMN = "CANCELLED"
DIVERTED_COLUMN = "DIVERTED"
CANCELLATION_CODE_COLUMN = "CANCELLATION_CODE"

# ============================================================
# Flight operation columns
# ============================================================

DISTANCE_COLUMN = "DISTANCE"

# ============================================================
# Delay-related columns
# ============================================================

DEPARTURE_DELAY_COLUMN = "DEP_DELAY"
ARRIVAL_DELAY_COLUMN = "ARR_DELAY"

DEPARTURE_DELAY_FLAG_COLUMN = "DEP_DEL15"
ARRIVAL_DELAY_FLAG_COLUMN = "ARR_DEL15"

DELAY_CAUSE_COLUMNS = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY",
]


# ============================================================
# Model target configuration
# ============================================================

TARGET_COLUMN = ARRIVAL_DELAY_FLAG_COLUMN
DELAY_THRESHOLD_MINUTES = 15


# ============================================================
# Modeling configuration
# ============================================================

RANDOM_SEED = 42
TRAIN_RATIO = 0.80
TEST_RATIO = 0.20


# ============================================================
# Operational analysis configuration
# ============================================================

MIN_OPERATIONAL_FLIGHTS = 1000

LOW_RISK_THRESHOLD = 0.30
HIGH_RISK_THRESHOLD = 0.60


# ============================================================
# Reusable column groups
# ============================================================

KEY_CATEGORICAL_COLUMNS = [
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    CANCELLATION_CODE_COLUMN,
]

KEY_OPERATIONAL_COLUMNS = [
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    CANCELLED_COLUMN,
    DIVERTED_COLUMN,
    DEPARTURE_DELAY_COLUMN,
    ARRIVAL_DELAY_COLUMN,
    TARGET_COLUMN,
]

# ============================================================
# Operational analysis configuration
# ============================================================

MIN_OPERATIONAL_FLIGHTS = 1000
MIN_ROUTE_FLIGHTS = 100
TOP_N_RESULTS = 20

LOW_RISK_THRESHOLD = 0.30
HIGH_RISK_THRESHOLD = 0.60