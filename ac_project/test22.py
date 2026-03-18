def lire_polynome():
    """Lit les coefficients d'un polynôme depuis l'entrée standard."""
    coeffs = input("Entrez les coefficients du polynôme, séparés par des espaces : ")
    coeffs = list(map(float, coeffs.split()))
    co_pu=[[0]*2 for i in range (len(coeffs))]
    for i in range(len(coeffs)):
        co_pu[i][0]=coeffs[i]
    i=len(coeffs)-1
    while i>=0:
        co_pu[i][1]=len(coeffs)-i-1
        i-=1
    print (co_pu) 
    return co_pu

def mult_polynome(p1, p2):
    """Calcule le produit de deux polynômes."""
    # Créer une matrice de zéros pour le polynôme résultat
    res = [[0] * 2 for i in range(len(p1) + len(p2) - 1)]

    # Calculer les produits de chaque paire de coefficients
    for i in range(len(p1)):
        for j in range(len(p2)):
            res[i+j][0] += p1[i][0] * p2[j][0]
    i=len(p1) + len(p2) - 2
    while i>=0:
        res[i][1]=len(res)-(i+1)
        i-=1

    return res

# Lecture des deux polynômes
print("Premier polynôme :")
p1 = lire_polynome()
print("Deuxième polynôme :")
p2 = lire_polynome()

# Multiplication des deux polynômes
res = mult_polynome(p1, p2)

# Affichage du résultat
print("Résultat de la multiplication :", res)
