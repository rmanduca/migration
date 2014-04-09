#Make a shortname metros lookup


import os
import sys
#import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#import pyproj
import numpy as np
from scipy.stats import gaussian_kde
import re

os.chdir("/Users/Eyota/projects/thesis")

metros = pd.io.parsers.read_csv("output/msadata.csv")
metros['shortname'] = metros['MSAName'].apply(lambda x: re.search('^.*?[-,]',x).group(0)[:-1] + re.search(', [A-Z][A-Z]',x).group(0))
metros.to_csv('output/msadata_shortname.csv')