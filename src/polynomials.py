from groups import multiplicative_group, additive_group, incremental_set


class polynomial:
    def __init__(self, coef_grp, coefs):
        if type(coef_grp) is dict:
            self.coef_grp = coef_grp
        elif type(coef_grp) is multiplicative_group:
            self.coef_grp = {"mul":coef_grp,
                             "add":cpef_grp.subop}
        elif type(coef_grp) is additive_group:
            self.coef_grp = {"add":coef_grp}
        else:
            assert False, "Unrecognized coef_grp: %s" % coef_grp
        self.coefs = coefs

    def __repr__(self):
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tc0*x^0 + c1*x^1 + ... + c{N-1}*x^{N-1},\n"
        s += "\tcoefs = %s>" % self.coefs
        return s

    def __len__(self):
        return len(self.coefs)

    def __getitem__(self, i):
        if type(i) is str:
            return self.coef_grp[i]
        else:
            return self.coefs[i]

    def __iter__(self):
        for coef in self.coefs:
            yield coef
    
    def __lshift__(self, amount):
        '''Shift down (left) by amount'''
        assert amount <= len(self), "Shift amount must be <= length of polynomial"
        return polynomial(self.coef_grp, self.coefs[amount:])

    def __rshift__(self, amount):
        '''Shift up (right) by amount'''
        assert amount <= len(self), "Shift amount must be <= length of polynomial"
        coefs = array('I', [0] * amount + self.coefs.tolist())
        return polynomial(self.coef_grp, coefs)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        if self.coef_grp != other.coef_grp:
            return False
        result = True
        for i in range(len(self)):
            result = result & (self.coefs[i] == other[i])
        return result

    def scale(self, k):
        assert k in self.coef_grp["mul"], "%s is not in %s" % (k, self.coef_grp["mul"])
        return polynomial(self.coef_grp, [self.coef_grp["mul"].synthesize(c, k) for c in self])

    def __add__(self, other):
        '''Add two polynomials whose coefs are of the same additive group'''
        assert self.coef_grp["add"] == other["add"], "polynomials must have the same additive group to add"
        M,N = len(self), len(other)
        if M > N:
            result = [self.coef_grp["add"].synthesize(a,b) for a, b in zip(self[:N],other)] + self.coefs[N:]
        elif N > M:
            result = [self.coef_grp["add"].synthesize(a,b) for a, b in zip(self,other[:M])] + other[M:]
        else:
            result = [self.coef_grp["add"].synthesize(a,b) for a, b in zip(self,other)]
        return polynomial(self.coef_grp, result)

    def __mul__(self, other):
        '''Multiply two polynomials whose coefs are of the same multiplicative group'''
        assert self.coef_grp["mul"] == other["mul"], "polynomials must have the same multiplicative group to multiply"
        M,N = len(self), len(other)
        A = [(self >> n).scale(other[n]) for n in range(N)]
        print("A=",A)

        
if __name__ == '__main__':
    from array import array as array
    from groups import binary_group

    p1 = polynomial(binary_group, array('I', [1, 1, 1, 1]))
    p2 = polynomial(binary_group, array('I', [1, 0, 0, 1]))

    print('p1 =', p1)
    print()
    print('p2 =', p2)
    print()
    print('p1 + p2 =', p1 + p2)
    print()

    print('p2 >> 3 =', p2 >> 3)
    print('p1 << 2 =', p1 << 2)
    print()
    
    print('p1 * p2 =', p1*p2)
