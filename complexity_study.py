import random
import time
import matplotlib.pyplot as plt

# -----------------------------
# Helper: Breadth-First Search for Ford–Fulkerson
# -----------------------------
def Breadth_Search(n, residual, source, sink):
    parent = [-1] * n
    visited = [False] * n
    queue = [source]
    visited[source] = True
    while queue:
        u = queue.pop(0)
        for v in range(n):
            if not visited[v] and residual[u][v] > 0:
                visited[v] = True
                parent[v] = u
                queue.append(v)
                if v == sink:
                    return parent
    return None if not visited[sink] else parent

# -----------------------------
# Ford–Fulkerson (debug printing removed)
# -----------------------------
def Ford_Fulkerson(n, capacities, source=0, sink=None):
    if sink is None:
        sink = n - 1  # Last vertex as sink

    flow = [[0] * n for _ in range(n)]
    residual = [row[:] for row in capacities]
    max_flow = 0

    while True:
        parent = Breadth_Search(n, residual, source, sink)
        if not parent:
            break

        # Reconstruct path from source to sink
        path = []
        v = sink
        while v != source:
            path.append(v)
            v = parent[v]
        path.append(source)
        path.reverse()

        # Determine minimum capacity in path
        min_capacity = min(residual[parent[v]][v] for v in path[1:])

        # Update residual graph and flow
        for v in path[1:]:
            u = parent[v]
            residual[u][v] -= min_capacity
            residual[v][u] += min_capacity
            flow[u][v] += min_capacity

        max_flow += min_capacity

    return max_flow

# -----------------------------
# Push–Relabel (debug printing removed)
# -----------------------------
def Push_Relabel(n, capacity, source=0, sink=None):
    if sink is None:
        sink = n - 1

    flow = [[0] * n for _ in range(n)]
    height = [0] * n
    excess = [0] * n

    height[source] = n
    for v in range(n):
        flow[source][v] = capacity[source][v]
        flow[v][source] = -flow[source][v]
        excess[v] = capacity[source][v]
        excess[source] -= capacity[source][v]

    def push(u, v):
        delta = min(excess[u], capacity[u][v] - flow[u][v])
        flow[u][v] += delta
        flow[v][u] -= delta
        excess[u] -= delta
        excess[v] += delta

    def relabel(u):
        min_height = float('inf')
        for v in range(n):
            if capacity[u][v] - flow[u][v] > 0:
                min_height = min(min_height, height[v])
        if min_height < float('inf'):
            height[u] = min_height + 1

    def discharge(u):
        while excess[u] > 0:
            for v in range(n):
                if capacity[u][v] - flow[u][v] > 0 and height[u] == height[v] + 1:
                    push(u, v)
                    if excess[u] == 0:
                        break
            else:
                relabel(u)

    active = [i for i in range(n) if i != source and i != sink and excess[i] > 0]
    p = 0
    while p < len(active):
        u = active[p]
        old_height = height[u]
        discharge(u)
        if height[u] > old_height:
            active.insert(0, active.pop(p))
            p = 0
        else:
            p += 1

    max_flow = sum(flow[source][i] for i in range(n))
    return max_flow

# -----------------------------
# Min–Cost Flow (debug printing removed)
# -----------------------------
def Min_Cost_Flow(n, capacities, costs, source=0, sink=None):
    if sink is None:
        sink = n - 1

    flow = [[0] * n for _ in range(n)]
    residual_cap = [row[:] for row in capacities]
    residual_cost = [
        [costs[i][j] if capacities[i][j] > 0 else 0 for j in range(n)]
        for i in range(n)
    ]
    total_flow = 0
    total_cost = 0

    while True:
        # Bellman-Ford shortest path search in residual graph
        dist = [float('inf')] * n
        parent = [-1] * n
        dist[source] = 0

        for _ in range(n - 1):
            for u in range(n):
                for v in range(n):
                    if residual_cap[u][v] > 0 and dist[u] + residual_cost[u][v] < dist[v]:
                        dist[v] = dist[u] + residual_cost[u][v]
                        parent[v] = u

        if parent[sink] == -1:
            break  # No augmenting path

        # Reconstruct the path from source to sink
        path = []
        v = sink
        while v != source:
            path.append(v)
            v = parent[v]
        path.append(source)
        path.reverse()

        # Determine the minimum residual capacity along the path
        min_cap = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            min_cap = min(min_cap, residual_cap[u][v])

        # Update residual capacities, flows, and reverse edge costs
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual_cap[u][v] -= min_cap
            residual_cap[v][u] += min_cap
            flow[u][v] += min_cap
            residual_cost[v][u] = -costs[u][v]

        total_flow += min_cap
        total_cost += min_cap * dist[sink]

    return total_flow, total_cost

# -----------------------------
# Random Flow Problem Generator
# -----------------------------
def generate_flow_problem(n):
    capacities = [[0] * n for _ in range(n)]
    costs = [[0] * n for _ in range(n)]

    candidates = [(i, j) for i in range(n) for j in range(n) if i != j]
    num_edges = int((n * n) / 2)
    selected_edges = random.sample(candidates, num_edges)

    for (i, j) in selected_edges:
        capacities[i][j] = random.randint(1, 100)
        costs[i][j] = random.randint(1, 100)

    return capacities, costs

# -----------------------------
# Complexity Study: Test Functions for Each Algorithm
# -----------------------------
def test_ford_fulkerson():
    global results_ff  # Store results globally
    n_values = [10, 20, 40, 100]
    num_iterations = 100
    results_ff = []  # Store results globally
    avg_times_ff = []  # Store average times for line plot

    for n in n_values:
        times = []
        for _ in range(num_iterations):
            capacities, _ = generate_flow_problem(n)
            source, sink = 0, n - 1
            start = time.process_time()
            _ = Ford_Fulkerson(n, capacities, source, sink)
            elapsed = time.process_time() - start
            times.append(elapsed)
        results_ff.append((n, times))
        avg_times_ff.append(sum(times) / len(times))  # Compute the average

    # Plot the results
    plt.figure(figsize=(8, 6))

    # Scatter plot for individual execution times
    for n, t_list in results_ff:
        plt.scatter([n] * len(t_list), t_list, marker='x', c='red', label="Ford-Fulkerson (individual runs)" if n == n_values[0] else "")

    # Line plot connecting the averages
    plt.plot(n_values, avg_times_ff, linestyle='-', marker='o', color='black', label="Ford-Fulkerson (average)")

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Problem size n")
    plt.ylabel("Execution time (s)")
    plt.title("Etude de Complexité: Ford-Fulkerson")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.show()




def test_push_relabel():
    global results_pr  # Store results globally
    n_values = [10, 20, 40, 100,400,1000]
    num_iterations = 100
    results_pr = []  # Store results globally
    avg_times_pr = []  # Store average times for line plot

    for n in n_values:
        times = []
        for _ in range(num_iterations):
            capacities, _ = generate_flow_problem(n)
            source, sink = 0, n - 1
            start = time.process_time()
            _ = Push_Relabel(n, capacities, source, sink)
            elapsed = time.process_time() - start
            times.append(elapsed)
        results_pr.append((n, times))
        avg_times_pr.append(sum(times) / len(times))  # Compute the average

    # Plot the results
    plt.figure(figsize=(8, 6))

    # Scatter plot for individual execution times
    for n, t_list in results_pr:
        plt.scatter([n] * len(t_list), t_list, marker='o', c='blue', label="Push-Relabel (individual runs)" if n == n_values[0] else "")

    # Line plot connecting the averages
    plt.plot(n_values, avg_times_pr, linestyle='-', marker='o', color='black', label="Push-Relabel (average)")

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Problem size n")
    plt.ylabel("Execution time (s)")
    plt.title("Complexity Study: Push-Relabel")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.show()



def test_min_cost_flow():
    n_values = [10]
    num_iterations = 10
    results = []

    for n in n_values:
        times = []
        for _ in range(num_iterations):
            capacities, costs = generate_flow_problem(n)
            source, sink = 0, n - 1
            start = time.process_time()
            _ = Min_Cost_Flow(n, capacities, costs, source, sink)
            elapsed = time.process_time() - start
            times.append(elapsed)
        results.append((n, times))

    plt.figure(figsize=(8, 6))
    for n, t_list in results:
        plt.scatter([n] * len(t_list), t_list, marker='^', c='green',
                    label="Min–Cost Flow" if n == n_values[0] else "")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Problem size n")
    plt.ylabel("Execution time (s)")
    plt.title("Complexity Study: Min–Cost Flow")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.show()


# -----------------------------
# Test Function: Plot O(Ford-Fulkerson) / O(Push-Relabel)
# -----------------------------
# -----------------------------
# Test Function: Plot O(Ford-Fulkerson) / O(Push-Relabel)
# -----------------------------
def test_ratio_ff_pr():
    global results_ff, results_pr  # Ensure access to global variables

    if not results_ff or not results_pr:
        print("Error: Ford-Fulkerson or Push-Relabel test data is missing. Run their tests first.")
        return

    # Ensure matching values of n
    common_n_values = set(n for n, _ in results_ff) & set(n for n, _ in results_pr)
    if not common_n_values:
        print("Error: No common problem sizes found between Ford-Fulkerson and Push-Relabel tests.")
        return

    ratios = []
    n_values_ratio = []

    for n in sorted(common_n_values):
        ff_times = [t for n_ff, t_list in results_ff if n_ff == n for t in t_list]
        pr_times = [t for n_pr, t_list in results_pr if n_pr == n for t in t_list]

        if not ff_times or not pr_times:
            continue  # Skip if no times were recorded for this problem size

        avg_ff = sum(ff_times) / len(ff_times)
        avg_pr = sum(pr_times) / len(pr_times)

        if avg_pr > 0:  # Avoid division by zero
            ratios.append(avg_ff / avg_pr)
            n_values_ratio.append(n)

    if not ratios:
        print("Error: No valid ratio values computed.")
        return

    # Plot the ratio O(ff) / O(pr)
    plt.figure(figsize=(8, 6))
    plt.plot(n_values_ratio, ratios, marker='s', linestyle='-', color='purple', label="O(ff) / O(pr)")

    plt.xscale("log")
    plt.xlabel("Problem size n")
    plt.ylabel("Ratio O(ff) / O(pr)")
    plt.title("Complexity Ratio: Ford-Fulkerson vs Push-Relabel")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.show()


if __name__ == "__main__":
    test_ford_fulkerson()  # Run Ford-Fulkerson test first
    test_push_relabel()    # Run Push-Relabel test next
    test_ratio_ff_pr()     # Run ratio test AFTER the previous two tests

