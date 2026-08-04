"""Graphical User Interface for Jupyter notebooks"""
# TODO: Refactor the whole GUI and move to submodule!

#from IPython.html.widgets import interact
#from IPython.html import widgets # IPython < 4

#import warnings
#import time
from collections import OrderedDict
import os.path
import os
import ast
import copy

import numpy as np
import ipywidgets as widgets
#from traitlets import link
#from traitlets import Unicode
from IPython.display import display
from IPython.display import clear_output
#from IPython import get_ipython
from lmfit import Parameters

#from IPython.core.pylabtools import print_figure
#import base64

from pyrho.parameters import modelParams, modelList, modelLabels, protList, protParams, simList, simParams, unitLabels, stateLabs, simUnitLabels, protParamLabels, protUnitLabels, protParamNotes, PyRhOparameters
from pyrho.models import *
from pyrho.simulators import *
from pyrho.protocols import *
from pyrho.expdata import *
from pyrho.fitting import *
from pyrho.config import simAvailable, GUIdir, setupGUI #, dDir # For dataSet loading
from pyrho.utilities import *
from pyrho import config
from pyrho.config import verbose

__all__ = ['loadGUI']

# LaTeX in widget descriptions/labels
# FloatRangeSlider and IntRangeSlider
# An Output widget was added, which allows you to print and display within widgets - replace Popup
# A SelectMultiple widget was added
# Suppress widget warning
# Add placeholder attribute to text widgets
# Tooltip on toggle button
# Dropdown options can be a dict, tuple or list


### Enable these for NEURON!!!
#import neuron
#from neuron import h

#%precision %.6g
#import numpy as np
#np.set_printoptions(precision=6)
#pprint()


# Create lists and dictionaries of titles
modelTitles = ['Three-state model', 'Four-state model', 'Six-state model']

fitMethodsDict = OrderedDict([(m,i) for i,m in enumerate(methods)])

# State keys must be padded with a leading ' ' to avoid a widgets bug: https://github.com/ipython/ipython/issues/6469
#statesDict = OrderedDict([(' '+s,i) for i,s in enumerate(list(modelParams.keys()))]) # enumerate(modelList)
#statesDict = OrderedDict([(' 3',0), (' 4',1), (' 6',2)])
statesDict = OrderedDict([(s,i) for i,s in enumerate(list(modelParams))]) #.keys()
statesArray = modelList #statesArray = list(statesDict) #.keys() #[' 3', ' 4', ' 6'] # [u' 3',u' 4',u' 6'] ### Redundant!

TabGroups = {'Fit':0, 'Models':1, 'Protocols':2, 'Simulators':3}
#TabGroups = {'Models':0, 'Simulators':1, 'Protocols':2}

#clearDelay = 1.5 # Pause [s] before clearing text entry fields

# Structures for cross-referencing arrays of widgets to their corresponding parameters
# http://stackoverflow.com/questions/18809482/python-nesting-dictionary-ordereddict-from-collections
#mParamsK2I = OrderedDict([ (model,OrderedDict([(p,i) for i,p in enumerate(list(modelParams[model]))])) for model in modelList ])
#mParamsI2K = OrderedDict([ (model,list(modelParams[model])) for model in modelList ])
modelParamsList = OrderedDict([ (model, list(modelParams[model])) for model in modelList ])

#sParamsK2I = OrderedDict([ (sim,OrderedDict([(p,i) for i,p in enumerate(list(simParams[sim]))])) for sim in simList ])
#sParamsI2K = OrderedDict([ (sim,list(simParams[sim])) for sim in simList ])
simParamsList = OrderedDict([ (sim, list(simParams[sim])) for sim in simList ])
loadedSims = [ sim for sim in simList if simAvailable(sim) ]

#pParamsK2I = OrderedDict([ (prot,OrderedDict([(p,i) for i,p in enumerate(list(protParams[prot]))])) for prot in protList ])
#pParamsI2K = OrderedDict([ (prot,list(protParams[prot])) for prot in protList ])
protParamsList = OrderedDict([ (prot, list(protParams[prot])) for prot in protList ])

boolDict = OrderedDict([('True',True), ('False',False)])

