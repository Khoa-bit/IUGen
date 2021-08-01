import xlsxwriter

if __name__ == "__main__":
    workbook = xlsxwriter.Workbook("sandbox.xlsx")
    worksheet = workbook.add_worksheet()

    data = ("Foo", "Bar", "Baz")
    worksheet.write_row(0, 0, data)

    workbook.close()
