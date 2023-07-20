from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from streamlit_option_menu import option_menu
from datetime import datetime, timedelta, date
from selenium import webdriver
from utils import *
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

# load data
def read_xlsx(name):
    instance = xw.App(visible=False)
    xlsx_data = xw.Book(name).sheets[0]
    df = xlsx_data.range('A1').options(pd.DataFrame, index = False, expand = 'table').value
    instance.quit()
    instance.kill()
    return df

def read_data(file):
    try:
        output = pd.read_excel(file)
    except:
        output = read_xlsx(file)
    return output

def get_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(options=options)

def main():
    today = date.today()
    end_dt = datetime.strftime(today, '%Y-%m-%d')
    diff_day = timedelta(days=60)
    start_dt = datetime.strftime(today - diff_day, '%Y-%m-%d')

    api_key = '1b39652cef07f626c9d37375edf582ee51b1407f'
    dart = OpenDartReader(api_key)
    opt = '기업금융1부'

    # C=발행공시, D=지분공시
    market_dict = {"Y": "코스피","K": "코스닥", "N": "코넥스", "E": "기타"}

    info_df = dart.list(start=start_dt, end=end_dt, kind_detail='C001')
    info_df = pd.concat([info_df, dart.list(start=start_dt, end=end_dt, kind_detail='G002')])
    info_df = info_df.loc[[True if "증권발행실적보고서" in x else False for x in info_df.report_nm]]
    info_df = info_df.loc[info_df.corp_cls.isin(['Y', 'K'])]
    info_df.corp_cls = info_df.corp_cls.map(market_dict)

    driver = get_driver()
    driver.set_window_size(1920, 1080)
    first_df = kind_main(driver, info_df, start_dt, end_dt)

    # ipo stock
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    ipo_df = ipo_main(driver, info_df)
    first_df = pd.merge(first_df, ipo_df, on = 'corp_name', how = 'left')

    # 38커뮤니케이션
    outer_df = get_38(start_dt, end_dt)
    second_df = pd.merge(first_df, outer_df, on = 'stock_code', how = 'inner')

    # DART
    third_df = get_dd(dart, second_df)
    third_df, fourth_df = get_d_tables(dart, third_df)

    form_1 = change_form(fourth_df, opt, 1)
    form_2 = change_form(third_df, opt, 2)
    form_3 = change_form(fourth_df, opt, 3)

    form_1 = form_1.loc[form_1['상장일'] >= start_dt]
    form_2 = form_2.loc[form_2['상장일'] >= start_dt]
    form_3 = form_3.loc[form_3['상장일'] >= start_dt]

    data_path = './datasets/'

    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    if os.path.isfile(data_path + "corporate-finance-data.xlsx"):
        o_form1 = read_data(data_path + "form1.xlsx")
        o_form2 = read_data(data_path + "form2.xlsx")
        o_form3 = read_data(data_path + "form3.xlsx")

        o_form1 = pd.concat([o_form1, form_1]).sort_values("상장일").drop_duplicates()
        o_form2 = pd.concat([o_form2, form_2]).sort_values("청약일").drop_duplicates()
        o_form3 = pd.concat([o_form3, form_3]).sort_values("인수기관").drop_duplicates()

        o_form1.to_excel(data_path + "form1.xlsx", index = False)
        o_form2.to_excel(data_path + "form2.xlsx", index = False)
        o_form3.to_excel(data_path + "form3.xlsx", index = False)

        with pd.ExcelWriter(data_path + "corporate-finance-data.xlsx", engine = 'xlsxwriter') as writer:
            o_form1.to_excel(writer, sheet_name="01_리그테이블", index=False)
            o_form2.to_excel(writer, sheet_name="02_통합집계_Rawdata", index=False)
            o_form3.to_excel(writer, sheet_name="03_IPO현황_Summary", index=False)
    else:
        form_1.to_excel(data_path + "form1.xlsx", index = False)
        form_2.to_excel(data_path + "form2.xlsx", index = False)
        form_3.to_excel(data_path + "form3.xlsx", index = False)

        with pd.ExcelWriter(data_path + "corporate-finance-data.xlsx", engine = 'xlsxwriter') as writer:
            form_1.to_excel(writer, sheet_name="01_리그테이블", index=False)
            form_2.to_excel(writer, sheet_name="02_통합집계_Rawdata", index=False)
            form_3.to_excel(writer, sheet_name="03_IPO현황_Summary", index=False)