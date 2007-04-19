import math
import random

from rasmus import util


class SeqDict (dict):
    """\
    A dictionary for sequences.  Also keeps track of their order, useful for 
    reading and writing sequences from fasta's.  See fasta.FastaDict for
    subclass that implements FASTA reading and writing.
    """

    def __init__(self):
        dict.__init__(self)
        
        self.names = []
    

    
    
    def orderNames(self, aln):
        """Orders the names in the same order they appear in aln"""
        
        lookup = util.list2lookup(aln.keys())
        self.names.sort(key=lambda x: lookup[x])
        
    
    # add a key, value pair
    def add(self, key, value, errors=False):
        if key in self:
            if errors:
                util.logger("duplicate key", key)

            # keep the longest value, by default
            if len(value) >= len(self[key]):
                dict.__setitem__(self, key, value)
        else:    
            self.names.append(key)
            dict.__setitem__(self, key, value)
    
    
    def get(self, keys, new=None):
        """Return a subset of the sequences"""
        
        if new == None:
            new = type(self)()
        
        for key in keys:
            if key in self:
                new[key] = self[key]
        
        return new


    def alignlen(self):
        """
        If this SeqDict is an alignment, this function 
        will return its length
        """
        
        return len(self.values()[0])
        
    
    # The following methods keep names in sync with dictionary keys
    def __setitem__(self, key, value):
        if key not in self:
            self.names.append(key)
        dict.__setitem__(self, key, value)
    
    def __delitem__(self, key):
        self.names.remove(key)

    def update(self, dct):
        for key in dct:
            if key not in self.names:
                self.names.append(key)
        dict.update(self, dct)
    
    def setdefault(self, key, value):
        if key not in self.names:
            self.names.append(key)
        dict.setdefault(self, key, value)
    
    def clear(self):
        self.names = []
        dict.clear(self)

    # keys are always sorted in order added
    def keys(self):
        return self.names

    def iterkeys(self):
        return iter(self.names)
    
    def values(self):
        return [self[key] for key in self.iterkeys()]
    
    def itervalues(self):
        def func():
            for key in self.iterkeys():
                yield self[key]
        return func()
        
    def iteritems(self):
        def func():
            for key in self.iterkeys():
                yield (key, self[key])
        return func()

    def __iter__(self):
        return iter(self.names)
    
    def __len__(self):
        return len(self.names)


 
BASE2INT = {
    "A": 0,
    "C": 1,
    "G": 2,
    "T": 3
}

INT2BASE = ["A", "C", "G", "T"]

KIMURA_MATRIX = [
    ['r', 's', 'u', 's'],
    ['s', 'r', 's', 'u'],
    ['u', 's', 'r', 's'],
    ['s', 'u', 's', 'r']
]


def evolveKimuraSeq(seq, time, alpha=1, beta=1):
    probs = {
        's': .25 * (1 - math.e**(-4 * beta * time)),
        'u': .25 * (1 + math.e**(-4 * beta * time)
                      - 2*math.e**(-2*(alpha+beta)*time))
    }
    probs['r'] =  1 - 2*probs['s'] - probs['u']
    
    seq2 = []
    
    for base in seq:
        cdf = 0
        row = KIMURA_MATRIX[BASE2INT[base]]
        pick = random.random()
        
        for i in range(4):
            cdf += probs[row[i]]
            if cdf >= pick:
                seq2.append(INT2BASE[i])
                break
    
    assert len(seq2) == len(seq), "probabilities do not add to one"
    
    return "".join(seq2)


def evolveKimuraBase(base, time, alpha, beta):
    probs = {
        's': .25 * (1 - math.e**(-4 * beta * time)),
        'u': .25 * (1 + math.e**(-4 * beta * time)
                      - 2*math.e**(-2*(alpha+beta)*time))
    }
    probs['r'] =  1 - 2*probs['s'] - probs['u']
    
    cdf = 0
    row = KIMURA_MATRIX[BASE2INT[base]]
    pick = random.random()
    
    for i in range(4):
        cdf += probs[row[i]]
        if cdf >= pick:
            return INT2BASE[i]
    
    assert False, "probabilities do not add to one"
    



