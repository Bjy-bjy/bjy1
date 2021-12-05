# coding=gbk
import xlrd
def read_excel(excel_path, sheet_name):
    # ���ȴ�excel��formatting_info=True ������excelԭ���ĸ�ʽ
    xls = xlrd.open_workbook(excel_path, formatting_info=True)
    # ͨ��sheet�����ƻ��sheet����
    sheet = xls.sheet_by_name(sheet_name)
    # ͨ��sheet������ȥ���sheet����
    # sheet =xls.sheet_by_index(0)
    # ����һ���յ��б����ڶ�ȡ���������
    datalist = []
    for rows in range(1, sheet.nrows):  # �ӵ�2�п�ʼѭ��ȥ��
        # ��ȡ���е�����
        # print(sheet.row_values(rows))
        # ����һ���ݴ��б�
        temptlist = []
        for cols in range(0, sheet.ncols-2):  # �ӵ�1��ѭ��ȥ��ȡ�У�����������3�У�����2�У��ֱ�������д�����ʱ�䡢���Խ��
            if cols == 0:
                temptlist.append(rows)  # �ж�����ǵ�1�У���ֱ�Ӵ�������
            else:
            	temptlist.append(sheet.cell_value(rows, cols))  # ���� ��ȡ��Ԫ������
        datalist.append(temptlist)  # ��ÿһ��ѭ������һ�е�������֮�󣬽�����׷�ӵ�datalist�б���
    return datalist


if __name__ == "__main__":
    print(read_excel("data/data2.xlsx", "��Ӧ�̵Ĺ�����(m?)"))
