from pyqtgraph.exporters.ImageExporter import USE_PYSIDE, QtGui, ImageExporter
II = ImageExporter

class ImageExporter(II):
    #ADDED
    @staticmethod
    def getSupportedImageFormats():
        if USE_PYSIDE:
            filter = ["*."+str(f) for f in QtGui.QImageWriter.supportedImageFormats()]
        else:
            filter = ["*."+bytes(f).decode('utf-8') for f in QtGui.QImageWriter.supportedImageFormats()]
        preferred = ['*.png', '*.tif', '*.jpg']
        for p in preferred[::-1]:
            if p in filter:
                filter.remove(p)
                filter.insert(0, p) 
        return filter  
    
    #MODIFIED
    def export(self, fileName=None, toBytes=False, copy=False):
        if fileName is None and not toBytes and not copy:
            ##<<REPLACED
            filter = self.getSupportedImageFormats()
            ##>>
            self.fileSaveDialog(filter=filter)
            return