MON = 0
TUE = 1
WED = 2
THU = 3
FRI = 4
SAT = 5
SUN = 6


def generate_schedule(course_idx, courses_list_list: list):
    if course_idx >= len(courses_list_list):
        print_schedule()
        return
    else:
        for group_tuple in courses_list_list[course_idx]:
            if not is_free(group_tuple):
                return
            set_periods(course_idx, group_tuple)
            generate_schedule(course_idx + 1, courses_list_list)
            free_periods(group_tuple)

        return


def is_free(group_tuple) -> bool:
    global week_list
    for classroom in group_tuple:
        for i in range(classroom[2]):
            if week_list[classroom[0]][classroom[1] + i - 1] != -1:
                return False
    return True


def set_periods(course_idx, group_tuple):
    global week_list
    for classroom in group_tuple:
        for i in range(classroom[2]):
            week_list[classroom[0]][classroom[1] + i - 1] = course_idx


def free_periods(group_tuple):
    global week_list
    for classroom in group_tuple:
        for i in range(classroom[2]):
            week_list[classroom[0]][classroom[1] + i - 1] = -1


def print_schedule():
    global week_list
    for week_date_list in week_list:
        print(week_date_list)
    print("=================================")


if __name__ == "__main__":
    courses = [
        (((MON, 1, 3), (TUE, 7, 4)), ((WED, 1, 3), (FRI, 7, 4))),
        (((TUE, 7, 3), (FRI, 1, 4)), ((MON, 1, 3), (FRI, 7, 4))),
        (((MON, 5, 2),), ((TUE, 5, 2),)),
    ]

    periods_per_day = 12
    week_days = 7
    # -1 = Free
    # other = Occupied
    week_list = [[-1 for _ in range(periods_per_day)] for _ in range(week_days)]
    generate_schedule(0, courses)
