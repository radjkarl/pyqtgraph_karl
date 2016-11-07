from pyqtgraph.parametertree.ParameterItem import ParameterItem as PI
from pyqtgraph.Qt import QtGui, QtCore

class ParameterItem(PI):
    #EXTENDED
    def __init__(self, param, depth=0):
        PI.__init__(self, param, depth)
        
        menuitems = self.param.opts.get('addToContextMenu', [])
        for i in menuitems:
            if isinstance(i, QtGui.QMenu):
                self.contextMenu.addMenu(i)
            elif isinstance(i, QtGui.QAction):
                self.contextMenu.addAction(i)
            else:
                raise AttributeError('need either QMenu or QAction instances to add to the context menu')

        # SLIDING
        if param.opts.get('sliding', False):
            self.controls = QtGui.QWidget()
            btnlayout = QtGui.QVBoxLayout()
            btnlayout.setContentsMargins(0, 0, 0, 0)
            btnlayout.setSpacing(0)
            self.controls.setLayout(btnlayout)
            slideBtnUp = QtGui.QPushButton()
            slideBtnDown = QtGui.QPushButton()

            for btn in (slideBtnUp, slideBtnDown):
                btn.setFixedWidth(10)
                btn.setFixedHeight(10)
                btnlayout.addWidget(btn)

            slideBtnUp.setIcon(
                QtGui.QApplication.style().standardIcon(
                    QtGui.QStyle.SP_ArrowUp))
            slideBtnDown.setIcon(
                QtGui.QApplication.style().standardIcon(
                    QtGui.QStyle.SP_ArrowDown))
            slideBtnUp.clicked.connect(
                lambda: self.slideChild(-1))  # param.slide(-1))
            slideBtnDown.clicked.connect(
                lambda: self.slideChild(1))  # param.slide(1))

        param = self.param
        # DUPLICABILITY
        if param.opts.get('duplicatable', False):
            self.contextMenu.addAction(
                "Duplicate").triggered.connect(param.duplicate)
        if param.opts.get('type') == 'group':# or param.opts.get(
                #'highlight', False):
            self.updateDepth(depth)
        # ICON
        iconpath = param.opts.get('icon', False)
        if iconpath:
            #iconpath = os.path.join(os.path.dirname(nIOp.__file__), icon)
            i = QtGui.QIcon(iconpath)
            self.setIcon(0, i)
        # TOOLTIP
        # TODO: test
        tip = param.opts.get('tip', False)
        if tip:
            self.setToolTip(0, tip)
        # KEYBOARD SHORTCUT
        self.key = None
        self.setShortcut(param.opts.get('key'), param.opts.get('keyParent'))


    #MODIFIED
    def contextMenuEvent(self, ev):
        if (not self.param.opts.get('removable', False) 
            and not self.param.opts.get('renamable', False)
            ##<<ADDED
            and not self.param.opts.get('addToContextMenu', False)):
            ##>>
            return
        self.contextMenu.popup(ev.globalPos())

    #ADDED
    def setShortcut(self, key, parent):
        if key:
            k = QtGui.QShortcut(parent)
            if not isinstance(key, QtGui.QKeySequence):
                key = QtGui.QKeySequence(key)
            k.setKey(QtGui.QKeySequence(key))
            k.setContext(QtCore.Qt.ApplicationShortcut)
            try:
                # for ActionParameter
                k.activated.connect(self.param.activate)
            except AttributeError:
                # toggle
                k.activated.connect(
                    lambda: self.param.setValue(
                        not self.param.value()))
            self.key = k

    #ADDED
    def slideChild(self, nPos):
        c = self.treeWidget().currentItem()
        for n in range(self.childCount()):
            if c == self.child(n):
                c.param.slide(nPos)
                cnew = self.child(n + nPos)
                #TODO: c has no parent any more
                return self.treeWidget().setCurrentItem(cnew, 0)

    #EXTENDED
    def treeWidgetChanged(self):
        super(ParameterItem, self).treeWidgetChanged()
        
        if self.param.opts.get('sliding', False):
            t = self.treeWidget()
            i = t.itemWidget(self, 0)
            if i is None:
                t.setItemWidget(self, 0, self.controls)
                # move the name a bit
                # if self.text(0)
                # self._setTextSliding(0,self.text(0))
            else:
                # TODO: does this work??
                i.insertWidget(0, self.controls)
