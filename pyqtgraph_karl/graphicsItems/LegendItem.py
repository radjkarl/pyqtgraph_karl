from pyqtgraph.graphicsItems.LegendItem import *
from pyqtgraph.graphicsItems.LegendItem import LabelItem, ItemSample
from pyqtgraph import functions as fn

LL = LegendItem
del LegendItem




class LegendItem(LL):
    
    #APPENDED
    def __init__(self, size=None, offset=None, drawFrame=True):
        LL.__init__(self, size, offset)
        
        self.drawFrame = drawFrame
        self.columnCount = 1
        self.rowCount = 1
        self.curRow = 0


    #CHANGED
    def addItem(self, item, name):
        label = LabelItem(name)
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item)  
        ##<<CHANGED    
        self.items.append((sample, label))
        self._addItemToLayout(sample, label)
        ##>>
        self.updateSize()
        
    #ADDED
    def _addItemToLayout(self, sample, label):
        col = self.layout.columnCount()
        row = self.layout.rowCount()
        if row:
            row -= 1
        nCol = self.columnCount*2
        #FIRST ROW FULL
        if col == nCol:
            for col in range(0,nCol,2):
                #FIND RIGHT COLUMN
                if not self.layout.itemAt(row, col):
                    break
            if col+2 == nCol:
                #MAKE NEW ROW
                col = 0
                row += 1
        self.layout.addItem(sample, row, col)
        self.layout.addItem(label, row, col+1)
    
    #ADDED
    def setColumnCount(self, columnCount):
        '''
        change the orientation of all items of the legend 
        '''
        if columnCount != self.columnCount:
            self.columnCount = columnCount
            self.rowCount = int(len(self.items)/columnCount)
            for i in range(self.layout.count()-1,-1,-1):
                self.layout.removeAt(i)  #clear layout
            for sample, label in self.items:
                self._addItemToLayout(sample, label) 
            self.updateSize()
    
    #ADDED 
    def getLabel(self, plotItem):
        """
        return the labelItem inside the legend for a given plotItem
        the label-text can be changed via labenItem.setText
        """
        for i in self.items:
            if i[0].item == plotItem:
                return i[1]


    #REPLACED
    def updateSize(self):
        if self.size is not None:
            return   
        height = 0
        width = 0
        for row in range(self.layout.rowCount()):
            row_height = 0 
            col_witdh = 0
            for col in range(self.layout.columnCount()):
                item = self.layout.itemAt(row, col)
                if item:
                    col_witdh += item.width() + 3
                    row_height = max(row_height, item.height())
            width = max(width, col_witdh)
            height += row_height
        self.setGeometry(0, 0, width, height)


    #CHANGED
    def paint(self, p, *args):
        ##<<Changed
        if self.drawFrame:
            ##>>
            p.setPen(fn.mkPen(255,255,255,100))
            p.setBrush(fn.mkBrush(100,100,100,50))
            p.drawRect(self.boundingRect())

# 
# import pyqtgraph.graphicsItems.LegendItem as mod
# print (LegendItem)
# mod.LegendItem = LegendItem