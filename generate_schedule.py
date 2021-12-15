import xlsxwriter

from models import Course
from settings import (
    INPUT_TABULAR,
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

    def __init__(self, tabular_file=INPUT_TABULAR):
        self.courses_dict = read_ods_catalog(tabular_file)
        self.default_cell_format = None
        self.color_cell_formats_list = None
        self.header_format = None
        self.break_format = None
        self.worksheet = None
        self.rows_pointer = 0

        self.schedule_table = [
            [None for _ in range(self.WEEK_DAYS)] for _ in range(PERIODS_PER_DAY)
        ]
        self.cells_format_list = [
            [DEFAULT_CELL_PROPERTIES for _ in range(self.WEEK_DAYS)]
            for _ in range(PERIODS_PER_DAY)
        ]

        self.courses_tuple = ()

    def run(self):
        self.courses_tuple = tuple(self.courses_dict.values())

        with xlsxwriter.Workbook(RESULT_XLSX) as workbook:
            print("Setting up workbook...")
            self.worksheet = workbook.add_worksheet()
            self.worksheet.set_column(1, 7, 20)
            self.rows_pointer = 0

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

            print("Generating schedules to {}...".format(RESULT_XLSX))
            self._generate_schedule_recursive(0)
            print("Done generating schedules to {}...".format(RESULT_XLSX))

    def _generate_schedule_recursive(self, course_idx):
        if course_idx >= len(self.courses_tuple):
            self._xlsx_write_schedule()
            print("\t-> Successfully generated a schedule")
        else:
            course: Course = self.courses_tuple[course_idx]
            for classrooms_tuple in course.all_classrooms:
                if not self._is_free(classrooms_tuple):
                    continue
                self._schedule_assign_classroom(course_idx, classrooms_tuple)
                self._generate_schedule_recursive(course_idx + 1)
                self._schedule_remove_classroom(classrooms_tuple)

    def _is_free(self, classrooms_tuple) -> bool:
        for classroom in classrooms_tuple:
            for i in range(classroom.no_periods):
                if (
                    self.schedule_table[classroom.start_period + i - 1][classroom.week_date]
                    is not None
                ):
                    return False
        return True

    def _schedule_assign_classroom(self, course_idx, classrooms_tuple):
        for classroom in classrooms_tuple:
            self.schedule_table[classroom.start_period - 1][
                classroom.week_date
            ] = self.courses_tuple[course_idx].name
            for i in range(classroom.no_periods - 1):
                self.cells_format_list[classroom.start_period + i - 1][
                    classroom.week_date
                ] = self.color_cell_formats_list[course_idx]

            self.schedule_table[classroom.start_period + classroom.no_periods - 2][
                classroom.week_date
            ] = "{} - {}".format(classroom.professor, classroom.name)
            self.cells_format_list[classroom.start_period + classroom.no_periods - 2][
                classroom.week_date
            ] = self.color_cell_formats_list[course_idx]

    def _schedule_remove_classroom(self, classrooms_tuple):
        for classroom in classrooms_tuple:
            for i in range(classroom.no_periods):
                self.schedule_table[classroom.start_period + i - 1][
                    classroom.week_date
                ] = None
                self.cells_format_list[classroom.start_period + i - 1][
                    classroom.week_date
                ] = self.default_cell_format

    def _xlsx_write_schedule(self):
        self.worksheet.set_row(self.rows_pointer, 30)
        self.worksheet.write_row(
            self.rows_pointer, 1, list(WEEK_DAYS_DICT.keys()), self.header_format
        )
        self.rows_pointer += 1

        for period in enumerate(self.schedule_table):
            self.worksheet.write(
                self.rows_pointer, 0, period[0] + 1, self.default_cell_format
            )
            for week_date in enumerate(self.schedule_table[period[0]]):
                self.worksheet.write(
                    self.rows_pointer,
                    week_date[0] + 1,
                    self.schedule_table[period[0]][week_date[0]],
                    self.cells_format_list[period[0]][week_date[0]],
                )
                self.worksheet.set_row(self.rows_pointer, 30)
            self.rows_pointer += 1

        self.worksheet.set_row(self.rows_pointer, 50, self.break_format)
        self.rows_pointer += 1
