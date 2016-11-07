from pyqtgraph.graphicsItems.PlotItem.PlotItem import QtGui,ButtonItem,\
    pixmaps, ViewBox, AxisItem, LabelItem, os, WidgetGroup, \
    weakref, Ui_Form, GraphicsWidget
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem as PP
from pyqtgraph.widgets import PlotWidget as PlotWidgetCls
from pyqtgraph_karl.graphicsItems.LegendItem import LegendItem

try:
    basestring
except NameError:
    basestring = str    




class PlotItem(PP):
    #MODIFIED
    def __init__(self, parent=None, name=None, labels=None, title=None, 
                 viewBox=None, axisItems=None, enableMenu=True, **kargs):
        GraphicsWidget.__init__(self, parent)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        ## Set up control buttons
        path = os.path.dirname(__file__)
        #self.autoImageFile = os.path.join(path, 'auto.png')
        #self.lockImageFile = os.path.join(path, 'lock.png')
        self.autoBtn = ButtonItem(pixmaps.getPixmap('auto'), 14, self)
        self.autoBtn.mode = 'auto'
        self.autoBtn.clicked.connect(self.autoBtnClicked)
        #self.autoBtn.hide()
        self.buttonsHidden = False ## whether the user has requested buttons to be hidden
        self.mouseHovering = False
        
        self.layout = QtGui.QGraphicsGridLayout()
        self.layout.setContentsMargins(1,1,1,1)
        self.setLayout(self.layout)
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        
        if viewBox is None:
            viewBox = ViewBox(parent=self)
        self.vb = viewBox
        self.vb.sigStateChanged.connect(self.viewStateChanged)
        self.setMenuEnabled(enableMenu, enableMenu) ## en/disable plotitem and viewbox menus
        
        if name is not None:
            self.vb.register(name)
        self.vb.sigRangeChanged.connect(self.sigRangeChanged)
        self.vb.sigXRangeChanged.connect(self.sigXRangeChanged)
        self.vb.sigYRangeChanged.connect(self.sigYRangeChanged)
        
        self.layout.addItem(self.vb, 2, 1)
        self.alpha = 1.0
        self.autoAlpha = True
        self.spectrumMode = False
        
        self.legend = None
        ##<<REPLACED
        self.axes = {}
        self.setAxes(axisItems)
        ##>>
        self.titleLabel = LabelItem('', size='11pt', parent=self)
        self.layout.addItem(self.titleLabel, 0, 1)
        self.setTitle(None)  ## hide
        
        
        for i in range(4):
            self.layout.setRowPreferredHeight(i, 0)
            self.layout.setRowMinimumHeight(i, 0)
            self.layout.setRowSpacing(i, 0)
            self.layout.setRowStretchFactor(i, 1)
            
        for i in range(3):
            self.layout.setColumnPreferredWidth(i, 0)
            self.layout.setColumnMinimumWidth(i, 0)
            self.layout.setColumnSpacing(i, 0)
            self.layout.setColumnStretchFactor(i, 1)
        self.layout.setRowStretchFactor(2, 100)
        self.layout.setColumnStretchFactor(1, 100)
        

        self.items = []
        self.curves = []
        self.itemMeta = weakref.WeakKeyDictionary()
        self.dataItems = []
        self.paramList = {}
        self.avgCurves = {}
        
        ### Set up context menu
        
        w = QtGui.QWidget()
        self.ctrl = c = Ui_Form()
        c.setupUi(w)
        dv = QtGui.QDoubleValidator(self)
        
        menuItems = [
            ('Transforms', c.transformGroup),
            ('Downsample', c.decimateGroup),
            ('Average', c.averageGroup),
            ('Alpha', c.alphaGroup),
            ('Grid', c.gridGroup),
            ('Points', c.pointsGroup),
        ]
        
        
        self.ctrlMenu = QtGui.QMenu()
        
        self.ctrlMenu.setTitle('Plot Options')
        self.subMenus = []
        for name, grp in menuItems:
            sm = QtGui.QMenu(name)
            act = QtGui.QWidgetAction(self)
            act.setDefaultWidget(grp)
            sm.addAction(act)
            self.subMenus.append(sm)
            self.ctrlMenu.addMenu(sm)
        
        self.stateGroup = WidgetGroup()
        for name, w in menuItems:
            self.stateGroup.autoAdd(w)
        
        self.fileDialog = None
        
        c.alphaGroup.toggled.connect(self.updateAlpha)
        c.alphaSlider.valueChanged.connect(self.updateAlpha)
        c.autoAlphaCheck.toggled.connect(self.updateAlpha)

        c.xGridCheck.toggled.connect(self.updateGrid)
        c.yGridCheck.toggled.connect(self.updateGrid)
        c.gridAlphaSlider.valueChanged.connect(self.updateGrid)

        c.fftCheck.toggled.connect(self.updateSpectrumMode)
        c.logXCheck.toggled.connect(self.updateLogMode)
        c.logYCheck.toggled.connect(self.updateLogMode)

        c.downsampleSpin.valueChanged.connect(self.updateDownsampling)
        c.downsampleCheck.toggled.connect(self.updateDownsampling)
        c.autoDownsampleCheck.toggled.connect(self.updateDownsampling)
        c.subsampleRadio.toggled.connect(self.updateDownsampling)
        c.meanRadio.toggled.connect(self.updateDownsampling)
        c.clipToViewCheck.toggled.connect(self.updateDownsampling)

        self.ctrl.avgParamList.itemClicked.connect(self.avgParamListClicked)
        self.ctrl.averageGroup.toggled.connect(self.avgToggled)
        
        self.ctrl.maxTracesCheck.toggled.connect(self.updateDecimation)
        self.ctrl.maxTracesSpin.valueChanged.connect(self.updateDecimation)
        ##<<COMMENTED
#         self.hideAxis('right')
#         self.hideAxis('top')
#         self.showAxis('left')
#         self.showAxis('bottom')
        ##>>
        
        if labels is None:
            labels = {}
        for label in list(self.axes.keys()):
            if label in kargs:
                labels[label] = kargs[label]
                del kargs[label]
        for k in labels:
            if isinstance(labels[k], basestring):
                labels[k] = (labels[k],)
            self.setLabel(k, *labels[k])
                
        if title is not None:
            self.setTitle(title)
        
        if len(kargs) > 0:
            self.plot(**kargs)


    #ADDED
    def setAxes(self, axisItems):
        """
        Create and place axis items
        For valid values for axisItems see __init__
        """
        if axisItems is None:
            axisItems = {}
        self.axes = {}
        for k, pos in (('top', (1,1)), ('bottom', (3,1)), ('left', (2,0)), ('right', (2,2))):
            axis = axisItems.get(k, None)
            if axis:
                axis.setOrientation(k)
            else:
                axis = AxisItem(orientation=k)
            axis.linkToView(self.vb)
            self.axes[k] = {'item': axis, 'pos': pos}
            self.layout.addItem(axis, *pos)
            axis.setZValue(-1000)
            axis.setFlag(axis.ItemNegativeZStacksBehindParent)
            
        self.hideAxis('right')
        self.hideAxis('top')
        self.showAxis('left')
        self.showAxis('bottom')


    #SAME ONLY TO LOAD MODIFIED LEGENDITEM
    def addLegend(self, size=None, offset=(30, 30)):
        """
        Create a new LegendItem and anchor it over the internal ViewBox.
        Plots will be automatically displayed in the legend if they
        are created with the 'name' argument.
        """
        self.legend = LegendItem(size, offset)
        self.legend.setParentItem(self.vb)
        return self.legend

PlotWidgetCls.PlotItem = PlotItem
