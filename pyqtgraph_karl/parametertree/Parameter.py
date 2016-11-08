# from pyqtgraph.parametertree.Parameter import *
from pyqtgraph.parametertree.Parameter import Parameter as PP
from pyqtgraph.Qt import QtCore
# PP = Parameter



class Parameter(PP):
    """
    add new options to pyQtGraphs 'Parameter'-Class to be fully interactive
    and log all changes:
            * 'duplicatable' (see ParameterItem)
            * 'key' -> name or QKeySequence of the shortcut (see ParameterItem)
            * 'keyParent' -> QWidget where the key is active
            * 'highlight' -> True/False (coded in ParameterItem)
            * 'icon' -> 'path/to/icon' (see ParameterItem)
   
    new kwargs:
        =================            ===========================================
        movable                      Allow drag/and drop. See example XXX to more information
        sliding                      Allow change of position of parameters within the same 
                                     hierarchy level
        addToContextMenu             List of QMenu or QAction instances to add to the context 
                                     menu
        =================            ============================================

    """
    sigChildRemoved = QtCore.Signal(object, object, object)  ## self, child, index
    sigDuplicated = QtCore.Signal()
    sigRemoved = QtCore.Signal()
    #TODO: remove either sigChildRemoved or sigRemoved

    
#     def saveState(self, *args, **kwargs):
#         state = PP.saveState(self, *args, **kwargs)
# 
# #         for key, value in list(state.items()):
# #             #remove pointers to instances that cannot be restored
# #             #e.g. with entry 'addToContextMenu'
# #             if 'object at 0x' in value.__repr__():
# #                 state.pop(key)
# #         try: state.pop('addToContextMenu')
# #         except KeyError: pass
#         return state
    
    ##added duplicate feature
    def addChild(self, child, duplicate=False):
        return self.insertChild(len(self.childs), child, duplicate)


                                                            # ADDED duplicate
    def insertChild(self, pos, child, autoIncrementName=None, duplicate=False):
        """
        Insert a new child at pos.
        If pos is a Parameter, then insert at the position of that Parameter.
        If child is a dict, then a parameter is constructed using
        :func:`Parameter.create <pyqtgraph.parametertree.Parameter.create>`.
        
        By default, the child's 'autoIncrementName' option determines whether
        the name will be adjusted to avoid prior name collisions. This 
        behavior may be overridden by specifying the *autoIncrementName* 
        argument. This argument was added in version 0.9.9.
        """
        if isinstance(child, dict):
            child = Parameter.create(**child)
        
        name = child.name()
        if name in self.names and child is not self.names[name]:
            if autoIncrementName is True or (autoIncrementName is None and child.opts.get('autoIncrementName', False)):
                name = self.incrementName(name)
                child.setName(name)
            else:
                raise Exception("Already have child named %s" % str(name))
        if isinstance(pos, Parameter):
            pos = self.childs.index(pos)
            
        with self.treeChangeBlocker():
            ##<<CHANGED
            if child.parent() is not None and not duplicate:
            ##>>
                child.remove()
                
            self.names[name] = child
            self.childs.insert(pos, child)
            ##<<ADDED
            if not duplicate:
            ##>>
                child.parentChanged(self)
            self.sigChildAdded.emit(self, child, pos)
            child.sigTreeStateChanged.connect(self.treeStateChanged)
        return child


    def removeChild(self, child):
        """Remove a child parameter."""
        name = child.name()
        if name not in self.names or self.names[name] is not child:
            raise Exception("Parameter %s is not my child; can't remove." % str(child))
        del self.names[name]
        ##<<CHANGED/ADDED ind
        ind = self.childs.index(child)
        self.childs.pop(ind)
        child.parentChanged(None)
        self.sigChildRemoved.emit(self, child, ind)
        ##>>
        try:
            child.sigTreeStateChanged.disconnect(self.treeStateChanged)
        except (TypeError, RuntimeError):  ## already disconnected
            pass


    def slide(self, nPos):
        '''change the position within the same level +-nPos'''
        p = self.parent()
        if p:
            index = p.childs.index(self)
            self.moveChild(self, index+nPos)


    def moveChild(self, child, index_new):
        '''move self or a child to a given index position'''
        if child==self:
            p = self.parent()
        else:
            p = self
        if index_new < 0 or index_new > len(p.childs)-1:
            return
        p.opts['aboutToMove'] = True
        p.insertChild(index_new,child)
        p.opts['aboutToMove'] = False
        
    #ADDED
    def duplicate(self, recursive=True):
        p = Parameter.create(type=self.opts['type'], name='', value='')
        p.restoreState(self.saveState(), recursive=recursive)

        self.sigDuplicated.emit()
        return p
    
    #EXTENDED
    def remove(self):
        PP.remove(self)
        self.sigRemoved.emit()

    #EXTENDED
    def blockSignals(self, boolean):
        """add block/unblock of keyboard shortcut"""
        PP.blockSignals(self, boolean)
        try:
            item = self.items[0]
            if item.key:
                item.key.blockSignals(boolean)
        except:
            pass

    #ADDED
    def hasVisibleChilds(self):  # TODO: remove?
        for ch in self.children():
            if ch.opts['visible']:
                return True
        return False


    #ADDED
    def isVisible(self):
        if self.opts['visible']:
            p = self
            while True:
                p = p.parent()
                if not p:
                    return True
                if not p.opts['visible']:
                    break
        return False


    #ADDED
    def replaceWith(self, param):
        """replace this parameter with another"""
        i = self.parent().children().index(self)
        # TODO: transfer the children:
        p = self.parent()
        self.parent().removeChild(self)
        p.insertChild(i, param)
        self = param
    
    #ADDED
    def path(self):
        c = p = self.parent()
        l = self.name()
        while p:
            l = p.name() + ', ' + l
            c = p
            p = p.parent()
        return c, l
