from itertools import product
from math import fabs

class group:
    def __init__(self, base, members):
        assert base != 0, "Base cannot be 0"
        assert type(base) is int, "base must be an int"
        self.base = base
        assert type(members) is list, "members must be a list"
        self.members = members
        
    def __repr__(self) -> str:
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tfor which operations are defined modulo %d,\n" % self.base
        s += "\tmembers = %s,\n" % self.members
        s += "\tisBijective: %s>\n" % self.isBijective()
        return s

    def __iter__(self) -> int:
        for member in self.members:
            yield member

    def __len__(self) -> int:
        return len(self.members)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def isBijective(self):
        return False

        
class incremental_set(group):
    def __init__(self, base, symmetry=False):
        assert base != 0, "Base cannot be 0"
        assert type(base) is int, "base must be an int"
        self.base = base
        if base > 0:
            b = base
        else:
            b = -base
        if ( ( b % 2 ) == 1 ) and symmetry:
            members = list(range(b//2+1))
            self.members = [-member for member in members[-1:0:-1]] + members 
        else:
            self.members = list(range(b))
        self.analysis = [self.members[-1]] + self.members[:-1]
        self.synthesis = self.members[1:] + [self.members[0]]

    def __repr__(self) -> str:
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tfor which operations are defined modulo %d,\n" % self.base
        s += "\tmembers = %s,\n" % self.members
        s += "\tsynthesis = %s,\n" % self.synthesis
        s += "\tanalysis = %s>" % self.analysis
        return s

    def synthesize(self, member) -> int:
        return self.synthesis[self.members.index(member)]

    def analyze(self, member) -> int:
        return self.analysis[self.members.index(member)]

    def isBijective(self):
        return True
    
    
class additive_group(group):
    def __init__(self, inc_grp):
        self.subop = inc_grp
        self.members = self.subop.members
        self.base = self.subop.base
        self.identity = 0
        self.inverse = self.members[:]
        self.inverse.reverse()
        
    def __repr__(self) -> str:
        s = "<Instance of %s at addr %s:\n" % (self.__class__.__name__, id(self))
        s += "\tfor which operations are defined modulo %d,\n" % self.base
        s += "\tidentity = %s,\n" % self.identity
        s += "\tmembers = %s,\n" % self.members
        s += "\tinverse = %s>" % self.inverse
        return s

    def synthesize(self, *members) -> int:
        z = self.identity
        for each in members:
            if each > self.identity:
                for i in range(each):
                    z = self.subop.synthesize(z)
            elif each < self.identity:
                for i in range(-each):
                    z = self.subop.analyze(z)                
        return z

    def analyze(self, *members) -> int:
        z = self.identity
        for each in members:
            if each > self.identity:
                for i in range(each):
                    z = self.subop.analyze(z)
            elif each < self.identity:
                for i in range(-each):
                    z = self.subop.synthesize(z)                
        return z

    def invert(self, member) -> int:
        result = self.inverse[self.members.index(member)]
        assert result is not None, "Inverse for %s does not exist in %s" % (member, self.__class__.__name__)
        return result

    def isBijective(self):
        return sum([self.inverse.count(each) for each in self.inverse]) == len(self.inverse) and None not in self.inverse
    
    
class multiplicative_group(additive_group):
    def __init__(self, add_grp):
        self.subop = add_grp
        self.members = self.subop.members
        self.base = self.subop.base
        self.identity = 1
        self.inverse = [None] * len(self)
        m = max(self.members)
        for x in self.members:
            if x in self.inverse or x == 0:
                continue
            if x == 1:
                self.inverse[self.members.index(x)] = 1
                continue
            if x == -1:
                self.inverse[self.members.index(x)] = -1
                continue
            for y in self.members:
                if y in self.inverse or fabs(x*y) < m or y < x:
                    continue                
                if self.synthesize(x, y) == self.identity:
                    self.inverse[self.members.index(x)] = y
                    self.inverse[self.members.index(y)] = x
                    break

    def synthesize(self, *members) -> int:
        if self.subop.identity in members:
            return self.subop.identity
        z = self.identity
        for each in members:
            if each == -self.identity:
                z = -z
            elif each > self.identity:
                z = self.subop.synthesize(*[z]*each)
            elif each < -self.identity:
                z = self.subop.analyze(*[z]*(-each))                
        return z

    def analyze(self, *members) -> int:
        assert self.subop.identity not in members, "%s.analyze() by %s not allowed" % (self.__class__.__name__,
                                                                                       self.subop.identity)
        z = self.identity
        for each in members:
            if each == -self.identity:
                z = -z
            elif each > self.identity:
                z = self.subop.analyze(*[z]*each)
            elif each < -self.identity:
                z = self.subop.synthesize(*[z]*(-each))                
        return z


class exponential_group(incremental_set):
    def __init__(self, mul_grp):
        self.subop = mul_grp
        self.members = self.subop.members
        self.base = self.subop.base
        self.synthesis = {}
        for member in self.members:
            if member == 0 or member == 1:
                self.synthesis[str(member)] = member
            else:
                self.synthesis[str(member)] = [self.subop.invert(self.subop.synthesize(*[member]*(-each))) for each in self.members if each < 0]
                self.synthesis[str(member)] += [self.subop.synthesize(*[member]*each) for each in self.members if each >= 0]
        self.analysis = {}
        for member in self.members:
            if member == 0 or member == 1:
                self.analysis[str(member)] = None
            else:
                self.analysis[str(member)] = []
                for each in self.members:
                    n = self.synthesis[str(member)].count(each)
                    if n == 0:
                        self.analysis[str(member)] += [None]
                    elif n == 1:
                        index = self.synthesis[str(member)].index(each)
                        self.analysis[str(member)] += [self.members[index]]
                    else:
                        indices = [i for i,x in enumerate(self.synthesis[str(member)]) if x == each]
                        self.analysis[str(member)] += [tuple([self.members[j] for j in indices])]
        self.identity = None
        self.generator = None

    def set_generator(self, member):
        assert member not in [0,1], "Cannot set generator to 1 or 0 in %s" % self.__class__.__name__
        self.generator = member
        
    def synthesize(self, member) -> int:
        assert self.generator != None, "Cannot call %s.synthesize() with generator=None; first call %s.set_generator()" % self.__class__.__name__
        return self.synthesis[str(self.generator)][self.members.index(member)]

    def analyze(self, member) -> int:
        assert self.generator != None, "Cannot call %s.analyze() with generator=None; first call %s.set_generator()" % self.__class__.__name__
        return self.analysis[str(self.generator)][self.members.index(member)]

    def isBijective(self):
        return False

    
# some groups are pre-defined for convenience    
binary_group = {'mul':multiplicative_group(additive_group(incremental_set(base=2))),
                'add':additive_group(incremental_set(base=2))}

ternary_group = {'exp':exponential_group(multiplicative_group(additive_group(incremental_set(base=-3, symmetry=True)))),
                 'mul':multiplicative_group(additive_group(incremental_set(base=-3, symmetry=True))),
                 'add':additive_group(incremental_set(base=-3, symmetry=True))}

pentary_group = {'exp':exponential_group(multiplicative_group(additive_group(incremental_set(base=-5, symmetry=True)))),
                 'mul':multiplicative_group(additive_group(incremental_set(base=-5, symmetry=True))),
                 'add':additive_group(incremental_set(base=-5, symmetry=True))}

septary_group = {'exp':exponential_group(multiplicative_group(additive_group(incremental_set(base=7)))),
                 'mul':multiplicative_group(additive_group(incremental_set(base=7))),
                 'add':additive_group(incremental_set(base=7))}


if __name__ == '__main__':
    print("Instantiate the incremental group")
    b = incremental_set(base=2)
    print(b)
    print()
    t = incremental_set(base=-3, symmetry=True)
    print(t)
    print()
    f = incremental_set(base=5, symmetry=True)
    print(f)
    print()
    print("f.synthesize(member=1) =", f.synthesize(member=1))

    print("\nInstantiate the additive group")
    g = additive_group(f)
    print("g=",g)
    print()
    
    print("g.synthesize(1,2)=", g.synthesize(1,2))
    print("g.synthesize(2,2)=", g.synthesize(2,2))
    print()

    print("Testing the 5-ary +ve group synthesis for all the combinations (of 2):")
    for x, y in product(g, repeat=2):
        print("%s + %s = %s" % (x, y, g.synthesize(x,y)))
    print()

    print("Testing the 5-ary +ve group analysis for all the combinations (of 2):")
    for x, y in product(g, repeat=2):
        print("%s - %s = %s" % (x, y, g.synthesize(x, g.invert(y))))
    print()

    
    print("Instantiate the multiplicative group")
    h = multiplicative_group(g)
    print("h=",h)
    print()

    print("Testing the 5-ary *ve group synthesis for all the combinations (of 2):")
    for x, y in product(h, repeat=2):
        print("%s * %s = %s" % (x, y, h.synthesize(x,y)))
    print()

    print("Testing the 5-ary *ve group analysis for all the combinations (of 2):")
    for x, y in product(h, repeat=2):
        try:
            result = h.synthesize(x, h.invert(y))
        except AssertionError:
            print("*** Correctly asserted no *ve inverse for %s, skipping..." % y)
            continue
        print("%s / %s = %s" % (x, y, result))
    print()


    print("Instantiate the exponential group")
    j = exponential_group(h)
    print("j=",j)
    print()

    j.set_generator(2)
    result = j.synthesize(2)
    print('2 squared, or 2 to the power 2, or 2 ** 2, or 2 ^ 2 = ', result)
    print()

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
