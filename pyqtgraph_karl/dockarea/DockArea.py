from pyqtgraph.dockarea import DockArea as cls
from pyqtgraph.dockarea.DockArea import DockArea as DD
from pyqtgraph.dockarea.Container import Container

from pyqtgraph_karl.dockarea import Dock

cls.Dock = Dock


class DockArea(DD):
    
    #EXTENDED
    def __init__(self, max_docks_xy=(), **kwargs):
        '''
        ============== =================================================================
        **Arguments:**
        max_docks_xy   len2-tuple like (2,2) or (3,4)
                       if Docks are added with DockArea.addDock without specified
                       arguments 'position' and 'relativeTo' docks are placed like:
                       e.g. max_docks_xy=(2,2): 
                       [1] ->  [1]  ->  [1,2]  ->  [1,3]
                               [2]      [3  ]      [2,4]
                       all following Docks are tabbed in [4] 
        ============== =================================================================
         
        '''
        DD.__init__(self, **kwargs)
        self.max_docks_xy = max_docks_xy

    #EXTENDED
    def addDock(self, dock=None, position=None, relativeTo=None, **kwds):
        ##<<ADDED
        (position, relativeTo) = self._findGridPosition(position, relativeTo)
        ##>>
        dock = DD.addDock(self, dock, position, relativeTo)
        
#         if dock is None:
#             dock = Dock(**kwds)
#         
#         ## Determine the container to insert this dock into.
#         ## If there is no neighbor, then the container is the top.
#         if relativeTo is None or relativeTo is self:
#             if self.topContainer is None:
#                 container = self
#                 neighbor = None
#             else:
#                 container = self.topContainer
#                 neighbor = None
#         else:
#             if isinstance(relativeTo, str):
#                 relativeTo = self.docks[relativeTo]
#             container = self.getContainer(relativeTo)
#             neighbor = relativeTo
#         
#         ## what container type do we need?
#         neededContainer = {
#             'bottom': 'vertical',
#             'top': 'vertical',
#             'left': 'horizontal',
#             'right': 'horizontal',
#             'above': 'tab',
#             'below': 'tab'
#         }[position]
#         
#         ## Can't insert new containers into a tab container; insert outside instead.
#         if neededContainer != container.type() and container.type() == 'tab':
#             neighbor = container
#             container = container.container()
#             
#         ## Decide if the container we have is suitable.
#         ## If not, insert a new container inside.
#         if neededContainer != container.type():
#             if neighbor is None:
#                 container = self.addContainer(neededContainer, self.topContainer)
#             else:
#                 container = self.addContainer(neededContainer, neighbor)
#             
#         ## Insert the new dock before/after its neighbor
#         insertPos = {
#             'bottom': 'after',
#             'top': 'before',
#             'left': 'before',
#             'right': 'after',
#             'above': 'before',
#             'below': 'after'
#         }[position]
#         #print "request insert", dock, insertPos, neighbor
#         old = dock.container()
#         container.insert(dock, insertPos, neighbor)
#         dock.area = self
#         self.docks[dock.name()] = dock
#         if old is not None:
#             old.apoptose()
        
        ##<<ADDED
        dock.checkShowControls()
        #adding a new dock means to restore a ramaining mazmized dock:
        maxDock = getattr(self, 'maximized_dock', None) 
        if maxDock:
            maxDock.label.toggleMaximize()
        ##>>
        return dock

    #ADDED
    def _findGridPosition(self, position, relativeTo):
        '''
        place added Docks if 'position' and 'relativeTo' are unspecified
        see __init__-doc for more information
        '''        
        if ( (position == None and relativeTo == None) #position in DockArea not specified
            and (self.max_docks_xy  and len(self.max_docks_xy) == 2) # max grid number is defined
            and self.topContainer): # at least one Dock is already there 
            
            y = self.topContainer.count()
            if y == self.max_docks_xy[1]:
                #max grid number of docks in y direction is reached
                found_space = False
                for iy in range(y):
                    c = self.topContainer.widget(iy)
                    is_container = isinstance(c,Container)
                    #max number of docks in x direction not reached yet: add dock there
                    if not is_container or c.count() < self.max_docks_xy[0]:
                        position = 'right'
                        found_space = True
                        break
                # every space is used: add dock below the last dock down-right
                if not found_space:
                    position = 'below'
                w = c
                if is_container:
                    #get widget from container
                    w = c.widget(c.count()-1)
                    if isinstance(w,Container):
                        # last container (down,right) is TContainer, not a Dock:
                        # take first widget, because docks can only moved relative to docks and not containers
                        w = w.widget(w.count()-1)
                relativeTo = w 
        if position == None:
            position = 'bottom'
        return position, relativeTo


