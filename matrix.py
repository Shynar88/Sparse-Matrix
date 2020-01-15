#
# Implementation of a sparse matrix
#

class Node(object):
  """Objects of type Node represent all non-zero entries of the matrix.
A Node object stores the coordinates of the entry, its value el,
and has a link to the next non-zero entry to the right (in the same row)
and below (in the same column)."""
  def __init__(self, row, col, el, right, down):
    self.row = row
    self.col = col
    self.el = el
    self.right = right
    self.down = down

class Matrix(object):
  def __init__(self, nrows, ncols):
    self.nrows = nrows
    self.ncols = ncols
    self._prow = [None] * nrows
    self._pcol = [None] * ncols

  def _findnode(self, row, col):
    """Returns the node for (row, col) and the previous node in the same row.
Both are None if they do not exist."""
    p = self._prow[row]
    q = None
    while p is not None and p.col < col:
      q = p
      p = p.right
    if p is None or p.col == col:
      return p, q     #p tot chto pravee  q tot chto levee    p eto nuzhnyi element 
    return None, q

  def _finduppernode(self, row, col):
    p = self._pcol[col]
    q = None
    while p is not None and p.row < row:
      q = p
      p = p.down
    if p is None or p.row == row:
      return p, q
    return None, q
    #searchs from node in same column atarting from row 0 until row-1 inclusively
    #returns wanted element and upper one

  def _insertnode(self, row, col, q, el):
    """Insert a new node for entry (row, col) with value el.
q is the previous node on the same row, or None."""
    n = Node(row, col, el, None, None)
    pc, qc = self._finduppernode(row, col)
    if  qc == None:
      if self._pcol[col] == None:
        self._pcol[col] = n
      else:
        n.down = self._pcol[col]
        self._pcol[col] = n
    else:
      n.down = qc.down
      qc.down = n
    if q == None:    #elif if diff??
      if self._prow[row] == None:
        self._prow[row] = n
      else: 
        n.right = self._prow[row]
        self._prow[row] = n
    else:
      n.right = q.right
      q.right = n


  def _removenode(self, p, q):
    "Remove the node p. q is the previous node on the same row, or None."
    pc, qc = self._finduppernode(p.row, p.col)
    if  qc == None:
        self._pcol[p.col] = p.down
    else:
      qc.down = p.down
    if q == None:    
      self._prow[p.row] = p.right
    else:
      q.right = p.right


  def __getitem__(self, pos):
    "Return matrix entry pos = (row, col)."
    row, col = pos
    p, q = self._findnode(row, col)
    if p is None:
      return 0.0
    return p.el

  def __setitem__(self, pos, el):
    "Set matrix entry pos = (row, col) to value el."
    row, col = pos
    p, q = self._findnode(row, col)
    if p is None:
      if el != 0.0:
        self._insertnode(row, col, q, el)
    else:
      if el == 0.0:
        self._removenode(p, q)
      else:
        p.el = el
    
  def __repr__(self):
    s = ""
    for row in range(min(self.nrows, 10)):
      if row == 0:
        s += "/"
      elif row == self.nrows-1:
        s += "\\"
      else:
        s += "|"
      for col in range(min(self.ncols, 10)):
        s += "%6s " % self[row, col]
      if self.ncols > 10:
        s += "... "
      if row == 0:
        s += "\\\n"
      elif row == self.nrows-1:
        s += "/\n"
      else:
        s += "|\n"
    if self.nrows > 10:
      s += "...\n"
    return s

  def __eq__(self, rhs):
    "Test two matrices for equality."
    if self.nrows != rhs.nrows or self.ncols != rhs.ncols:
      return False
    for row in range(self.nrows):
      p1 = self._prow[row]
      p2 = rhs._prow[row]
      while p1 is not None and p2 is not None:
        if p1.col != p2.col or p1.el != p2.el:
          return False
        p1 = p1.right
        p2 = p2.right
      if p1 is not None or p2 is not None:
        return False
    return True

  def __mul__(self, rhs):
    "Multiply matrix with vector from the right."
    if self.ncols != len(rhs):
      raise ValueError("Dimensions of matrix and vector do not match")
    result = [0.0] * self.nrows
    for row in range(self.nrows):
      p = self._prow[row] 
      while p is not None:
        result[row] += p.el * rhs[p.col]
        p = p.right
    return result


  def __rmul__(self, lhs):
    "Multiply matrix with vector from the left."
    if self.nrows != len(lhs):
      raise ValueError("Dimensions of matrix and vector do not match")
    result = [0.0] * self.ncols
    for col in range(self.ncols):
      p = self._pcol[col] 
      while p is not None:
        result[col] += p.el * lhs[p.row]
        p = p.down
    return result

  def transposed(self):
    result = Matrix(self.ncols, self.nrows)
    for row in range(self.nrows):
      p = self._prow[row] 
      while p is not None:
      	result.__setitem__((p.col, p.row), p.el)
      	p = p.right
    return result

  def __add__(self, rhs):
    	if self.nrows != rhs.nrows or self.ncols != rhs.ncols:
    		raise ValueError("Dimensions of matrices do not match")
    	result = Matrix(self.nrows, self.ncols)
    	for row in range(self.nrows):
    		p1 = self._prow[row]
    		while p1 is not None:
    			el2 = rhs.__getitem__((p1.row, p1.col))
    			if el2 != 0:
    				if p1.el + el2 != 0:
    					result.__setitem__((p1.row, p1.col), p1.el + el2)
    			else:
    				result.__setitem__((p1.row, p1.col), p1.el)
    			p1 = p1.right
    	for row in range(self.nrows):
    		p1 = rhs._prow[row]
    		while p1 is not None:
    			el = result.__getitem__((p1.row, p1.col))
    			if el == 0:
    				if self.__getitem__((p1.row, p1.col)) == 0:
    					result.__setitem__((p1.row, p1.col), p1.el)
    			p1 = p1.right
    	return result

# --------------------------------------------------------------------

def identity(n):
  "Create an nxn identity matrix."
  M = Matrix(n, n)
  for i in range(n):
    M[i,i] = 1.0
  return M

# --------------------------------------------------------------------

if __name__ == "__main__":
  m = identity(4)
  print(m)
  m[1,1] = 7
  print(m)
  m[2,1] = 13
  print(m)
  m[0,3] = -2
  print(m)
  m[3,3] = 0
  print(m)
  m[0,0] = 0
  print(m)
  m2 = Matrix(4, 4)
  m2[0,3] = -2
  m2[1,1] = 7
  m2[2,1] = 13
  print(m2)
  print(m == m2)
  m2[2,2] = -1
  m2[2,0] = 5
  m[1,0] = 6
  print("This is m2")
  print(m2)
  print("This is m1")
  print(m)
  m3 = m2 + m
  print("This is m3")
  print(m3)
  # print(m == m2)
  # print(m * [ 1, 2, 3, 4 ] )
  # print([1, 2, 3, 4] * m)
  # t = m.transposed()
  # print(t)
  # print([1, 2, 3, 4] * t)
  # print(t * [ 1, 2, 3, 4 ] )
  # m3 = m + t
  # print(m3)
  # print(m3 == m3.transposed())
  
# --------------------------------------------------------------------
