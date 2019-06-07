import psycopg2

import xlrd

conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
cur = conn.cursor()

ExcelFileName= 'Testing_data.xlsx'
#--- open the excel file
workbook = xlrd.open_workbook(ExcelFileName)
#--- go to the sheet in the excel file
worksheet = workbook.sheet_by_name("test")

#--- number of rows that contain test data
num_rows = 1000

#--- number of column that contain test data
num_cols = 2

# read the data from each row and column and store in db
result_data =[]
for curr_row in range(0, num_rows, 1):
    headline = worksheet.cell_value(curr_row, 0)
    polarity = worksheet.cell_value(curr_row, 1)
    sql = """INSERT INTO public."testdataset"("data_headline", "data_polarity") VALUES ( %s, %s);"""
    data = (headline,polarity)
    cur.execute(sql, data)

conn.commit()
cur.close()
