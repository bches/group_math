import array

class incremental_set:
    '''The incremental set is an ordered set of consecutive integers 
    for which the unary operations, increment and decrement, are defined.
    Incrementing past the largest number of the set results in the smallest 
    number in the set. Similarly, decrementing below the smallest number 
    in the set results in the largest number in the set.'''
    def __init__(self, m, n):
        '''The incremental set has the following symmetry options:
        m = 1: gives the symmetric group under composition, Sn.
        m = -n: the members are symmetric about 0.
        m = 0: no interesting symmetry in the members'''
        assert m < n, "m must be less than n"
        self.members = array.array("i", range(m,n+1))
        self.index = 0
        self.direction = True

    def __repr__(self) -> str:
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tindex = %s,\n" % self.index
        s += "\tmembers = %s>" % self.members
        return s

    def reset(self, member):
        assert member in self.members, "%s not in %s" % (member, self.members)
        self.index = self.members.index(member)

    def set_direction(self, direction):
        '''direction = True : increment
        direction = False : decrement'''
        assert type(direction) is bool, "direction must be type bool (got %s)" % type(direction)
        self.direction = direction

    def __len__(self) -> int:
        return len(self.members)
        
    def __next__(self) -> int:
        if self.direction:
            if self.index == (len(self)-1):
                self.index = 0
            else:
                self.index += 1
        else:
            if self.index == 0:
                self.index = len(self)-1
            else:
                self.index -= 1
        return self.members[self.index]

    def __iter__(self):
        return self

    def __call__(self, repeat) -> int:
        if repeat > 0:
            self.set_direction(True)
            [next(self) for i in range(repeat)]
        elif repeat < 0:
            self.set_direction(False)
            [next(self) for i in range(-repeat)]            
        return self.members[self.index] 
    
        
class group:
    def __init__(self, subop):
        self.subop = subop
        self.members = subop.members
        self.inverse = []
        self.identity = None
        self.generator = None
        
    def __repr__(self) -> str:
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tidentity = %s,\n" % self.identity
        s += "\tmembers = %s,\n" % self.members
        s += "\tinverse = %s,\n" % self.inverse
        s += "\tsubop = %s,\n" % self.subop
        s += "\tisBijective: %s>\n" % self.isBijective()
        return s

    def __iter__(self) -> int:
        for member in self.members:
            yield member

    def __len__(self) -> int:
        return len(self.members)

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__

    def isBijective(self) -> bool:
        return sum([self.inverse.count(each) for each in self.inverse]) == len(self.inverse) and None not in self.inverse

    def reset(self, member):
        assert member in self.members, "%s not in %s" % (member, self.members)
        self.generator = member

        
class additive_group(group):
    def __init__(self, inc_grp):
        self.subop = inc_grp
        self.members = self.subop.members
        self.identity = 0
        self.inverse = self.members[:]
        self.inverse.reverse()
        
    def synthesize(self, *members) -> int:
        self.subop.reset(self.identity)
        z = [self.subop(repeat=member) for member in members]
        return z[-1]

    def invert(self, member) -> int:
        result = self.inverse[self.members.index(member)]
        assert result is not None, "Inverse for %s does not exist in %s" % (member, self.__class__.__name__)
        return result

    def __call__(self, repeat) -> int:
        if repeat > self.identity:
            args = [self.generator] * repeat
            self.generator =  self.synthesize(*args)
            return self.generator
        elif repeat < self.identity:
            args = [-self.generator] * (-repeat)
            self.generator =  self.synthesize(*args)
            return self.generator
        else:
            return self.generator

    
class multiplicative_group(additive_group):
    def __init__(self, add_grp):
        self.subop = add_grp
        self.members = self.subop.members
        self.identity = 1
        self.inverse = [None] * len(self)

    def synthesize(self, *members) -> int:
        if self.subop.identity in members:
            return self.subop.identity
        self.subop.reset(self.identity)
        return [self.subop(repeat=member) for member in members][-1]

    def invert(self, member) -> int:
        '''Find the multiplicative inverse of member
        using the Extended Euclidean algorithm'''
        assert member in self.members, "%s not in %s" % (member, self.members)
        assert member != 0, "0 has no multiplicative inverse"
        if member < 0:
            a = -member
            negate_result = True
        else:
            a = member
            negate_result = False
        t, newt = 0, 1
        r, newr = len(self), a
        while newr != 0:
            quotient = r // newr
            (t, newt) = (newt, t - quotient * newt)
            (r, newr) = (newr, r - quotient * newr)
        assert r == 1 or r == -1, "%s is not invertible" % member
        if negate_result:
            return -t
        else:
            return t

    
# some groups are pre-defined for convenience    
binary_group = {'mul':multiplicative_group(additive_group(incremental_set(0,1))),
                'add':additive_group(incremental_set(0,1))}


if __name__ == '__main__':
    print("Instantiate the incremental group")
    b = incremental_set(0,1)
    print(b)
    print()
    t = incremental_set(-1,1)
    print(t)
    print()
    f = incremental_set(-2,2)
    print(f)
    print()
    print('Increment from -2 twice:', [next(f) for i in range(2)])

    print("\nInstantiate the additive group")
    g = additive_group(f)
    print("g=",g)
    print()
    
    print("g.synthesize(1,2)=", g.synthesize(1,2))
    print("g.synthesize(2,2)=", g.synthesize(2,2))
    print("f(-2):", f(-2))
    print("g.synthesize(-2,-2)=", g.synthesize(-2,-2))
    print()

    print("Instantiate the multiplicative group")
    h = multiplicative_group(g)
    print("h=",h)
    print()

    print("h.synthesize(2,2)=", h.synthesize(2,2))
    print("h.synthesize(-2,2)=", h.synthesize(-2,2))
    print("h.synthesize(2,-2)=", h.synthesize(2,-2))
    print("h.synthesize(-2,-2)=", h.synthesize(-2,-2))
    print()
    
    print("h.invert(2)=", h.invert(2))
    print("h.invert(-2)=", h.invert(-2))
    print("h.invert(1)=", h.invert(1))
    print("h.invert(-1)=", h.invert(-1))
    print()
    
    h.reset(2)
    result = h(2)
    print('2 squared, or 2 to the power 2, or 2 ** 2, or 2 ^ 2 = ', result)
    print()

    assert False, "stop here"


    result = j.analyze(-1)
    print('log2(-1) = ', result)
    print()
   
    grp2 = binary_group
    print("binary_group =", grp2)

    print()
    print('add:')
    for x, y in product(grp2["add"], repeat=2):
        print("\t%s + %s = %s" % (x,y,grp2["add"].synthesize(x, y)))
    print()

    print('sub:')
    inv = grp2["add"].invert
    for x, y in product(grp2["add"], repeat=2):
        z = grp2["add"].synthesize(x, inv(y))
        print("\t%s - %s = %s" % (x,y,z))
    print()


    grp3 = ternary_group
    print('ternary_group:', grp3)
    print()
    
    print('group equality:')
    print('grp2 == grp3:', grp2 == grp3)
    print('grp3 == grp3:', grp3 == grp3)
    print()

    print('Bijective:')
    for k in grp3.keys():
        print('grp3[%s].isBijective(): %s' % (k, grp3[k].isBijective()))

    print()
    grp = multiplicative_group(additive_group(incremental_set(base=9, symmetry=False)))
    print('grp =', grp)
    print('grp.isBijective():', grp.isBijective())
