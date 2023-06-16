from array import array
from itertools import product

class space:
    def __init__(self, grp, *vectors):
        self.grp = grp
        self.vectors = tuple(vectors)
        assert len(self) > 0, "Number of vectors must be greater than 0"

    def __len__(self) -> int:
        return len(self.vectors)

    def __iter__(self):
        for i in range(len(self)):
            yield self.vectors[i]
    
    def __repr__(self) -> str:
        s = '<Instance of %s at addr %s,\n' % (self.__class__.__name__, id(self))
        s += '\tvectors:\n'
        for v in self:
            s += '\t' + str(v) + ',\n'
        s += '>'
        return s

    def __getitem__(self, i):
        return type(self)(self.grp, self.vectors[i])
    
    def __add__(self, other):
        '''Point-wise vector addition'''
        assert type(other) is type(self), "Point-wise vector add can only be performed on spaces of the same type"
        assert len(self) == len(other), "Point-wise vector add can only be performed on spaces of the same length"
        assert self.grp is other.grp, "Point-wise vector add can only be performed on spaces of the same group"
        result = []
        N = len(self)
        for i in range(N):
            u, v = self.vectors[i], other.vectors[i]
            assert len(u) == len(v), "vectors must be the same length to add"
            M = len(u)
            if self.grp is not None:
                result += [array(self.vectors[i].typecode,
                                 [self.grp["add"].synthesize(u[j], v[j]) for j in range(M)])]
            else:
                result += [array(self.vectors[i].typecode,
                                 [u[j] + v[j] for j in range(M)])]
        return type(self)(self.grp, *result)

    def __mul__(self, other):
        '''Point-wise vector multiply'''
        assert type(other) is type(self), "Point-wise vector mul can only be performed on spaces of the same type"
        assert len(self) == len(other), "Point-wise vector mul can only be performed on spaces of the same length"
        assert self.grp is other.grp, "Point-wise vector mul can only be performed on spaces of the same group"
        result = []
        N = len(self)
        for i in range(N):
            u, v = self.vectors[i], other.vectors[i]
            assert len(u) == len(v), "vectors must be the same length to mul"
            M = len(u)
            if self.grp is not None:
                result += [array(self.vectors[i].typecode,
                                 [self.grp["mul"].synthesize(u[j], v[j]) for j in range(M)])]
            else:
                result += [array(self.vectors[i].typecode,
                                 [u[j] * v[j] for j in range(M)])]
        return type(self)(self.grp, *result)

    
class rowspace(space):
    def __repr__(self) -> str:
        s = '<Instance of %s at addr %s,\n' % (self.__class__.__name__, id(self))
        s += '\trows:\n'
        for v in self:
            s += '\t' + str(v) + ',\n'
        s += '>'
        return s

    def transpose(self):
        '''Transpose a matrix by swapping the rows and columns.
        Uses the same vectors of rowspace to create a colspace'''
        return colspace(self.grp, *self.vectors)

    def columns(self):
        '''Return the number of columns'''
        return len(self.vectors[0])
    
    def as_colspace(self):
        '''Do not tranpose the matrix, instead find the vectors
        that define a colspace corresponding to the same matrix'''
        M = len(self)
        N = len(self.vectors[0])
        cols = [array(self.vectors[0].typecode, [0]*M) for n in range(N)]
        rows = self.vectors
        for row, col in product(range(M), range(N)):
            cols[col][row] = rows[row][col]
        return colspace(self.grp, *cols)
    
    def dot(self, other, return_type=None):
        assert type(other) is colspace, "rowspace must multiply on the right a colspace"
        assert self.columns() == other.rows(), "rowspace (left) must have as many columns as columnspace (right) has rows"
        assert self.grp is other.grp, "rowspace and colspace must have the same group"
        result = []
        M = len(self)
        N = len(other)
        grp = self.grp
        if return_type is None:
            for i in range(M):
                row = []
                for j in range(N):
                    u, v = self[i], other[j].transpose()
                    assert len(u) == len(v), "vectors must be the same length to dot"
                    if self.grp is not None:
                        row += [ self.grp["add"].synthesize( *(u*v).vectors[0].tolist() ) ]
                    else:
                        row += [ u*v ]
                result += [array(self.vectors[0].typecode, row)]
            return type(self)(self.grp, *result)
        else:
            for j in range(N):
                col = []
                for i in range(M):
                    u, v = self[i], other[j].transpose()
                    assert len(u) == len(v), "vectors must be the same length to dot"
                    if self.grp is not None:
                        col += [ self.grp["add"].synthesize( *(u*v).vectors[0].tolist() ) ]
                    else:
                        col += [ u*v ]
                result += [array(self.vectors[0].typecode, col)]
        return type(other)(self.grp, *result)
                    
    
class colspace(space):
    def __repr__(self) -> str:
        s = '<Instance of %s at addr %s,\n' % (self.__class__.__name__, id(self))
        s += '\tcolumns:\n'
        for v in self:
            s += '\t' + str(v) + ',\n'
        s += '>'
        return s

    def transpose(self):
        '''Transpose a matrix by swapping the rows and columns.
        Uses the same vectors of colspace to create a rowspace'''
        return rowspace(self.grp, *self.vectors)

    def rows(self):
        '''Return the number of rows'''
        return len(self.vectors[0])
    

class diagonal(space):
    def __init__(self, grp, vector):
        '''Diagonal takes a single vector as input argument
        containing the values along the diagonal of a matrix'''
        space.__init__(self, grp, vector)

    def expand(self):
        N = len(self.vectors[0])
        v = [array(self.vectors[0].typecode, [0]*N) for n in range(N)]
        for i in range(N):
            v[i][i] = self.vectors[0][i]
        return v
        
    def as_rowspace(self):
        return rowspace(self.grp, *self.expand())
    
    def as_colspace(self):
        return colspace(self.grp, *self.expand())

        

if __name__ == '__main__':
    from groups import binary_group, multiplicative_group, additive_group, incremental_set

    a1 = array("I", [1,2,3])
    a2 = array("I", [4,5,6])
    a3 = array("I", [7,8,9])

    A = space(None, a1, a2, a3)
    print('A=',A)
    print()
    
    b1 = array("I", [1,1,1])
    b2 = array("I", [1,0,1])
    B = rowspace(binary_group, b1, b2)
    print('B =', B)
    print()
    
    Bt = B.transpose()
    print('Bt =', Bt)
    Btt = Bt.transpose()
    print('Btt =', Btt)
    print('Btt is Bt =', Btt is Bt)
    print()

    B1 = colspace(binary_group, b1)
    B2 = colspace(binary_group, b2)
    print("B1+B2=",B1+B2)
    print()
    print("A+A=",A+A)
    print()

    print("B1*B2=",B1*B2)
    print()

    print("B.dot(Bt)=",B.dot(Bt))
    print()

    add_grp = additive_group(incremental_set(-7,7))
    mul_grp = multiplicative_group(add_grp)
    grp = {"add":add_grp, "mul":mul_grp}
    U = rowspace(grp,
                 array("i", [-1, 1, -1]),
                 array("i", [-1, -1, 1]),
                 array("i", [1, -1, -1]),
                 array("i", [1, 1, 1]) )
    print("U =", U)

    Sigma = diagonal(grp, array("i", [3, 2, 1]))
    print("Sigma =", Sigma)
    print("Sigma.as_rowspace() =", Sigma.as_rowspace())
    print("Sigma.as_colspace() =", Sigma.as_colspace())
    
    V = colspace(grp,
                 array("i", [1, -1, 1, -1]),
                 array("i", [-1, -1, 1, 1]),
                 array("i", [1, -1, -1, 1]) )
    print("Vt =", V.transpose())
    print("Vt [as colspace] =", V.transpose().as_colspace())

    print("Sigma.dot(Vt) =", Sigma.as_rowspace().dot(V.transpose().as_colspace()))
    
    A = U.dot(Sigma.as_rowspace().dot(V.transpose().as_colspace(), return_type=colspace))
    print("A = U.dot(Sigma.dot(Vt)) =", A)

    Answer = rowspace(grp,
                      array("i", [-6, 2, 0, 4]),
                      array("i", [0, 4, -6, 2]),
                      array("i", [4, 0, 2, -6]),
                      array("i", [2, -6, 4, 0]) )
