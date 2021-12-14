from pandas_ods_reader import read_ods

from models import Classroom, Course
from settings import INPUT_ODS, WEEK_DAYS_DICT


def read_ods_catalog(courses_dict):
    catalog_df = read_ods(INPUT_ODS, 0)

    for _, row in catalog_df.iterrows():
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
