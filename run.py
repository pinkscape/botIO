
# import all/wanted classes
from frameworks.Framework import *
from frameworks.BotIOChromeExtension import *
from learningschemes.LearningScheme import *
from learningschemes.PolicyGradient import *
from nnarchitectures.NNArchitecture import *
from nnarchitectures.CNN import *
import tensorflow as tf

# create environment
# framework: serves picture, applies commands
# alternatives: UniverseFW, BotIOChromeExtension
frw = (BotIOChromeExtension,{})

# architecture of neural network
# alternatives: CNN, RNN, FC, [LSTM, FractalNet, HighwayNets, uNet, ...]
arc = (CNN, {"layers":10, "window_size":3, "stride":0, "optimizer":tf.GradientDescentOptimizer(0.5)})

# learning scheme: gets pictures from framework, uses network
# alternatives: PolicyGradient, QLearning,
lsc = (PolicyGradient,{"window_inc":0, "window_size":100})

# TODO: http://www.saltycrane.com/blog/2008/01/how-to-use-args-and-kwargs-in-python/

# run
frw.run(lsc, arc, save_after_cycles=100)