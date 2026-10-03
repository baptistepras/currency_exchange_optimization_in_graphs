import math
import time

"""
Javier Pena Castano, Martin Leiva, Baptiste Pras

We wrote 4 algorithms:
- Code 1: naive and inefficient
- Code 2: based on the Bellman-Ford principle, more efficient
- Code 3: improvement of algorithm 2 when p > X
- Code 4: smart adaptive use of algorithms 2 and 3, best code

Small differences in gain can appear in the tests because the algorithms
traverse the cycles in a different direction, so the rounding errors of
floats are not the same, but the final result is the same. (The same
cycles are taken the same number of times in the paths of each algorithm.)
"""


# Code 1: brute force
def best_cycle(G, start, p):
    """
    G : adjacency dictionary of the exchange rates
    start : starting currency ('E')
    p : maximum number of allowed exchanges

    Returns : (best gain, list of exchanges to make)

    Description :
        Recursively explores all possible paths up to p exchanges and keeps
        the cycle giving the highest total gain. This approach tests all
        possible combinations.

    Complexity :
        Time : O(|X|^p), with |X| = number of vertices
        Memory : O(p), maximum depth of the recursion
    """
    def dfs(node, gain, path, depth):
        best_gain = 0.0
        best_path = []

        # If we are back at the start, it is a valid cycle that we record
        if node == start and depth > 0:
            best_gain = gain
            best_path = path

        # If we reached the maximum depth
        if depth == p:
            return best_gain, best_path

        # We keep exploring
        for next_node, rate in G[node].items():
            next_gain, next_path = dfs(next_node, gain * rate, path + [next_node], depth + 1)
            if next_gain > best_gain:
                best_gain, best_path = next_gain, next_path

        return best_gain, best_path

    return dfs(start, 1.0, [start], 0)


# Code 2: optimized code
def best_cycle_improved(G, start, p):
    """
    G : adjacency dictionary of the exchange rates
    start : starting currency ('E')
    p : maximum number of allowed exchanges

    Returns : (best gain, list of exchanges to make)

    Description :
        Uses an approach inspired by Bellman-Ford to compute the best cycle
        in at most p exchanges. At each iteration k, we store the maximum gain
        to reach each vertex in k steps, then we look for the most profitable
        cycle and rebuild the best path afterwards.

    Complexity :
        Time : O(p|U|), with |U| = number of edges
        Memory : O(p|X|), with |X| = number of vertices
    """
    # dp[k][u] = best gain to reach u in exactly k exchanges
    # parent[k][u] = predecessor of u for this best gain
    dp = [{u: 0.0 for u in G} for _ in range(p + 1)]
    parent = [{u: None for u in G} for _ in range(p + 1)]

    dp[0][start] = 1.0

    for k in range(1, p + 1):
        updated = False

        for u in G:
            if dp[k - 1][u] <= 0.0:
                continue  # If the gain is zero we do not use it

            current_gain = dp[k - 1][u]

            # We try every possible exchange from u
            for v, rate in G[u].items():
                new_gain = current_gain * rate

                # If this new gain is better, we keep it
                if new_gain > dp[k][v]:
                    dp[k][v] = new_gain
                    parent[k][v] = u
                    updated = True

        # No improvement of the best gain
        if not updated:
            break

    # Search for the best cycle coming back to the starting currency
    best_gain = 0.0
    best_k = None
    for k in range(1, p + 1):
        if dp[k][start] > best_gain:
            best_gain = dp[k][start]
            best_k = k

    # No cycle found
    if best_k is None:
        return 0.0, []

    # Rebuild the optimal cycle from the parents
    reversed_cycle = []
    currency = start

    for step in range(best_k, 0, -1):
        previous = parent[step][currency]
        reversed_cycle.append(previous)
        currency = previous

    # Reverse to get the cycle in the right order
    reversed_cycle.reverse()
    best_cycle = reversed_cycle + [start]

    return best_gain, best_cycle


# Code 3: even better optimized code
def best_cycle_optimal(G, start, p, X=-1):
    """
    G : adjacency dictionary of the exchange rates
    start : starting currency ('E')
    p : maximum number of allowed exchanges

    Returns : (best gain, list of exchanges to make)

    Description :
        Step 1: runs an improved Bellman-Ford up to |X| iterations
        to get the best simple cycle of each possible size (2 to |X|).

        Step 2: uses a "sum with repetition" DP
        to combine these simple cycles and reach a total <= p exchanges.

    Complexity :
        Time : O(|X||U| + p|X|), with |U| = number of edges and |X| = number of vertices
        Memory : O(|X|^2 + p)
    """
    if X==-1:
        X = len(G)

    # Algorithm 2 up to |X| iterations
    dp = [{u: 0.0 for u in G} for _ in range(X + 1)]
    parent = [{u: None for u in G} for _ in range(X + 1)]

    dp[0][start] = 1.0
    best_simple_cycle = {}

    for k in range(1, X + 1):
        updated = False
        for u in G:
            if dp[k - 1][u] <= 0.0:
                continue
            current_gain = dp[k - 1][u]
            for v, rate in G[u].items():
                new_gain = current_gain * rate
                if new_gain > dp[k][v]:
                    dp[k][v] = new_gain
                    parent[k][v] = u
                    updated = True
        if not updated:
            break

        # We check whether there is a cycle of size k
        if dp[k][start] > 0.0:
            # Rebuild the cycle
            reversed_cycle = []
            currency = start
            for step in range(k, 0, -1):
                previous = parent[step][currency]
                reversed_cycle.append(previous)
                currency = previous
            reversed_cycle.reverse()
            best_simple_cycle[k] = (dp[k][start], reversed_cycle + [start])

    # Combine the simple cycles with a "sum" DP
    # dp2[t] = best total gain for an exact total of t exchanges
    dp2 = [0.0] * (p + 1)
    parent2 = [None] * (p + 1)
    dp2[0] = 1.0  # neutral gain

    # The same simple cycle can be used several times
    for t in range(1, p + 1):
        for k, (cycle_gain, _) in best_simple_cycle.items():
            if k <= t and dp2[t - k] > 0.0:
                new_gain = dp2[t - k] * cycle_gain
                if new_gain > dp2[t]:
                    dp2[t] = new_gain
                    parent2[t] = k

    best_t = max(range(p + 1), key=lambda t: dp2[t])
    best_gain = dp2[best_t]

    # Rebuild the combination of merged simple cycles (the order does not matter)
    combo = []
    t = best_t
    while t > 0 and parent2[t] is not None:
        k = parent2[t]
        combo.append(best_simple_cycle[k][1])
        t -= k
    combo.reverse()  # back to the natural order

    # Merge while strictly respecting the budget best_t (number of exchanges)
    merged = []
    budget = best_t  # number of edges to place

    for cyc in combo:
        if budget == 0:
            break
        if not merged:
            # first cycle: we can take up to 'budget' edges
            taken = min(budget, len(cyc) - 1)
            merged = cyc[:taken + 1]
            budget -= taken
        else:
            # next cycles: we only add edges, so nodes from index 1
            taken = min(budget, len(cyc) - 1)
            # if the cycle must be truncated, we only take the needed slice
            merged += cyc[1:1 + taken]
            budget -= taken

    return best_gain, merged


# Code 4: the best possible code
def final_algorithm(G, start, p):
    """
    G : adjacency dictionary of the exchange rates
    start : starting currency ('E')
    p : maximum number of allowed exchanges

    Returns : (best gain, list of exchanges to make)

    Description :
        Step 1: runs an improved Bellman-Ford up to |X| iterations
        to get the best simple cycle of each possible size (2 to |X|).

        Step 2: uses a "sum with repetition" DP
        to combine these simple cycles and reach a total <= p exchanges.

    Complexity :
        Time : min{O(|X||U| + p|X|), O(p|U|)}, with |U| = number of edges and |X| = number of vertices
        Memory : min{O(|X|^2 + p), O(p|X|)}
    """
    X = len(G)
    # Solve |X||U| + p|X| < p|U| (complexity of algorithm 3 < complexity of algorithm 4) with |U| = |X|*(|X|-1) <=> p > (|X|^2 - |X|) / (|X| - 2)
    threshold = (X*X) / (X-1)
    if p > threshold:  # If p is larger than the threshold, algorithm 3 is more efficient (in practice the threshold tends to |X|+1)
        return best_cycle_optimal(G, start, p, X=X)
    else:
        return best_cycle_improved(G, start, p)


# Adjacency dictionary (each node maps to a dictionary of all adjacent nodes with the associated rates)
G = {
    'E': {'D': 1.19, 'J': 1.33, 'F': 1.62},
    'D': {'E': 0.84, 'J': 1.12, 'F': 1.37},
    'J': {'E': 0.75, 'D': 0.89, 'F': 1.22},
    'F': {'E': 0.62, 'D': 0.73, 'J': 0.82}
}

best_gain, best_path = best_cycle(G, 'E', p=10)
print("Best cycle found:", best_path)
print("Total gain:", best_gain)

best_gain, best_path = best_cycle_improved(G, 'E', p=10)
print("Best cycle found:", best_path)
print("Total gain:", best_gain)

best_gain, best_path = best_cycle_optimal(G, 'E', p=10)
print("Best cycle found:", best_path)
print("Total gain:", best_gain)

best_gain, best_path = final_algorithm(G, 'E', p=10)
print("Best cycle found:", best_path)
print("Total gain:", best_gain)

# To test the speed of both and check that they return the same path


def count_cycles(path):
    """
    The only way to check that two paths are the same is to check that they contain the same cycles
    The algorithms can rebuild the paths in a different order but the order does not matter
    """
    pattern1 = ['E', 'D', 'F', 'E']
    pattern2 = ['E', 'F', 'E']
    n = len(path)
    count_edfe = 0
    count_efe = 0

    # sliding scan over the path
    for i in range(n - len(pattern1) + 1):
        if path[i:i + len(pattern1)] == pattern1:
            count_edfe += 1
    for i in range(n - len(pattern2) + 1):
        if path[i:i + len(pattern2)] == pattern2:
            count_efe += 1

    return count_edfe, count_efe


"""
algo1, algo2 = 0, 0

for p in range(15):
    start = time.time()
    gain1, c1 = best_cycle(G, 'E', p=p)
    algo1 += time.time() - start
    # print(p, ": algo1 :", time.time() - start)
    start = time.time()
    gain2, c2 = best_cycle_improved(G, 'E', p=p)
    algo2 += time.time() - start
    # print(p, ": algo2 :", time.time() - start)
    if count_cycles(c1) != count_cycles(c2):
        print("NO EQUALITY BETWEEN THE TWO RESULTS FOR p =", p)
print(algo1, algo2)

algo2, algo3 = 0, 0

for p in range(1000):
    start = time.time()
    gain1, c1, = best_cycle_improved(G, 'E', p=p)
    algo2 += time.time() - start
    #print(p, ": algo2 :", time.time() - start)
    start = time.time()
    gain2, c2, = best_cycle_optimal(G, 'E', p=p)
    algo3 += time.time() - start
    #print(p, ": algo2 :", time.time() - start)
    if count_cycles(c1) != count_cycles(c2):
        print("NO EQUALITY BETWEEN THE TWO RESULTS FOR p =", p)
print(algo2, algo3)
"""
