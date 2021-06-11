# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import os
#my_dir = os.getcwd()
#os.chdir(my_dir)
#import sys
import pandas as pd
import numpy as np
#import scipy.fft
import streamlit as st
import plotly.express as px
from streamlit_multiApp import MultiApp
from tdi_capstone_apps import *


app = MultiApp()

app.add_app("Homepage", homepage_app)
app.add_app("Select Company", single_company_stats)
app.add_app("Company Comparison", company_comparison)
app.run()