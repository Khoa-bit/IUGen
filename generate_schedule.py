import xlsxwriter

from models import Course
from settings import (
    BREAK_PROPERTIES,
    COLOR_CELL_PROPERTIES,
    COLOR_PALETTE,
    DEFAULT_CELL_PROPERTIES,
    HEADER_PROPERTIES,
    PERIODS_PER_DAY,
    RESULT_XLSX,
    WEEK_DAYS_DICT,
)
from utils import read_ods_catalog


class Generator:
    WEEK_DAYS = 7

    def __init__(self):
        self.courses_dict = {}

        self.default_cell_format = None
        self.color_cell_formats_list = None
        self.header_format = None
        self.break_format = None
        self.worksheet = None
        self.rows_written = 0

        self.week_list = [
            [None for _ in range(self.WEEK_DAYS)] for _ in range(PERIODS_PER_DAY)
        ]
        self.cells_format_list = [
            [DEFAULT_CELL_PROPERTIES for _ in range(self.WEEK_DAYS)]
            for _ in range(PERIODS_PER_DAY)
        ]

        self.courses_tuple = ()

    def run(self):
        read_ods_catalog(self.courses_dict)
        self.courses_tuple = tuple(self.courses_dict.values())

        with xlsxwriter.Workbook(RESULT_XLSX) as workbook:
            self.worksheet = workbook.add_worksheet()
            self.worksheet.set_column(1, 7, 20)
            self.rows_written = 0

            def get_format_color(i):
                color_cell_format = workbook.add_format(COLOR_CELL_PROPERTIES)
                color_cell_format.set_bg_color(COLOR_PALETTE[i])
                return color_cell_format

            self.default_cell_format = workbook.add_format(DEFAULT_CELL_PROPERTIES)
            self.color_cell_formats_list = [
                get_format_color(i) for i in range(len(self.courses_tuple))
            ]
            self.header_format = workbook.add_format(HEADER_PROPERTIES)
            self.break_format = workbook.add_format(BREAK_PROPERTIES)

            self.cells_format_list = [
                [self.default_cell_format for _ in range(self.WEEK_DAYS)]
                for _ in range(PERIODS_PER_DAY)
            ]

            self.generate_schedule(0)

    def generate_schedule(self, course_idx):
        if course_idx >= len(self.courses_tuple):
            self.xlsx_write_schedule()
        else:
            course: Course = self.courses_tuple[course_idx]
            for group_tuple in course.groups_list:
                if not self.is_free(group_tuple):
                    continue
                self.set_periods(course_idx, group_tuple)
                self.generate_schedule(course_idx + 1)
                self.free_periods(group_tuple)

    def is_free(self, group_tuple) -> bool:
        for classroom in group_tuple:
            for i in range(classroom.no_periods):
                if (
                    self.week_list[classroom.start_period + i - 1][classroom.week_date]
                    is not None
                ):
                    return False
        return True

    def set_periods(self, course_idx, group_tuple):
        for classroom in group_tuple:
            self.week_list[classroom.start_period - 1][
                classroom.week_date
            ] = self.courses_tuple[course_idx].name
            for i in range(classroom.no_periods - 1):
                self.cells_format_list[classroom.start_period + i - 1][
                    classroom.week_date
                ] = self.color_cell_formats_list[course_idx]

            self.week_list[classroom.start_period + classroom.no_periods - 2][
                classroom.week_date
            ] = "{} - {}".format(classroom.professor, classroom.name)
            self.cells_format_list[classroom.start_period + classroom.no_periods - 2][
                classroom.week_date
            ] = self.color_cell_formats_list[course_idx]

    def free_periods(self, group_tuple):
        for classroom in group_tuple:
            for i in range(classroom.no_periods):
                self.week_list[classroom.start_period + i - 1][
                    classroom.week_date
                ] = None
                self.cells_format_list[classroom.start_period + i - 1][
                    classroom.week_date
                ] = self.default_cell_format

    def xlsx_write_schedule(self):
        self.worksheet.set_row(self.rows_written, 30)
        self.worksheet.write_row(
            self.rows_written, 1, list(WEEK_DAYS_DICT.keys()), self.header_format
        )
        self.rows_written += 1

        for period in enumerate(self.week_list):
            self.worksheet.write(
                self.rows_written, 0, period[0] + 1, self.default_cell_format
            )
            for week_date in enumerate(self.week_list[period[0]]):
                self.worksheet.write(
                    self.rows_written,
                    week_date[0] + 1,
                    self.week_list[period[0]][week_date[0]],
                    self.cells_format_list[period[0]][week_date[0]],
                )
                self.worksheet.set_row(self.rows_written, 30)
            self.rows_written += 1

        self.worksheet.set_row(self.rows_written, 50, self.break_format)
        self.rows_written += 1
