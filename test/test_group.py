import sys
from itertools import product
sys.path.append('../src')
from groups import incremental_set, additive_group, multiplicative_group

if __name__ == '__main__':
    g = additive_group(incremental_set(-2,2))
    print("g=",g)
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
    
