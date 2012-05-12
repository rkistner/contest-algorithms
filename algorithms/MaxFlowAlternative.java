
import java.io.*;
import java.util.*;

/*
This code assumes a directed graph.
It works with multiple edges between the same two nodes.
For an undirected graph, add an edge in both directions.

This algorithm works just as well with an adjecency matrix. When there are multiple edges between the same two nodes, we can just add the 
capacities together.

An alternative implementation of reverse edges does the following:
 - Separate edges are used for forwards and backwards.
 - Reverse edges have a capacity of 0.
 - Flows can be negative.

For maximum matching, simply create a bipartite graph and to max flow.
*/
public class MaxFlow {
    static class Node {
        int n;
        boolean start, end; // Is this the source or sink?
        List<Edge> edges = new ArrayList<Edge>();
        List<Edge> reverseEdges = new ArrayList<Edge>();
        
        public Node(int n) {
            this.n = n;
        }
    }
    
    static class Edge {
        // We store both from and to, as we have to backtrack
        Node from;
        Node to;
        int capacity;   // Maximum capacity in this direction. Constant.
        int flow;       // Current flow in this direction. Must be reset before flowing again in min-cut.
        
        public Edge(Node from, Node to, int capacity) {
            this.from = from;
            this.to = to;
            this.capacity = capacity;
            this.from.edges.add(this);
            this.to.reverseEdges.add(this);
        }
    }
    
    static class ToVisit {
        // This class is used to visit a path
        Node n;             // Node to visit
        ToVisit previous;   // previous visit, may be null
        Edge e;             // Edge used to get to the node
        boolean reverse;    // Was the edge used in reverse?
        int maxflow;        // Maximum flow in the path up to this point
        
        ToVisit(Node n, ToVisit previous, Edge e, boolean reverse, int maxflow) {
            this.n = n;
            this.previous = previous;
            this.e = e;
            this.reverse = reverse;
            this.maxflow = maxflow;
        }
    }
    
    
    static int bfs(Node node) {
        // This does a bfs to find any path with available capacity, and floods it.
        // The amount of flow sent through is returned.
        // If 0 is returned, we are done.
        Set<Node> visited = new HashSet<Node>();
        Queue<ToVisit> tovisit = new LinkedList<ToVisit>();
        tovisit.add(new ToVisit(node, null, null, false, Integer.MAX_VALUE));
        while(!tovisit.isEmpty()) {
            ToVisit tv = tovisit.remove();
            Node visit = tv.n;
            if(visit.end) {
                int flow = tv.maxflow;
                // Backtrack
                while(tv != null && tv.e != null) {
                    if(!tv.reverse) {
                        tv.e.flow += flow;
                    } else {
                        tv.e.flow -= flow;
                    }
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
                    tovisit.add(new ToVisit(e.to, tv, e, false, Math.min(tv.maxflow, e.capacity-e.flow)));
                }
            }
            
            // Back edges
            for(Edge e : visit.reverseEdges) {
                if(e.flow > 0) {
                    tovisit.add(new ToVisit(e.from, tv, e, true, Math.min(tv.maxflow, e.flow)));
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
            new Edge(nodes[from[i]], nodes[to[i]], capacity[i]);
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
                e.from.edges.remove(e);
                e.to.reverseEdges.remove(e);
            } else {
                e.capacity = cap;
            }
        }
        
        return solution;
    }
}
