from ..Qt import QtCore, QtGui

from .DockDrop import *
from ..widgets.VerticalLabel import VerticalLabel
from ..python2_3 import asUnicode

from Container import TContainer

# import weakref

class Dock(QtGui.QWidget, DockDrop):
    
    sigStretchChanged = QtCore.Signal()
    sigMinimized = QtCore.Signal()
    sigRestored = QtCore.Signal()
    sigMaximized = QtCore.Signal()
    
    def __init__(self, name, area=None, size=(10, 10), widget=None, hideTitle=False, 
                 autoOrientation=True,
                 #TODO: general option whether Dock controls (min,max,close) or not: 
                 closable=False, minimizable=False, maximizable=False):
        QtGui.QWidget.__init__(self)
        DockDrop.__init__(self)
        self.area = area
        self.label = DockLabel(name, self, closable, minimizable, maximizable)
          
        if closable:
            self.label.sigCloseClicked.connect(self.close)
        if minimizable:
            self.label.sigMinClicked.connect(self.minimize)
            self.label.sigDeMinClicked.connect(self.deMinimize)
        if maximizable:
            self.label.sigMaxClicked.connect(self.maximize)
            self.label.sigDeMaxClicked.connect(self.deMaximize)

        self.labelHidden = False
        self.moveLabel = True  ## If false, the dock is no longer allowed to move the label.
        self.autoOrient = autoOrientation
        self.orientation = 'horizontal'
        #self.label.setAlignment(QtCore.Qt.AlignHCenter)
        self.topLayout = QtGui.QGridLayout()
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(0)
        self.setLayout(self.topLayout)
        self.topLayout.addWidget(self.label, 0, 1)
        self.widgetArea = QtGui.QWidget()
        self.topLayout.addWidget(self.widgetArea, 1, 1)
        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.widgetArea.setLayout(self.layout)
        self.widgetArea.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.widgets = []
        self.currentRow = 0
        #self.titlePos = 'top'
        self.raiseOverlay()
        self.hStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }"""
        self.vStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }"""
        self.nStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        Dock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""
        self.setAutoFillBackground(False)
        self.widgetArea.setStyleSheet(self.hStyle)
        
        self.setStretch(*size)
        
        if widget is not None:
            self.addWidget(widget)

        if hideTitle:
            self.hideTitleBar()


    def checkShowControls(self):
        '''
        decide whether to show/hide the min- and max-button in the title bar
        ''' 
        #hide dock.label.controls if only on dock is in area
        if len(self.area.docks) == 1:
            lastDock = self.area.docks.values()[0]
            lastDock.label.showControls(False)
        #show label.controls when second dock is added
        elif len(self.area.docks) == 2:
            for dock in self.area.docks.values():
                dock.label.showControls()

    def implements(self, name=None):
        if name is None:
            return ['dock']
        else:
            return name == 'dock'
        
    def setStretch(self, x=None, y=None):
        """
        Set the 'target' size for this Dock.
        The actual size will be determined by comparing this Dock's
        stretch value to the rest of the docks it shares space with.
        """
        #print "setStretch", self, x, y
        #self._stretch = (x, y)
        if x is None:
            x = 0
        if y is None:
            y = 0
        #policy = self.sizePolicy()
        #policy.setHorizontalStretch(x)
        #policy.setVerticalStretch(y)
        #self.setSizePolicy(policy)
        self._stretch = (x, y)
        self.sigStretchChanged.emit()
        #print "setStretch", self, x, y, self.stretch()
        
    def stretch(self):
        #policy = self.sizePolicy()
        #return policy.horizontalStretch(), policy.verticalStretch()
        return self._stretch
        
    #def stretch(self):
        #return self._stretch

    def hideTitleBar(self):
        """
        Hide the title bar for this Dock.
        This will prevent the Dock being moved by the user.
        """
        self.label.hide()
        self.labelHidden = True
        if 'center' in self.allowedAreas:
            self.allowedAreas.remove('center')
        self.updateStyle()
        
    def showTitleBar(self):
        """
        Show the title bar for this Dock.
        """
        self.label.show()
        self.labelHidden = False
        self.allowedAreas.add('center')
        self.updateStyle()
        
    def setOrientation(self, o='auto', force=False):
        """
        Sets the orientation of the title bar for this Dock.
        Must be one of 'auto', 'horizontal', or 'vertical'.
        By default ('auto'), the orientation is determined
        based on the aspect ratio of the Dock.
        """
        #print self.name(), "setOrientation", o, force
        if o == 'auto' and self.autoOrient:
            if self.container().type() == 'tab':
                o = 'horizontal'
            elif self.width() > self.height()*1.5:
                o = 'vertical'
            else:
                o = 'horizontal'
        if force or self.orientation != o:
            self.orientation = o
            self.label.setOrientation(o)
            self.updateStyle()
        
    def updateStyle(self):
        ## updates orientation and appearance of title bar
        #print self.name(), "update style:", self.orientation, self.moveLabel, self.label.isVisible()
        if self.labelHidden:
            self.widgetArea.setStyleSheet(self.nStyle)
        elif self.orientation == 'vertical':
            self.label.setOrientation('vertical')
            if self.moveLabel:
                #print self.name(), "reclaim label"
                self.topLayout.addWidget(self.label, 1, 0)
            self.widgetArea.setStyleSheet(self.vStyle)
        else:
            self.label.setOrientation('horizontal')
            if self.moveLabel:
                #print self.name(), "reclaim label"
                self.topLayout.addWidget(self.label, 0, 1)
            self.widgetArea.setStyleSheet(self.hStyle)

    def resizeEvent(self, ev):
        self.setOrientation()
        self.resizeOverlay(self.size())

    def name(self):
        return asUnicode(self.label.text())

    def container(self):
        return self._container

    def addWidget(self, widget, row=None, col=0, rowspan=1, colspan=1):
        """
        Add a new widget to the interior of this Dock.
        Each Dock uses a QGridLayout to arrange widgets within.
        """
        if row is None:
            row = self.currentRow
        self.currentRow = max(row+1, self.currentRow)
        self.widgets.append(widget)
        self.layout.addWidget(widget, row, col, rowspan, colspan)
        self.raiseOverlay()
        
        
    def startDrag(self):
        self.drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        #mime.setPlainText("asd")
        self.drag.setMimeData(mime)
        self.widgetArea.setStyleSheet(self.dragStyle)
        self.update()
        action = self.drag.exec_()
        self.updateStyle()
        
    def float(self):
        if self.label.minimized:
            self.label.minClicked()
        self.area.floatDock(self)
            
    def containerChanged(self, c):
        #print self.name(), "container changed"
        self._container = c
        if c.type() != 'tab':
            self.moveLabel = True
            self.label.setDim(False)
        else:
            self.moveLabel = False
            
        self.setOrientation(force=True)
        
    def raiseDock(self):
        """If this Dock is stacked underneath others, raise it to the top."""
        self.container().raiseDock(self)
        

    def close(self):
        """Remove this dock from the DockArea it lives inside."""
        if self.label.maximized:
            self.label.toggleMaximize()
        self.setParent(None)
        self.label.setParent(None)
        if self._container != self.area.topContainer:
            self._container.apoptose()
        self._container = None
        for key, value in self.area.docks.iteritems():
            #have to iterate because the dock.name() can be different now
            if value == self:
                self.area.docks.pop(key)
                break
        self.checkShowControls()


    def minimize(self):       
        try:
            #try to add dock to the minimized_container:
            self.area.minimized_container.insert(self)
            self.area.minimized_docks.append(self)
        except AttributeError:
            #there is no minimized-container -> create one
            m = self.area.minimized_container = TContainer(self.area)
            #add this container to the bottom of the area:
            self.area.layout.addWidget(m)
            #set container to minimim size
            m.setFixedHeight(self.label.size().height())
            #apoptose is not needed - this container is closed manually
            m.apoptose = lambda: 0
            #add the dock to the container:
            m.insert(self)
            self.area.minimized_docks = [self]
        #'minimize' via hiding its content:
        self.widgetArea.hide()
        self.sigMinimized.emit()
    
    
    def deMinimize(self):
        if not self.label.minimized:
            self.area.minimized_docks.remove(self)
            #remove dock to the top 
            self.area.moveDock(self, position='top', neighbor=None)
            #'maximize' via show its content
            self.widgetArea.show()
            if not self.area.minimized_docks:
                #if there are not other minimized docks: close the container
                self.area.minimized_container.close()
                del self.area.minimized_container
            self.sigRestored.emit()


    def maximize(self):
        if self.label.minimized:
            self.label.toggleMinimize()
        for dock in self.area.docks.values():
            if dock != self:
                dock.hide()
        self.area.maximized_dock = self


    def deMaximize(self):
        if self.label.minimized:
            self.label.toggleMinimize()
        for dock in self.area.docks.values():
            if dock != self and dock._container:#if not closed
                dock.show()
        self.area.maximized_dock = None


    def __repr__(self):
        return "<Dock %s %s>" % (self.name(), self.stretch())

    ## PySide bug: We need to explicitly redefine these methods
    ## or else drag/drop events will not be delivered.
    def dragEnterEvent(self, *args):
        DockDrop.dragEnterEvent(self, *args)

    def dragMoveEvent(self, *args):
        DockDrop.dragMoveEvent(self, *args)

    def dragLeaveEvent(self, *args):
        DockDrop.dragLeaveEvent(self, *args)

    def dropEvent(self, *args):
        dock = args[0].source() 
        #restore the source dock if it is minimized before the drop    
        if dock.label.minimized:
            dock.label.toggleMinimize()
        DockDrop.dropEvent(self, *args)



class DockLabel(VerticalLabel):
    
    sigClicked = QtCore.Signal(object, object)
    sigCloseClicked = QtCore.Signal()
    #TODO: change to sigMaxToggled and sigMinToggled to decrease number of signals to 2:
    sigMinClicked = QtCore.Signal()
    sigDeMinClicked = QtCore.Signal()
    sigMaxClicked = QtCore.Signal()
    sigDeMaxClicked = QtCore.Signal()

    
    def __init__(self, text, dock, 
                 showCloseButton, showMinimizeButton, showMaximizeButton):

        self.selected = False
        self.dim = False
        self.fixedWidth = False
        VerticalLabel.__init__(self, text, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        self.dock = dock
        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False
        self.minimized = False
        self.maximized = False

        self.minButton = None
        if showMinimizeButton:
            self.minButton = QtGui.QToolButton(self)
            self.minButton.clicked.connect(self.toggleMinimize)
            self.minButtonSetIcon()
            
        self.maxButton = None 
        if showMaximizeButton:
            self.maxButton = QtGui.QToolButton(self)
            self.maxButton.clicked.connect(self.toggleMaximize)
            self.maxButtonSetIcon()

        self.closeButton = None
        if showCloseButton:
            self.closeButton = QtGui.QToolButton(self)
            self.closeButton.clicked.connect(self.sigCloseClicked)
            self.closeButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))

    def showControls(self, show=True):
        if self.minButton:
            self.minButton.show() if show else self.minButton.hide()
        if self.maxButton:
            self.maxButton.show() if show else self.maxButton.hide()
        #if self.closeButton:
        #    self.closeButton.show() if show else self.closeButton.hide()

    def minButtonSetIcon(self):
        if self.minimized:
            self.minButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarNormalButton))
        else:   
            self.minButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarMinButton))

    def maxButtonSetIcon(self):
        if self.maximized:
            self.maxButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarNormalButton))
        else:   
            self.maxButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarMaxButton))



    def toggleMinimize(self):
        self.minimized = not self.minimized
        self.minButtonSetIcon()
        if self.minimized:
            self.sigMinClicked.emit()
        else:
            self.sigDeMinClicked.emit()


    def toggleMaximize(self):
        self.maximized = not self.maximized
        self.maxButtonSetIcon()
        if self.maximized:
            self.minButton.hide()
            self.sigMaxClicked.emit()
        else:
            self.minButton.show()
            self.sigDeMaxClicked.emit()


    def updateStyle(self):
        r = '3px'
        if self.selected:
            fg = '#fff'
            bg = '#44aa44'
            border = '#2f762f'
        elif self.dim:
            fg = '#aaa'
            bg = '#44a'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'
        
        if self.orientation == 'vertical':
            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)

    def setSelected(self, s):
        '''
        change label color when dock is selected
        '''
        if self.selected != s:
            self.selected = s
            self.updateStyle() 

    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()
    
    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()
        
    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()
            
    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            self.sigClicked.emit(self, ev)
        ev.accept()
        
    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()
            
    def resizeEvent (self, ev):
        if self.closeButton:
            if self.orientation == 'vertical':
                size = ev.size().width()
                pos = QtCore.QPoint(0, 0)
            else:
                size = ev.size().height()
                pos = QtCore.QPoint(ev.size().width() - size, 0)
            self.closeButton.setFixedSize(QtCore.QSize(size, size))
            self.closeButton.move(pos)
        if self.maxButton:
            if self.orientation == 'vertical':
                size = ev.size().width()
                pos = QtCore.QPoint(0, -4)
            else:
                size = ev.size().height()
                pos = QtCore.QPoint(ev.size().width() - 2*size, 0)
            self.maxButton.setFixedSize(QtCore.QSize(size, size))
            self.maxButton.move(pos)  
        if self.minButton:
            if self.orientation == 'vertical':
                size = ev.size().width()
                pos = QtCore.QPoint(0, -4)
            else:
                size = ev.size().height()
                pos = QtCore.QPoint(ev.size().width() - 3*size, 0)
            self.minButton.setFixedSize(QtCore.QSize(size, size))
            self.minButton.move(pos)           
        super(DockLabel,self).resizeEvent(ev)
