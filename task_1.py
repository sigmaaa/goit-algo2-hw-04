import networkx as nx
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------
# Функції алгоритму Форда-Фалкерсона (Edmonds-Karp)
# ------------------------------
def bfs(capacity_matrix, flow_matrix, source, sink, parent):
    visited = [False] * len(capacity_matrix)
    queue = deque([source])
    visited[source] = True

    while queue:
        current_node = queue.popleft()
        for neighbor in range(len(capacity_matrix)):
            if (
                not visited[neighbor]
                and capacity_matrix[current_node][neighbor]
                - flow_matrix[current_node][neighbor]
                > 0
            ):
                parent[neighbor] = current_node
                visited[neighbor] = True
                if neighbor == sink:
                    return True
                queue.append(neighbor)
    return False


def edmonds_karp(capacity_matrix, source, sink):
    num_nodes = len(capacity_matrix)
    flow_matrix = [[0] * num_nodes for _ in range(num_nodes)]
    parent = [-1] * num_nodes
    max_flow = 0

    while bfs(capacity_matrix, flow_matrix, source, sink, parent):
        path_flow = float("Inf")
        current_node = sink
        while current_node != source:
            prev_node = parent[current_node]
            path_flow = min(
                path_flow,
                capacity_matrix[prev_node][current_node]
                - flow_matrix[prev_node][current_node],
            )
            current_node = prev_node

        current_node = sink
        while current_node != source:
            prev_node = parent[current_node]
            flow_matrix[prev_node][current_node] += path_flow
            flow_matrix[current_node][prev_node] -= path_flow
            current_node = prev_node

        max_flow += path_flow

    return max_flow, flow_matrix


# ------------------------------
# Функція для побудови таблиці "Термінал → Магазин"
# ------------------------------
def build_flow_table(flow_matrix, terminals, warehouses, stores):
    rows = []
    for t in terminals:
        for w in warehouses:
            flow_tw = flow_matrix[t][w]
            if flow_tw > 0:
                for m in stores:
                    flow_wm = flow_matrix[w][m]
                    if flow_wm > 0:
                        actual_flow = min(flow_tw, flow_wm)
                        rows.append((f"Термінал {t+1}", f"Магазин {m-5}", actual_flow))
    df = pd.DataFrame(
        rows, columns=["Термінал", "Магазин", "Фактичний Потік (одиниць)"]
    )
    return df


# ------------------------------
# Функція для побудови та візуалізації графа
# ------------------------------
def build_and_draw_graph(
    capacity_matrix,
    flow_matrix,
    terminals,
    warehouses,
    stores,
    super_source,
    super_sink,
    max_flow,
):
    G = nx.DiGraph()
    node_labels = {}

    # Додаємо вузли
    for t in terminals:
        G.add_node(t)
        node_labels[t] = f"T{t+1}"
    for w in warehouses:
        G.add_node(w)
        node_labels[w] = f"W{w-1}"
    for s in stores:
        G.add_node(s)
        node_labels[s] = f"S{s-5}"
    G.add_node(super_source)
    node_labels[super_source] = "SuperSource"
    G.add_node(super_sink)
    node_labels[super_sink] = "SuperSink"

    # Додаємо ребра
    n = len(capacity_matrix)
    for u in range(n):
        for v in range(n):
            if capacity_matrix[u][v] > 0:
                G.add_edge(u, v, capacity=capacity_matrix[u][v], flow=flow_matrix[u][v])

    # Позиції вузлів
    pos = {}
    for i, t in enumerate(terminals):
        pos[t] = (0, i)
    for i, w in enumerate(warehouses):
        pos[w] = (1, i)
    for i, s in enumerate(stores):
        pos[s] = (2, i)
    pos[super_source] = (-1, 0.5)
    pos[super_sink] = (3, 0.5)

    # Візуалізація
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=700)
    edge_colors = []
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        cap, flow = data["capacity"], data["flow"]
        edge_labels[(u, v)] = f"{flow}/{cap}"
        edge_colors.append("red" if cap <= 15 else "black")  # вузькі місця червоним

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="green")

    plt.title(f"Логістична мережа — Максимальний потік: {max_flow}")
    plt.axis("off")
    plt.show()


# ------------------------------
# Головна функція
# ------------------------------
def main():
    # --- Побудова мережі ---
    n = 22
    capacity_matrix = [[0] * n for _ in range(n)]
    edges = [
        (0, 2, 25),
        (0, 3, 20),
        (0, 4, 15),
        (1, 4, 15),
        (1, 5, 30),
        (1, 3, 10),
        (2, 6, 15),
        (2, 7, 10),
        (2, 8, 20),
        (3, 9, 15),
        (3, 10, 10),
        (3, 11, 25),
        (4, 12, 20),
        (4, 13, 15),
        (4, 14, 10),
        (5, 15, 20),
        (5, 16, 10),
        (5, 17, 15),
        (5, 18, 5),
        (5, 19, 10),
    ]

    super_source = 20
    super_sink = 21
    terminals = [0, 1]
    warehouses = [2, 3, 4, 5]
    stores = list(range(6, 20))

    # суперджерело → термінали
    for t in terminals:
        capacity_matrix[super_source][t] = 9999
    # магазини → суперстік
    for s in stores:
        capacity_matrix[s][super_sink] = 9999
    # звичайні ребра
    for u, v, c in edges:
        capacity_matrix[u][v] = c

    # --- Запуск алгоритму ---
    max_flow, flow_matrix = edmonds_karp(capacity_matrix, super_source, super_sink)
    print(f"\nМаксимальний потік у мережі: {max_flow} одиниць\n")

    # --- Таблиця потоків ---
    df = build_flow_table(flow_matrix, terminals, warehouses, stores)
    print(df.to_string(index=False))

    # --- Візуалізація графа ---
    build_and_draw_graph(
        capacity_matrix,
        flow_matrix,
        terminals,
        warehouses,
        stores,
        super_source,
        super_sink,
        max_flow,
    )


# ------------------------------
# Запуск
# ------------------------------
if __name__ == "__main__":
    main()
