from pyqtgraph.graphicsItems.ViewBox.ViewBox import *
VV = ViewBox

class ViewBox(VV):
    #ADDED
    def getAspectRatio(self):
        '''return the current aspect ratio'''
        rect = self.rect()
        vr = self.viewRect()
        if rect.height() == 0 or vr.width() == 0 or vr.height() == 0:
            currentRatio = 1.0
        else:
            currentRatio = (rect.width()/float(rect.height())) / (vr.width()/vr.height())
        return currentRatio

    #MODIFIED
    def setAspectLocked(self, lock=True, ratio=1):
        """
        If the aspect ratio is locked, view scaling must always preserve the aspect ratio.
        By default, the ratio is set to 1; x and y both have the same scaling.
        This ratio can be overridden (xScale/yScale), or use None to lock in the current ratio.
        """
        
        if not lock:
            if self.state['aspectLocked'] == False:
                return
            self.state['aspectLocked'] = False
        else:
            ##<<REPLACED
            currentRatio = self.getAspectRatio()
            ##>>
            if ratio is None:
                ratio = currentRatio
            if self.state['aspectLocked'] == ratio: # nothing to change
                return
            self.state['aspectLocked'] = ratio
            if ratio != currentRatio:  ## If this would change the current range, do that now
                #self.setRange(0, self.state['viewRange'][0][0], self.state['viewRange'][0][1])
                self.updateViewRange()
        
        self.updateAutoRange()
        self.updateViewRange()
        self.sigStateChanged.emit(self)