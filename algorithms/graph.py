# -*- coding: utf-8 -*-
#
# Copyright 2012 Ralf Kistner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Graph(object):
    def edges(self, node, **kwargs):
        """
        All edges from node to its neighbours.

        Additional parameters may be passed, for example "distance" - the current shortest distance to node.

        If the node does not exist, an empty dictionary will be returned.

        Result: {neighbour: weight}
        """
        return {}

    def nodes(self):
        """
        Iterator generating all nodes in this graph.

        The value of each node is implementation-specific.
        """
        return []

    def value(self, node):
        """
        Returns the value associated with a node. Optional.
        """
        return None

    def total_edges(self):
        total = 0
        for node in self.nodes():
            total += len(self.edges(node))
        return total


class GridGraph(Graph):
    """
    Represents a grid as a graph.

    `filter` is a function to filter out a block. The default filter accepts any block that evaluates to True.

    >>> g = GridGraph([[1, 0], [1, 1]])
    >>> g
    1 0
    1 1
    >>> list(g.all_nodes())
    [(0, 0), (0, 1), (1, 0), (1, 1)]
    >>> list(g.nodes())
    [(0, 0), (1, 0), (1, 1)]
    >>> sorted(g.edges((0, 0)).keys())
    [(1, 0)]
    """

    def __init__(self, grid, filter=None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

        if not filter:
            filter = lambda x: bool(x)

        self.filter = filter

    def distance(self, a, b, **kwargs):
        return 1

    def edges(self, node, **kwargs):
        row, col = node
        neighbours = []
        if row > 0:
            neighbours.append((row - 1, col))
        if col > 0:
            neighbours.append((row, col - 1))
        if col < self.cols - 1:
            neighbours.append((row, col + 1))
        if row < self.rows - 1:
            neighbours.append((row + 1, col))

        return {n: self.distance(node, n, **kwargs) for n in filter(self.node_filter, neighbours)}

    def node_filter(self, node):
        return self.filter(self.value(node))


    def all_nodes(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield (row, col)

    def value(self, node):
        return self.grid[node[0]][node[1]]

    def nodes(self):
        return filter(self.node_filter, self.all_nodes())

    def __str__(self):
        result = ""
        for row in self.grid:
            result += " ".join(map(str, row)) + "\n"
        return result.strip()

    def __repr__(self):
        return str(self)


class DirectedGraph(Graph):
    def __init__(self, G=None):
        """
        The input graph G is assumed to have the following
        representation: A vertex can be any object that can
        be used as an index into a dictionary.  G is a
        dictionary, indexed by vertices.  For any vertex v,
        G[v] is itself a dictionary, indexed by the neighbors
        of v.  For any edge v->w, G[v][w] is the length of
        the edge.

        >>> g = DirectedGraph({1: {2: 1}, 2: {3: 1}})
        >>> sorted(list(g.nodes()))
        [1, 2, 3]
        >>> sorted(g.edges(1).keys())
        [2]
        >>> sorted(g.edges(2).keys())
        [3]
        """
        G = G or {}
        self.G = {}
        for a, edges in G.items():
            for b, weight in edges.items():
                self.add_edge(a, b, weight)

    def edges(self, node, **kwargs):
        return self.G.get(node) or {}

    def add_edge(self, a, b, weight=1):
        if not a in self.G:
            self.G[a] = {}
        if not b in self.G:
            self.G[b] = {}
        self.G[a][b] = weight

    def nodes(self):
        return self.G.keys()

    def __str__(self):
        return str(self.G)

    def __repr__(self):
        return "<Directed %s>" % self


class UndirectedGraph(DirectedGraph):
    def __init__(self, G=None):
        """
        The input graph G is assumed to have the following
        representation: A vertex can be any object that can
        be used as an index into a dictionary.  G is a
        dictionary, indexed by vertices.  For any vertex v,
        G[v] is itself a dictionary, indexed by the neighbors
        of v.  For any edge v->w, G[v][w] is the length of
        the edge.

        For any edge v->w, the reverse edge w->v is automatically created.

        >>> g = UndirectedGraph({1: {2: 1}, 2: {3: 1}})
        >>> sorted(list(g.nodes()))
        [1, 2, 3]
        >>> sorted(g.edges(1).keys())
        [2]
        >>> sorted(g.edges(2).keys())
        [1, 3]
        """

        super(UndirectedGraph, self).__init__(G)

    def add_edge(self, a, b, weight=1):
        super(UndirectedGraph, self).add_edge(a, b, weight)
        super(UndirectedGraph, self).add_edge(b, a, weight)

    def total_edges(self):
        return super().total_edges() // 2

    def __repr__(self):
        return "<Undirected %s>" % self


def floodfill(graph):
    """
    Given a graph, performs a flood fill. The result is undefined on directed graphs.

    Group numbers (i) start at 1.

    Result: (n, {node => i})

    >>> g = GridGraph([[1, 1], [0, 0], [1, 1]])
    >>> n, d = floodfill(g)
    >>> n
    2
    >>> sorted(d.items())
    [((0, 0), 1), ((0, 1), 1), ((2, 0), 2), ((2, 1), 2)]
    """

    result = {}
    i = 0
    for node in graph.nodes():
        if node in result:
            continue
        i += 1
        queue = [node]
        result[node] = i
        while queue:
            next = queue.pop()
            for neighbour in graph.edges(next):
                if not neighbour in result:
                    queue.append(neighbour)
                    result[neighbour] = i
    return i, result


# Dijkstra's algorithm for shortest paths


def dijkstra(graph, start, end=None):
    """
    Find shortest paths from the start vertex to all
    vertices nearer than or equal to the end.

    The input graph G is assumed to have the following
    representation: A vertex can be any object that can
    be used as an index into a dictionary.  G is a
    dictionary, indexed by vertices.  For any vertex v,
    G[v] is itself a dictionary, indexed by the neighbors
    of v.  For any edge v->w, G[v][w] is the length of
    the edge.

    The output is a pair (D,P) where D[v] is the distance
    from start to v and P[v] is the predecessor of v along
    the shortest path from s to v.

    Original by
    David Eppstein, UC Irvine, 4 April 2002
    http://code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/

    >>> G = DirectedGraph({'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, \
            'y':{'s':7, 'v':6}})
    >>> distances, predecessors = dijkstra(G, 's', 'v')
    >>> sorted(distances.items())
    [('s', 14), ('u', 8), ('v', 9), ('x', 5), ('y', 7)]
    >>> sorted(predecessors.items())
    [('s', 'y'), ('u', 'x'), ('v', 'u'), ('x', 's'), ('y', 'x')]
    """
    import heapq

    distances = {}  # dictionary of final distances
    predecessors = {}  # dictionary of predecessors (previous node)
    queue = []  # queue
    heapq.heappush(queue, (0, start))

    while len(queue) > 0:
        distance, node = heapq.heappop(queue)
        if node in distances and distance > distances[node]:
            continue
        if node == end:
            break

        # Loop through neighbours
        edges = graph.edges(node, distance=distance)
        for neighbour, length in edges.items():
            total = distance + length
            if neighbour in distances:
                if total >= distances[neighbour]:
                    continue
            distances[neighbour] = total
            predecessors[neighbour] = node
            heapq.heappush(queue, (total, neighbour))

    return distances, predecessors


def shortest_path(graph, start, end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as Dijkstra().
    The output is a list of the vertices in order along
    the shortest path.

    >>> G = DirectedGraph({'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, \
            'y':{'s':7, 'v':6}})
    >>> shortest_path(G, 's', 'v')
    ['s', 'x', 'u', 'v']
    """

    distances, predecessors = dijkstra(graph, start, end)
    path = []
    while 1:
        path.append(end)
        if end == start: break
        end = predecessors[end]
    path.reverse()
    return path
