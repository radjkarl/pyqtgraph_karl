

from fancytools.pystructure.fallbackPackage import fallbackPackage
from fancytools.pystructure.FallBack import FallBack
import pyqtgraph



#rebuilt structure 
from pyqtgraph_karl.imageview.ImageView import ImageView
from pyqtgraph_karl.graphicsItems.PlotItem.PlotItem import PlotItem
from pyqtgraph_karl.graphicsItems.AxisItem import AxisItem
from pyqtgraph_karl.graphicsItems.ViewBox.ViewBox import ViewBox
from pyqtgraph_karl.graphicsItems.GradientEditorItem import GradientEditorItem
from pyqtgraph_karl.graphicsItems.HistogramLUTItem import HistogramLUTItem
from pyqtgraph_karl.graphicsItems.LegendItem import LegendItem
from pyqtgraph_karl.imageview.ImageView import ImageView


fallbackPackage('pyqtgraph_karl', 'pyqtgraph')
FallBack(__name__, pyqtgraph)

# from parametertree.parameterTree import parameterTree


# 
# for item in dir(pyqtgraph):
#     print(item)

# 
# from pyqtgraph_karl import AxisItem



# getattr(object, name)