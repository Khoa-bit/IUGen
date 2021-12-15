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
        self.all_classrooms = []

    def add_classroom(self, classroom: Classroom):
        classroom.course = self
        self.all_classrooms.append((classroom,))

    def add_pair_classrooms(self, pair_classrooms: list):
        pair_classrooms[0].course = self
        pair_classrooms[1].course = self

        self.all_classrooms.append(tuple(pair_classrooms))

    def __repr__(self):
        return f"{self.all_classrooms}"
