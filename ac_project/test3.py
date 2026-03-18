import numpy as np
print("mtrice A")
cA=int(input("donner c : "))
lA=int(input("donner l : "))
A=[[0]*cA for i in range(lA)]
for i in range (lA) :
        for j in range (cA):
            A[i][j]=int(input("donner A("+str(i+1)+","+str(j+1)+") : "))
print("mtrice B")
B=[[0]*cA for i in range(lA)]
for i in range (lA) :
        for j in range (cA):
            B[i][j]=int(input("donner B("+str(i+1)+","+str(j+1)+") : "))
if cA==lA:
    print(np.matmul(A,B))
else:
    print("not correct")
print(np.add(A,B))
print (np.subtract(A,B))