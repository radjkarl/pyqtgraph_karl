# from pyqtgraph import PlotWidget as PP
# from pyqtgraph.widgets import PlotWidget as cls
# 
# cls.PlotItem = 
# 
# class PlotWidget(PP):
#     def __init__(self, parent=None, background='default', **kargs):
#         PP
#         
#         
#         GraphicsView.__init__(self, parent, background=background)
#         self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#         self.enableMouse(False)
#         self.plotItem = PlotItem(**kargs)
#         self.setCentralItem(self.plotItem)
#         ## Explicitly wrap methods from plotItem
#         ## NOTE: If you change this list, update the documentation above as well.
#         for m in ['addItem', 'removeItem', 'autoRange', 'clear', 'setXRange', 
#                   'setYRange', 'setRange', 'setAspectLocked', 'setMouseEnabled', 
#                   'setXLink', 'setYLink', 'enableAutoRange', 'disableAutoRange', 
#                   'setLimits', 'register', 'unregister', 'viewRect']:
#             setattr(self, m, getattr(self.plotItem, m))
#         #QtCore.QObject.connect(self.plotItem, QtCore.SIGNAL('viewChanged'), self.viewChanged)
#         self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)
#     