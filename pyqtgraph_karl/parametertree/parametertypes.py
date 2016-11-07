# from pyqtgraph.Qt import QtGui
from pyqtgraph.parametertree.parameterTypes import SimpleParameter
from pyqtgraph.parametertree.parameterTypes import WidgetParameterItem as WPI
from pyqtgraph.parametertree.parameterTypes import TextParameterItem as TPI
from pyqtgraph.parametertree.parameterTypes import ActionParameterItem as API
from pyqtgraph.parametertree.parameterTypes import registerParameterType, \
        QtGui, QtCore, ListParameter, ListParameterItem, TextParameter, ActionParameter,\
        GroupParameterItem

from pyqtgraph.parametertree import parameterTypes as mod


from .Parameter import Parameter
from .ParameterItem import ParameterItem

mod.ParameterItem = ParameterItem

WPI.__bases__ = (ParameterItem,)
API.__bases__ = (ParameterItem,)
GroupParameterItem.__bases__ = (ParameterItem,)


registerParameterType('slider', SimpleParameter, override=True)


class WidgetParameterItem(WPI):
    """
    ParameterTree item with:
    
    * label in second column for displaying value
    * simple widget for editing value (displayed instead of label when item is selected)
    * button that resets value to default
    
    ==========================  =============================================================
    **Registered Types:**
    int                         Displays a :class:`SpinBox <pyqtgraph.SpinBox>` in integer
                                mode.
    float                       Displays a :class:`SpinBox <pyqtgraph.SpinBox>`.
    bool                        Displays a QCheckBox
    str                         Displays a QLineEdit
    color                       Displays a :class:`ColorButton <pyqtgraph.ColorButton>`
    colormap                    Displays a :class:`GradientWidget <pyqtgraph.GradientWidget>`
    ##<<ADDED
    slider                      Displays a :class:`SliderWidget <pyqtgraph.SliderWidget>`.
    ##>>
    ==========================  =============================================================
    
    This class can be subclassed by overriding makeWidget() to provide a custom widget.
    """
    def __init__(self, *args, **kwargs ):
        WPI.__init__(self, *args, **kwargs)
        opts = self.param.opts
        
        #hide defaults-button if param is readonly:
        if opts.get('readonly', False):
            self.defaultBtn.hide()        
        
        if opts.get('sliding', False):
            #add slide up/down button to the parameterItem:
            btnlayout = QtGui.QVBoxLayout() 
            slideBtnUp = QtGui.QPushButton()
            slideBtnDown = QtGui.QPushButton()
            
            for btn in (slideBtnUp, slideBtnDown):
                btn.setFixedWidth(10)
                btn.setFixedHeight(10)
                btnlayout.addWidget(btn)
            
            slideBtnUp.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowUp))
            slideBtnDown.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
            slideBtnUp.clicked.connect(lambda: self.param.slide(-1))
            slideBtnDown.clicked.connect(lambda: self.param.slide(1))
            
            self.layoutWidget.layout().addLayout(btnlayout)
        
        
        
#     def valueChanged(self, param, val, force=False):
#         print (self.widget, self.widget.sigChanged)
#         print (param, val)
#         WPI.valueChanged(self, param, val, force=force) 

  
    #EXTEBDED    
    def makeWidget(self):  
        try:
            w = WPI.makeWidget(self)
        
        except Exception as ex:
            opts = self.param.opts
            t = opts['type']
            if t == 'slider':
                from ..widgets.SliderWidget import SliderWidget
                w = SliderWidget()
                w.sigChanged = w.sigValueChanged
                w.sigChanging = w.sigValueChanged
                l = opts.get('limits')
                if l:
                    w.setRange(*l)
                v = opts.get('value')
                if l:
                    w.setValue(v)
                self.hideWidget = False
            else:
                raise ex
        return w


    #TODO: check still needed?
    def limitsChanged(self, param, limits):
        # set up forward / reverse mappings for name:value
        
        if len(limits) == 0:
            limits = ['']  ## Can never have an empty list--there is always at least a singhe blank item.
        
        self.forward, self.reverse = ListParameter.mapping(limits)
        try:
            self.widget.blockSignals(True)
            val = self.targetValue  #asUnicode(self.widget.currentText())
            ##<ADDED
            if val != None:
                # because self.setValue wont be executed every time
                # self.targetValue can sometimes be wrong
                val = param.value()
            ##>>
            self.widget.clear()
            for k in self.forward:
                self.widget.addItem(k)
                if k == val:
                    self.widget.setCurrentIndex(self.widget.count()-1)
                    self.updateDisplayLabel()
        finally:
            self.widget.blockSignals(False)
            

SimpleParameter.itemClass = WidgetParameterItem
TPI.__bases__ = (WidgetParameterItem,)

 

#TODO: still needed?
class ActionParameterItem(API):
    def nameChanged(self, name):
        #Pass method, otherwise name is additionally set in tableView
        pass
ActionParameter.itemClass = ActionParameterItem


class TextParameterItem(TPI):
    def selected(self, value):
        #this dummymethod prevent the following error:
            #Traceback (most recent call last):
            #File "/usr/lib/pymodules/python2.7/pyqtgraph/parametertree/ParameterTree.py", line 107, in selectionChanged
            #self.lastSel.selected(False)
            #AttributeError: 'QTreeWidgetItem' object has no attribute 'selected'
        pass
#TextParameter.itemClass = TextParameterItem



class EmptyParameter(Parameter):
    """
    """
    itemClass = ParameterItem
registerParameterType('empty', EmptyParameter, override=True)


class _DummySignal:
    @staticmethod
    def disconnect(x): pass
    @staticmethod
    def connect(x): pass

class MenuParameterItem(WidgetParameterItem):
    """
    Group parameters are used mainly as a generic parent item that holds (and groups!) a set
    of child parameters. It also provides a simple mechanism for displaying a button or combo
    that can be used to add new parameters to the group.
    """

    def __init__(self, param, depth):

        WidgetParameterItem.__init__(self, param, depth)
        self.hideWidget = False

    def makeWidget(self):
        v = self.param.opts.get(
            'value', self.param.opts.get(
                'limits', [''])[0])
        w = QtGui.QMenuBar()
        w.menu = w.addMenu(v)
        w.sigChanged = _DummySignal
        w.value = lambda: ''
        w.setValue = lambda x:None
        w.menu.aboutToShow.connect(
            lambda menu=w.menu: self.param.aboutToShow.emit(menu))
        return w


class MenuParameter(Parameter):
    itemClass = MenuParameterItem
    aboutToShow = QtCore.Signal(object)  # qmenu

    def value(self):
        return self.items.keyrefs()[0]().widget.menu.title()
    # TODO: doesnt work
#     def setValue(self, val):
#         self.items[xxx].widget.setTitle(val)

registerParameterType('menu', MenuParameter, override=True)


class ResetListParameterItem(ListParameterItem):
    """
    a list-Parameter that always returning to the first item
    """

    def __init__(self, param, depth):
        super(ResetListParameterItem, self).__init__(param, depth)
        # the resetList will reset automatically - there is no need for a
        # default button
        self.defaultBtn.hide()

    def valueChanged(self, *args, **kwargs):
        self.widget.setCurrentIndex(0)
        self.targetValue = self.widget.itemText(0)  # .currentText()

    def limitsChanged(self, param, limits):
        self.widget.setCurrentIndex(0)
        super(ResetListParameterItem, self).limitsChanged(param, limits)


class ResetListParameter(ListParameter):
    itemClass = ResetListParameterItem
registerParameterType('resetList', ResetListParameter, override=True)


# registerParameterType('empty', EmptyParameter, override=True)
