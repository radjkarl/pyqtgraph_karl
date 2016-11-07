from pyqtgraph.opengl.items.GLGridItem import *
GG = GLGridItem

#TODO: push these changes into pyqtgraph

class GLGridItem(GG):

    def __init__(self, size=None, color=None, antialias=True, glOptions='translucent'):
        GLGraphicsItem.__init__(self)
        self.setGLOptions(glOptions)
        self.antialias = antialias
        ##<<ADDED
        self.setColor(color)   
        ##>>   
        if size is None:
            size = QtGui.QVector3D(20,20,1)
        self.setSize(size=size)
        self.setSpacing(1, 1, 1)

    def setColor(self, color):
        """
        set the color of the Grid
        'color' can be any value accepted by QColor
        """
        if color == None:
            self.color = (1, 1, 1, .3)
        else:
            self.color = QtGui.QColor(color).getRgbF()


    def paint(self):
        self.setupGLState()
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        xs,ys,zs = self.spacing()
        xvals = np.arange(-x/2., x/2. + xs*0.001, xs) 
        yvals = np.arange(-y/2., y/2. + ys*0.001, ys) 
        ##<<CHANGED
        glColor4f(*self.color)
        ##>>
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x,  yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        
        glEnd()
