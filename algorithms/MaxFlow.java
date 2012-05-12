/*
This code assumes a directed graph.
It works with multiple edges between the same two nodes.
For undirected graphs, only the creation of edges is different (Edge.connectDirected).

This algorithm works just as well with an adjecency matrix. When there are multiple edges between the same two nodes, we can just add the 
capacities together.

For maximum matching, simply create a bipartite graph and do max flow.

An alternative implementation of reverse edges does the following:
 - The same edge is used for both directions.
 - Nodes have separate lists of forward and back edges.
 - Flows cannot be negative.
*/

import java.io.*;
import java.util.*;

public class MaxFlow {
    static class Node {
        int n;
        boolean start, end; // Is this the source or sink?
        List<Edge> edges = new ArrayList<Edge>();
        
        public Node(int n) {
            this.n = n;
        }
    }
    
    static class Edge {
        Node to;
        // Maximum capacity in this direction. Constant; may be 0.
        int capacity;
        // Current flow in this direction. Must be reset before flowing again in min-cut.
        int flow;
        Edge reverse;
        
        public Edge(Node to, int capacity) {
            this.to = to;
            this.capacity = capacity;
        }
        
        static void connectDirected(Node from, Node to, int capacity) {
            Edge forward = new Edge(to, capacity);
            Edge back = new Edge(from, 0);  // For undirected, also set this to capacity
            forward.reverse = back;
            back.reverse = forward;
            from.edges.add(forward);
            to.edges.add(back);
        }
    }
    
    static class ToVisit {
        // This class is used to visit a path
        Node n;             // Node to visit. Equal to e.to, unless of course when e == null
        ToVisit previous;   // previous visit; may be null
        Edge e;             // Edge used to get to the node; may be null
        int maxflow;        // Maximum flow in the path up to this point
        
        ToVisit(Node n, ToVisit previous, Edge e, int maxflow) {
            this.n = n;
            this.previous = previous;
            this.e = e;
            this.maxflow = maxflow;
        }
    }
    
    
    static int bfs(Node node) {
        // This does a bfs to find any path with available capacity, and floods it.
        // The amount of flow sent through is returned.
        // If 0 is returned, we are done.
        
        // This is a standard BFS, but we keep track of the path.
        Set<Node> visited = new HashSet<Node>();
        Queue<ToVisit> tovisit = new LinkedList<ToVisit>();
        tovisit.add(new ToVisit(node, null, null, Integer.MAX_VALUE));
        while(!tovisit.isEmpty()) {
            ToVisit tv = tovisit.remove();
            Node visit = tv.n;
            if(visit.end) {
                int flow = tv.maxflow;
                // Backtrack
                while(tv != null && tv.e != null) {
                    tv.e.flow += flow;
                    tv.e.reverse.flow -= flow;
                    tv = tv.previous;
                }
                return flow;
            }
            
            // Never visit the same node twice
            if(visited.contains(visit))
                continue;
            visited.add(visit);
            
            // Forward edges
            for(Edge e : visit.edges) {
                if(e.capacity - e.flow > 0) {
                    tovisit.add(new ToVisit(e.to, tv, e, Math.min(tv.maxflow, e.capacity-e.flow)));
                }
            }
        }
        return 0;
    }
    
    static int maxFlow(Node start) {
        int totalFlow = 0, flow = 0;
        do {
            flow = bfs(start);
            totalFlow += flow;
        } while(flow > 0);
        
        // The following would give the same result:
        //for(Edge e : start.edges) {
        //    totalFlow += e.flow;
        //}
        
        return totalFlow;
    }
    
    public static Node[] construct(int N, int[] from, int[] to, int[] capacity) {
        // Just an example to setup the data structures.
        // nodes[0] is the start node, nodes[n-1] is the end node.
        Node[] nodes = new Node[N];
        for(int i = 0; i < N; i++) {
            nodes[i] = new Node(i);
        }
        nodes[0].start = true;
        nodes[N-1].end = true;
        int M = from.length;
        for(int i = 0; i < M; i++) {
            Edge.connectDirected(nodes[from[i]], nodes[to[i]], capacity[i]);
        }
        
        return nodes;
    }
    
    
    // The following code is only applicable to find the minimum cut.
    static void reset(List<Edge> edges) {
        for(Edge e : edges) {
            e.flow = 0;
        }
    }
        
    
    public static List<Edge> minCut(Node[] nodes, List<Edge> edges) {
        // This finds the set of edges with the minimum total cost (capacity),
        // such that the source and sink are disconnected if the edges are removed from the system.

        // Note that we need a list of ALL the edges (not just the forward edges), as we use the list to reset the graph on each run.
        List<Edge> solution = new ArrayList<Edge>();
        
        int remainingFlow = maxFlow(nodes[0]);
        reset(edges);
        
        for(Edge e : edges) {
            int cap = e.capacity;
            if(cap == 0)
                continue;
            
            // Remove edge from the system and flow again.
            e.capacity = 0;
            int newFlow = maxFlow(nodes[0]);
            reset(edges);
            
            if(remainingFlow - newFlow == cap) {
                remainingFlow = newFlow;
                solution.add(e);
                
                // This is just a possible optimization, and is not needed for the solution to work:
                // e.reverse.to.edges.remove(e);
                // e.to.edges.remove(e.reverse);
            } else {
                e.capacity = cap;
            }
        }
        
        return solution;
    }
}
