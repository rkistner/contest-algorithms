# -*- coding: utf-8 -*-
# Dijkstra's algorithm for shortest paths
# Original by
# David Eppstein, UC Irvine, 4 April 2002
# http://code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/

import heapq

def Dijkstra(G,start,end=None):
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
    """

    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors (previous node)
    Q = []  # queue
    heapq.heappush(Q, (0, start))
    
    while len(Q) > 0:
        d, v = heapq.heappop(Q)
        if v in D and d > D[v]:
            continue
        if v == end: break
        
        # Loop through neighbours
        for w in G[v]:
            vwLength = d + G[v][w]
            if w in D:
                if vwLength >= D[w]:
                    continue
            D[w] = vwLength
            P[w] = v
            heapq.heappush(Q, (vwLength, w))
    
    return (D,P)
            
def shortestPath(G,start,end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as Dijkstra().
    The output is a list of the vertices in order along
    the shortest path.
    """

    D,P = Dijkstra(G,start,end)
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        end = P[end]
    Path.reverse()
    return Path
    
# Example:
# G = {'s':{'u':10, 'x':5}, 'u':{'v':1, 'x':2}, 'v':{'y':4}, 'x':{'u':3, 'v':9, 'y':2}, 'y':{'s':7, 'v':6}}
# print Dijkstra(G, 's', 'v')
# print shortestPath(G, 's', 'v')

