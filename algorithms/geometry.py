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


# Many of these geometry formulas come from
# http://www.topcoder.com/tc?module=Static&d1=tutorials&d2=geometry2

# Classes used:
# Vector - point or distance
# Line - general line specified by an equation
# LineSegment - a Line specified/bounded by two points - has additional functionality
# Circle - a circle specified by it's center and radius

import math

class GeometryException(Exception):
    """
    Used when a particular operation cannot be performed,
    for example an intersection does not exist.
    """
    pass

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def size(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
        
    def dist(self, other):
        return (self-other).size()
        
    def normalize(self):
        return self * (1.0/self.size())
        
    def crossp(self, other):
        """ Equal to ab sin(theta) """
        return self.x*other.y - self.y*other.x
        
    def dotp(self, other):
        """ Equal to ab cos(theta) """
        return self.x*other.x + self.y*other.y
        
    def __str__(self):
        return "(%.3f, %.3f)" % (self.x, self.y)
        
    def __repr__(self):
        return str(self)
        
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
        
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
        
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
        
    def __eq__(self, other):
        return self.dist(other) < 0.000001
    
    def __ne__(self, other):
        return not (self == other)
        
    def __hash__(self):
        return hash((round(self.x, 6), round(self.y, 6)))

    def __iter__(self):
        """ Enables x, y = line """
        return iter((self.x, self.y))
        
def ccw(a, b, c):
    """
    1: c is left of the line a->b
    -1: c is on the right of line a->b
    0: c is on the line a->b
    """
    cp = (b-a).crossp(c-a)
    if cp > 0.0:
        return 1
    elif cp < 0.0:
        return -1
    return 0

class Line(object):
    def __init__(self, A, B, C):
        """
        Constructs a line with the equation A*x + B*y + C = 0 
        """
        self.A = A
        self.B = B
        self.C = C
        
    def params(self):
        return self.A, self.B, self.C
        
    def intersection(self, other):
        """
        The intersection between this line and other, or None if it does not exist.
        
        Raises GeometryException if the lines are parallel
        """
        A1, B1, C1 = self.params()
        A2, B2, C2 = other.params()
        det = A1*B2 - A2*B1
        if det == 0:
            raise GeometryException()
            
        x = (B2*C1 - B1*C2)/det
        y = (A1*C2 - A2*C1)/det
        return Vector(x, y)
        
    def direction(self):
        """
        If from a line segment, this is the direction from point a to point b
        """
        A, B, C = self.params()
        return Vector(-B, A).normalize()
        
    def perpendicular(self, point):
        """
        The perpendicular to this line going through the specified point.
        The point may or may not be on this line.
        """
        A, B, C = self.params()
        D = -B*point.x + A*point.y
        return Line(-B, A, D)
        
    def drop_perpendicular(self, point):
        """  The point of intersection of a perpendicular line dropped from the specified point to this line. """
        p = self.perpendicular(point)
        i = self.intersection(p)    # point on the line
        return i
        
    def reflection(self, point):
        """ Reflection of a point over this line. """
        i = self.drop_perpendicular(point)
        return i*2-point
        
    
    def dist(self, point):
        """ The (perpendicular) distance from this line to a point. """
        i = self.drop_perpendicular(point)
        return point.dist(i)
        
        
        
class LineSegment(Line):
    def __init__(self, a, b):
        """ Constructs a line segment from Vector a to Vector b. """
        self.a = a
        self.b = b
        A = self.b.y - self.a.y
        B = self.a.x - self.b.x
        C = self.A * self.a.x + self.B * self.a.y
        super().__init__(A, B, C)
        
    def __iter__(self):
        """ Allows a, b = line """
        return iter((self.a, self.b))
   
    def direction(self):
        """
        This is an alternative implementation of the same method in Line.
        """
        return (self.b - self.a).normalize()
                
    def midpoint(self):
        return (self.a + self.b) * 0.5
        
    def perpendicular_bisector(self):
        return self.perpendicular(self.midpoint())
        
    def contains(self, point):
        """ Point must be on this line. Returns True if it is on this line segment. """
        return (point.x - self.a.x)*(point.x - self.b.x) < 0 or (point.y - self.a.y)*(point.y - self.b.y) < 0
        
    def length(self):
        return self.a.dist(self.b)
        
        
    def __str__(self):
        return "[%s - %s]" % (self.a, self.b)
        
    def __repr__(self):
        return str(self)
        
class Circle:
    def __init__(self, c, r):
        """ Constructs a circle with center Vector c and radius r. """
        self.c = c
        self.r = r
        
    def __str__(self):
        return "{%s %s}" % (self.c, self.r)
        
    def tangents(self, point):
        """
        The two tangent of the tangents of this circle through
        the specified point, as LineSegments.
        
        Raises GeometryException if the point is inside the circle
        """
        d = self.c.dist(point)
        r = self.r
        if r > d:
            return GeometryException()
        a = math.sqrt(d*d-r*r)
        b = a*a/d
        p = (self.c - point) * (b/d) + point
        k = LineSegment(self.c, point).perpendicular(p).direction()
        s = k * (r*a/d)
        #print d, r, a, b, p, s
        return LineSegment(point, p+s), LineSegment(point, p-s)
        
    def common(self, other, outer=True):
        """
        Common tangents of the two circles, as line segments between the tangent points,
        as well as their intersection.
        
        The first point of the first tangent is the tangent point on this circle, which is on
        the left of the line from this.c to other.c
        """
        cline = LineSegment(self.c, other.c)
        if outer and (self.r == other.r):
            la = cline.perpendicular(self.c)
            lb = cline.perpendicular(other.c)
            a1 = self.c + la.direction()*self.r
            a2 = self.c - la.direction()*self.r
            b1 = other.c + lb.direction()*other.r
            b2 = other.c - lb.direction()*other.r
            if ccw(self.c, other.c, a1) == 1:
                return LineSegment(a1, b1), LineSegment(a2, b2), None
            else:
                return LineSegment(a2, b2), LineSegment(a1, b1), None
        
        i = None
        
        tries = [(0, 1), (1, 0)]
        for s in tries:
            pa = self.c + Vector(self.r*s[0], self.r*s[1])
            if outer:
                pb = other.c + Vector(other.r*s[0], other.r*s[1])
            else:
                pb = other.c - Vector(other.r*s[0], other.r*s[1])
            tline = LineSegment(pa, pb)
            try:
                i = cline.intersection(tline)
                break
            except GeometryException:
                continue
            
        if i is None:
            return Exception("Should not happen")
        
        t1 = self.tangents(i)
        t2 = other.tangents(i)
        line1 = LineSegment(t1[0].b, t2[0].b)
        line2 = LineSegment(t1[1].b, t2[1].b)
        
        if ccw(self.c, other.c, t1[0].b) == 1:
            return line1, line2, i
        else:
            return line2, line1, i
        
    def intersects(self, line):
        """ Returns the average of the points of intersection, or None """
        p = line.drop_perpendicular(self.c)
        if self.c.dist(p) <= self.r:
            return p
        else:
            return None
            
    def intersections(self, line):
        """
        Returns the two points of intersection of this circle and the line.
        
        Raises GeometryException if the line and points don't intersect.
        """
        p = self.intersects(line)
        if p is None:
            raise GeometryException()
        d = self.c.dist(p)
        a = math.sqrt(self.r*self.r - d*d)
        return p + line.direction()*a, p - line.direction()*a
        
        

def circle(a, b, c):
    """ Constructs a circle passing through a, b and c. """
    line1 = LineSegment(a, b)
    line2 = LineSegment(b, c)
    p1 = line1.perpendicular_bisector()
    p2 = line2.perpendicular_bisector()
    c = p1.intersection(p2)
    if c is None:
        return None
    r = c.dist(a)
    return Circle(c, r)

def heron(a, b, c):
    """
    Calculates the area of a triangle with sides a, b and c.
    """
    s = (a + b + c)/2
    return math.sqrt(s*(s-a)*(s-b)*(s-c))

def area(v1, v2):
    """ Calculates of a triangle defined by two vectors. """
    return abs(v1.crossp(v2))/2.0
    
def dist(a, b):
    """
    The distance between two points of the same dimention.
    The points must be iterable (list or tuple)
    """
    s = 0
    for p, q in zip(a, b):
        d = p - q
        s += d*d
    return math.sqrt(s)
    
def translate_2d(a, b, c):
    """
    Translates 3 points in 3D space to 3 points in 2D space,
    keeping the distances between the points constant.
    
    The first point is put at the origin.
    The second point is put on the positive x-axis.
    The third point is put in one of the two top quadrants (y is positive).
    """
    d1 = dist(a, b)
    d2 = dist(a, c)
    d3 = dist(b, c)
    A = heron(d1, d2, d3)
    h = A/d1*2
    p = math.sqrt(d2*d2-h*h)
    q = math.sqrt(d3*d3-h*h)
    
    if p + q <= d1:
        s = p
    elif p > q:
        s = p
    else:
        s = -p
    return [Vector(0.0, 0.0), Vector(d1, 0.0), Vector(s, h)]

   
def circle_intersects_in(circle, a, b):
    """ Checks if a line segment intersects a circle. """
    ls = LineSegment(a, b)
    try:
        a, b = circle.intersections(ls)
        return ls.contains(a) or ls.contains(b)
    except GeometryException:
        return False    # No intersection

def circle_intersects_further(circle, segment):
    """ Checks is a circle intersects on the "positive side" of a circle. """
    try:
        a, b = circle.intersections(segment)
        return a.dist(segment.a) > segment.length() and a.dist(segment.a) > a.dist(segment.b)
    except GeometryException:
        return False    # No intersection
        