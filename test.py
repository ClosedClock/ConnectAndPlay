
def f2():
    global name
    print(name)
    name = 'b'
    print(name)



name = 'u'
f2()
print(name)
