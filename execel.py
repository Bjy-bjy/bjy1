# coding=gbk
import xlrd
def read_excel(excel_path, sheet_name):
    # 首先打开excel表，formatting_info=True 代表保留excel原来的格式
    xls = xlrd.open_workbook(excel_path, formatting_info=True)
    # 通过sheet的名称获得sheet对象
    sheet = xls.sheet_by_name(sheet_name)
    # 通过sheet的索引去获得sheet对象
    # sheet =xls.sheet_by_index(0)
    # 定义一个空的列表，用于读取后存入数据
    datalist = []
    for rows in range(1, sheet.nrows):  # 从第2行开始循环去读
        # 获取整行的内容
        # print(sheet.row_values(rows))
        # 定义一个暂存列表
        temptlist = []
        for cols in range(0, sheet.ncols-2):  # 从第1列循环去读取列，读到倒数第3列，倒数2列，分别是用于写入测试时间、测试结果
            if cols == 0:
                temptlist.append(rows)  # 判断如果是第1列，则直接存入行数
            else:
            	temptlist.append(sheet.cell_value(rows, cols))  # 否则 获取单元格内容
        datalist.append(temptlist)  # 把每一次循环读完一行的所有列之后，将数据追加到datalist列表中
    return datalist


if __name__ == "__main__":
    print(read_excel("data/data2.xlsx", "供应商的供货量(m?)"))
