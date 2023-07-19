from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta, date
from selenium import webdriver
from utils import *
from pyxlsb import open_workbook as open_xlsb

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
options.add_argument('--disable-gpu')
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")

## 01. functions
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('CP949')

#@st.cache_resource
def get_driver():
    #return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
    
    api_key = '1b39652cef07f626c9d37375edf582ee51b1407f'
    #api_key = 'd08546d14aedde5f2918b783aa10188e789f8f5f'
    dart = OpenDartReader(api_key)
    
    # C=발행공시, D=지분공시
    market_dict = {"Y": "코스피","K": "코스닥", "N": "코넥스", "E": "기타"}

    info_df = dart.list(start=start_dt, end=end_dt, kind_detail='C001')
    info_df = pd.concat([info_df, dart.list(start=start_dt, end=end_dt, kind_detail='G002')])

    info_df = info_df.loc[[True if "증권발행실적보고서" in x else False for x in info_df.report_nm]]
    info_df = info_df.loc[info_df.corp_cls.isin(['Y', 'K'])]
    info_df.corp_cls = info_df.corp_cls.map(market_dict)
    
    p_ratio = 0.05
    p_bar.progress(p_ratio, text=progress_text)
    
    # kind
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    p_ratio = 0.10
    p_bar.progress(p_ratio, text=progress_text)
    
    #driver = webdriver.Chrome()
    st.write('<p style="font-size:14px; color:black"> - KIND 수집 시작 (1/2) </p>',unsafe_allow_html=True)
    p_ratio = 0.15
    first_df = kind_main(driver, info_df, start_dt, end_dt)
    p_ratio = 0.55
    p_bar.progress(p_ratio, text=progress_text)
    
    # ipo stock
    st.write('<p style="font-size:14px; color:black"> - OpenDART 수집 시작 (2/2) </p>',unsafe_allow_html=True)
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    p_ratio = 0.60
    p_bar.progress(p_ratio, text=progress_text)
    
    ipo_df = ipo_main(driver, info_df)
    first_df = pd.merge(first_df, ipo_df, on = 'corp_name', how = 'left')
    p_ratio = 0.8
    p_bar.progress(p_ratio, text=progress_text)
    
    # 38커뮤니케이션
    outer_df = get_38(start_dt, end_dt)
    second_df = pd.merge(first_df, outer_df, on = 'stock_code', how = 'inner')
    p_ratio = 0.9
    p_bar.progress(p_ratio, text=progress_text)
    
    # DART
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
    
    
end_date = date.today()
diff_day = timedelta(days=60)
diff_day2 = timedelta(days=31)
start_date = end_date - diff_day
origin_start_date = end_date - diff_day2

form_1, form_2, form_3 = main(start_dt, end_dt, opt = '기업금융1부')
form_1 = form_1.loc[form_1['상장일'] >= origin_start_date]
form_2 = form_2.loc[form_2['상장일'] >= origin_start_date]
form_3 = form_3.loc[form_3['상장일'] >= origin_start_date]

with pd.ExcelWriter('기업금융1부-IPO 집계 데이터.xlsx', engine = 'xlsxwriter') as writer:
    form_1.to_excel(writer, sheet_name="01_리그테이블", index=False)
    form_2.to_excel(writer, sheet_name="02_통합집계_Rawdata", index=False)
    form_3.to_excel(writer, sheet_name="03_IPO현황_Summary", index=False)