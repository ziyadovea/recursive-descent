import os

dir = os.path.abspath(os.curdir)

with open(dir + '\\f.txt') as f:
    lines = f.readlines()

ans = ''
f = False
set = set()
for line in lines:
    for el in line:
        if el == '<':
            f = True
        if el == '>' and ans:
            ans += '>, '
            set.add(ans)
            ans = ''
            f = False
        if f:
            ans += el

ans = ''       
for el in set:
    ans += el

print(ans)