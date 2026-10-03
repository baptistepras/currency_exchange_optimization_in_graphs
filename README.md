# Currency Exchange Optimization in Graphs

Finds the most profitable sequence of at most `p` currency exchanges that starts and ends with the same currency. Currencies are the vertices of a weighted graph, exchange rates are the edge weights, and the problem becomes a search for the best cycle.

`code.py` contains four algorithms:

| Algorithm | Idea | Time complexity |
| --- | --- | --- |
| `best_cycle` | Brute force over all paths | O(\|X\|^p) |
| `best_cycle_improved` | Dynamic programming in the spirit of Bellman-Ford | O(p\|U\|) |
| `best_cycle_optimal` | Best simple cycle of each length, then an unbounded knapsack over these cycles | O(\|X\|\|U\| + p\|X\|) |
| `final_algorithm` | Picks the faster of the two previous ones from the size of the graph and `p` | min of both |

## Usage

```bash
python code.py
```

The script runs the four algorithms on an example graph of four currencies and prints the best cycle and its gain.

## Authors

Javier Peña Castaño, Martin Leiva, and Baptiste Pras.
