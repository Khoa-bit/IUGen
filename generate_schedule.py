import csv
import glob
from pathlib import Path

import pandas as pd
import xlsxwriter
from pandas_ods_reader import read_ods

week_days_dict = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}


def read_ods_catalog():
    catalog_df = read_ods("catalog.ods", 0)

    for idx, row in catalog_df.iterrows():
        if row["Select"] is None:
            continue

        try:
            course = courses_dict[row["Course Code"]]
        except KeyError:
            course = Course(
                code=row["Course Code"],
                name=row["Course Name"].lstrip("\xa0"),
                no_credits=row["Credits"],
            )
            courses_dict[row["Course Code"]] = course

        if row["Has Lab"] is not None:
            name_list = row["Classroom"].split("\xa0")
            week_date_list = row["Week Date"].split("\xa0")
            start_period_list = row["Start Period"].split("\xa0")
            no_periods_list = row["No. Periods"].split("\xa0")
            professor_list = row["Professor"].split("\xa0")
            duration_list = row["Duration"].split("\xa0")
            pair_classrooms = []
            for i in range(2):
                pair_classrooms.append(
                    Classroom(
                        name=name_list[i],
                        week_date=parse_week_date(week_date_list[i]),
                        start_period=int(start_period_list[i]),
                        no_periods=int(no_periods_list[i]),
                        professor=professor_list[i],
                        duration=duration_list[i],
                        course_group=row["Course Group"],
                        lab_group=row["Lab Group"],
                        no_students=row["No. Students"],
                        no_slots=row["No. Slots"],
                    )
                )
            course.add_pair_classrooms(pair_classrooms)
        else:
            classroom = Classroom(
                name=row["Classroom"],
                week_date=parse_week_date(row["Week Date"]),
                start_period=int(row["Start Period"]),
                no_periods=int(row["No. Periods"]),
                professor=row["Professor"],
                duration=row["Duration"],
                course_group=row["Course Group"],
                lab_group=row["Lab Group"],
                no_students=row["No. Students"],
                no_slots=row["No. Slots"],
            )
            course.add_classroom(classroom)


def parse_week_date(week_date_str: str) -> int:
    global week_days_dict
    week_date_str = week_date_str.rstrip(" ")
    if week_date_str == "Hai":
        week_date_int = week_days_dict["MON"]
    elif week_date_str == "Ba":
        week_date_int = week_days_dict["TUE"]
    elif week_date_str == "Tư":
        week_date_int = week_days_dict["WED"]
    elif week_date_str == "Năm":
        week_date_int = week_days_dict["THU"]
    elif week_date_str == "Sáu":
        week_date_int = week_days_dict["FRI"]
    elif week_date_str == "Bảy":
        week_date_int = week_days_dict["SAT"]
    elif week_date_str == "Chủ Nhật":
        week_date_int = week_days_dict["SUN"]
    else:
        week_date_int = -1
    return week_date_int


class Classroom:
    def __init__(
        self,
        name,
        week_date,
        start_period,
        no_periods,
        professor,
        duration,
        course_group,
        lab_group,
        no_students,
        no_slots,
    ):
        self.name = name
        self.week_date = week_date
        self.start_period = start_period
        self.no_periods = no_periods
        self.professor = professor
        self.duration = duration
        self.course_group = course_group
        self.lab_group = lab_group
        self.no_students = no_students
        self.no_slots = no_slots
        self.schedule = (self.week_date, self.start_period, self.no_periods)
        self.course = None

    def __repr__(self):
        return f"{self.schedule}"


class Course:
    def __init__(self, code, name, no_credits):
        self.code = code
        self.name = name
        self.no_credits = no_credits
        self.groups_list = []

    def add_classroom(self, classroom: Classroom):
        classroom.course = self
        self.groups_list.append((classroom,))

    def add_pair_classrooms(self, pair_classrooms: list):
        pair_classrooms[0].course = self
        pair_classrooms[1].course = self

        self.groups_list.append(tuple(pair_classrooms))

    def __repr__(self):
        return f"{self.groups_list}"


def generate_schedule(course_idx, courses_tuple: tuple):
    if course_idx >= len(courses_tuple):
        print_schedule()
        return
    else:
        course: Course = courses_tuple[course_idx]
        for group_tuple in course.groups_list:
            if not is_free(group_tuple):
                continue
            set_periods(course_idx, group_tuple)
            generate_schedule(course_idx + 1, courses_tuple)
            free_periods(group_tuple)

        return


def is_free(group_tuple) -> bool:
    global week_list
    for classroom in group_tuple:
        for i in range(classroom.no_periods):
            if (
                week_list[classroom.start_period + i - 1][classroom.week_date]
                is not None
            ):
                return False
    return True


def set_periods(course_idx, group_tuple):
    global week_list, cells_format_list, workbook
    for classroom in group_tuple:
        cell_format = workbook.add_format(
            {"bg_color": color_palette[course_idx], "border": 1, "text_wrap": 1}
        )
        week_list[classroom.start_period - 1][classroom.week_date] = courses_list[
            course_idx
        ].name
        for i in range(classroom.no_periods - 1):
            cells_format_list[classroom.start_period + i - 1][
                classroom.week_date
            ] = cell_format

        week_list[classroom.start_period + classroom.no_periods - 2][
            classroom.week_date
        ] = "{} - {}".format(classroom.professor, classroom.name)
        cells_format_list[classroom.start_period + classroom.no_periods - 2][
            classroom.week_date
        ] = cell_format


def free_periods(group_tuple):
    global week_list, cells_format_list, default_cell_format
    for classroom in group_tuple:
        for i in range(classroom.no_periods):
            week_list[classroom.start_period + i - 1][classroom.week_date] = None
            cells_format_list[classroom.start_period + i - 1][
                classroom.week_date
            ] = default_cell_format


def print_schedule():
    global week_list, cells_format_list, worksheet, rows_written, default_cell_format
    week_list_dataframe = pd.DataFrame(week_list, columns=list(week_days_dict.keys()))
    # with open(RESULT_CSV, "a") as f:
    #     f.write(week_list_dataframe.to_csv(index=True))
    #     f.write("###," + "#################################," * 7 + "\n")

    header_format = workbook.add_format({"border": 1, "bold": 1, "center_across": 1})
    worksheet.set_row(rows_written, 30)
    worksheet.write_row(rows_written, 1, list(week_days_dict.keys()), header_format)
    rows_written += 1

    for period in range(len(week_list)):
        worksheet.write(rows_written, 0, period + 1, default_cell_format)
        for week_date in range(len(week_list[period])):
            worksheet.write(
                rows_written,
                week_date + 1,
                week_list[period][week_date],
                cells_format_list[period][week_date],
            )
            worksheet.set_row(rows_written, 30)
        rows_written += 1

    break_format = workbook.add_format({"bg_color": "#808080"})
    worksheet.set_row(rows_written, 50, break_format)
    rows_written += 1


courses_dict = {
    # 'AA': (((MON, 1, 3), (TUE, 7, 4)), ((WED, 1, 3), (FRI, 7, 4))),
    # 'BB': (((TUE, 7, 3), (FRI, 1, 4)), ((MON, 1, 3), (FRI, 7, 4))),
    # 'CC': (((MON, 5, 2),), ((MON, 5, 2),)),
}

color_palette = [
    "96BAFF",
    "88FFF7",
    "D59BF6",
    "9DF3C4",
    "F5E79D",
    "FE9898",
    "DBE2EF",
    "FF9A3C",
]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
RESULT_CSV = BASE_DIR / "schedules.csv"

# Courses list can have many Courses
# Course can have many groups
# Group can have 1 or 2 Classroom

if __name__ == "__main__":
    read_ods_catalog()

    with open(RESULT_CSV, "w") as f:
        f.write("")

    workbook = xlsxwriter.Workbook(str(RESULT_CSV)[:-4] + ".xlsx")
    worksheet = workbook.add_worksheet()
    worksheet.set_column(1, 7, 20)
    rows_written = 0

    default_cell_format = workbook.add_format({"border": 1})
    periods_per_day = 12
    week_days = 7
    week_list = [[None for _ in range(week_days)] for _ in range(periods_per_day)]
    cells_format_list = [
        [default_cell_format for _ in range(week_days)] for _ in range(periods_per_day)
    ]

    courses_list = tuple(courses_dict.values())
    generate_schedule(0, courses_list)

    workbook.close()
