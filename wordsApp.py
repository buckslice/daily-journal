import sys
from PyQt5 import QtGui, QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        self.setWindowTitle("Mary's Journals")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(600,600)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')

        quitAction = QtWidgets.QAction('Save and Quit', self)
        quitAction.setShortcut('Ctrl+W') # Q wont work for some reason?
        quitAction.triggered.connect(self.closeApp)
        fileMenu.addAction(quitAction)
        

        fontAction = QtWidgets.QAction('Font', self)
        fontAction.triggered.connect(self.openFontWindow)
        menuBar.addAction(fontAction)
        

        self.tabs = QtWidgets.QTabWidget()
        self.mainLayout.addWidget(self.tabs)

        # JOURNAL ----------------------------------------------------
        self.jtab = QtWidgets.QWidget()
        self.tabs.addTab(self.jtab, "Journal")
        jlayout = QtWidgets.QVBoxLayout()
        self.testButton = QtWidgets.QPushButton('Test Button')
        jlayout.addWidget(self.testButton)

        self.editor = MyPlainTextEdit()
        #self.editor.setTabStopWidth(16)
        jlayout.addWidget(self.editor)

        # dark mode test
        #vp = self.editor.viewport()
        #p = vp.palette()
        #p.setColor(vp.backgroundRole(), QtGui.QColor(0,0,0))
        #p.setColor(vp.foregroundRole(), QtGui.QColor(200,200,200))
        #vp.setPalette(p)

        sansFont = QtGui.QFont("Helvetica", 14)
        self.editor.setFont(sansFont)

        self.jtab.setLayout(jlayout)

        # have program save all settings in config file!
        # need date thing
        # one journal per day, open and close by date (QCalendar!!!)
        # make toolbar
            # have dark mode option
            # font size
            # have font select dropdown
            # file save and open by date
            # spellcheck ? https://stackoverflow.com/questions/8722061/pyqt-how-to-turn-on-off-spellchecking

        # ANALYSIS ---------------------------------------------------
        self.atab = QtWidgets.QWidget()
        self.tabs.addTab(self.atab, "Analysis")

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtWidgets.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        alayout = QtWidgets.QVBoxLayout()
        alayout.addWidget(self.toolbar)
        alayout.addWidget(self.canvas)
        alayout.addWidget(self.button)
        self.atab.setLayout(alayout)


    def closeApp(self):
        self.close() # so close event is triggered

    def openFontWindow(self):
        font,valid = QtWidgets.QFontDialog.getFont()
        if valid:
            self.editor.setFont(font)

    def closeEvent(self, e):
        print('goodbye!!!')
        # save config options here to file

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()

class MyPlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, *args):
        QtWidgets.QPlainTextEdit.__init__(self, *args)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText('    ')
            event.accept()
        else:
            QtWidgets.QPlainTextEdit.keyPressEvent(self, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()
    main.plot()

    sys.exit(app.exec_())