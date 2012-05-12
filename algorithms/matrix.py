"""
Some basic matrix-related functionality.
"""

def cumulative2d(grid):
    """
    >>> cumulative2d([[2, 5, 4], [3, 8, 1]])
    [[0, 0, 0, 0], [0, 2, 7, 11], [0, 5, 18, 23]]
    """
    rows = []
    for row in grid:
        rrr = [0]
        last = 0
        for col in row:
            last += col
            rrr.append(last)
        rows.append(rrr)
    blocks = []
    last = [0]*len(rows[0])
    blocks.append(last)
    for row in rows:
        last = list(map(sum, zip(last, row)))
        blocks.append(last)
    return blocks


def transpose(grid):
    """
    Switches rows and columns.
    
    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    """
    R = len(grid)
    C = len(grid[0])
    inverted = []
    for r in range(C):
        row = [c[r] for c in grid]
        inverted.append(row)
    return inverted
    
def moment(array):
    """
    >>> moment([5, 6, 7, 2, 4])
    [0, 6, 14, 6, 16]
    """
    return list(map(lambda i_v: i_v[0]*i_v[1], enumerate(array)))
    
def moment2d(grid):
    """
    >>> moment2d([[5, 6, 7, 2, 4]])
    [[0, 6, 14, 6, 16]]
    """
    return list(map(moment, grid))