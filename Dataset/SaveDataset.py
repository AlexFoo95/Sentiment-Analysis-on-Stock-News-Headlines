import psycopg2

import xlrd

conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
cur = conn.cursor()

ExcelFileName= 'headlines_dataset.xlsx'
workbook = xlrd.open_workbook(ExcelFileName)
worksheet = workbook.sheet_by_name("Sheet1") # We need to read the data

num_rows = 60000
num_cols = 2

result_data =[]
for curr_row in range(0, num_rows, 1):
    headline = worksheet.cell_value(curr_row, 0)
    polarity = worksheet.cell_value(curr_row, 1)
    sql = """INSERT INTO public."dataset"("data_headline", "data_polarity") VALUES ( %s, %s);"""
    data = (headline,polarity)
    cur.execute(sql, data)

conn.commit()
cur.close()


