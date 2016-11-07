from pyqtgraph.parametertree.ParameterTree import ParameterTree as PT

class ParameterTree(PT):
    #EXTENDED
    def __init__(self, parameter=None, showHeader=False,
                 showTop=False, animated=True):
        PT.__init__(self, showHeader=showHeader)
        
        #inform parameter when expanded or collapsed by user: 
        self.itemExpanded.connect(lambda item: 
                item.param.opts.__setitem__ ('expanded',True))
        self.itemCollapsed.connect(lambda item: 
                item.param.opts.__setitem__ ('expanded',False))

        self.setAnimated(animated)
        if parameter:
            self.setParameters(parameter, showTop)

    #ADDED
    def returnParameterOnKlick(self, activate, executeMethod=None):
        if activate:
            self.selectionChanged = self._doReturnParameterOnKlick
            self._execute_ReturnParam = executeMethod
        else:
            self.selectionChanged = super(ParameterTree, self).selectionChanged


    #ADDED
    def _doReturnParameterOnKlick(self, *args):
        sel = self.selectedItems()
        for item in sel:
            try:
                param = item.param
                if self._execute_ReturnParam:
                    self._execute_ReturnParam(param)
            except AttributeError:
                pass
        super(ParameterTree, self).selectionChanged(*args)