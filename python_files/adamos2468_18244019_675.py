lis=input().split()
a=int(lis[0])
b=int(lis[1])
c=int(lis[2])
if(b-a<0):
	if(c<0):
		d=-(b-a)
		dc=-c
		if(d%dc==0):
			print('YES')
		else:
			print('NO')
	else:
		print ('NO')			
elif(b==a):
	print('YES')
else:
	if(c>0):
		if((b-a)%c==0):
			print('YES')
		else:
			print('NO')
	else:
		print('NO')