def add_polynome(p1, p2):
    """Calcule la somme de deux polynômes."""
    # Créer une liste de zéros pour le polynôme résultat
    res = [0] * max(len(p1), len(p2))

    # Ajouter les coefficients de chaque polynôme
    for i in range(len(p1)):
        res[i] += p1[i]
    for i in range(len(p2)):
        res[i] += p2[i]

    return res

# Deux polynômes d'exemple
p1 = [3,0,2,1]
p2 = [2,0,1]

# Addition des deux polynômes
res = add_polynome(p1, p2)

# Affichage du résultat
print("Résultat de l'addition :", res)
