import math
import time


# Code 1: brut force
def meilleur_cycle(G, debut, p):
    """
    G : matrice d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Explore récursivement tous les chemins possibles jusqu’à p échanges et conserve 
        le cycle donnant le gain total le plus élevé. Cette approche teste toutes les 
        combinaisons possibles.

    Complexité :
        Temps : O(n^p), avec n = nombre de monnaies
        Mémoire : O(p), profondeur maximale de la récursion
    """
    def dfs(noeud, gain, chemin, profondeur):
        meilleur_gain = 0.0
        meilleur_chemin = []

        # Si on est de retour au début, c'est un cycle valide qu'on enregistre
        if noeud == debut and profondeur > 0:
            meilleur_gain = gain
            meilleur_chemin = chemin

        # Si on a atteint la profondeur maximale
        if profondeur == p:
            return meilleur_gain, meilleur_chemin

        # On continue l'exploration
        for suivant, taux in G[noeud].items():
            gain_suiv, chemin_suiv = dfs(suivant, gain * taux, chemin + [suivant], profondeur + 1)
            if gain_suiv > meilleur_gain:
                meilleur_gain, meilleur_chemin = gain_suiv, chemin_suiv

        return meilleur_gain, meilleur_chemin

    return dfs(debut, 1.0, [debut], 0)


# Code 2: code optimisé
def meilleur_cycle_ameliore(G, debut, p):
    """
    G : matrice d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Utilise une approche inspirée de Bellman-Ford pour calculer le meilleur cycle 
        en au plus p échanges. À chaque itération k, on mémorise le gain maximal pour 
        atteindre chaque sommet en k étapes, puis on cherche le cycle le plus rentable
        et on reconstruit le meilleur chemin ensuite.

    Complexité :
        Temps : O(pE), avec E = nombre d’arêtes
        Mémoire : O(pV), avec V = nombre de sommets
    """
    # dp[k][u] = meilleur gain pour atteindre u en exactement k échanges
    # parent[k][u] = prédécesseur de u pour ce meilleur gain
    dp = [{u: 0.0 for u in G} for _ in range(p + 1)]
    parent = [{u: None for u in G} for _ in range(p + 1)]

    dp[0][debut] = 1.0

    for k in range(1, p + 1):
        maj = False 

        for u in G:
            if dp[k - 1][u] <= 0.0:
                continue  # Si le gain est nul on ne l'utilise pas

            gain_courant = dp[k - 1][u]

            # On essaye tous les échanges possibles depuis u
            for v, taux in G[u].items():
                nouveau_gain = gain_courant * taux

                # Si ce nouveau gain est meilleur, on le conserve
                if nouveau_gain > dp[k][v]:
                    dp[k][v] = nouveau_gain
                    parent[k][v] = u
                    maj = True

        # Pas d'amélioration du meilleur gain
        if not maj:
            break

    # Recherche du meilleur cycle revenant à la monnaie de départ
    meilleur_gain = 0.0
    meilleur_k = None
    for k in range(1, p + 1):
        if dp[k][debut] > meilleur_gain:
            meilleur_gain = dp[k][debut]
            meilleur_k = k

    # Aucun cycle trouvé
    if meilleur_k is None:
        return 0.0, []

    # Reconstruction du cycle optimal à partir des parents
    cycle_inverse = []
    monnaie = debut

    for etape in range(meilleur_k, 0, -1):
        precedent = parent[etape][monnaie]
        cycle_inverse.append(precedent)
        monnaie = precedent

    # Inversion pour retrouver le cycle dans le bon ordre
    cycle_inverse.reverse()
    meilleur_cycle = cycle_inverse + [debut]

    return meilleur_gain, meilleur_cycle


G = {
    'E': {'D': 1.19, 'J': 1.33, 'F': 1.62},
    'D': {'E': 0.84, 'J': 1.12, 'F': 1.37},
    'J': {'E': 0.75, 'D': 0.89, 'F': 1.22},
    'F': {'E': 0.62, 'D': 0.73, 'J': 0.82}
}

meilleur_gain, meilleur_chemin = meilleur_cycle(G, 'E', p=3)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

meilleur_gain, meilleur_chemin = meilleur_cycle_ameliore(G, 'E', p=3)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

"""
# Pour tester la rapidité des deux et le fait qu'ils renvoient le même chemin
algo1 = 0
algo2 = 0

for p in range(15):
    debut = time.time()
    gain1, _ = meilleur_cycle(G, 'E', p=p)
    algo1 += time.time() - debut
    print(p, ": algo1 :", time.time() - debut)
    debut = time.time()
    gain2, _ = meilleur_cycle_ameliore(G, 'E', p=p)
    algo2 += time.time() - debut
    print(p, ": algo2 :", time.time() - debut)
    if gain1 != gain2:
        print("PAS D'ÉGALITÉ ENTRE LES DEUX RÉSULTATS POUR p =", p)
print(algo1, algo2)
"""