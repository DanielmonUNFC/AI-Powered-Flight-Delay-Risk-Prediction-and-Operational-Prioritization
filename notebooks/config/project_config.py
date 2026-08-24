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
PROCESSED_PATH = f"{VOLUME_PATH}/processed"

# Processed Delta file locations
CLEAN_DELTA_PATH = f"{PROCESSED_PATH}/flights_clean"
FEATURES_DELTA_PATH = f"{PROCESSED_PATH}/flights_features"

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
FEATURES_V2_TABLE = f"{CATALOG}.{SCHEMA}.flights_features_v2"
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
ORIGIN_STATE_COLUMN = "ORIGIN_STATE_NM"
DESTINATION_CITY_COLUMN = "DEST_CITY_NAME"
DESTINATION_STATE_COLUMN = "DEST_STATE_NM"


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
TAXI_OUT_COLUMN = "TAXI_OUT"
TAXI_IN_COLUMN = "TAXI_IN"
SCHEDULED_ELAPSED_TIME_COLUMN = "CRS_ELAPSED_TIME"
ACTUAL_ELAPSED_TIME_COLUMN = "ACTUAL_ELAPSED_TIME"
AIR_TIME_COLUMN = "AIR_TIME"

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

TARGET_COLUMN = ARRIVAL_DELAY_FLAG_COLUMN
DELAY_THRESHOLD_MINUTES = 15


# ============================================================
# Engineered feature columns
# ============================================================

DEP_HOUR_COLUMN = "DEP_HOUR"
DEP_MINUTE_COLUMN = "DEP_MINUTE"
ARR_HOUR_COLUMN = "ARR_HOUR"
ARR_MINUTE_COLUMN = "ARR_MINUTE"
IS_WEEKEND_COLUMN = "IS_WEEKEND"
SEASON_COLUMN = "SEASON"
TIME_OF_DAY_COLUMN = "TIME_OF_DAY"
FLIGHT_DISTANCE_CATEGORY_COLUMN = "FLIGHT_DISTANCE_CATEGORY"
ROUTE_COLUMN = "ROUTE"
DEP_TIME_SIN_COLUMN = "DEP_TIME_SIN"
DEP_TIME_COS_COLUMN = "DEP_TIME_COS"
ARR_TIME_SIN_COLUMN = "ARR_TIME_SIN"
ARR_TIME_COS_COLUMN = "ARR_TIME_COS"
MONTH_SIN_COLUMN = "MONTH_SIN"
MONTH_COS_COLUMN = "MONTH_COS"
DAY_OF_WEEK_SIN_COLUMN = "DAY_OF_WEEK_SIN"
DAY_OF_WEEK_COS_COLUMN = "DAY_OF_WEEK_COS"
ORIGIN_SCHEDULED_DEPARTURES_HOUR_COLUMN = (
    "ORIGIN_SCHEDULED_DEPARTURES_HOUR"
)
DEST_SCHEDULED_ARRIVALS_HOUR_COLUMN = "DEST_SCHEDULED_ARRIVALS_HOUR"
ROUTE_DAILY_FLIGHT_COUNT_COLUMN = "ROUTE_DAILY_FLIGHT_COUNT"
SCHEDULED_SPEED_MPH_COLUMN = "SCHEDULED_SPEED_MPH"


# ============================================================
# Data parsing and validation configuration
# ============================================================

FL_DATE_PARSE_FORMAT = "M/d/yyyy h:mm:ss a"
BINARY_DOMAIN_VALUES = [0, 1]
WEEKEND_DAYS = (6, 7)

EXPECTED_RAW_COLUMNS = [
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    ORIGIN_CITY_COLUMN,
    ORIGIN_STATE_COLUMN,
    DESTINATION_COLUMN,
    DESTINATION_CITY_COLUMN,
    DESTINATION_STATE_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
    DEPARTURE_DELAY_COLUMN,
    DEPARTURE_DELAY_FLAG_COLUMN,
    TAXI_OUT_COLUMN,
    TAXI_IN_COLUMN,
    SCHEDULED_ARRIVAL_COLUMN,
    ARRIVAL_DELAY_COLUMN,
    ARRIVAL_DELAY_FLAG_COLUMN,
    CANCELLED_COLUMN,
    CANCELLATION_CODE_COLUMN,
    DIVERTED_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    ACTUAL_ELAPSED_TIME_COLUMN,
    AIR_TIME_COLUMN,
    DISTANCE_COLUMN,
    *DELAY_CAUSE_COLUMNS,
]

BUSINESS_KEY_COLUMNS = [
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
]

MODELING_JOIN_KEY_COLUMNS = [
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
]

MODEL_HASHED_OUTPUT_COLUMNS = [
    *MODELING_JOIN_KEY_COLUMNS,
    TARGET_COLUMN,
    "features",
]

BINARY_INDICATOR_COLUMNS = [
    DEPARTURE_DELAY_FLAG_COLUMN,
    ARRIVAL_DELAY_FLAG_COLUMN,
    CANCELLED_COLUMN,
    DIVERTED_COLUMN,
]

CODE_COLUMNS = [
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    ORIGIN_STATE_COLUMN,
    DESTINATION_COLUMN,
    DESTINATION_STATE_COLUMN,
    CANCELLATION_CODE_COLUMN,
]

TEXT_COLUMNS = [
    ORIGIN_CITY_COLUMN,
    DESTINATION_CITY_COLUMN,
]

INTEGER_COLUMNS = [
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
    SCHEDULED_ARRIVAL_COLUMN,
]

DOUBLE_COLUMNS = [
    DEPARTURE_DELAY_COLUMN,
    TAXI_OUT_COLUMN,
    TAXI_IN_COLUMN,
    ARRIVAL_DELAY_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    ACTUAL_ELAPSED_TIME_COLUMN,
    AIR_TIME_COLUMN,
    DISTANCE_COLUMN,
    *DELAY_CAUSE_COLUMNS,
]

STANDARDIZED_TYPE_COLUMNS = [
    FLIGHT_DATE_COLUMN,
    *BINARY_INDICATOR_COLUMNS,
]

CLEANING_PREVIEW_COLUMNS = [
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    DEPARTURE_DELAY_FLAG_COLUMN,
    ARRIVAL_DELAY_FLAG_COLUMN,
    CANCELLED_COLUMN,
    DIVERTED_COLUMN,
]

DOMAIN_RULES = {
    QUARTER_COLUMN: [1, 2, 3, 4],
    MONTH_COLUMN: list(range(1, 13)),
    DAY_OF_WEEK_COLUMN: list(range(1, 8)),
    DEPARTURE_DELAY_FLAG_COLUMN: BINARY_DOMAIN_VALUES,
    ARRIVAL_DELAY_FLAG_COLUMN: BINARY_DOMAIN_VALUES,
    CANCELLED_COLUMN: BINARY_DOMAIN_VALUES,
    DIVERTED_COLUMN: BINARY_DOMAIN_VALUES,
}


# ============================================================
# Feature engineering configuration
# ============================================================

FEATURE_INPUT_COLUMNS = [
    FLIGHT_DATE_COLUMN,
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
    SCHEDULED_ARRIVAL_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    DISTANCE_COLUMN,
    ARRIVAL_DELAY_FLAG_COLUMN,
    CANCELLED_COLUMN,
    DIVERTED_COLUMN,
]

MODEL_ELIGIBLE_STATUS_VALUE = 0

DISTANCE_SHORT_MAX_MILES = 500
DISTANCE_MEDIUM_MAX_MILES = 1500

TIME_OF_DAY_BUCKETS = [
    {"label": "Overnight", "start_hour": 0, "end_hour": 5},
    {"label": "Morning", "start_hour": 6, "end_hour": 11},
    {"label": "Afternoon", "start_hour": 12, "end_hour": 16},
    {"label": "Evening", "start_hour": 17, "end_hour": 20},
    {"label": "Night", "start_hour": 21, "end_hour": 23},
]

SEASON_MONTH_GROUPS = {
    "Winter": (12, 1, 2),
    "Spring": (3, 4, 5),
    "Summer": (6, 7, 8),
    "Fall": (9, 10, 11),
}

MODEL_FEATURE_COLUMNS = [
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    FLIGHT_DATE_COLUMN,
    AIRLINE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    DISTANCE_COLUMN,
    ORIGIN_CITY_COLUMN,
    ORIGIN_STATE_COLUMN,
    DESTINATION_CITY_COLUMN,
    DESTINATION_STATE_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
    SCHEDULED_ARRIVAL_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    DEP_HOUR_COLUMN,
    DEP_MINUTE_COLUMN,
    ARR_HOUR_COLUMN,
    ARR_MINUTE_COLUMN,
    IS_WEEKEND_COLUMN,
    SEASON_COLUMN,
    TIME_OF_DAY_COLUMN,
    FLIGHT_DISTANCE_CATEGORY_COLUMN,
    TARGET_COLUMN,
]

# Version 2 preserves every V1 feature and adds only information derivable
# from the published schedule. No observed operational outcome is introduced.
MODEL_V2_ENGINEERED_FEATURE_COLUMNS = [
    ROUTE_COLUMN,
    DEP_TIME_SIN_COLUMN,
    DEP_TIME_COS_COLUMN,
    ARR_TIME_SIN_COLUMN,
    ARR_TIME_COS_COLUMN,
    MONTH_SIN_COLUMN,
    MONTH_COS_COLUMN,
    DAY_OF_WEEK_SIN_COLUMN,
    DAY_OF_WEEK_COS_COLUMN,
    ORIGIN_SCHEDULED_DEPARTURES_HOUR_COLUMN,
    DEST_SCHEDULED_ARRIVALS_HOUR_COLUMN,
    ROUTE_DAILY_FLIGHT_COUNT_COLUMN,
    SCHEDULED_SPEED_MPH_COLUMN,
]

MODEL_FEATURE_COLUMNS_V2 = [
    *[column for column in MODEL_FEATURE_COLUMNS if column != TARGET_COLUMN],
    *MODEL_V2_ENGINEERED_FEATURE_COLUMNS,
    TARGET_COLUMN,
]

MODEL_PREDICTOR_COLUMNS = [
    column for column in MODEL_FEATURE_COLUMNS if column != TARGET_COLUMN
]

MODEL_HISTORICAL_RATE_COLUMNS = [
    "AIRLINE_HIST_DELAY_RATE",
    "ORIGIN_HIST_DELAY_RATE",
    "DEST_HIST_DELAY_RATE",
    "ROUTE_HIST_DELAY_RATE",
]

MODEL_INTERACTION_HISTORICAL_RATE_COLUMNS = [
    "AIRLINE_ORIGIN_HIST_DELAY_RATE",
    "AIRLINE_DEST_HIST_DELAY_RATE",
]

HISTORICAL_RECENT_WINDOW_DAYS = (7, 30)
MODEL_RECENT_HISTORICAL_RATE_COLUMNS = [
    f"{entity}_{window_days}D_HIST_DELAY_RATE"
    for entity in ("AIRLINE", "ORIGIN", "DEST", "ROUTE")
    for window_days in HISTORICAL_RECENT_WINDOW_DAYS
]

MODEL_HISTORICAL_RATE_COLUMNS_V2 = [
    *MODEL_HISTORICAL_RATE_COLUMNS,
    *MODEL_INTERACTION_HISTORICAL_RATE_COLUMNS,
    *MODEL_RECENT_HISTORICAL_RATE_COLUMNS,
]

# Intermediate leakage-safe building blocks. Never used as model inputs.
MODEL_INTERMEDIATE_HIST_COLUMNS = [
    "AIRLINE_PRIOR_FLIGHTS",
    "AIRLINE_PRIOR_DELAYS",
    "ORIGIN_PRIOR_FLIGHTS",
    "ORIGIN_PRIOR_DELAYS",
    "DEST_PRIOR_FLIGHTS",
    "DEST_PRIOR_DELAYS",
    "ROUTE_PRIOR_FLIGHTS",
    "ROUTE_PRIOR_DELAYS",
    "DAILY_FLIGHT_COUNT",
    "DAILY_DELAY_COUNT",
    "DAILY_ORIGIN_FLIGHT_COUNT",
    "DAILY_ORIGIN_DELAY_COUNT",
    "DAILY_DEST_FLIGHT_COUNT",
    "DAILY_DEST_DELAY_COUNT",
    "DAILY_ROUTE_FLIGHT_COUNT",
    "DAILY_ROUTE_DELAY_COUNT",
]

MODEL_CATEGORICAL_COLUMNS = [
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    ORIGIN_CITY_COLUMN,
    ORIGIN_STATE_COLUMN,
    DESTINATION_CITY_COLUMN,
    DESTINATION_STATE_COLUMN,
    SEASON_COLUMN,
    TIME_OF_DAY_COLUMN,
    FLIGHT_DISTANCE_CATEGORY_COLUMN,
]

MODEL_NUMERICAL_COLUMNS = [
    QUARTER_COLUMN,
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    DISTANCE_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    DEP_HOUR_COLUMN,
    DEP_MINUTE_COLUMN,
    ARR_HOUR_COLUMN,
    ARR_MINUTE_COLUMN,
    IS_WEEKEND_COLUMN,
    *MODEL_HISTORICAL_RATE_COLUMNS,
]

# Raw HHMM schedule-time columns (SCHEDULED_DEPARTURE_COLUMN,
# SCHEDULED_ARRIVAL_COLUMN) are intentionally excluded from
# MODEL_NUMERICAL_COLUMNS: their format is not an ordinary continuous
# integer (e.g. 2359 -> 1 at midnight is a 2-minute gap encoded as a
# ~2358-unit jump), so they must not be fed to the model as raw numeric
# values. ARR_HOUR_COLUMN / ARR_MINUTE_COLUMN (decomposed, like
# DEP_HOUR_COLUMN / DEP_MINUTE_COLUMN) carry the same information safely.
# The raw columns remain in MODEL_FEATURE_COLUMNS for display/reporting
# use in notebooks 10/11, just not as model inputs here.

MODEL_INPUT_COLUMNS = MODEL_CATEGORICAL_COLUMNS + MODEL_NUMERICAL_COLUMNS

# SCHEDULED_DEPARTURE_COLUMN is carried through as a passthrough join/
# reporting key (see MODELING_JOIN_KEY_COLUMNS and MODEL_HASHED_OUTPUT_COLUMNS
# above, and its use in notebook 10 for display formatting), not as a model
# input -- it stays out of MODEL_INPUT_COLUMNS for the reason explained above,
# but must still survive the hist-table selection or the later
# .select(*MODEL_HASHED_OUTPUT_COLUMNS) call fails to resolve it.
MODEL_HIST_TABLE_COLUMNS = [
    *MODEL_INPUT_COLUMNS,
    FLIGHT_DATE_COLUMN,
    FLIGHT_NUMBER_COLUMN,
    SCHEDULED_DEPARTURE_COLUMN,
    TARGET_COLUMN,
]

MODELING_REQUIRED_HIST_COLUMNS = set(MODEL_HIST_TABLE_COLUMNS)


# ============================================================
# Modeling configuration
# ============================================================

RANDOM_SEED = 42
TRAIN_RATIO = 0.80
TEST_RATIO = 0.20

TRAIN_END_DATE = "2025-08-31"
VALIDATION_START_DATE = "2025-09-01"
VALIDATION_END_DATE = "2025-10-31"
TEST_START_DATE = "2025-11-01"

HISTORICAL_SMOOTHING_STRENGTH = 100.0
# Symmetric Bernoulli prior used only when no earlier training date exists.
HISTORICAL_INITIAL_PRIOR_RATE = 0.5


# ============================================================
# Operational analysis configuration
# ============================================================

MIN_OPERATIONAL_FLIGHTS = 1000
MIN_ROUTE_FLIGHTS = 100
TOP_N_RESULTS = 20

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

LEAKAGE_COLUMNS = [
    DEPARTURE_DELAY_COLUMN,
    ARRIVAL_DELAY_COLUMN,
    DEPARTURE_DELAY_FLAG_COLUMN,
    TAXI_OUT_COLUMN,
    TAXI_IN_COLUMN,
    ACTUAL_ELAPSED_TIME_COLUMN,
    AIR_TIME_COLUMN,
    *DELAY_CAUSE_COLUMNS,
]


# ============================================================
# Model training notebook configuration
# ============================================================

TUNING_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_tree_tuning"
MODELS_PATH = f"{VOLUME_PATH}/models"
SELECTED_MODEL_PATH = f"{MODELS_PATH}/xgboost_final"
SELECTED_MODEL_BUNDLE_PATH = f"{SELECTED_MODEL_PATH}/model_bundle.joblib"
SELECTED_MODEL_METADATA_PATH = f"{SELECTED_MODEL_PATH}/model_metadata.json"
SELECTED_MODEL_METRICS_PATH = f"{SELECTED_MODEL_PATH}/model_metrics.json"
FINAL_MODEL_EVALUATION_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_final_model_evaluation"
)
FINAL_MODEL_THRESHOLD_COMPARISON_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_final_threshold_comparison"
)
FINAL_MODEL_CALIBRATION_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_final_calibration"
)
FINAL_MODEL_LIFT_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_final_lift"
FINAL_MODEL_SUBGROUP_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_final_subgroup_evaluation"
)

HASH_VECTOR_SIZE = 2**12

TREE_TUNING_SAMPLE_FRACTIONS = {
    0.0: 0.10,
    1.0: 0.30,
}

FINAL_TRAINING_SAMPLE_FRACTIONS = TREE_TUNING_SAMPLE_FRACTIONS

TUNING_FOLDS = [
    {
        "fold": "Fold 1",
        "train_start": "2025-01-01",
        "train_end": "2025-03-31",
        "validation_start": "2025-04-01",
        "validation_end": "2025-04-30",
    },
    {
        "fold": "Fold 2",
        "train_start": "2025-01-01",
        "train_end": "2025-04-30",
        "validation_start": "2025-05-01",
        "validation_end": "2025-05-31",
    },
    {
        "fold": "Fold 3",
        "train_start": "2025-01-01",
        "train_end": "2025-05-31",
        "validation_start": "2025-06-01",
        "validation_end": "2025-06-30",
    },
    {
        "fold": "Fold 4",
        "train_start": "2025-01-01",
        "train_end": "2025-06-30",
        "validation_start": "2025-07-01",
        "validation_end": "2025-07-31",
    },
    {
        "fold": "Fold 5",
        "train_start": "2025-01-01",
        "train_end": "2025-07-31",
        "validation_start": "2025-08-01",
        "validation_end": "2025-08-31",
    },
]

# The executable source of truth remains candidate_model_selection.json.
# This constant mirrors the currently approved V1 candidate for summaries.
SELECTED_MODEL_NAME = "XGBoost"

MODELING_TRAIN_HASHED_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_modeling_train_hashed"
MODELING_VALIDATION_HASHED_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_modeling_validation_hashed"
)
MODELING_TEST_HASHED_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_modeling_test_hashed"
MODELING_TRAIN_HIST_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_modeling_train_hist"
MODELING_VALIDATION_HIST_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_modeling_validation_hist"
)
MODELING_TEST_HIST_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_modeling_test_hist"
TUNED_MODEL_COMPARISON_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_tuned_model_comparison"
BASELINE_MODEL_COMPARISON_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_baseline_model_comparison"
)
FINALIST_MODEL_COMPARISON_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_finalist_model_comparison"
)
CANDIDATE_SELECTION_PATH = f"{MODELS_PATH}/candidate_model_selection.json"
MODEL_FEATURE_MANIFEST_PATH = f"{MODELS_PATH}/model_feature_manifest.json"
TUNED_MODEL_COMPARISON_V2_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_tuned_model_comparison_v2"
)
BASELINE_MODEL_COMPARISON_V2_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_baseline_model_comparison_v2"
)
FINALIST_MODEL_COMPARISON_V2_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_finalist_model_comparison_v2"
)
MODEL_VERSION_COMPARISON_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_model_version_comparison"
)
CANDIDATE_SELECTION_V2_PATH = (
    f"{MODELS_PATH}/candidate_model_selection_v2.json"
)
MODEL_FEATURE_MANIFEST_V2_PATH = f"{MODELS_PATH}/model_feature_manifest_v2.json"
TUNED_MODEL_COMPARISON_V3_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_tuned_model_comparison_v3"
)
BASELINE_MODEL_COMPARISON_V3_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_baseline_model_comparison_v3"
)
FINALIST_MODEL_COMPARISON_V3_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_finalist_model_comparison_v3"
)
MODEL_VERSION_COMPARISON_V3_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_model_version_comparison_v3"
)
CANDIDATE_SELECTION_V3_PATH = (
    f"{MODELS_PATH}/candidate_model_selection_v3.json"
)
MODEL_FEATURE_MANIFEST_V3_PATH = f"{MODELS_PATH}/model_feature_manifest_v3.json"

# Standard-Python model inputs. City/state fields and QUARTER are omitted
# because they duplicate information already represented by airport and MONTH.
PYTHON_MODEL_CATEGORICAL_COLUMNS = [
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    SEASON_COLUMN,
    TIME_OF_DAY_COLUMN,
    FLIGHT_DISTANCE_CATEGORY_COLUMN,
]
PYTHON_MODEL_NUMERICAL_COLUMNS = [
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    DISTANCE_COLUMN,
    SCHEDULED_ELAPSED_TIME_COLUMN,
    DEP_HOUR_COLUMN,
    DEP_MINUTE_COLUMN,
    ARR_HOUR_COLUMN,
    ARR_MINUTE_COLUMN,
    IS_WEEKEND_COLUMN,
    *MODEL_HISTORICAL_RATE_COLUMNS,
]
PYTHON_MODEL_INPUT_COLUMNS = (
    PYTHON_MODEL_CATEGORICAL_COLUMNS + PYTHON_MODEL_NUMERICAL_COLUMNS
)

PYTHON_MODEL_CATEGORICAL_COLUMNS_V2 = [
    *PYTHON_MODEL_CATEGORICAL_COLUMNS,
    ROUTE_COLUMN,
]
PYTHON_MODEL_NUMERICAL_COLUMNS_V2 = [
    *[
        column
        for column in PYTHON_MODEL_NUMERICAL_COLUMNS
        if column not in MODEL_HISTORICAL_RATE_COLUMNS
    ],
    DEP_TIME_SIN_COLUMN,
    DEP_TIME_COS_COLUMN,
    ARR_TIME_SIN_COLUMN,
    ARR_TIME_COS_COLUMN,
    MONTH_SIN_COLUMN,
    MONTH_COS_COLUMN,
    DAY_OF_WEEK_SIN_COLUMN,
    DAY_OF_WEEK_COS_COLUMN,
    ORIGIN_SCHEDULED_DEPARTURES_HOUR_COLUMN,
    DEST_SCHEDULED_ARRIVALS_HOUR_COLUMN,
    ROUTE_DAILY_FLIGHT_COUNT_COLUMN,
    SCHEDULED_SPEED_MPH_COLUMN,
    *MODEL_HISTORICAL_RATE_COLUMNS_V2,
]
PYTHON_MODEL_INPUT_COLUMNS_V2 = (
    PYTHON_MODEL_CATEGORICAL_COLUMNS_V2 + PYTHON_MODEL_NUMERICAL_COLUMNS_V2
)

# Runtime-aware deep tuning. Sampling is uniform within each chronological
# period, so the natural on-time/delayed distribution is preserved.
TUNING_MAX_TRAIN_ROWS = 80000
TUNING_MAX_VALIDATION_ROWS = 30000
CONFIRMATION_MAX_TRAIN_ROWS = 500000
CONFIRMATION_MAX_VALIDATION_ROWS = 250000
FINAL_MODEL_MAX_TRAIN_ROWS = 1000000
FINAL_HOLDOUT_MAX_ROWS = 500000
LOGISTIC_BROAD_SEARCH_SIZE = 16
LOGISTIC_REFINEMENT_SIZE = 4
RANDOM_FOREST_BROAD_SEARCH_SIZE = 20
RANDOM_FOREST_REFINEMENT_SIZE = 6
XGBOOST_BROAD_SEARCH_SIZE = 28
XGBOOST_REFINEMENT_SIZE = 8

# Each candidate receives a validation threshold selected by the same rule:
# maximize delayed-flight F1 while achieving at least 60% delayed recall.
MODEL_SELECTION_MIN_DELAY_RECALL = 0.60
MODEL_SELECTION_PR_AUC_TOLERANCE = 0.01
MODEL_SELECTION_MAX_PR_AUC_STD = 0.05
MODEL_SELECTION_THRESHOLD_MIN = 0.05
MODEL_SELECTION_THRESHOLD_MAX = 0.75
MODEL_SELECTION_THRESHOLD_STEP = 0.01

SHAP_SAMPLE_SIZE = 20000
SHAP_VALUES_SAMPLE_ROWS = 1000
SHAP_VALUES_TOP_FEATURES = 10
SHAP_GLOBAL_IMPORTANCE_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_shap_global_importance"
)
SHAP_DIRECTION_EFFECTS_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_delay_shap_direction_effects"
)
SHAP_VALUES_SAMPLE_TABLE = f"{CATALOG}.{SCHEMA}.flight_delay_shap_values_sample"
SHAP_ARTIFACTS_PATH = f"{MODELS_PATH}/shap_artifacts"
SHAP_LOCAL_EXPLANATION_PATH = f"{SHAP_ARTIFACTS_PATH}/local_explanation.json"
CALIBRATION_BINS = 10
CALIBRATION_SAMPLE_FRACTION = 0.20
TOP_RISK_PERCENTILES = [0.05, 0.10, 0.20]
THRESHOLD_SEARCH_MIN = 0.10
THRESHOLD_SEARCH_MAX = 0.90
THRESHOLD_SEARCH_STEP = 0.05
DEFAULT_DECISION_THRESHOLD = 0.50

SUBGROUP_ERROR_COLUMNS = [
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    MONTH_COLUMN,
    TIME_OF_DAY_COLUMN,
    SEASON_COLUMN,
]

MODEL_TRAINING_REQUIRED_COLUMNS = set(MODEL_FEATURE_COLUMNS)
MODEL_TRAINING_REQUIRED_COLUMNS_V2 = set(MODEL_FEATURE_COLUMNS_V2)


# ============================================================
# Statistical analysis configuration
# ============================================================

STATISTICAL_RESULTS_TABLE = f"{CATALOG}.{SCHEMA}.statistical_analysis_results"
STATISTICAL_RESULTS_PATH = f"{PROCESSED_PATH}/statistical_analysis_results"

STATISTICAL_SIGNIFICANCE_ALPHA = 0.05
STATISTICAL_SAMPLE_FRACTION = 0.05
STATISTICAL_MIN_EXPECTED_FREQUENCY = 5
STATISTICAL_TOP_AIRLINES = 10
STATISTICAL_TOP_AIRPORTS = 15
STATISTICAL_TOP_DEST_AIRPORTS = 15

STATISTICAL_CATEGORICAL_FACTORS = [
    MONTH_COLUMN,
    DAY_OF_WEEK_COLUMN,
    AIRLINE_COLUMN,
    ORIGIN_COLUMN,
    DESTINATION_COLUMN,
    SEASON_COLUMN,
    TIME_OF_DAY_COLUMN,
    IS_WEEKEND_COLUMN,
]

RESEARCH_QUESTIONS = {
    "RQ1": "Can flight delays be accurately predicted before departure using operational flight information?",
    "RQ2": "Which operational factors contribute the most to flight delays?",
    "RQ3": "Do certain airlines and airports consistently experience higher delay rates than others?",
    "RQ4": "Can prescriptive analytics improve operational decision-making by prioritizing high-risk flights under limited resources?",
    "RQ5": "Can Explainable Artificial Intelligence (SHAP) improve the interpretability of flight delay predictions for airline operations?",
}


# ============================================================
# Operational prioritization configuration
# ============================================================

PREDICTIONS_DELTA_PATH = f"{PROCESSED_PATH}/flight_predictions"
PRIORITIZATION_RESULTS_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_prioritization_results"
)
PRIORITIZATION_EVALUATION_TABLE = (
    f"{CATALOG}.{SCHEMA}.flight_prioritization_evaluation"
)
PRIORITIZATION_RESULTS_PATH = f"{PROCESSED_PATH}/flight_prioritization_results"
PRIORITIZATION_EVALUATION_PATH = (
    f"{PROCESSED_PATH}/flight_prioritization_evaluation"
)

CAPACITY_K_OPTIONS = (10, 25, 50, 100)
DEFAULT_CAPACITY_K = 25
MAX_FLIGHTS_PER_AIRPORT = 5
MAX_FLIGHTS_PER_AIRLINE = 4
PRIORITIZATION_POOL_MIN_PROB = HIGH_RISK_THRESHOLD

SCORING_START_DATE = VALIDATION_START_DATE
SCORING_END_DATE = VALIDATION_END_DATE

RISK_RECOMMENDATIONS = {
    "LOW": "Routine Monitoring",
    "MEDIUM": "Increased Operational Monitoring",
    "HIGH": "Priority Operational Review",
    "CRITICAL": "Immediate Operational Assessment",
}

CRITICAL_RISK_THRESHOLD = 0.80
MEDIUM_RISK_THRESHOLD = LOW_RISK_THRESHOLD


# ============================================================
# Dashboard preparation configuration
# ============================================================

DASHBOARD_DELTA_PATH = f"{PROCESSED_PATH}/flight_dashboard"
DASHBOARD_METADATA_PATH = f"{MODELS_PATH}/dashboard_metadata.json"
DASHBOARD_EXPLORER_TABLE = f"{CATALOG}.{SCHEMA}.flight_dashboard_explorer"
DASHBOARD_EXPLORER_PATH = f"{PROCESSED_PATH}/flight_dashboard_explorer"
DASHBOARD_INSIGHTS_TABLE = f"{CATALOG}.{SCHEMA}.flight_dashboard_insights"
DASHBOARD_INSIGHTS_PATH = f"{PROCESSED_PATH}/flight_dashboard_insights"

DELAY_CAUSE_LABELS = {
    "CARRIER_DELAY": "Carrier",
    "WEATHER_DELAY": "Weather",
    "NAS_DELAY": "NAS",
    "SECURITY_DELAY": "Security",
    "LATE_AIRCRAFT_DELAY": "Late Aircraft",
}
