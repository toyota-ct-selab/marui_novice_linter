x = input()
if '.' not in x:
  x += '.'
a, b = x.strip('0').split('.')
if len(a):
  e = len(a)-1
  b = (a[1:] + b).rstrip('0')
  a = a[0]
else:
  e = -len(b)
  b = b.lstrip('0')
  a = b[0]
  b = b[1:]
  e += len(b)
print('%s%s%s' % (a, ('.'+b) if b != '' else '', ('E'+str(e)) if e != 0 else ''))