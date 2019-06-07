import psycopg2

import xlrd

conn = psycopg2.connect(host="localhost", database="StockList", user="postgres", password="bursa")
cur = conn.cursor()

ExcelFileName= 'Company_Raw_Data.xlsx'
workbook = xlrd.open_workbook(ExcelFileName)
worksheet = workbook.sheet_by_name("Company_Raw_Data") # We need to read the data

num_rows = 932
num_cols = 2

result_data =[]
for curr_row in range(0, num_rows, 1):
    code = worksheet.cell_value(curr_row, 0)
    code = str(code)
    name = worksheet.cell_value(curr_row, 1)
    sql = """INSERT INTO public."company"("company_name", "company_code") VALUES ( %s, %s);"""
    data = (name,code)
    cur.execute(sql, data)

conn.commit()
cur.close()