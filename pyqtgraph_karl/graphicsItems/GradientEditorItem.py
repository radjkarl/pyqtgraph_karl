from pyqtgraph.graphicsItems.GradientEditorItem import GradientEditorItem as GG

class GradientEditorItem(GG):
    
    #EXTENDED
    def __init__(self, *args, **kargs):
        GG.__init__(self, *args, **kargs)
        self.linkedGradients = {}
        
    #ADDED
    def showTicks(self, show=True):
        for tick in self.ticks.keys():
            if show:
                tick.show()
                orig = getattr(self, '_allowAdd_backup', None)
                if orig: 
                    self.allowAdd = orig
            else:
                self._allowAdd_backup = self.allowAdd
                self.allowAdd = False #block tick creation
                tick.hide()
    
    #EXTENDED     
    def saveState(self):
        state = GG.saveState(self)
        state['ticksVisible'] = next(iter(self.ticks)).isVisible()
        return state
    
    #EXTENDED
    def restoreState(self, state):
        GG.restoreState(self, state)
        self.showTicks( state.get('ticksVisible', next(iter(self.ticks)).isVisible()) )

    #ADDED
    def linkGradient(self, slaveGradient, connect=True):
        if connect:
            fn = lambda g, slave=slaveGradient:slave.restoreState(g.saveState())
            self.linkedGradients[id(slaveGradient)] = fn
            self.sigGradientChanged.connect(fn)
            self.sigGradientChanged.emit(self)
        else:
            fn = self.linkedGradients.get(id(slaveGradient), None)
            if fn:
                self.sigGradientChanged.disconnect(fn)