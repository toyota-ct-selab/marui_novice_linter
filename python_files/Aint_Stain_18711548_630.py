a,b,c=map(float,input().split())
q=((b*b-4*a*c)**0.5)
x=((-b+q)/(2*a))
y=((-b-q)/(2*a))
print(max(x,y))
print(min(x,y))