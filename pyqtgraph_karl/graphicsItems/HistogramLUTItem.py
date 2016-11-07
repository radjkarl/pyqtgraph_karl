from pyqtgraph.graphicsItems.HistogramLUTItem import \
        ViewBox, QtGui, GraphicsWidget, LinearRegionItem, AxisItem,\
        PlotDataItem
    
from pyqtgraph_karl.graphicsItems.GradientEditorItem import GradientEditorItem
    
from pyqtgraph.graphicsItems.HistogramLUTItem import HistogramLUTItem as HH
from pyqtgraph.widgets import HistogramLUTWidget

class HistogramLUTItem(HH):
    
    
    #CHANGED
    def __init__(self, image=None, fillHistogram=True, 
                 #ADDED:
                 gradientPosition='left'):
        """
        If *image* (ImageItem) is provided, then the control will be automatically linked to the image and changes to the control will be immediately reflected in the image's appearance.
        By default, the histogram is rendered with a fill. For performance, set *fillHistogram* = False.
        #ADDED:
        gradientPosition -> 'left' OR 'right' / set to left to have a matplotlib-like layout
        """
        GraphicsWidget.__init__(self)
        self.lut = None
        self.imageItem = lambda: None  # fake a dead weakref
        
        self.layout = QtGui.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(0)
        self.vb = ViewBox(parent=self)
        self.vb.setMaximumWidth(152)
        self.vb.setMinimumWidth(45)
        self.vb.setMouseEnabled(x=False, y=True)
        self.gradient = GradientEditorItem()
        ##<<CHANGED
        o = 'left' if gradientPosition == 'right' else 'right'
        self.gradient.setOrientation(o)
        ##>>

        self.gradient.loadPreset('grey')
        self.region = LinearRegionItem([0, 1], LinearRegionItem.Horizontal)
        self.region.setZValue(1000)
        self.vb.addItem(self.region)
        ##<<CHANGED
        self.axis = AxisItem('right', linkView=self.vb, maxTickLength=-10, parent=self)
        self.layout.addItem(self.vb, 0, 1)
        pos = (0,2) if gradientPosition == 'right' else (2,0)
        self.layout.addItem(self.axis, 0, pos[0])
        self.layout.addItem(self.gradient, 0, pos[1])
        self.linkedHistograms = {}
        ##>>
        self.range = None
        self.gradient.setFlag(self.gradient.ItemStacksBehindParent)
        self.vb.setFlag(self.gradient.ItemStacksBehindParent)
        
        #self.grid = GridItem()
        #self.vb.addItem(self.grid)
        
        self.gradient.sigGradientChanged.connect(self.gradientChanged)
        self.region.sigRegionChanged.connect(self.regionChanging)
        self.region.sigRegionChangeFinished.connect(self.regionChanged)
        self.vb.sigRangeChanged.connect(self.viewRangeChanged)
        self.plot = PlotDataItem()
        self.plot.rotate(90)
        self.fillHistogram(fillHistogram)
            
        self.vb.addItem(self.plot)
        self.autoHistogramRange()
        
        if image is not None:
            self.setImageItem(image)


    #EXTENDED
    def paint(self, p, *args):
        if self.region.isVisible():
            HH.paint(self, p, *args)


    #ADDED
    def linkHistogram(self, slaveHistogram, connect=True):
        if connect:
            fn = lambda h, slave=slaveHistogram:slave.setLevels(*h.getLevels())
            self.linkedHistograms[id(slaveHistogram)] = fn
            self.sigLevelsChanged.connect(fn)
            self.sigLevelsChanged.emit(self)
            #self.vb.setYLink(slaveHistogram.vb)
        else:
            fn = self.linkedHistograms.get(id(slaveHistogram), None)
            if fn:
                self.sigLevelsChanged.disconnect(fn)


HistogramLUTWidget.HistogramLUTItem = HistogramLUTItem