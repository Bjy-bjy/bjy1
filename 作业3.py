def demo(n):
    lst = list(range(1,21))
    lst.append(n)
    lst.sort()
    return lst
print(demo(5))