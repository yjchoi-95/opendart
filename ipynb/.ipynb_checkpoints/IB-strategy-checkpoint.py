from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

options = Options()
options.add_argument('--headless')

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

def main(start_dt, end_dt, opt = 'IB전략'):
    progress_text = "Operation in progress. Please wait."
    p_bar = st.progress(0.0, text=progress_text)
    
    # Dart
    start_dt2 = datetime.strftime(datetime.strptime(end_dt, '%Y-%m-%d') - timedelta(days = 80), '%Y-%m-%d')
    start_dt3 = datetime.strftime(datetime.strptime(end_dt, '%Y-%m-%d') - timedelta(days = 180), '%Y-%m-%d')
    dart_df, dart = initial_set(start_dt2, end_dt)
    p_ratio = 0.05
    p_bar.progress(p_ratio, text=progress_text)
    
    # kind
    driver = get_driver(viz_opt = True)
    driver.set_window_size(1920, 1080)
    time.sleep(3)
    p_ratio = 0.10
    p_bar.progress(p_ratio, text=progress_text)
    
    st.write('<p style="font-size:14px; color:black"> - KIND 수집 시작 (1/4) </p>',unsafe_allow_html=True)
    p_ratio = 0.15
    table = set_kind(driver, start_dt3, end_dt)
    kind_output = get_kind_inner(driver, table)
    first_df = post_proc(dart_df, kind_output, start_dt)
    p_ratio = 0.55
    p_bar.progress(p_ratio, text=progress_text)
    
    # ipo stock
    st.write('<p style="font-size:14px; color:black"> - IPO 스탁 수집 시작 (2/4) </p>',unsafe_allow_html=True)
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    p_ratio = 0.60
    p_bar.progress(p_ratio, text=progress_text)
    
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    ipo_df = ipo_main(driver, first_df)
    first_df = pd.merge(first_df, ipo_df, on = 'corp_name', how = 'left')
    first_df.replace(np.NaN, 0, inplace = True)
    first_df['key'] = [change_join(x) if "스팩" in x else x for x in list(first_df.corp_name)]
    p_ratio = 0.8
    p_bar.progress(p_ratio, text=progress_text)
    
    # 38커뮤니케이션
    st.write('<p style="font-size:14px; color:black"> - 38커뮤니케이션 수집 시작 (3/4) </p>',unsafe_allow_html=True)
    outer_df = get_38(start_dt, end_dt)
    second_df = pd.merge(first_df, outer_df, left_on = 'key', right_on = '기업명', how = 'inner')
    del second_df['기업명'], second_df['key'], second_df['stock_code_x']
    second_df.rename(columns = {'stock_code_y':'stock_code'}, inplace = True)
    p_ratio = 0.9
    p_bar.progress(p_ratio, text=progress_text)
    
    # DART
    st.write('<p style="font-size:14px; color:black"> - OpenDART 수집 시작 (4/4) </p>',unsafe_allow_html=True)
    third_df = get_dd(dart, second_df)
    third_df, fourth_df = get_d_tables(dart, third_df)
    p_ratio = 1.0
    p_bar.progress(p_ratio, text=progress_text)
    
    if opt == 'IB전략':
        head_df = change_form(third_df, opt)
        return head_df
    
    else:
        form_1 = change_form(fourth_df, opt, 1)
        form_2 = change_form(third_df, opt, 2)
        form_3 = change_form(fourth_df, opt, 3)
        return form_1, form_2, form_3
    
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

origin_start_date = copy.deepcopy(start_date)
origin_start_date = datetime.strftime(start_date,'%Y-%m-%d')

start_date -= timedelta(days=30)
start_dt = datetime.strftime(start_date,'%Y-%m-%d')
end_dt = datetime.strftime(end_date,'%Y-%m-%d')

start_btn = st.button('🛠 수집')

if start_btn:
    head_df = main(start_dt, end_dt, opt = 'IB전략')
    head_df = head_df.loc[head_df['상장일'] >= origin_start_date]
    head_df = head_df.sort_values("수요예측(시작일)")
    head_df.index = [x for x in range(1, head_df.shape[0]+1)]
    st.write('<p style="font-size:15px; color:white"><span style="background-color: #1c82e1;"> ✔ {} </span></p>'.format('IPO 공모기업 현황'),unsafe_allow_html=True)
    st.dataframe(head_df)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        head_df.to_excel(writer, sheet_name="IPO 공모 기업 현황", index=False)
        
    processed_data = output.getvalue()
    
    st.download_button(label='📥 다운로드',
                                data=processed_data ,
                                file_name= 'IB전략컨설팅부-IPO 집계 데이터_{}~{}.xlsx'.format(origin_start_date[2:].replace('-', '.'), end_dt[2:].replace('-', '.')))