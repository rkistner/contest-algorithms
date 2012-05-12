
import java.io.*;
import java.util.*;

public class Geometry {
    static class Point {
        double x;
        double y;
        
        Point(double x, double y) {
            this.x = x;
            this.y = y;
        }
        
        double size2() {
            return x*x + y*y;
        }

        double size() {
            return Math.sqrt(size2());
        }
        
        public String toString() {
            return String.format("(%.2f,%.2f)", x, y);
        }
    }
    
    static double crossp(Point a, Point b) {
        return a.x*b.y - b.x*a.y;
    }
    
    static Point subtract(Point a, Point b) {
        return new Point(a.x-b.x, a.y-b.y);
    }
    
    static int ccw(Point a, Point b, Point c) {
        // This version is useful when we do not need functions such as cross-product for anything else.
        double dx1 = b.x - a.x;
        double dy1 = b.y - a.y;
        double dx2 = c.x - a.x;
        double dy2 = c.y - a.y;
        double c1 = dx1*dy2;
        double c2 = dx2*dy1;
        if(c1 > c2)
            return 1;
        else if(c1 < c2)
            return -1;
        else
            return 0;
    }
    
    static int ccw2(Point a, Point b, Point c) {
        // This version is easier to understand.
        Point d1 = subtract(b, a);
        Point d2 = subtract(c, a);
        double cp = crossp(d1, d2);
        if(cp > 0.0)
            return 1;   // Counter-clockwise order
        else if(cp < 0.0)
            return -1;   // Clockwise order
        else
            return 0;   // Straight line
    }
    
    static class CCWComparator implements Comparator<Point> {
        Point root;
        
        CCWComparator(Point r) {
            root = r;
        }

        @Override
        public int compare(Point a, Point b) {
            int ccw = ccw(root, a, b);
            if(ccw == 0) {
                // nearest one first
                return Double.compare(subtract(a, root).size2(), subtract(b, root).size2());
            } else {
                // Sort in counter-clockwise order
                return -ccw;
            }
        }
        
    };
    
    
    
    public static double convexHull(List<Point> points) {
        int N = points.size();
        
        // Find the leftmost points first, choosing the bottom one if there are multiple leftmost points
        Point min = new Point(Double.MAX_VALUE, Double.MAX_VALUE);
        for(Point p : points) {
            if(p.x < min.x || (p.x == min.x && p.y < min.y)) {
                min = p;
            }
        }
        
        // Sort
        Collections.sort(points, new CCWComparator(min));

        // To complete the cycle, add the first point again.
        points.add(points.get(0));
        
        // This is essentially a stack.
        Point[] inhull = new Point[N+1];
        inhull[0] = points.get(0);
        inhull[1] = points.get(1);
        int l = 2;
        for(int c = 2; c <= N; c++) {
            Point pc = points.get(c);
            while(l >= 2) {
                Point pa = inhull[l-2];
                Point pb = inhull[l-1];
                if(ccw(pa, pb, pc) <= 0) {
                    l -= 1;
                } else {
                    break;
                }
            }
            inhull[l++] = pc;
        }
        
        // To calculate the length of the convex hull
        double length = 0;
        for(int i = 0; i < l-1; i++) {
            Point a = inhull[i];
            Point b = inhull[i+1];
            length += subtract(b, a).size();
        }
        return length;
    }
}