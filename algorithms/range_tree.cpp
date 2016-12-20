// Fenwick Tree / Segment Tree ?

/*
Tree structure:
# level                               # blevel

       0   1   2   3   4   5   6   7      # li - leaf index

3      8   9   10  11  12  13  14  15  0   # ni - node index
        \ /     \ /     \ /     \ /
2        4       5       6       7     1
           \   /          \    /  
1            2              3          2
                \        / 
0                    1                 3

0 is empty

D = 3
0 <= level <= D

MAX_LEAVES = 2 ^ D = 8
0 <= li < MAX_LEAVES         # leaf index

TREE_SIZE = 2 ^ (D + 1) = 16
1 <= ni < TREE_SIZE

blevel = D - level
level_nodes = 2 ^ level      # number of nodes on the level
level_ni = 2 ^ level         # first ni on the level
leaf_coverage = 2 ^ blevel   # number of leaf nodes covered by a node on the level
leveli = ni - level_ni       # position of node in level. 0 <= leveli < level_nodes
lower_li = leveli * leaf_coverage # leaf index of first leaf covered by the node
upper_li = (leveli + 1) * leaf_coverage # leaf index of last leaf covered by the node, + 1
                             # lower_li <= li < upper_li

ni = li + MAX_LEAVES
*/

const int D = 16; // 2^16 = 65536 > 50000
const int MAX_LEAVES = 1 << D;
const int TREE_SIZE = 1 << (D + 1);


class Node {
   public:
    int level;
    int ni;
    int val;
    
    Node() {}
    Node(int d, int _ni) : level(d), ni(_ni), val(0) { }
    Node(int _ni) : level(0), ni(_ni), val(0) {
        // Slow!
        int k = _ni;
        while(k > 1) {
            level += 1;
            k >>= 1;
        }
    }
    
    int blevel() {
        return D - level;
    }

    // Returns the max ni + 1 covered by this node
    int upper_li() {
        int leaf_coverage = 1 << blevel();
        return (leveli() + 1) * leaf_coverage;
    }

    int lower_li() {
        int leaf_coverage = 1 << blevel();
        return (leveli()) * leaf_coverage;
    }

    int leveli() {
        return ni - (1 << level);
    }
};


class RangeTree {
    public:
    Node nodes[TREE_SIZE];

    RangeTree() {
        for(int d = 0; d <= D; d++) {
            int start = 1 << d;
            int end = 2 << d;
            for(int ni = start; ni < end; ni++) {
                nodes[ni] = Node(d, ni);
            }
        }
    }


    int parent_i(int ni) {
        return (ni) / 2;
    }

    int node_i(int li) {
        return li + MAX_LEAVES;
    }

    void insert(int li, int val) {
        int ni = node_i(li);
        while(ni > 0) {
            auto& node = nodes[ni];
            node.val += val; // OR: node.val = (node.val + val) % P
            ni >>= 1;
        }
    }

    // Sum of values where li < upper_leaf_bound
    // For a range, use sum(upper_bound) - sum(lower_bound)
    int sum(int upper_leaf_bound) {
        // Highest leaf node we cover
        int ni = upper_leaf_bound - 1 + MAX_LEAVES; // node_i(upper_leaf_bound-1)
        int s = 0;
        while(ni > 0) {
            int parenti = ni >> 1;

            if(nodes[parenti].upper_li() <= upper_leaf_bound && ni > 1) {
                // Parent covers the node - move to parent
                ni = parenti;
            } else {
                // Parent doesn't cover it, but we do.
                // Add ourselves
                Node& self = nodes[ni];

                s += self.val;  // OR: s = (s + self.val) % P
                if(self.leveli() > 0) {
                    // Move left on the same level
                    ni -= 1;
                } else {
                    // We can't move further left - we have covered everything
                    break;
                }
            }
        }
        return s;
    }
};
