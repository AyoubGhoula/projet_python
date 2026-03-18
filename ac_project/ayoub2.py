def div_polynome(dividende, diviseur):
    deg_dividende = len(dividende) - 1
    deg_diviseur = len(diviseur) - 1

    if deg_diviseur < 0:
        raise ValueError("Le diviseur ne peut pas être le polynôme nul.")

    if deg_dividende < deg_diviseur:
        return [], dividende

    quotient = [0] * (deg_dividende - deg_diviseur + 1)

    while deg_dividende >= deg_diviseur:
        coef = dividende[deg_dividende] / diviseur[deg_diviseur]
        quotient[deg_dividende - deg_diviseur] = coef

        for i in range(deg_diviseur + 1):
            dividende[deg_dividende - i] -= coef * diviseur[deg_diviseur - i]

        deg_dividende -= 1

    reste = dividende[:deg_diviseur]
    return quotient, reste
