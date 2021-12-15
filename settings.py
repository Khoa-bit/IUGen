from pathlib import Path

WEEK_DAYS_DICT = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}

COLOR_PALETTE = [
    "F38181",
    "F08A5D",
    "F9ED69",
    "A7FF83",
    "3282B8",
    "AA96DA",
    "FC5185",
    "DCD6F7",
]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
INPUT_TABULAR = BASE_DIR / "inputs/catalog.ods"
RESULT_XLSX = BASE_DIR / "results/schedules.xlsx"

DEFAULT_CELL_PROPERTIES = {"border": 1, "text_wrap": 1}
COLOR_CELL_PROPERTIES = {"border": 1, "text_wrap": 1, "bg_color": 0}
HEADER_PROPERTIES = {"border": 1, "text_wrap": 1, "bold": 1, "center_across": 1}
BREAK_PROPERTIES = {"bg_color": "#808080"}

PERIODS_PER_DAY = 12
