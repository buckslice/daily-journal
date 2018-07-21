import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random
import functools

configPath = 'config.txt'

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.loadConfig()

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QtWidgets.QVBoxLayout(self.centralWidget)

        self.setWindowTitle("Mary's Journals")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(600,600)

        # setup menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')

        self.toolBar = QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        quitAction = QtWidgets.QAction('Save and Quit', self)
        quitAction.setShortcut('Ctrl+W') # Q wont work for some reason?
        quitAction.triggered.connect(self.closeApp)
        fileMenu.addAction(quitAction)

        journalAction = QtWidgets.QAction('Journal', self)
        journalAction.triggered.connect(self.openJournal)
        menuBar.addAction(journalAction)

        analysisAction = QtWidgets.QAction('Analysis', self)
        analysisAction.triggered.connect(self.openAnalysis)
        menuBar.addAction(analysisAction)
        

        #self.openJournal()

    def loadConfig(self):
        self.opts = {} # make sure values are always lists (makes things simpler)
        if os.path.isfile(configPath):
            with open(configPath, 'r') as file:
                lines = file.readlines()
            lines = [line.strip() for line in lines]
            
            for line in lines:
                if line:
                    splits = line.split(':')
                    if len(splits) == 2:
                        ss = splits[1].split(',')
                        self.opts[splits[0]] = ss[0] if len(ss) == 1 else ss
                    else:
                        print('weow somethings wrong with the config file lol')

            #print(self.opts)


    def locateFiles(self):

        #if self.opts

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Data display window is disabled for now sorry!")
        msg.setWindowTitle("Please specify ")
        msg.exec_()


        # search for config file

    def saveConfig(self):
        with open(configPath, 'w') as file:
            for k,v in self.opts.items():
                if isinstance(v, list):
                    file.write(f'{k}:{",".join(str(x) for x in v)}\n')
                else:
                    file.write(f'{k}:{v}\n')



    def openJournal(self):
        self.clearLayout(self.layout)

        self.toolBar.clear()
        fontAction = QtWidgets.QAction('Font', self)
        fontAction.triggered.connect(self.openFontWindow)
        self.toolBar.addAction(fontAction)

        bgColorAction = QtWidgets.QAction('Set BG', self)
        bgColorAction.triggered.connect(functools.partial(self.setEditorColor, True))
        self.toolBar.addAction(bgColorAction)

        fgColorAction = QtWidgets.QAction('Set FG', self)
        fgColorAction.triggered.connect(functools.partial(self.setEditorColor, False))
        self.toolBar.addAction(fgColorAction)

        jlayout = QtWidgets.QVBoxLayout()

        self.editor = MyPlainTextEdit()
        self.loadEditorSettings()

        jlayout.addWidget(self.editor)

        self.layout.addLayout(jlayout)

        #self.jtab.setLayout(jlayout)

        # have program save all settings in config file!
        # need date thing
        # one journal per day, open and close by date (QCalendar!!!)
        # make toolbar
            # have dark mode option
            # font size
            # have font select dropdown
            # file save and open by date
            # spellcheck ? https://stackoverflow.com/questions/8722061/pyqt-how-to-turn-on-off-spellchecking

    def openAnalysis(self):
        self.clearLayout(self.layout)

        self.toolBar.clear()

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        alayout = QtWidgets.QVBoxLayout()
        alayout.addWidget(self.toolbar)
        alayout.addWidget(self.canvas)
        self.layout.addLayout(alayout)

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


    # deserialize option and return correct object
    def getOpt(self, opt):
        od = self.opts[opt]
        if opt == 'font':
            return QtGui.QFont(od[0], int(od[1]))
        elif opt == 'bgColor' or opt == 'fgColor':
            c = [int(col) for col in od]
            return QtGui.QColor(c[0],c[1],c[2])
        else:
            print(f'unknown opt: {opt}!')

    def openFontWindow(self):
        font,valid = QtWidgets.QFontDialog.getFont(self.getOpt('font'))
        if valid:
            self.editor.setFont(font)
            self.opts['font'] = [font.family(), font.pointSize()]

    def loadEditorSettings(self):
        if 'font' not in self.opts:
            self.opts['font'] = ['Helvetica', 14]
        if 'bgColor' not in self.opts:
            self.opts['bgColor'] = [255,255,255]
        if 'fgColor' not in self.opts:
            self.opts['fgColor'] = [0,0,0]

        self.editor.setFont(self.getOpt('font'))
        self.setEditorColor(True,self.getOpt('bgColor'))
        self.setEditorColor(False,self.getOpt('fgColor'))

    def setEditorColor(self, isBg, color = None):
        if not color:
            optStr = 'bgColor' if isBg else 'fgColor'
            color = QtWidgets.QColorDialog.getColor(self.getOpt(optStr))
            if not color.isValid():
                return
            self.opts[optStr] = [color.red(), color.green(), color.blue()]
        vp = self.editor.viewport()
        p = vp.palette()
        p.setColor((vp.backgroundRole() if isBg else vp.foregroundRole()), color)
        vp.setPalette(p)


    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.layout():
                self.clearLayout(child.layout())
            elif child.widget():
                child.widget().deleteLater()


    def closeApp(self):
        self.close() # so close event is triggered

    def closeEvent(self, e):
        self.saveConfig()
        print('goodbye!!!')
        # save config options here to file



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

    sys.exit(app.exec_())