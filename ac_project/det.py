import numpy
while True :
    c=int(input("donner c : "))
    m=[[0]*c for i in range(c)]
    print(m)
    for i in range (c) :
        for j in range (c):
            m[i][j]=int(input("donner m("+str(i+1)+","+str(j+1)+") : "))
    print(m)
    if (numpy.linalg.det(m))<0:
        print(int(numpy.linalg.det(m)-0.0000001))
    else :
        print(int(numpy.linalg.det(m)+0.0000001))
        
