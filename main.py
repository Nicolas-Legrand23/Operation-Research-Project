#!/usr/bin/env python3
import sys


# -----------------------------------------------------------------------------
# Data Reading
# -----------------------------------------------------------------------------
def read_flow_data(filename):
    """
    Reads a text file and parses the graph data.
    The file is expected to contain:
      - First nonempty line: n, the number of vertices.
      - Next n lines: capacity matrix.
      - Optionally, following n lines: cost matrix.
    Returns: (n, capacity_matrix, cost_matrix)
             where cost_matrix is None if not provided.
    """
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return None, None, None

    # Remove blank lines and strip whitespace.
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        print(f"Empty file or no valid data in {filename}.")
        return None, None, None

    n = int(lines[0])
    if len(lines) < 1 + n:
        print(f"Insufficient lines for capacity matrix in {filename}.")
        return None, None, None

    # Read capacity matrix.
    capacity = []
    for i in range(1, 1 + n):
        row = list(map(float, lines[i].split()))
        if len(row) != n:
            print(f"Error on capacity matrix row {i} in {filename}: "
                  f"expected {n} entries, got {len(row)}.")
            return None, None, None
        capacity.append(row)

    # Check for an optional cost matrix.
    cost = None
    if len(lines) >= 1 + 2 * n:
        cost = []
        for i in range(1 + n, 1 + 2 * n):
            row = list(map(float, lines[i].split()))
            if len(row) != n:
                print(f"Error on cost matrix row {i} in {filename}: "
                      f"expected {n} entries, got {len(row)}.")
                return None, None, None
            cost.append(row)

    return n, capacity, cost


# -----------------------------------------------------------------------------
# Display Functions (with meticulous formatting)
# -----------------------------------------------------------------------------
import string

import string

def print_table(matrix, title="Table", col_width=12):
    """
    Prints a matrix with column headers labeled: s, a, b, c, ..., t.
    Ensures columns align using fixed-width formatting.
    """
    n = len(matrix)
    print("\n" + title)

    # Generate labels: ['s', 'a', 'b', ..., 't']
    if n < 2:
        print("Matrix size too small to label properly.")
        return

    labels = ['s'] + list(string.ascii_lowercase[:n-2]) + ['t']

    # Print header row with labels
    header = f"{'':>{col_width}}"  # Empty space for row index
    for label in labels:
        header += f"{label:>{col_width}}"
    print(header)

    # Print each row with corresponding label
    for i, row in enumerate(matrix):
        row_label = labels[i]
        row_str = f"{row_label:>{col_width}}"  # Row index as letter
        for item in row:
            row_str += f"{item:>{col_width}.0f}"  # Format numbers for alignment
        print(row_str)
    print("")


import string


def print_flow_capacity_matrix(flow, capacity, title="Final Flow/Capacity Matrix", col_width=12):
    """
    Displays the final flow/capacity matrix.
    Each cell is printed in the format "flow/capacity".
    The row and column headers are labeled: s, a, b, ..., t,
    where "s" is the source and "t" is the sink.
    Blank cells are printed for edges with zero capacity and flow.
    """
    n = len(capacity)
    if n < 2:
        print("Matrix size is too small!")
        return

    # Create labels: first is 's', then letters 'a', 'b', ... for intermediate vertices, and 't' as last.
    labels = ['s'] + list(string.ascii_lowercase[:n - 2]) + ['t']

    print("\n" + title)
    # Print header row.
    header = f"{'':>{col_width}}"
    for label in labels:
        header += f"{label:>{col_width}}"
    print(header)

    # Print a separator line.
    print(" " + "-" * (col_width * (n + 1)))

    # Print each row.
    for i in range(n):
        row_label = labels[i]
        row_str = f"{row_label:>{col_width}}"
        for j in range(n):
            # Only print a cell if either capacity or flow on that edge is nonzero.
            if capacity[i][j] > 0 or flow[i][j] > 0:
                # Format the cell as "flow/capacity" (both as integers for clarity).
                cell = f"{int(flow[i][j])}/{int(capacity[i][j])}"
                row_str += f"{cell:>{col_width}}"
            else:
                row_str += " " * col_width
        print(row_str)


def print_bellman_table(bellman_table):
    """
    Prints the detailed Bellman-Ford table.
    Each row displays the iteration number, and then the 'Distance' and 'Parent'
    arrays.
    """
    if not bellman_table:
        print("Empty Bellman Table.\n")
        return
    n = len(bellman_table[0]["Distance"])
    col_width = 12
    # Header for vertices.
    header = f"{'':>{col_width}}"
    for j in range(n):
        header += f"v{j:>{col_width - 1}}"
    print("\nBellman-Ford Distance Table:")
    print(header)
    for row in bellman_table:
        iter_label = f"Iter {row['Iteration']} D"
        line = f"{iter_label:>{col_width}}"
        for d in row["Distance"]:
            cell = "inf" if d == float('inf') else f"{d:.0f}"
            line += f"{cell:>{col_width}}"
        print(line)

    print("\nBellman-Ford Parent Table:")
    header = f"{'':>{col_width}}"
    for j in range(n):
        header += f"v{j:>{col_width - 1}}"
    print(header)
    for row in bellman_table:
        iter_label = f"Iter {row['Iteration']} P"
        line = f"{iter_label:>{col_width}}"
        for p in row["Parent"]:
            line += f"{p:>{col_width}}"
        print(line)
    print("")


# -----------------------------------------------------------------------------
# Max Flow: Ford-Fulkerson (BFS / Edmonds-Karp)
# -----------------------------------------------------------------------------
def bfs(residual, source, sink):
    """
    Performs BFS on the residual graph.
    Returns a tuple: (path, parent, details_string)
      - 'path' is the discovered path as a list of vertices, or None if not found.
      - 'parent' is used for backtracking.
      - 'details_string' logs the BFS execution.
    """
    n = len(residual)
    visited = [False] * n
    parent = [-1] * n
    queue = [source]
    visited[source] = True
    details = f"Queue starts with: {queue}\n"

    while queue:
        u = queue.pop(0)
        details += f"Visiting: {u}\n"
        if u == sink:
            break
        for v in range(n):
            if not visited[v] and residual[u][v] > 0:
                queue.append(v)
                visited[v] = True
                parent[v] = u
                details += f"  Discovered vertex {v} from vertex {u}\n"

    if visited[sink]:
        # Reconstruct the path from sink to source.
        path = []
        v = sink
        while v != -1:
            path.append(v)
            v = parent[v]
        path.reverse()
        details += f"BFS found augmenting path: {path}\n"
        return path, parent, details
    else:
        details += "BFS did not find a path to sink.\n"
        return None, parent, details


def ford_fulkerson(capacity, source, sink):
    """
    Uses the Ford–Fulkerson method (via BFS/Edmonds-Karp) to compute max flow.
    Displays details of each BFS search, the found augmenting path,
    and modifications to the residual graph.
    At the end, it computes a flow matrix and displays it in the form "flow/capacity".
    """
    n = len(capacity)
    residual = [row[:] for row in capacity]  # Deep copy for residual graph.
    max_flow = 0
    iteration = 1

    print("\n--- Ford-Fulkerson (BFS/Edmonds-Karp) ---")
    while True:
        path, parent, bfs_details = bfs(residual, source, sink)
        print(f"Iteration {iteration} - BFS Details:")
        print(bfs_details)

        if not path:
            print("No augmenting path found. Terminating Ford-Fulkerson.\n")
            break

        # Find the bottleneck capacity along the path.
        bottleneck = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u

        path_str = " -> ".join(str(v) for v in path)
        print(f"Found augmenting path: {path_str} with flow = {bottleneck:.0f}")

        # Update the residual graph along the path.
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
            v = u

        max_flow += bottleneck
        print("Updated Residual Graph:")
        print_table(residual, title="Residual Graph", col_width=12)
        iteration += 1

    print(f"Maximum Flow (Ford-Fulkerson): {max_flow:.0f}\n")

    # Compute the flow matrix from the residual graph:
    flow_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if capacity[i][j] > 0:
                flow_matrix[i][j] = capacity[i][j] - residual[i][j]

    # Print the final flow/capacity matrix.
    print_flow_capacity_matrix(flow_matrix, capacity, title="Final Flow/Capacity Matrix (FF)")

    return max_flow, residual


# -----------------------------------------------------------------------------
# Max Flow: Push-Relabel Algorithm
# -----------------------------------------------------------------------------
from collections import deque


from collections import deque

def push_relabel(capacity, source, sink):
    """
    Refined push-relabel maximum flow algorithm.
    It initializes a preflow, then processes vertices using an active node queue.
    At the end, the function computes the net flow (for original edges) as:
        net_flow[u][v] = capacity[u][v] - residual[u][v]
    This net_flow matrix is then printed in the format "flow/capacity"
    so that the displayed result matches the Ford–Fulkerson output.
    """
    n = len(capacity)
    # Create the residual graph (deep copy of capacity).
    residual = [row[:] for row in capacity]
    height = [0] * n
    excess = [0] * n
    flow = [[0] * n for _ in range(n)]  # internal flow bookkeeping (includes reverse flows)
    current = [0] * n  # current neighbor pointer for each vertex

    # Preflow: saturate edges leaving the source.
    height[source] = n
    for v in range(n):
        if capacity[source][v] > 0:
            f = capacity[source][v]
            flow[source][v] = f
            residual[source][v] -= f
            residual[v][source] += f
            excess[v] += f
            excess[source] -= f

    print("\n--- Push-Relabel (refined) ---")
    print("Initial Heights:", height)
    print("Initial Excess:", excess)
    print("Initial Residual Graph:")
    print_table(residual, title="Residual Graph", col_width=12)

    # Initialize the active node queue (all nodes except source and sink with positive excess).
    active = deque([u for u in range(n) if u != source and u != sink and excess[u] > 0])
    iteration = 0  # iteration counter for logging

    def push(u, v):
        nonlocal iteration
        delta = min(excess[u], residual[u][v])
        if delta > 0:
            flow[u][v] += delta
            residual[u][v] -= delta
            residual[v][u] += delta
            excess[u] -= delta
            excess[v] += delta
            print(f"Iteration {iteration}: Pushed {delta:.0f} from {u} to {v}")
            print("Excess:", excess)
            print_table(residual, title="Residual Graph", col_width=12)
        return delta

    def relabel(u):
        nonlocal iteration
        min_height = float('inf')
        for v in range(n):
            if residual[u][v] > 0:
                min_height = min(min_height, height[v])
        old_height = height[u]
        height[u] = min_height + 1
        print(f"Iteration {iteration}: Relabeled vertex {u} from height {old_height} to {height[u]}")
        iteration += 1

    def discharge(u):
        nonlocal iteration
        # Continue processing u until no excess remains (using a small tolerance for floating-point issues).
        while excess[u] > 1e-8:
            if current[u] < n:
                v = current[u]
                if residual[u][v] > 0 and height[u] == height[v] + 1:
                    push(u, v)
                    # If v becomes active (and it's not source or sink), add it to the queue.
                    if v != source and v != sink and excess[v] > 1e-8 and v not in active:
                        active.append(v)
                else:
                    current[u] += 1
            else:
                relabel(u)
                current[u] = 0

    # Process active nodes until none remain.
    while active:
        u = active.popleft()
        discharge(u)
        if excess[u] > 1e-8:
            active.append(u)

    # Instead of printing the raw "flow" matrix, compute the net flow for each original edge.
    net_flow = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            # For each original edge, the net flow equals the original capacity minus the residual.
            if capacity[i][j] > 0:
                net_flow[i][j] = capacity[i][j] - residual[i][j]

    # Display the final flow/capacity matrix using the computed net flow.
    print_flow_capacity_matrix(net_flow, capacity, title="Final Flow/Capacity Matrix (Push-Relabel)")

    # Maximum flow is, for example, the flow accumulated at the sink.
    max_flow = excess[sink]
    print(f"\nMaximum Flow (Push-Relabel, refined): {max_flow:.0f}")
    print(f"Flow accumulated at sink (excess[{sink}]): {excess[sink]:.0f}")

    return max_flow, residual, flow, height, excess



# -----------------------------------------------------------------------------
# Minimum-Cost Flow (Using Bellman-Ford)
# -----------------------------------------------------------------------------
def min_cost_flow(capacity, cost, source, sink, target_flow=None):
    """
    Solves the minimum-cost flow problem.
    At each iteration the Bellman-Ford algorithm is run, a detailed table is displayed,
    and an augmenting path is found. If target_flow is provided, the algorithm will
    push until that flow has been reached (or no further improvements are possible).
    """
    n = len(capacity)
    # Initialize residual capacities and build residual cost matrix.
    residual_capacity = [row[:] for row in capacity]
    residual_cost = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if capacity[u][v] > 0:
                residual_cost[u][v] = cost[u][v]

    max_flow = 0
    min_cost = 0
    iteration = 0

    print("\n--- Minimum-Cost Flow (Using Bellman-Ford) ---")
    while True:
        # Set up Bellman-Ford search.
        distance = [float('inf')] * n
        parent = [-1] * n
        distance[source] = 0

        bellman_table = []
        for i in range(n - 1):
            bellman_table.append({
                "Iteration": i,
                "Distance": distance.copy(),
                "Parent": parent.copy()
            })
            updated = False
            for u in range(n):
                for v in range(n):
                    if residual_capacity[u][v] > 0 and distance[u] + residual_cost[u][v] < distance[v]:
                        distance[v] = distance[u] + residual_cost[u][v]
                        parent[v] = u
                        updated = True
            if not updated:
                break

        print(f"\nBellman-Ford Table for iteration {iteration}:")
        print_bellman_table(bellman_table)

        if distance[sink] == float('inf'):
            print("No more augmenting paths found for minimum-cost flow.\n")
            break

        # Determine bottleneck along the path.
        flow = float('inf')
        path = []
        v = sink
        while v != source:
            u = parent[v]
            if u == -1:
                break
            flow = min(flow, residual_capacity[u][v])
            path.append(v)
            v = u
        path.append(source)
        path.reverse()

        # If a target flow is provided, ensure not to exceed it.
        if target_flow is not None:
            flow = min(flow, target_flow - max_flow)
            if flow <= 0:
                break

        print(f"Found augmenting path (min cost): {' -> '.join(map(str, path))} " +
              f"with flow = {flow:.0f} and path cost = {distance[sink]:.0f}")

        # Update the residual graph.
        v = sink
        while v != source:
            u = parent[v]
            residual_capacity[u][v] -= flow
            residual_capacity[v][u] += flow
            residual_cost[v][u] = -residual_cost[u][v]
            v = u

        max_flow += flow
        min_cost += flow * distance[sink]
        print("Updated Residual Capacity Matrix:")
        print_table(residual_capacity, title="Residual Capacity", col_width=12)
        iteration += 1

        if target_flow is not None and max_flow >= target_flow:
            break

    print(f"Minimum-Cost Flow Results: Flow = {max_flow:.0f}, Total Cost = {min_cost:.0f}\n")
    return max_flow, min_cost, residual_capacity


# -----------------------------------------------------------------------------
# Main Function: Interactive Testing Loop
# -----------------------------------------------------------------------------

def main():
    
    """
    Interactive loop:
      - The user chooses a problem number (1-10).
      - The corresponding file (e.g. proposal1.txt) is read.
      - The capacity (and cost, if available) matrices are displayed.
      - For max-flow (problems 1-5): the user selects which algorithm to use.
      - For min-cost flow (problems 6-10): the user enters the desired flow value.
      - The chosen algorithm is executed and the results (max flow or min cost flow)
        are displayed.
    The session repeats as long as the user wishes.
    """
    while True:
        try:
            problem_input = input("Enter the number of the problem to process (1-10, or 0 to exit): ")
            problem_num = int(problem_input)
        except ValueError:
            print("Invalid input. Please enter an integer.")
            continue

        if problem_num == 0:
            break

        if problem_num < 1 or problem_num > 10:
            print("Please choose a problem number between 1 and 10.")
            continue

        filename = f"proposal/proposal {problem_num}.txt"
        print(f"\nProcessing {filename} ...")
        n, capacity, cost = read_flow_data(filename)
        if n is None:
            continue

        # Display the capacity matrix.
        print_table(capacity, title=f"Capacity Matrix for Proposal {problem_num}", col_width=12)
        if cost is not None:
            print_table(cost, title=f"Cost Matrix for Proposal {problem_num}", col_width=12)
        else:
            print("No cost matrix detected (max-flow problem).")

        source = 0  # v1 as source.
        sink = n - 1  # vn as sink.

        # For problems 1-5, run a max-flow algorithm.
        if problem_num <= 5:
            print("This is a MAX-FLOW problem.")
            print("Choose the algorithm:")
            print("  1. Ford-Fulkerson (BFS/Edmonds-Karp)")
            print("  2. Push-Relabel")
            alg_choice = input("Enter your choice (1 or 2): ")
            if alg_choice == "1":
                max_flow, _ = ford_fulkerson(capacity, source, sink)
                print(f"Maximum Flow computed using Ford-Fulkerson: {max_flow:.0f}")
            elif alg_choice == "2":
                max_flow, _, _, _, _ = push_relabel(capacity, source, sink)
                print(f"Maximum Flow computed using Push-Relabel: {max_flow:.0f}")
            else:
                print("Invalid choice. Skipping this problem.")
        else:
            # For problems 6-10, run the minimum-cost flow algorithm.
            print("This is a MINIMUM-COST FLOW problem.")
            try:
                target_flow = float(input("Enter the desired flow value for the min-cost flow problem: "))
            except ValueError:
                print("Invalid flow value. Skipping this problem.")
                continue
            max_flow, total_cost, _ = min_cost_flow(capacity, cost, source, sink, target_flow=target_flow)
            if max_flow < target_flow:
                print(f"Warning: Only {max_flow:.0f} flow could be sent.")
            print(f"Minimum-Cost Flow result: Flow = {max_flow:.0f}, Total Cost = {total_cost:.0f}")

        # Ask if the user wants to process another problem.
        again = input("Do you want to process another flow problem? (y/n): ")
        if again.strip().lower() != 'y':
            break

    print("End of testing session.")

import os
import sys


def redirect_output(filename):
    """
    Redirects print output to a specified file.
    """
    sys.stdout = open(filename, 'w', encoding='utf-8')


def reset_output():
    """
    Resets print output to the console.
    """
    sys.stdout.close()
    sys.stdout = sys.__stdout__


# -----------------------------------------------------------------------------
# Execution trac efile generator main alternative function
# -----------------------------------------------------------------------------

'''def main():
    """
    Automatically processes all 10 proposals and stores execution traces in files.
    - Proposals 1-5 → Ford-Fulkerson & Push-Relabel traces
    - Proposals 6-10 → Minimum-cost flow trace
    """
    execution_dir = "execution_traces"
    os.makedirs(execution_dir, exist_ok=True)  # Create directory for output files

    for problem_num in range(1, 11):
        filename = f"proposal/proposal {problem_num}.txt"
        print(f"\nProcessing {filename} ...")
        n, capacity, cost = read_flow_data(filename)
        if n is None:
            print(f"Skipping {filename} due to read error.")
            continue

        # Create file paths for execution traces
        ff_trace_file = os.path.join(execution_dir, f"proposal{problem_num}_FF.txt")
        pr_trace_file = os.path.join(execution_dir, f"proposal{problem_num}_PR.txt")
        mcf_trace_file = os.path.join(execution_dir, f"proposal{problem_num}_MCF.txt")

        source, sink = 0, n - 1

        if problem_num <= 5:
            # Redirect output for Ford-Fulkerson
            redirect_output(ff_trace_file)
            print(f"Execution Trace for Proposal {problem_num} (Ford-Fulkerson)\n")
            max_flow_ff, residual_ff = ford_fulkerson(capacity, source, sink)
            reset_output()

            # Redirect output for Push-Relabel
            redirect_output(pr_trace_file)
            print(f"Execution Trace for Proposal {problem_num} (Push-Relabel)\n")
            max_flow_pr, residual_pr, flow_pr, height_pr, excess_pr = push_relabel(capacity, source, sink)
            reset_output()

        else:
            # Redirect output for Minimum-Cost Flow
            redirect_output(mcf_trace_file)
            print(f"Execution Trace for Proposal {problem_num} (Minimum-Cost Flow)\n")
            target_flow = 1000  # Example default flow value; modify as needed
            max_flow_mcf, total_cost_mcf, residual_mcf = min_cost_flow(capacity, cost, source, sink, target_flow)
            reset_output()

        print(f"Execution trace saved for Proposal {problem_num}.")

    print("All proposals processed successfully. Execution traces saved.")
'''

if __name__ == '__main__':
    main()
