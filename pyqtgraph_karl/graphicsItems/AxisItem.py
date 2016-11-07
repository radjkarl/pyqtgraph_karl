from pyqtgraph.graphicsItems.AxisItem import GraphicsWidget, QtGui, AxisItem, weakref, QtCore
AA = AxisItem

class AxisItem(AxisItem):
    sigLabelChanged = QtCore.Signal(object, object, object, object)#text, unit, prefix, args
    sigRangeChanged = QtCore.Signal(object, object)#mn, mx
    sigFontSizeChanged = QtCore.Signal(object) #fontSize
    
    #MODIFIED
    def __init__(self, orientation, pen=None, 
                     linkView=None, parent=None, maxTickLength=-5, showValues=True):
        GraphicsWidget.__init__(self, parent)
        self.label = QtGui.QGraphicsTextItem(self)
        self.picture = None
        ##<<CHANGED
        self.orientation = None
        self.setOrientation(orientation)
        ##>>
            
        self.style = {
            'tickTextOffset': [5, 2],  ## (horizontal, vertical) spacing between text and axis 
            'tickTextWidth': 30,  ## space reserved for tick text
            'tickTextHeight': 18, 
            'autoExpandTextSpace': True,  ## automatically expand text space if needed
            'tickFont': None,
            'stopAxisAtTick': (False, False),  ## whether axis is drawn to edge of box or to last tick 
            'textFillLimits': [  ## how much of the axis to fill up with tick text, maximally. 
                (0, 0.8),    ## never fill more than 80% of the axis
                (2, 0.6),    ## If we already have 2 ticks with text, fill no more than 60% of the axis
                (4, 0.4),    ## If we already have 4 ticks with text, fill no more than 40% of the axis
                (6, 0.2),    ## If we already have 6 ticks with text, fill no more than 20% of the axis
                ],
            'showValues': showValues,
            'tickLength': maxTickLength,
            'maxTickLevel': 2,
            'maxTextLevel': 2,
        }
        
        self.textWidth = 30  ## Keeps track of maximum width / height of tick text 
        self.textHeight = 18
        
        # If the user specifies a width / height, remember that setting
        # indefinitely.
        self.fixedWidth = None
        self.fixedHeight = None
        
        self.labelText = ''
        self.labelUnits = ''
        self.labelUnitPrefix=''
        self.labelStyle = {}
        self.logMode = False
        self.tickFont = None
        
        self._tickLevels = None  ## used to override the automatic ticking system with explicit ticks
        self._tickSpacing = None  # used to override default tickSpacing method
        self.scale = 1.0
        self.autoSIPrefix = True
        self.autoSIPrefixScale = 1.0
        
        self.setRange(0, 1)
        
        if pen is None:
            self.setPen()
        else:
            self.setPen(pen)
        
        self._linkedView = None
        if linkView is not None:
            self.linkToView(linkView)
        
        self.showLabel(False)
        
        self.grid = False


    #ADDED
    def setOrientation(self, orientation):
        """
        orientation = 'left', 'right', 'top', 'bottom'
        """
        if orientation != self.orientation:
            if orientation not in ['left', 'right', 'top', 'bottom']:
                raise Exception("Orientation argument must be one of 'left', 'right', 'top', or 'bottom'.")
            #rotate absolute allows to change orientation multiple times:
            if orientation in ['left', 'right']:
                self.label.setRotation(-90)
            else:
                self.label.setRotation(0) 
            self.orientation = orientation
            self.update()

    #ADDED
    def clone(self, orientation=None, **kwargs):
        """
        clone this axis. the new axis will behave like the origin. 
        """
        axis = self.copy(orientation, kwargs)
        self.sigLabelChanged.connect(axis.setLabel)
        self.sigRangeChanged.connect(axis.setRange)
        return axis
    
    #ADDED
    def copy(self, orientation=None, **kwargs):
        """
        Return a new axis sharing the same name and range (more attributes following...)
        """
        if orientation == None:
            orientation = self.orientation
        axis = AxisItem(orientation, **kwargs)
        if self.label.isVisible():
            axis.setLabel(self.labelText, self.labelUnits, self.labelUnitPrefix, **self.labelStyle)
        axis.setRange(*self.range)
        return axis
    
    #ADDED
    def setFontSize(self, ptSize):
        '''
        change the size of the label, ticks and tickValues proportional
        '''
        #change label size
        self.labelStyle['font-size'] = '%spt' %ptSize
        if self.isVisible():
            #only exec if visible, otherwise it would create empty space 
            #TODO: if exec when axis is not visible creates warning: 'QPainter::font: Painter not active'
            self.setLabel(self.labelText, self.labelUnits,**self.labelStyle)
            if not self.orientation in ['left', 'right']:
                txtoffs =  int(5.0/9*ptSize)
            else:
                txtoffs = int(2.0/9*ptSize)
            #change ticks sizes and tickValue distances
            self.setStyle(tickLength=-int(ptSize*0.7),
                          tickTextOffset=txtoffs,
                          tickTextWidth=int(30.0/9*ptSize),
                          tickTextHeight=int(18.0/9*ptSize),
                          )
        #change tickValue size
        if self.tickFont == None:
            tickFont = QtGui.QPainter().font()
            self.setTickFont(tickFont)
        self.tickFont.setPointSizeF(ptSize*0.9)
        self.sigFontSizeChanged.emit(ptSize)

    #EXTENDED
    def close(self):
        self.sigLabelChanged.disconnect()
        self.sigRangeChanged.disconnect()
        AA.close(self)

    #EXTENDED
    def setLabel(self, text=None, units=None, unitPrefix=None, **args):
        AA.setLabel(self, text=None, units=None, unitPrefix=None, **args)
        self.sigLabelChanged.emit(text, units, unitPrefix, args)
    
    #EXTENDED
    def setHeight(self, *args, **kwargs):
        self.setMinimumWidth(-1)#reset, if limited before...
        self.setMaximumWidth(-1) 
        AA.setHeight(self, *args, **kwargs)

    #EXTENDED
    def setWidth(self, *args, **kwargs):
        self.setMinimumHeight(-1)#reset, if limited before...
        self.setMaximumHeight(-1) 
        AA.setWidth(self, *args, **kwargs)
    
    #EXTENDED
    def setRange(self, mn, mx):   
        AA.setRange(self, mn, mx)
        self.sigRangeChanged.emit(mn,mx)

    #REPLACED
    def linkToView(self, view):
        """Link this axis to a ViewBox, causing its displayed range to match the visible range of the view."""
        oldView = self.linkedView()
        self._linkedView = weakref.ref(view)
        
        if oldView is not None:
            #orientation of axis in oldview unknown, so:
            try:
                oldView.sigYRangeChanged.disconnect(self.linkedViewChanged)
            except TypeError:
                oldView.sigXRangeChanged.disconnect(self.linkedViewChanged)
        
        if self.orientation in ['right', 'left']:
            view.sigYRangeChanged.connect(self.linkedViewChanged)
        else:
            view.sigXRangeChanged.connect(self.linkedViewChanged)
        
        if oldView is not None:
            oldView.sigResized.disconnect(self.linkedViewChanged)
        view.sigResized.connect(self.linkedViewChanged)