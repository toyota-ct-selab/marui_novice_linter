n = int(input())
b = list(map(int, input().split()))
b.append(0)
a = map(lambda x, y: str(x+y), b, b[1:])
print(" ".join(a))