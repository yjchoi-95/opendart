# 라이브러리
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from selenium import webdriver
from tqdm import tqdm
from bs4 import BeautifulSoup
from IB_utils import *
from datetime import datetime, timedelta, date

import requests
import streamlit as st
import pandas as pd
import numpy as np
import OpenDartReader
import warnings
import time
import re, os

warnings.filterwarnings('ignore')

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

# 셀레늄 실행
def get_driver(viz_opt = False):
    options = Options()
    options.add_argument('--headless')
    
    if viz_opt:
        return webdriver.Chrome()
    else:
        return webdriver.Chrome(options=options)

# RPA 코드 실행
def main():
    opt = 'IB전략'
    ### STEP1. 수집 시작 및 종료 날짜 할당
    # 신고서 제출일, 상장일, 수요예측일 간 차이를 반영하기 위해서 start_dt,start_dt2, start_dt3를 할당
    today = date.today()
    end_dt = datetime.strftime(today, '%Y-%m-%d')
    diff_day = timedelta(days=60)
    start_dt = datetime.strftime(today - diff_day, '%Y-%m-%d')
    start_dt2 = datetime.strftime(datetime.strptime(end_dt, '%Y-%m-%d') - timedelta(days = 80), '%Y-%m-%d')
    start_dt3 = datetime.strftime(datetime.strptime(end_dt, '%Y-%m-%d') - timedelta(days = 180), '%Y-%m-%d')
    
    ### STEP2. opendartreader 활용, 주어진 기간 내 증권신고서, 증권발행실적 보고서 가져오기
    dart_df, dart = initial_set(start_dt2, end_dt)

    ### STEP3. KIND 수집 항목 가져오기, 셀레늄 사용, 이 경우 viz_opt를 True로 함으로써 수집해야 함, False 시 조회 불가
    driver = get_driver(viz_opt = True)
    driver.set_window_size(1920, 1080)
    table = set_kind(driver, start_dt3, end_dt)
    kind_output = get_kind_inner(driver, table)
    first_df = post_proc(dart_df, kind_output, start_dt)

    ### STEP4. ipo stock 수집 항목 가져오기, 셀레늄 사용
    driver = get_driver()
    driver.set_window_size(1920, 1080)
    ipo_df = ipo_main(driver, first_df)
    first_df = pd.merge(first_df, ipo_df, on = 'corp_name', how = 'left')
    first_df.replace(np.NaN, 0, inplace = True)
    first_df['key'] = [change_join(x) if "스팩" in x else x for x in list(first_df.corp_name)]

    ### STEP5. 38커뮤니케이션 수집 항목 가져오기
    outer_df = get_38(start_dt, end_dt)
    second_df = pd.merge(first_df, outer_df, left_on = 'key', right_on = '기업명', how = 'inner')
    del second_df['기업명'], second_df['key'], second_df['stock_code_x']
    second_df.rename(columns = {'stock_code_y':'stock_code'}, inplace = True)

    ### STEP6. 현업 양식에 맞게끔 변경, opendartreader 활용, 인수인 정보 수집
    third_df = get_dd(dart, second_df)
    third_df, fourth_df = get_d_tables(dart, third_df)
    head_df = change_form(third_df, opt)

    ### STEP7. 파일 저장 및 갱신
    data_path = './datasets/'

    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    if os.path.isfile(data_path + "ib-strategy-data.xlsx"):
        origin_df = read_data(data_path + "ib-strategy-data.xlsx")
        origin_df = pd.concat([origin_df, head_df]).sort_values("수요예측(시작일)").drop_duplicates()
        origin_df.to_excel(data_path + "ib-strategy-data.xlsx", index = False)
    else:
        head_df.to_excel(data_path + "ib-strategy-data.xlsx", index = False)

if __name__=="__main__":
    main()