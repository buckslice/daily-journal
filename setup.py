# -*- coding: utf-8 -*-

# A very simple setup script to create a single executable
#
# hello.py is a very simple 'Hello, world' type script which also displays the
# environment in which the script runs
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

# from cx_Freeze import setup, Executable

# executables = [
    # Executable('words.py',base = "Win32GUI")
# ]
# import os
# os.environ['TCL_LIBRARY'] = r'C:\Users\Bucky\Anaconda3\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Users\Bucky\Anaconda3\tcl\tk8.6'

# additional_mods = ['numpy.core._methods', 'numpy.lib.format','matplotlib']
# packages = ['matplotlib.backends.backend_qt5agg']

# setup(name='MarysWritingAnalyzer',
      # version='0.1',
      # description='Analyzes for Metadata',
	  # options= {'build_exe':{'includes':additional_mods, 'packages':packages}},
      # executables=executables
	  # )

	  
import cx_Freeze
import sys
import matplotlib
import numpy.core._methods
import numpy.lib.format
import numpy

base = "Win32GUI"

executables = [
    cx_Freeze.Executable("words.py", base = base),
    ]

#import os
#os.environ['TCL_LIBRARY'] = r'C:\Users\Bucky\Anaconda3\tcl\tcl8.6'
#os.environ['TK_LIBRARY'] = r'C:\Users\Bucky\Anaconda3\tcl\tk8.6'
	
includes = ['numpy.core._methods', 'numpy.lib.format']
	
#build_exe_options = {"includes":["matplotlib.backends.backend_tkagg"],
                     #"include_files":[(matplotlib.get_data_path(), "mpl-data")],
                     #"excludes":[],
                     #}
cx_Freeze.setup(
    name = "script",
    #options = {"build_exe": build_exe_options},
	#options = {'build.exe': {'includes':includes}},
    version = "0.0",
    description = "A basic example",
    executables = executables)
	
	
	
	
	