
import jieba
import difflib
file1 = open("三国演义.txt",encoding='utf-8').read()
file2 = open("水浒传.txt",encoding='utf-8').read()
str11 = jieba.lcut(file1)
str22 = jieba.lcut(file2)
diff_result = difflib.SequenceMatcher(None, file1, file2).ratio()
print('方法一：Python标准库difflib的计算分值：' + str(diff_result))