a=input().split(".")
l=[[a[0]]]
for i in a[1:-1]:
	m=min(3,len(i)-1)
	l[-1]+=[i[:m]]
	l+=[[i[m:]]]
l[-1]+=[a[-1]]
if len(a)<2 or any(len(i) not in range(1,9) or len(j) not in range(1,4) for i,j in l):
	print("NO")
else:
	print("YES")
	print("\n".join(".".join(i) for i in l))