from pyqtgraph.imageview.ImageView import ImageView as II
from pyqtgraph.imageview.ImageView import ptime, QtGui,QtCore
import numpy as np

#overwrite:
# from pyqtgraph_karl.graphicsItems.HistogramLUTItem import HistogramLUTItem as LL
# from pyqtgraph.imageview import ImageViewTemplate_pyqt
# ImageViewTemplate_pyqt.HistogramLUTWidget = LL
# print (LL)

class ImageView(II):
    #APPENDED    
    def __init__(self, *args, **kwargs):
        II.__init__(self, *args, **kwargs)
        self.opts = {'autoLevels':True, 
                     'autoRange':True, 
                     'autoHistogramRange':True, 
                     'discreteTimeLine':False}
                
    #APPENDED    
    def setImage(self, img, autoRange=None, autoLevels=None, **kwargs):
        if autoLevels == None:
            autoLevels = self.opts['autoLevels']
        if autoRange == None:
            autoRange = self.opts['autoRange']
        return II.setImage(self, img, autoRange=autoRange, 
                           autoLevels=autoLevels, **kwargs)

    #ADDED
    #TODO: is that method really needed?
    def setOpts(self, **opts):
        '''
        change defaults view options, like:
        autoRange = [True, False]
        autoLevels = [True, False]
        discreteTimeSteps = [True, False]
        '''
        self.opts.update(opts)

    #MODIFIED
    def play(self, rate):
        """Begin automatically stepping frames forward at the given rate (in fps).
        This can also be accessed by pressing the spacebar."""
        #print "play:", rate
        self.playRate = rate
        if rate == 0:
            self.playTimer.stop()
            return
            
        self.lastPlayTime = ptime.time()
        if not self.playTimer.isActive():
            ##<<CHANGED
            self.playTimer.start(abs(int(1000/rate)))#was .start(16) before
            ##>>

    #ADDED
    def setHistogramLabel(self, text=None, **kwargs):
        """
        Set the label text of the histogram axis similar to 
        :func:`AxisItem.setLabel() <pyqtgraph.AxisItem.setLabel>`
        """
        a = self.ui.histogram.axis
        a.setLabel(text, **kwargs)
        if text == '':
            a.showLabel(False)
        self.ui.histogram.setMinimumWidth(135)

    #ADDED
    def setHistogramPrintView(self, printView=True, showHistogram=False):
        '''
        transforms the histogram into a more common shape to export the image
        for some season this method doesn't work when called in LUTHistogram directly
        * show/hide histogram plot
        * resize area <- TODO: works with static sizes, changes this!
        if hide:
        * set histogramAxis to current range
        * disable mouseinteraction for histogramAxis
        '''
        h = self.ui.histogram
        if printView:
            #fit range to axis
                #because h.gradient doens't go to the border
                #we need to extent the current region to be in level
                #with the gradient
            r = h.region.getRegion()
            ysize = h.vb.boundingRect().height()
            yRangePerPx = (r[1]-r[0]) / ysize
            distGradient2VbBorder = 9
            y_offset = distGradient2VbBorder * yRangePerPx
            
            h.vb.setYRange(r[0]-y_offset,r[1]+y_offset, padding=0)
            if showHistogram:
                h.region.hide()   
            else:       
                h.vb.hide()
                h.vb.setMinimumWidth(0)
                h.setFixedWidth(95)
            h.vb.state['mouseEnabled'][1] = False
        else:   
            h.vb.setMinimumWidth(45)
            h.region.show()
            h.vb.show()
            h.setMinimumWidth(135)
            h.vb.state['mouseEnabled'][1] = True     
        h.gradient.showTicks(not printView)
        h.update()
        h.gradient.update() 
        
    #ADDED
    @property
    def nframes(self):
        return self.getProcessedImage().shape[0]

    #MODIFIED
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Space:
            if self.playRate == 0:
                ##<<CHANGED
                fps = (self.nframes-1) / (self.tVals[-1] - self.tVals[0])
                ##>>
                self.play(fps)
            else:
                ##<<CHANGED
                self.play(self.playRate)
                ##>>
            ev.accept()
        elif ev.key() == QtCore.Qt.Key_Home:
            self.setCurrentIndex(0)
            self.play(0)
            ev.accept()
        elif ev.key() == QtCore.Qt.Key_End:
            ##<<CHANGED
            self.setCurrentIndex(self.nframes-1)
            ##>>
            self.play(0)
            ev.accept()
        elif ev.key() in self.noRepeatKeys:
            ev.accept()
            if ev.isAutoRepeat():
                return
            self.keysPressed[ev.key()] = 1
            self.evalKeyState()
        else:
            QtGui.QWidget.keyPressEvent(self, ev)


    #REPLACED
    def setCurrentIndex(self, ind):
        ind = np.clip(ind, 0, self.nframes-1)
        time = self.tVals[ind]
        self.timeLine.setValue(time)
        

    #APPENDED
    def timeLineChanged(self):
        II.timeLineChanged(self)
        if self.opts['discreteTimeSteps']:
            self.timeLine.sigPositionChanged.disconnect(self.timeLineChanged)
            self.timeLine.setPos(self.currentIndex)
            self.timeLine.sigPositionChanged.connect(self.timeLineChanged)
        
            
    #APPENDED
    def updateImage(self, autoHistogramRange=None):
        if autoHistogramRange == None:
            autoHistogramRange = self.opts['autoHistogramRange']
        return II.updateImage(self, autoHistogramRange)
    
    
    #MODIFIED
    def timeIndex(self, slider):
        ## Return the time and frame index indicated by a slider
        if self.image is None:
            return (0,0)
        
        t = slider.value()
        
        xv = self.tVals
        if xv is None:
            ind = int(t)
        else:
            if len(xv) < 2:
                return (0,0)
            ##<<CHANGED
            #totTime = xv[-1] + (xv[-1]-xv[-2])
            inds = np.argwhere(xv <= t)
            ##>>
            if len(inds) < 1:
                return (0,t)
            ind = inds[-1,0]
        return ind, t
        