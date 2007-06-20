"""
    
    Visualizations for Distance Matrices of molecular sequences

"""

# rasmus libs
from rasmus import util
from rasmus.bio import muscle
from rasmus.vis import genomebrowser

# summon libs
from summon.core import *
import summon
from summon import matrix
from summon import hud




class DistMatrixViewer (matrix.MatrixViewer):
    def __init__(self, distmat, seqs=None, 
                 colormap=None, 
                 rlabels=None, clabels=None, cutoff=-util.INF,
                 rperm=None, cperm=None, rpart=None, cpart=None,
                 style="quads",
                 **options):
        
        # setup matrix
        if isinstance(distmat, list):
            # create sparse matrix from dense matrix
            mat = Matrix()
            mat.from2DList(data, cutoff=cutoff)
        else:
            # already sparse
            mat = distmat
        
        if rlabels != None: mat.rowlabels = rlabels
        if clabels != None: mat.collabels = clabels
        if rperm != None:   mat.rperm = rperm
        if cperm != None:   mat.cperm = cperm
        if rpart != None:   mat.rpart = rpart
        if cpart != None:   mat.cpart = cpart
        mat.setup()
        
        if colormap != None:
            mat.colormap = colormap
        
        matrix.MatrixViewer.__init__(self, mat, onClick=self.onClick,
                                     style=style, drawzeros=True,
                                     **options)
        
        
        # distmatrix specific initialization
        self.seqs = seqs
        self.selgenes = set()
        self.aln = None


    def show(self):
        matrix.MatrixViewer.show(self)
        
        # build sidebar menu
        self.bar = hud.SideBar(self.win, width=150)
        self.bar.addItem(hud.MenuItem("align gene (a)", self.showAlign))
        self.bar.addItem(hud.MenuItem("clear genes (d)", self.clearSelection))
        self.bar.addItem(hud.MenuItem("show genes (s)", self.showSelection))

        # register key bindings
        self.win.reset_binding(input_key("a"), self.showAlign)
        self.win.reset_binding(input_key("d"), self.clearSelection)        
        self.win.reset_binding(input_key("s"), self.showSelection)
    
    
    def onClick(self, row, col, i, j, val):
        self.selgenes.add(row)
        self.selgenes.add(col)

        print row, col, i, j, val

    def clearSelection(self):
        self.selgenes.clear()
        print "clear selection"


    def showSelection(self):
        # sort genes by order in matrix
        genes = list(self.selgenes)
        lookup = util.list2lookup(self.mat.rowlabels)
        genes.sort(key=lambda x: lookup[x])
        
        print
        print "selected genes:"
        for i, gene in enumerate(genes):
            print "%3d %s" % (i+1, gene)
    
    
    def showAlign(self):
        if self.seqs == None:
            print "cannot build alignment: no sequences are loaded"
            return
    
        genes = list(self.selgenes)
        lookup = util.list2lookup(self.mat.rowlabels)
           
        self.aln = muscle.muscle(self.seqs.get(genes))
        self.aln.names.sort(key=lambda x: lookup[x])
        
        self.visaln = genomebrowser.showAlign(self.aln)
        self.visaln.win.set_name("alignment")
