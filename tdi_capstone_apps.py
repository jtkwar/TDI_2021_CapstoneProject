# -*- coding: utf-8 -*-
"""
Created on Sun May 16 16:50:07 2021

@author: stark
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import plotly.express as px
from datetime import datetime

def load_salesData(filename):
    df = pd.read_csv(filename)
    df['sold_at'] = df['sold_at'].astype('datetime64[ns]')
    df = df.set_index('sold_at')
    return df

def homepage_app():
    st.title("Washington State Cannabis Analytics")
    st.header("TDI Spring Cohort 2021")
    st.subheader("Jeffrey Kwarsick, PhD")
    # open the licensees .csv file
    license_info = "Licensees_0.csv"
    totalSales_df = load_salesData("total_sales.csv")
    companies = totalSales_df.columns
    
    
    license_df = pd.read_csv(license_info)
    # keep only some information for now
    license_df = license_df[['global_id', 'name', 'address1', 'address2', 'city']]
    # keep only processed companies in the list
    license_df = license_df[license_df["global_id"].isin(companies)]
    st.subheader("Project Description")
    st.write("[Github Repository Link](https://github.com/jtkwar/TDI_2021_CapstoneProject)")
    st.write("Analysis and Comparison of {0} Dispensaries in the State of Washington between January 1, 2018 and December 31, 2020.".format(len(companies)))
    st.write("This project aims to provide insight into the performance of different cannabis dispensaries across the State of Washington.  The 'Select Company' page allows for an in-depth look of sales data for an individual dispensary.  The 'Company Comparison' page allows one to compare the performance of one dispensary against others in the same city or all dispensaries in the state.")
    st.subheader("Process")
    st.markdown("""
                - Data was obtained from the [Washington State Liquor and Cannabis Board](https://lcb.wa.gov/), an agency responsible for promoting public safety and trust through fair administration and enforcement of liquor, cannabis, tabacco, and vapor laws. [Link to Data](https://lcb.app.box.com/s/fnku9nr22dhx04f6o646xv6ad6fswfy9?page=1)
                - Dispensaries across the state were identified for the available data
                - A pipeline was designed to extract the sales information for each dispensary from the overall dataset.
                    - Due to the time it takes to extract sales data for individual dispensaries, only a fraction of the total number of dispensaries are available at this time.  With additional time, all the dispensaries can/will be added.
                    - This pipeline was formulated in a Jupyter Notebook environment.  Please refer to these notebooks in the linked GitHub Repository.
                - Extracted dataset for each dispensary was reduced to time series sales data of the following categories:
                    - Total Sales (Medical Sales and Recreational Sales)
                    - Medical Sales
                    - Recreational Sales
                - Constructed streamlit application and pushed to Heroku
                """)
    st.subheader("Future Plans")
    st.markdown("""
                - Complete extraction of sales data for all dispensaries located in the State of Washington.
                - Build predictive capabilities utilizing sales data for each dispensary
                """)
    st.header("Locations of Dispensaries Across the State")
    st.table(license_df["city"].unique())
    
    
def single_company_stats():
    ### load the data ###
    license_info = "Licensees_0.csv"
    license_df = pd.read_csv(license_info)
    # keep only some information for now
    license_df = license_df[['global_id', 'name', 'address1', 'address2', 'city']]
    totalSales_df = load_salesData("total_sales.csv")
    recreationalSales_df = load_salesData("recreational_sales.csv")
    medicalSales_df = load_salesData("medical_sales.csv")
    companies = totalSales_df.columns
    # collapse the licensees dataframe to what is currently parsed
    license_df = license_df[license_df["global_id"].isin(companies)]
    
    ######################################################################################
    ######################################################################################
    st.title("Dispensary Statistics")
    st.header("Select Dispensary")
    select_col1, select_col2, select_col3 = st.beta_columns((1,1,1))
    with select_col1:
        city = st.selectbox("Select City", list(license_df["city"].unique()))
    with select_col2:
        company = st.selectbox("Select Dispensary", list(license_df[license_df['city'] == city]["name"]))
    with select_col3:
        company_id = st.selectbox("Select Dispensary Id", list(license_df.query("city == @city & name == @company")['global_id']))
    # return selected company information
    st.table(license_df.loc[license_df['name'] == str(company)])
    #st.table(totalSales_df)
    ######################################################################################
    ######################################################################################
    ### resampling dictionary ###
    resample_dict = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q',
                     'Yearly': 'Y'}
    st.header("Sales Data Summary for {}".format(company.rstrip()))
    tp_selection = st.selectbox("Select Time Period Sampling", list(resample_dict.keys()))
    ######################################################################################
    query_string = "`" + str(company_id) + "` > 0"
    
    medicalSales = medicalSales_df.query(query_string)[str(company_id)].resample(resample_dict[tp_selection]).sum().to_frame()
    recreationalSales = recreationalSales_df.query(query_string)[str(company_id)].resample(resample_dict[tp_selection]).sum().to_frame()
    totalSales = totalSales_df.query(query_string)[str(company_id)].resample(resample_dict[tp_selection]).sum().to_frame()
    min_date = pd.to_datetime(totalSales.index.values.min())
    max_date = pd.to_datetime(totalSales.index.values.max())
    st.write("Total Sales Between {0} to {1}: ${2:,.2f}".format(min_date.date(),
                                                                max_date.date(),
                                                                totalSales.sum()[0]))
    st.write("Average {0} Total Sales (Medical and Recreational): ${1:,.2f}".format(tp_selection, totalSales[str(company_id)].mean()))
    st.write("Average {0} Medical Sales: ${1:,.2f}".format(tp_selection, medicalSales[str(company_id)].mean()))
    st.write("Average {0} Recreational Sales: ${1:,.2f}".format(tp_selection, recreationalSales[str(company_id)].mean()))
    
    st.header("Sales Data Visualization")
    scol1, scol2, scol3 = st.beta_columns((1, 1, 1))
    if tp_selection == 'Daily' or tp_selection == 'Weekly' or tp_selection == 'Monthly':
        with scol1:
            f = px.line(totalSales,
                        x=totalSales.index,
                        y=totalSales.iloc[:,0],
                        title="{0} Sales (Medical and Recreational)".format(tp_selection))
            f.update_traces(mode="markers+lines")
            f.update_xaxes(title="Date")
            f.update_yaxes(title="Total Sales, USD")
            st.plotly_chart(f)
        with scol2:
            g = px.line(medicalSales,
                        x=medicalSales.index,
                        y=medicalSales.iloc[:,0],
                        title="{0} Medical Retail Sales".format(tp_selection))        
            g.update_traces(mode="markers+lines")
            g.update_xaxes(title="Date")
            g.update_yaxes(title="Total Sales, USD")            
            st.plotly_chart(g)
        with scol3:
            h = px.line(recreationalSales,
                        x=recreationalSales.index,
                        y=recreationalSales.iloc[:,0],
                        title="{0} Recreational Retail Sales".format(tp_selection))        
            h.update_traces(mode="markers+lines")
            h.update_xaxes(title="Date")
            h.update_yaxes(title="Total Sales, USD")            
            st.plotly_chart(h)
    else:
        with scol1:
            f = px.bar(totalSales, x=totalSales.index, y=totalSales.iloc[:,0],
                       title="{0} Sales (Recreational and Medical)".format(tp_selection))
            f.update_xaxes(title="Date")
            f.update_yaxes(title="Total Sales, USD")            
            st.plotly_chart(f)
        with scol2:
            g = px.bar(medicalSales, x=medicalSales.index, y=medicalSales.iloc[:,0],
                       title="{0} Medical Retail Sales".format(tp_selection))
            g.update_xaxes(title="Date")
            g.update_yaxes(title="Total Sales, USD")
            st.plotly_chart(g)
        with scol3:
            h = px.bar(recreationalSales, x=recreationalSales.index, y=recreationalSales.iloc[:,0],
                       title="{0} Recreational Retail Sales".format(tp_selection))
            h.update_xaxes(title="Date")
            h.update_yaxes(title="Total Sales, USD")
            st.plotly_chart(h)




def company_comparison():
    st.title("Dispensary Comparison")
    ### load the data ###
    license_info = "Licensees_0.csv"
    license_df = pd.read_csv(license_info)
    # keep only some information for now
    license_df = license_df[['global_id', 'name', 'address1', 'address2', 'city']]
    totalSales_df = load_salesData("total_sales.csv")
    recreationalSales_df = load_salesData("recreational_sales.csv")
    medicalSales_df = load_salesData("medical_sales.csv")
    companies = totalSales_df.columns
    # collapse the licensees dataframe to what is currently parsed
    license_df = license_df[license_df["global_id"].isin(companies)]
    ######################################################################################
    ######################################################################################
    st.header("Select Dispensary for Comparison")
    select_col1, select_col2, select_col3 = st.beta_columns((1,1,1))
    with select_col1:
        city = st.selectbox("Select City", list(license_df["city"].unique()))
    with select_col2:
        company = st.selectbox("Select Dispensary", list(license_df[license_df['city'] == city]["name"]))
    with select_col3:
        company_id = st.selectbox("Select Dispensary Id", list(license_df.query("city == @city & name == @company")['global_id']))
    # return selected company information
    st.table(license_df.loc[license_df['name'] == str(company)])
    ######################################################################################
    ######################################################################################
    scope = st.selectbox("Scope of Comparison", ['Statewide', 'Local (Same City)'])
    
    if scope == 'Statewide':
        st.write("Comparison of {0} ({1}) Performance Against All Dispensaries in the State".format(company, company_id))
        pass
    else:
        st.write("Comparison of {0} ({1}) Performance Against All Dispensaries in {2}".format(company, company_id, city))
        pass
    
    
    
    