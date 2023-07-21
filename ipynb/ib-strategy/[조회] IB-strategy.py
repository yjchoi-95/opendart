from streamlit_option_menu import option_menu
from datetime import datetime, timedelta, date
from selenium import webdriver
from IB_utils import *
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

import streamlit as st
import pandas as pd
import numpy as np
import OpenDartReader
import warnings
import time
import re
import os
import copy

warnings.filterwarnings('ignore')

## 01. functions
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('CP949')

def get_driver(viz_opt = False):
    #return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    if viz_opt:
        return webdriver.Chrome()
    else:
        return webdriver.Chrome(options=options)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

## 02. layout
st.set_page_config(layout='wide')

with st.sidebar:
    selected = option_menu("Menu", ["IB전략컨설팅부"],
                           icons=['card-list'],
                           menu_icon='cast', default_index=0,
                          styles={
                              "nav-link-selected": {"background-color": "#1c82e1"}
                          })


st.header('IB전략컨설팅부 - IPO 현황 수집')

c1, c2 = st.columns(2)

today = date.today()
diff_day = timedelta(days=60)

with c2:
    end_date = st.date_input('종료일', value=today, max_value = today)
with c1:
    start_date = st.date_input('시작일', value=end_date - timedelta(days=31), min_value = end_date - diff_day, max_value = end_date)
start_btn = st.button('🛠 수집')

start_dt = datetime.strftime(start_date,'%Y-%m-%d')
end_dt = datetime.strftime(end_date,'%Y-%m-%d')
data_path = './datasets/'

if start_btn:
    head_df = pd.read_excel(data_path + "ib-strategy-data.xlsx")
    head_df = head_df.loc[(head_df['상장일'] >= start_dt) & (head_df['상장일'] <= end_dt)]
    head_df.index = [x for x in range(1, head_df.shape[0]+1)]
    st.write('<p style="font-size:15px; color:white"><span style="background-color: #1c82e1;"> ✔ {} </span></p>'.format('IPO 공모기업 현황'),unsafe_allow_html=True)
    st.dataframe(head_df)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        head_df.to_excel(writer, sheet_name="IPO 공모 기업 현황", index=False)
        
    processed_data = output.getvalue()
    
    st.download_button(label='📥 다운로드',
                                data=processed_data ,
                                file_name= 'IB전략컨설팅부-IPO 집계 데이터_{}~{}.xlsx'.format(start_dt[2:].replace('-', '.'), end_dt[2:].replace('-', '.')))