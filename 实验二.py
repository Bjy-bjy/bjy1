import re
a= open("33.txt",encoding='utf-8').read()
b = ''.join(a)
c = re.sub('<[^<]+?>', '', b).replace('\n', '').strip()
print(c)
print("adsda")