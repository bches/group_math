from groups import binary_group


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
        return self.vectors[i]
    
    def __add__(self, other):
        '''Point-wise vector addition'''
        assert type(other) is type(self), "Point-wise vector add can only be performed on spaces of the same type"
        assert len(self) == len(other), "Point-wise vector add can only be performed on spaces of the same length"
        assert self.grp is other.grp, "Point-wise vector add can only be performed on spaces of the same group"
        result = []
        N = len(self)
        for i in range(N):
            u, v = self[i], other[i]
            assert len(u) == len(v), "vectors must be the same length to add"
            M = len(u)
            if self.grp is not None:
                result += [array("I", [self.grp["add"].synthesize(u[j], v[j]) for j in range(M)])]
            else:
                result += [array("I", [u[j] + v[j] for j in range(M)])]
        return type(self)(self.grp, *result)

    def __mul__(self, other):
        '''Point-wise vector multiply'''
        assert type(other) is type(self), "Point-wise vector mul can only be performed on spaces of the same type"
        assert len(self) == len(other), "Point-wise vector mul can only be performed on spaces of the same length"
        assert self.grp is other.grp, "Point-wise vector mul can only be performed on spaces of the same group"
        result = []
        N = len(self)
        for i in range(N):
            u, v = self[i], other[i]
            assert len(u) == len(v), "vectors must be the same length to mul"
            M = len(u)
            if self.grp is not None:
                result += [array("I", [self.grp["mul"].synthesize(u[j], v[j]) for j in range(M)])]
            else:
                result += [array("I", [u[j] * v[j] for j in range(M)])]
        return type(self)(self.grp, *result)
    
    
class rowspace(space):
    def get_rows(self):
        return self.vectors

    def transpose(self):
        return colspace(self.grp, *self.vectors)

    def dot(self, other):
        assert type(other) is colspace, "rowspace must multiply on the right a colspace"
        assert len(self) == len(other), "rowspace (left) must have as many rows as columnspace (right) has columns"
        assert self.grp is other.grp, "rowspace and colspace must have the same group"
        result = []
        N = len(self)
        grp = self.grp
        for i in range(N):
            u, v = self[i], other[i]
            assert len(u) == len(v), "vectors must be the same length to dot"
            M = len(u)
            print("u[i]*v[i]=",u[i]*v[i])
            #if self.grp is not None:
                #result += [array("I", [self.grp["mul"].synthesize(u[j], v[j]) for j in range(M)])]
           # else:
                #result += [array("I", [u[j] * v[j] for j in range(M)])]
        return type(other)(self.grp, *result)
            
        
    
class colspace(space):
    def get_cols(self):
        return self.vectors

    def transpose(self):
        return rowspace(self.grp, *self.vectors)
    

if __name__ == '__main__':
    from array import array

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
