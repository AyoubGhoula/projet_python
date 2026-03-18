def multiply_matrix(A,B,lA,cB):
  global C
  if  lA == cB:
    C=[[0]*lA for i in range(cB)]
    for row in range(lA): 
        for col in range(cB):
            for elt in range(len(B)):
              C[row][col] += A[row][elt] * B[elt][col]
    return C
  else:
    return "Sorry :'( erreur 404"
print("mtrice A")
cA=int(input("donner c : "))
lA=int(input("donner l : "))
A=[[0]*cA for i in range(lA)]
print("mtrice B")
cB=int(input("donner c : "))
lB=int(input("donner l : "))
B=[[0]*cB for i in range(lB)]
print(multiply_matrix(A,B,lA,cB))

    