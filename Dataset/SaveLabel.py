import psycopg2

import xlrd

conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
cur = conn.cursor()

ExcelFileName= 'Labels.xlsx'
workbook = xlrd.open_workbook(ExcelFileName)
worksheet = workbook.sheet_by_name("Sheet1") # We need to read the data

num_rows = 3
num_cols = 2

result_data =[]
for curr_row in range(0, num_rows, 1):
    Vocab = worksheet.cell_value(curr_row, 0)
    id = worksheet.cell_value(curr_row, 1)
    sql = """INSERT INTO public."labels"("label_id", "label_vocab") VALUES ( %s, %s);"""
    data = (id,Vocab)
    cur.execute(sql, data)

conn.commit()
cur.close()