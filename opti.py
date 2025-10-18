import math
import time

"""
Javier Pena Castano, Martin Leiva, Baptiste Pras

Nous avons fait 4 algorithmes:
- Code 1: naïf et inefficace
- Code 2: Fondé sur le principe de Bellman-Ford, plus efficace
- Code 3: Amélioration de l'algorithme 2 quand p > X
- Code 4: Utilisation adaptative intelligente des algorithmes 2 et 3, meilleur code

Des légères différences de gain peuvent arriver dans les tests car les algorithmes
prennent les cycles dans un sens différent, donc les erreurs d'arrondis liés aux
floats ne sont pas les mêmes, mais le résultat final est bien le même. (On fait
les mêmes cycles le même nombre de fois dans les chemins de chaque algorithme.)
"""


# Code 1: brut force
def meilleur_cycle(G, debut, p):
    """
    G : dictionnaire d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Explore récursivement tous les chemins possibles jusqu’à p échanges et conserve 
        le cycle donnant le gain total le plus élevé. Cette approche teste toutes les 
        combinaisons possibles.

    Complexité :
        Temps : O(|X|^p), avec |X| = nombre de sommets
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
    G : dictionnaire d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Utilise une approche inspirée de Bellman-Ford pour calculer le meilleur cycle 
        en au plus p échanges. À chaque itération k, on mémorise le gain maximal pour 
        atteindre chaque sommet en k étapes, puis on cherche le cycle le plus rentable
        et on reconstruit le meilleur chemin ensuite.

    Complexité :
        Temps : O(p|U|), avec |U| = nombre d’arêtes
        Mémoire : O(p|X|), avec |X| = nombre de sommets
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


# Code 3: code encore mieux optimisé
def meilleur_cycle_optimal(G, debut, p, X=-1):
    """
    G : dictionnaire d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Étape 1 — Exécute un Bellman-Ford amélioré jusqu'à |X| itérations
        pour obtenir le meilleur cycle simple de chaque taille possible (2 à |X|).

        Étape 2 — Utilise une DP "somme avec remise"
        pour combiner ces cycles simples et atteindre un total <= p échanges.

    Complexité :
        Temps : O(|X||U| + p|X|), avec |U| = nombre d’arêtes et |X| = nombre de sommets
        Mémoire : O(|X|^2 + p)
    """
    if X==-1:
        X = len(G)

    # Algo 2 jusqu’à |X| itérations
    dp = [{u: 0.0 for u in G} for _ in range(X + 1)]
    parent = [{u: None for u in G} for _ in range(X + 1)]

    dp[0][debut] = 1.0
    meilleur_cycle_simple = {} 

    for k in range(1, X + 1):
        maj = False
        for u in G:
            if dp[k - 1][u] <= 0.0:
                continue
            gain_courant = dp[k - 1][u]
            for v, taux in G[u].items():
                nouveau_gain = gain_courant * taux
                if nouveau_gain > dp[k][v]:
                    dp[k][v] = nouveau_gain
                    parent[k][v] = u
                    maj = True
        if not maj:
            break

        # On regarde si on a un cycle de taille k
        if dp[k][debut] > 0.0:
            # Reconstruction du cycle
            cycle_inverse = []
            monnaie = debut
            for etape in range(k, 0, -1):
                precedent = parent[etape][monnaie]
                cycle_inverse.append(precedent)
                monnaie = precedent
            cycle_inverse.reverse()
            meilleur_cycle_simple[k] = (dp[k][debut], cycle_inverse + [debut])

    # Combiner les cycles simples via DP "somme"
    # dp2[t] = meilleur gain total pour un total exact de t échanges
    dp2 = [0.0] * (p + 1)
    parent2 = [None] * (p + 1)
    dp2[0] = 1.0  # gain neutre

    # On peut utiliser plusieurs fois le même cycle simple
    for t in range(1, p + 1):
        for k, (gain_cycle, _) in meilleur_cycle_simple.items():
            if k <= t and dp2[t - k] > 0.0:
                nouveau_gain = dp2[t - k] * gain_cycle
                if nouveau_gain > dp2[t]:
                    dp2[t] = nouveau_gain
                    parent2[t] = k

    meilleur_t = max(range(p + 1), key=lambda t: dp2[t])
    meilleur_gain = dp2[meilleur_t]

    # Reconstruction de la combinaison de cycles simples fusionnés (l'ordre n'importe pas)
    combo = []
    t = meilleur_t
    while t > 0 and parent2[t] is not None:
        k = parent2[t]
        combo.append(meilleur_cycle_simple[k][1])   
        t -= k
    combo.reverse()  # remettre dans l'ordre naturel

    # Fusion en respectant strictement le budget meilleur_t (nb d'échanges)
    fusion = []
    budget = meilleur_t  # nombre d'arêtes à placer

    for cyc in combo:
        if budget == 0:
            break
        if not fusion:
            # premier cycle : on peut en prendre jusqu'à 'budget' arêtes
            retire = min(budget, len(cyc) - 1)
            fusion = cyc[:retire + 1]
            budget -= retire
        else:
            # cycles suivants : on n'ajoute que des arêtes, donc des noeuds depuis index 1
            retire = min(budget, len(cyc) - 1)
            # si on doit tronquer le cycle, on prend seulement la tranche nécessaire
            fusion += cyc[1:1 + retire]
            budget -= retire

    return meilleur_gain, fusion


# Code 4: le meilleur code possible
def algo_final(G, debut, p):
    """
    G : dictionnaire d'adjacence des taux d'échanges
    debut : monnaie de départ ('E')
    p : nombre maximum d'échanges autorisés

    Returns : (meilleur gain, liste d'échanges à faire)

    Description :
        Étape 1 — Exécute un Bellman-Ford amélioré jusqu'à |X| itérations
        pour obtenir le meilleur cycle simple de chaque taille possible (2 à |X|).

        Étape 2 — Utilise une DP "somme avec remise"
        pour combiner ces cycles simples et atteindre un total <= p échanges.

    Complexité :
        Temps : min{O(|X||U| + p|X|), O(p|U|)}, avec |U| = nombre d’arêtes et |X| = nombre de sommets
        Mémoire : min{O(|X|^2 + p), O(p|X|)}
    """
    X = len(G)
    # Résoudre |X||U| + p|X| < p|U| (complexité algo 3 < complexité algo 4) avec |U| = |X|*(|X|-1) <=> p > (|X|^2 - |X|) / (|X| - 2)
    seuil = (X*X) / (X-1)  
    if p > seuil:  # Si p est plus grand que le seuil, alors l'algo 3 est plus efficace (en pratique le seuil tend vers |X|+1)
        return meilleur_cycle_optimal(G, debut, p, X=X)
    else:
        return meilleur_cycle_ameliore(G, debut, p)


# Dictionnaire d'adjacence (on associe à chaque noeud un dictionnaire de tous les noeuds adjacents avec les taux associés)
G = {
    'E': {'D': 1.19, 'J': 1.33, 'F': 1.62},
    'D': {'E': 0.84, 'J': 1.12, 'F': 1.37},
    'J': {'E': 0.75, 'D': 0.89, 'F': 1.22},
    'F': {'E': 0.62, 'D': 0.73, 'J': 0.82}
}

meilleur_gain, meilleur_chemin = meilleur_cycle(G, 'E', p=10)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

meilleur_gain, meilleur_chemin = meilleur_cycle_ameliore(G, 'E', p=10)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

meilleur_gain, meilleur_chemin = meilleur_cycle_optimal(G, 'E', p=10)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

meilleur_gain, meilleur_chemin = algo_final(G, 'E', p=10)
print("Meilleur cycle trouvé :", meilleur_chemin)
print("Gain total :", meilleur_gain)

# Pour tester la rapidité des deux et le fait qu'ils renvoient le même chemin


def compter_cycles(chemin):
    """
    Le seul moyen de vérifier qu'un chemin est le même est de vérifier qu'il contient les mêmes cycles
    Les algorithmes peuvent reconstruire les chemins dans un ordre différent mais l'ordre n'importe pas
    """
    motif1 = ['E', 'D', 'F', 'E']
    motif2 = ['E', 'F', 'E']
    n = len(chemin)
    cpt_edfe = 0
    cpt_efe = 0

    # balayage glissant dans le chemin
    for i in range(n - len(motif1) + 1):
        if chemin[i:i + len(motif1)] == motif1:
            cpt_edfe += 1
    for i in range(n - len(motif2) + 1):
        if chemin[i:i + len(motif2)] == motif2:
            cpt_efe += 1

    return cpt_edfe, cpt_efe


"""
algo1, algo2 = 0, 0

for p in range(15):
    debut = time.time()
    gain1, c1 = meilleur_cycle(G, 'E', p=p)
    algo1 += time.time() - debut
    # print(p, ": algo1 :", time.time() - debut)
    debut = time.time()
    gain2, c2 = meilleur_cycle_ameliore(G, 'E', p=p)
    algo2 += time.time() - debut
    # print(p, ": algo2 :", time.time() - debut)
    if compter_cycles(c1) != compter_cycles(c2):
        print("PAS D'ÉGALITÉ ENTRE LES DEUX RÉSULTATS POUR p =", p)
print(algo1, algo2)

algo2, algo3 = 0, 0

for p in range(1000):
    debut = time.time()
    gain1, c1, = meilleur_cycle_ameliore(G, 'E', p=p)
    algo2 += time.time() - debut
    #print(p, ": algo2 :", time.time() - debut)
    debut = time.time()
    gain2, c2, = meilleur_cycle_optimal(G, 'E', p=p)
    algo3 += time.time() - debut
    #print(p, ": algo2 :", time.time() - debut)
    if compter_cycles(c1) != compter_cycles(c2):
        print("PAS D'ÉGALITÉ ENTRE LES DEUX RÉSULTATS POUR p =", p)
print(algo2, algo3)
"""
