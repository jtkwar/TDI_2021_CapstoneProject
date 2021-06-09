# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
#os.chdir("C:\\Users\\stark\\Documents\\Coding\\TDI\\streamlit_capstone")
os.chdir("C:\\Users\\Jeff\\Documents\\Cannabis Capstone\\streamlit")
import sys
import pandas as pd
import numpy as np
import scipy.fft
import matplotlib.pyplot as plt
import matplotlib
import datetime
import seaborn as sns
import streamlit as st
import plotly.express as px
from streamlit_multiApp import MultiApp
from tdi_capstone_apps import *


app = MultiApp()

app.add_app("Homepage", homepage_app)
app.add_app("Select Company", single_company_stats)
app.add_app("Company Comparison", company_comparison)
app.run()