import psycopg2
import random
import xlrd

conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
cur = conn.cursor()

ExcelFileName= 'Training_data.xlsx'
#--- open the excel file
workbook = xlrd.open_workbook(ExcelFileName)
#--- go to the sheet in the excel file
worksheet = workbook.sheet_by_name("Sheet1")

#--- number of rows that contain train data
num_rows = 20000
alldata = []
#--- number of column that contain train data
num_cols = 2

# read the data from each row and column and store in db
result_data =[]
for curr_row in range(0, num_rows, 1):
    sdata = []
    headline = worksheet.cell_value(curr_row, 0)
    polarity = worksheet.cell_value(curr_row, 1)
    sdata.append(headline)
    sdata.append(polarity)
    alldata.append(sdata)


random.shuffle(alldata)

for row in range (0,num_rows):
    sql = """INSERT INTO public."traindataset"("data_headline", "data_polarity") VALUES ( %s, %s);"""
    data = (alldata[row][0],alldata[row][1])
    cur.execute(sql, data)

conn.commit()
cur.close()


