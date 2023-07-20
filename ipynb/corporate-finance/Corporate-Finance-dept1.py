from streamlit_option_menu import option_menu
from datetime import datetime, timedelta, date
from selenium import webdriver
from utils import *
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

import streamlit as st
import pandas as pd
import numpy as np
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

# 파일 불러오기
def read_data(file):
    try:
        output = pd.read_excel(file)
    except:
        def read_xlsx(name):
            instance = xw.App(visible=False)
            xlsx_data = xw.Book(name).sheets[0]
            df = xlsx_data.range('A1').options(pd.DataFrame, index = False, expand = 'table').value
            instance.quit()
            instance.kill()
            return df
        output = read_xlsx(file)
    return output

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
    selected = option_menu("Menu", ["기업금융1부"],
                           icons=['card-list'],
                           menu_icon='cast', default_index=0,
                          styles={
                              "nav-link-selected": {"background-color": "#1c82e1"}
                          })

st.header('기업금융1부 - IPO 현황 수집')

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
    ## 파일 읽기
    form_1 = pd.read_excel(data_path + "corporate-finance-data.xlsx", sheet_name = '01_리그테이블')
    form_2 = pd.read_excel(data_path + "corporate-finance-data.xlsx", sheet_name = '02_통합집계_Rawdata')
    form_3 = pd.read_excel(data_path + "corporate-finance-data.xlsx", sheet_name = '03_IPO현황_Summary')
    
    form_1 = form_1.loc[(form_1['상장일'] >= start_dt) & (form_1['상장일'] <= end_dt)]
    form_2 = form_2.loc[(form_2['상장일'] >= start_dt) & (form_2['상장일'] <= end_dt)]
    form_3 = form_3.loc[(form_3['상장일'] >= start_dt) & (form_3['상장일'] <= end_dt)]
    
    form_1.index = [x for x in range(1, form_1.shape[0]+1)]
    form_2.index = [x for x in range(1, form_2.shape[0]+1)]
    form_3.index = [x for x in range(1, form_3.shape[0]+1)]
    
    st.write('<p style="font-size:15px; color:white"><span style="background-color: #1c82e1;"> ✔ {} </span></p>'.format('01_리그테이블'),unsafe_allow_html=True)
    st.dataframe(form_1)
    save_df1 = convert_df(form_1)
    
    st.write('<p style="font-size:15px; color:white"><span style="background-color: #1c82e1;"> ✔ {} </span></p>'.format('02_통합집계_Rawdata'),unsafe_allow_html=True)
    st.dataframe(form_2)
    save_df2 = convert_df(form_2)
    
    st.write('<p style="font-size:15px; color:white"><span style="background-color: #1c82e1;"> ✔ {} </span></p>'.format('03_IPO현황_Summary'),unsafe_allow_html=True)
    st.dataframe(form_3)
    save_df3 = convert_df(form_3)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        form_1.to_excel(writer, sheet_name="01_리그테이블", index=False)
        form_2.to_excel(writer, sheet_name="02_통합집계_Rawdata", index=False)
        form_3.to_excel(writer, sheet_name="03_IPO현황_Summary", index=False)
        
    processed_data = output.getvalue()
    st.download_button(label='📥 다운로드',
                                data=processed_data ,
                                file_name= '기업금융1부-IPO 집계 데이터_{}~{}.xlsx'.format(start_dt[2:].replace('-', '.'), end_dt[2:].replace('-', '.')))