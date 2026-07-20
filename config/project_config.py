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
EXTERNAL_PATH = f"{VOLUME_PATH}/external"
SAMPLES_PATH = f"{VOLUME_PATH}/samples"


# ============================================================
# Delta tables
# ============================================================

RAW_TABLE = f"{CATALOG}.{SCHEMA}.flights_raw"
CLEAN_TABLE = f"{CATALOG}.{SCHEMA}.flights_clean"
FEATURES_TABLE = f"{CATALOG}.{SCHEMA}.flights_features"
PREDICTIONS_TABLE = f"{CATALOG}.{SCHEMA}.flight_predictions"
DASHBOARD_TABLE = f"{CATALOG}.{SCHEMA}.flight_dashboard"


# ============================================================
# Raw data validation
# ============================================================

EXPECTED_FILE_COUNT = 12
EXPECTED_FILE_EXTENSION = ".csv"


# ============================================================
# Core date and time columns
# ============================================================

YEAR_COLUMN = "YEAR"
MONTH_COLUMN = "MONTH"
DAY_OF_MONTH_COLUMN = "DAY_OF_MONTH"
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
    YEAR_COLUMN,
    MONTH_COLUMN,
    DAY_OF_MONTH_COLUMN,
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