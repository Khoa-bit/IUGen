from pandas_ods_reader import read_ods

from models import Classroom, Course
from settings import WEEK_DAYS_DICT


def read_ods_catalog(ods_file):
    catalog_df = read_ods(ods_file, 0)
    courses_dict = {}

    for idx, row in catalog_df.iterrows():
        validate_row(idx, row, ods_file)

        if row["Select"] is None:
            continue

        course = get_or_create_course(courses_dict, row)

        if row["Has Lab"] is not None:
            pair_classrooms = create_pair_classrooms(row)
            course.add_pair_classrooms(pair_classrooms)
        else:
            classroom = create_classroom(row)
            course.add_classroom(classroom)

    return courses_dict


def create_classroom(row):
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
    return classroom


def create_pair_classrooms(row):
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
    return pair_classrooms


def validate_row(idx, row, ods_file):
    has_week_date = row["Week Date"] is not None and row["Week Date"] != "\xa0"
    has_start_period = row["Start Period"] is not None and row["Start Period"] != "\xa0"
    has_no_periods = row["No. Periods"] is not None and row["No. Periods"] != "\xa0"
    has_classroom = row["Classroom"] is not None and row["Classroom"] != "\xa0"
    if not (has_week_date and has_start_period and has_no_periods and has_classroom):
        raise RuntimeError(
            "Missing value on row {} of {}:\n{}".format(idx, ods_file, row)
        )


def get_or_create_course(courses_dict, row):
    try:
        course = courses_dict[row["Course Code"]]
    except KeyError:
        course = Course(
            code=row["Course Code"],
            name=row["Course Name"].lstrip("\xa0"),
            no_credits=row["Credits"],
        )
        courses_dict[row["Course Code"]] = course
    return course


def parse_week_date(week_date_str: str) -> int:
    week_date_str = week_date_str.rstrip(" ")
    if week_date_str == "Hai":
        week_date_int = WEEK_DAYS_DICT["MON"]
    elif week_date_str == "Ba":
        week_date_int = WEEK_DAYS_DICT["TUE"]
    elif week_date_str == "Tư":
        week_date_int = WEEK_DAYS_DICT["WED"]
    elif week_date_str == "Năm":
        week_date_int = WEEK_DAYS_DICT["THU"]
    elif week_date_str == "Sáu":
        week_date_int = WEEK_DAYS_DICT["FRI"]
    elif week_date_str == "Bảy":
        week_date_int = WEEK_DAYS_DICT["SAT"]
    elif week_date_str == "Chủ Nhật":
        week_date_int = WEEK_DAYS_DICT["SUN"]
    else:
        week_date_int = -1
    return week_date_int
