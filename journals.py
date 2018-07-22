import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random
import functools

configPath = 'config.txt'

class JournalWindow(QtWidgets.QMainWindow):
    def __init__(self, *args):
        QtWidgets.QMainWindow.__init__(self, *args)

        # init variables
        self.cal = None
        self.currentDate = QtCore.QDate.currentDate()
        self.firstPaint = True

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
        journalAction.triggered.connect(self.openJournalFrame)
        menuBar.addAction(journalAction)

        analysisAction = QtWidgets.QAction('Analysis', self)
        analysisAction.triggered.connect(self.openAnalysisFrame)
        menuBar.addAction(analysisAction)

        # delayed a bit so window has chance to open and draw
        QtCore.QTimer.singleShot(500, self.loadJournals)


    def openSaveDialog(self):
        options = QtWidgets.QFileDialog.DontResolveSymlinks |  QtWidgets.QFileDialog.ShowDirsOnly
        self.opts['saveLocation'] = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the save folder for your journals', '', options)

    def loadJournals(self):
        notInOpts = 'saveLocation' not in self.opts 
        if notInOpts or not os.path.exists(self.opts['saveLocation']):
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle('Journal Folder not found!')
            if notInOpts:
                msg.setText('Please select where you want to save your journals.')
                msg.setIcon(QtWidgets.QMessageBox.Information)
            else:
                msg.setText("Can't find journal folder! Did it move?")
                msg.setIcon(QtWidgets.QMessageBox.Critical)

            msg.exec_()

            self.opts['saveLocation'] = ''
            while not os.path.exists(self.opts['saveLocation']):
                self.openSaveDialog()


        print(f'loading journals from folder at: {self.opts["saveLocation"]}')

        # load all files in that folder recursively
        # check for correct date by name or by creation date
        # have journal show journal date at top of file in a label like 'July-16-2018, 5 days ago'
        files = self.getFilePaths(self.opts['saveLocation'])
        #print('\n'.join(files))

        # load all files into memory when you click either journal or analysis (show progress bar)
        # analize all files when you click analyze (add filename to set so know if need to reanalyze as u write more while program going)

        # if you change file then save it to disk and update loaded file and flag for analysis

        self.openJournalFrame()

    #finds abspath of all text files in rootDir (and subdirectories)
    def getFilePaths(self, rootDir = '.'): # default to local dir
        files = []
        for dirpath, dirnames, filenames in os.walk(rootDir):
            for s in filenames:
                if s.endswith('.txt'):
                    files.append(os.path.join(os.path.abspath(dirpath),s))              
        return files
        
    def saveCurrentJournal(self):
        if not self.editor:
            return

        name = self.currentDate.toString('yyyy-MM-dd.txt')
        with open(os.path.join(self.opts['saveLocation'],name), 'w') as file:
            file.write(str(self.editor.toPlainText()))



    def loadConfig(self):
        self.opts = {} # make sure values are always lists (makes things simpler)
        if os.path.isfile(configPath):
            with open(configPath, 'r') as file:
                lines = file.readlines()
            lines = [line.strip() for line in lines]
            
            for line in lines:
                if line:
                    splits = line.split(':',1)
                    if len(splits) == 2:
                        ss = splits[1].split(',')
                        self.opts[splits[0]] = ss[0] if len(ss) == 1 else ss
                    else:
                        print('problem with the config file...')

            #print(self.opts)


    def saveConfig(self):
        with open(configPath, 'w') as file:
            for k,v in self.opts.items():
                if isinstance(v, list):
                    file.write(f'{k}:{",".join(str(x) for x in v)}\n')
                else:
                    file.write(f'{k}:{v}\n')

    def openCalendar(self):
        self.cal = CalendarDateSelect(self)
        self.cal.show()

    def updateDate(self, date=None):
        if date:
            self.currentDate = date
        self.dateLabel.setText(self.currentDate.toString('MMMM d, yyyy'))

    def openJournalFrame(self):

        self.clearLayout(self.layout)

        self.toolBar.clear()

        hf = QtGui.QFont('Helvetica', 14)

        calendarAction = QtWidgets.QAction('Select Date', self)#, font= hf)
        calendarAction.triggered.connect(self.openCalendar)
        self.toolBar.addAction(calendarAction)

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

        self.dateLabel = QtWidgets.QLabel('', font=hf)
        self.updateDate()

        jlayout.addWidget(self.dateLabel)

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

    def openAnalysisFrame(self):
        self.saveCurrentJournal()

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
        if self.cal:
            self.cal.close()
        self.saveCurrentJournal()
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


class CalendarDateSelect(QtWidgets.QFrame):
    def __init__(self, window, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setWindowTitle('Select Journal Date')

        self.layout = QtWidgets.QVBoxLayout(self)
        self.cal = QtWidgets.QCalendarWidget()
        self.layout.addWidget(self.cal)

        self.doneButton = QtWidgets.QPushButton('Open Journal')
        self.doneButton.clicked.connect(self.returnDate)
        self.layout.addWidget(self.doneButton)

        self.window = window

        g = self.window.geometry()
        self.move(g.x() + 100, g.y() + 100)

    def returnDate(self):
        self.window.updateDate(self.cal.selectedDate())
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = JournalWindow()
    main.show()

    sys.exit(app.exec_())