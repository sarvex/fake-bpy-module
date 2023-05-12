from typing import List, Dict


class Node:
    def __init__(self, data=None):
        self._data = data
        self._in_edges: List['Edge'] = []
        self._out_edges: List['Edge'] = []

    def in_edges(self) -> List['Edge']:
        return self._in_edges

    def out_edges(self) -> List['Edge']:
        return self._out_edges

    def num_in_edges(self) -> int:
        return len(self.in_edges())

    def num_out_edges(self) -> int:
        return len(self.out_edges())

    def data(self):
        return self._data


class Edge:
    def __init__(self, src: 'Node', dst: 'Node'):
        self._src = src
        self._dst = dst
        src._out_edges.append(self)
        dst._in_edges.append(self)

    def src(self) -> 'Node':
        return self._src

    def dst(self) -> 'Node':
        return self._dst


class DAG:
    def __init__(self):
        self._root_node: 'Node' = Node()
        self._nodes: List['Node'] = [self._root_node]
        self._edges: List['Edge'] = []

    def make_node(self, data=None) -> 'Node':
        new_node = Node(data)
        self._nodes.append(new_node)
        self.make_edge(self._root_node, new_node)

        return new_node

    def make_edge(self, src: 'Node', dst: 'Node') -> 'Edge':
        new_edge = Edge(src, dst)
        self._edges.append(new_edge)

        return new_edge

    def root_node(self) -> 'Node':
        return self._root_node

    def nodes(self, with_root: bool = False) -> List['Node']:
        return (
            self._nodes
            if with_root
            else list(
                set(self._nodes)
                - {
                    self._root_node,
                }
            )
        )

    def edges(self, with_root: bool = False) -> List['Edge']:
        if with_root:
            return self._edges

        return [e for e in self._edges if e.src() != self._root_node]

    def num_nodes(self, with_root: bool = False) -> int:
        return len(self._nodes) if with_root else len(self._nodes) - 1

    def num_edges(self, with_root: bool = False) -> int:
        if with_root:
            return len(self._edges)

        return sum(1 for e in self._edges if e.src() != self._root_node)


def topological_sort(graph: 'DAG') -> List['Node']:
    ref_counts: Dict['Node', int] = {
        node: node.num_in_edges() for node in graph.nodes(with_root=True)
    }
    sorted_nodes: List['Node'] = []
    ready: List['Node'] = [graph.root_node()]
    while ready:
        node = ready.pop(0)

        if node != graph.root_node():
            sorted_nodes.append(node)

        for e in node.out_edges():
            ref_counts[e.dst()] -= 1
            if ref_counts[e.dst()] == 0:
                ready.append(e.dst())

    if graph.num_nodes(with_root=True) != len(sorted_nodes) + 1:
        diff = (
            set(graph.nodes(with_root=True))
            - set(sorted_nodes)
            - {graph.root_node()}
        )
        node_data_list = {n.data() for n in diff}
        raise ValueError(f"Cycle is detected. ({', '.join(node_data_list)})")

    return sorted_nodes
