"""
tables.py

Implements Manolis style tab-delimited table file format.

"""


from util import *


tableTypesLookup = {
        "string": str,
        "int": int,
        "float": float,
        "bool": str2bool,
        "unknown": str
    }



def parseTableTypes(line, delim):
    names = line.replace("#Types:", "").split(delim)
    types = []
    
    for name in names:
        if name in tableTypesLookup:
            types.append(tableTypesLookup[name])
        else:
            types.append(eval(name))
    return types


def formatTableTypes(types, delim):
    lookup = revdict(tableTypesLookup)
    names = []
    
    for t in types:
        if t in lookup:
            names.append(lookup[t])
        else:
            names.append(t.__name__)
    return delim.join(names)
    

def readTable(filename, delim="\t"):
    """Reads a character delimited file and returns a two-dimensional 
       list of all the tokens.
       
       notes:
       Lines that start with '#' are treated as comments and are skiped
       Blank lines are skipped.
       
       If the first comment starts with '#Types:' the following tokens
       are interpreted as the data type of the column and values in that
       column are automatically converted.
       
       supported datatypes:
       - string
       - int
       - float
       - bool
       - unknown (no conversion is done, left as a string)
       
    """

    infile = openStream(filename)
    
    types = []
    header = None
    table = []
    
    for line in infile:
        line = line.rstrip()
        
        # skip blank lines
        if len(line) == 0:
            continue
        
        # handle comments
        if line[0] == "#":
            if line.startswith("#Types:"):
                types = parseTableTypes(line, delim)
            continue
        
        tokens = line.split(delim)
        
        
        if not header:
            # parse header
            header = tokens
        else:
            # parse data
            row = {}
            for i in xrange(len(tokens)):
                if len(types) > 0:
                    row[header[i]] = types[i](tokens[i])
                else:
                    row[header[i]] = tokens[i]
            table.append(row)
    
    return table, header


def writeTable(filename, table, header=None, delim="\t"):
    out = openStream(filename, "w")
    
    # set default header if needed
    if not header:
        header = table[0].keys()
    
    # write types    
    entry = table.values()[0]
    types = map(lambda x: type(entry[x]), header)
    out.write("#Types:" + formatTableTypes(types, delim) + "\n")
    
    # write header
    print >>out, delim.join(header)
    
    # write data
    for row in table:
        print >>out, delim.join(map(lambda x: str(row[x]), header))


def lookupTable(table, key, index=False):
    lookup = {}
    if index:
        for i in xrange(len(table)):
            key2 = table[i][key]
            if key2 in lookup:
                raise Exception("duplicate key '%s'" % str(key2))
            lookup[key2] = i
    else:
        for i in xrange(len(table)):
            key2 = table[i][key]
            if key2 in lookup:
                raise Exception("duplicate key '%s'" % str(key2))
            lookup[key2] = table[i]
    return lookup


def lookupTableMulti(table, * keys):
    lookup = {}
    key = keys[0]
    for i in xrange(len(table)):
        key2 = table[i][key]
        if key2 not in lookup:
            lookup[key2] = []
        lookup[key2].append(table[i])
    
    if len(keys) > 1:
        keys2 = keys[1:]
        for key, value in lookup.iteritems():
            lookup[key] = lookupTableMulti(value, * keys2)
    
    return lookup