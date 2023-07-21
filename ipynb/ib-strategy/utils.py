######################
### import library ###
######################
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from selenium import webdriver
from bs4 import BeautifulSoup

import requests
import pandas as pd
import numpy as np
import OpenDartReader
import warnings
import time
import re, os

warnings.filterwarnings('ignore')

## functions
def cleansing(x):
    if x != '-':
        try:
            value = int(re.sub("[^0-9]", "", x))
        except:
            value = 0
        return value 
    else :
        return 0
    
######################
### KIND 수집 관련 ###
######################
def go_kind(driver, code, FIRST = True):
    ## 01. 회사명 검색하기
    name_element = driver.find_element(By.ID, 'AKCKwd')
    name_element.click()
    name_element.clear()
    time.sleep(0.1)
    name_element.send_keys(code)

    time.sleep(0.25)
    ## 02. 신규상장만 활용
    if FIRST:
        check_box = '/html/body/section[2]/section/form/section/div/div[1]/table/tbody/tr[7]/td/label[{}]'

        for idx in range(1, 4):
            driver.find_element(By.XPATH, check_box.format(idx+2)).click()

        time.sleep(0.1)

    ## 03. 기간 전체 설정
    driver.find_element(By.CLASS_NAME, 'ord-07').click()
    
    ## 04. 검색 시작
    search_element = driver.find_element(By.CLASS_NAME, 'btn-sprite.type-00.vmiddle.search-btn')
    search_element.click()
    time.sleep(1.5)

def go_inner(driver):
    # table 확인
    temp_df = pd.read_html(driver.page_source)
    listing_df = [x for x in temp_df if "회사명" in x and "상장유형" in x][0]

    if listing_df['회사명'].values[0] != '조회된 결과값이 없습니다.':
        driver.find_element(By.CSS_SELECTOR, '#main-contents > section.scrarea.type-00 > table > tbody > tr').click()
        time.sleep(0.25)

        driver.switch_to.window(driver.window_handles[1])
        wait = WebDriverWait(driver, 10, poll_frequency=0.25)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-sprite.type-98.vmiddle")))
    else:
        return "검색실패"

def get_overview(driver):
    # 상장주식수
    l_cnt = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(3) > tbody > tr:nth-child(9) > td:nth-child(2)')
    l_cnt = cleansing(l_cnt.text)

    # 유통가능주식수
    c_cnt = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(3) > tbody > tr:nth-child(10) > td.txr')
    c_cnt = cleansing(c_cnt.text)

    # 주요 제품
    m_product = driver.find_element(By.CSS_SELECTOR, "#tab-contents > table:nth-child(3) > tbody > tr:nth-child(6) > td").text
    
    # 상장주선인
    corps = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(3) > tbody > tr:nth-child(11) > td:nth-child(2)').text
    
    # 공모가
    f_price = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(6) > tbody > tr.first > td:nth-child(4)').text
    f_price = cleansing(f_price)
    
    return l_cnt, c_cnt, m_product, corps, f_price

def get_inform(driver):
    # 경쟁률
    ratio = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr:nth-child(3) > td').text
    # 신주모집
    new_s = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(5) > tbody > tr:nth-child(2) > td:nth-child(2)').text
    new_s = cleansing(new_s)
    # 구주매출
    old_s = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table:nth-child(5) > tbody > tr:nth-child(3) > td:nth-child(2)').text
    old_s = cleansing(old_s)
    # 기관 배정 수량
    a_cnt = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-foot.mt3 > tbody > tr:nth-child(3) > td:nth-child(2)').text
    a_cnt = cleansing(a_cnt)
    # 상장일
    l_date = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr:nth-child(4) > td').text
    # 수요예측일정
    f_date = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr.first > td:nth-child(4)').text
    # 공모청약일정
    temp_date1 = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr:nth-child(2) > td:nth-child(2)').text
    # 납입일
    temp_date2 = driver.find_element(By.CSS_SELECTOR, '#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr:nth-child(2) > td:nth-child(4)').text
    
    return ratio, new_s, old_s, a_cnt, l_date, f_date, temp_date1, temp_date2

def get_finstate(driver): 
    dfs = pd.read_html(driver.page_source, header=0)

    try:
        get_idx = [idx for idx, x in enumerate(dfs) if "매출액(수익)" in list(x['항목']) and "영업이익(손실)" in list(x['항목']) and "당기순이익(손실)" in list(x['항목'])][0]
    except:
        get_idx = 1
    df = dfs[get_idx]
    df = df.loc[df['항목'].isin(['매출액(수익)', '영업이익(손실)', '당기순이익(손실)'])]
    t_year = re.sub("[^0-9]", "", df.columns[-1])

    if df.shape[0] != 3:
        except_values = [x for x in ['매출액(수익)', '영업이익(손실)', '당기순이익(손실)'] if x not in list(df['항목'])]
        append_df = pd.DataFrame({"항목":[x for x in except_values],
                      df.columns[1]:[0 for x in range(len(except_values))],
                      df.columns[2]:[0 for x in range(len(except_values))],
                      df.columns[3]:[0 for x in range(len(except_values))]})
        df = pd.concat([df, append_df])
        df['항목'] = df['항목'].astype("category")
        df['항목'] = df['항목'].cat.set_categories(['매출액(수익)', '영업이익(손실)', '당기순이익(손실)'])
        df = df.sort_values("항목")

    col_names = [x+"매출액" + "({})".format(y) for x, y in zip(['전전연도', '직전연도', '당해연도'], ['T-2', 'T-1', 'T'])]
    col_names.extend([x+"영업이익" + "({})".format(y) for x, y in zip(['전전연도', '직전연도', '당해연도'], ['T-2', 'T-1', 'T'])])
    col_names.extend([x+"당기순이익" + "({})".format(y) for x, y in zip(['전전연도', '직전연도', '당해연도'], ['T-2', 'T-1', 'T'])])

    df_change = pd.DataFrame.from_dict({x:[y] for x,y in zip(col_names, np.array(df.iloc[:, 1:]).reshape(1, -1)[0])})
    df_change['기준연도(T=)'] = t_year
    df_change.index = [0]

    return df_change

## kind 수집 main ##
def kind_main(driver, info_df, start_dt, end_dt):
    ## 01.KIND 접속
    driver.get("https://kind.krx.co.kr/listinvstg/listingcompany.do?method=searchListingTypeMain")

    wait = WebDriverWait(driver, 10, poll_frequency=0.25)
    wait.until(EC.presence_of_element_located((By.ID, "fromDate")))

    value = '-'
    cnt = 0
    
    for idx, code in enumerate(info_df.stock_code):
        time.sleep(1)

        # kind 접속 및 code 검색
        if idx == 0:
            go_kind(driver, code)
        else:
            go_kind(driver, code, False)

        try:
            wait = WebDriverWait(driver, 10, poll_frequency=0.25)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-contents > section.scrarea.type-00 > table > tbody > tr > td:nth-child(2)")))
            l_date1 = driver.find_element(By.CSS_SELECTOR, '#main-contents > section.scrarea.type-00 > table > tbody > tr > td:nth-child(2)').text

        except:
            continue

        # 세부 홉페이지 접속
        value = go_inner(driver)

        driver.switch_to.window(driver.window_handles[-1])
        wait = WebDriverWait(driver, 10, poll_frequency=0.25)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-contents > table:nth-child(6) > tbody > tr:nth-child(2) > td:nth-child(4)")))

        ## 회사 개요 수집
        # 상장주식수, 유통가능주식수, 제품, 상장주선인, 공모가
        l_cnt, c_cnt, m_product, corps, f_price = get_overview(driver)

        ## 공모 정보 수집
        driver.find_element(By.CSS_SELECTOR, '#tabName > a[title="공모정보"]').click()
        time.sleep(0.25)
        wait = WebDriverWait(driver, 10, poll_frequency=0.25)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-contents > table.detail.type-01.chain-head.mt10 > tbody > tr:nth-child(3) > td")))

        # 경쟁률, 신주모집, 구주매출, 기관 배정 수량, 상장일, 수요예측일정, 공모청약일정, 납입일
        ratio, new_s, old_s, a_cnt, l_date2, f_date, temp_date1, temp_date2 = get_inform(driver)
        l_date = max([l_date1, l_date2])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # dataframe 만들기
        keys = ["stock_code", "상장주식수", '주요제품', '상장주선인', '공모가'
                 ,'경쟁률', '신주모집', '구주매출', '기관배정수량', '상장일', '수요예측일정', '공모청약일정' ,'납입일']
        values = [code, l_cnt, m_product, corps, f_price,
                  ratio, new_s, old_s, a_cnt, l_date, f_date, temp_date1, temp_date2]
        temp_dict = {x:[y] for x, y in zip(keys, values)}

        if cnt == 0:
            kind_df = pd.DataFrame(temp_dict)
            cnt += 1
        else:
            loop_df = pd.DataFrame(temp_dict)
            kind_df = pd.concat([kind_df, loop_df])

    kind_df = kind_df.loc[(kind_df['상장일'] >= start_dt) & (kind_df['상장일'] <= end_dt)]
    driver.close()
    
    select_cols = ['corp_name', 'corp_code','stock_code', 'corp_cls', 'rcept_no']
    first_df = pd.merge(info_df.loc[:, select_cols], kind_df, on ='stock_code', how = 'inner')

    # 후처리
    first_df['공모주식수'] = first_df['신주모집'] + first_df['구주매출']
    first_df['수요예측(시작일)'] = [x.split(" ~ ")[0] for x in first_df['수요예측일정']]
    first_df['수요예측(종료일)'] = [x.split(" ~ ")[1] for x in first_df['수요예측일정']]
    first_df['청약일'] = [x.split(" ~ ")[0] for x in first_df['공모청약일정']]

    del first_df['수요예측일정'], first_df['공모청약일정']
    
    return first_df

################################
### 38커뮤니케이션 수집 관련 ###
################################
def get_38df(soup, x):
    return pd.read_html(str(soup.select('table[summary="{}"]'.format(x))[0]))[0]

def change_corp(x):
    if "모간스탠리" in x : return "MS"
    elif "골드" in x : return "골드만"
    elif "씨티" in x : return "씨티"
    elif "메릴" in x : return "메릴린치"
    elif "케이비" in x : return "KB"
    elif "스위스" in x : return "CS"
    elif "엔에이치" in x : return "NH"
    elif "아이비케이" in x : return "IBK"
    elif "에스케이" in x : return "SK"
    elif "디비금융" in x : return "DB"
    else: return x.replace("투자", "").replace("금융", "").replace("증권", "").replace("에셋", "").replace("(주)", "").replace("㈜", "")

def change(x):
    return x.replace('TE', 'TD').replace('TU', 'TD')

def get_38(start_dt, end_dt, max_page = 30):
    cnt = 0
    p = 0

    for page in range(1, max_page+1):
        outer_url = 'http://www.38.co.kr/html/fund/index.htm?o=r1&page={}'.format(page)
        base_url = 'http://www.38.co.kr/html/fund'

        response = requests.get(outer_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tb_src = soup.select('table[summary="수요예측결과"]')

        temp_df = pd.read_html(str(tb_src))[0]
        temp_df = temp_df.loc[~temp_df['기업명'].isna()]

        if cnt == 0:
            url_tags = soup.select('tbody > tr > td > a')
            temp_df['url'] = [base_url + x.attrs['href'].split(".")[-1] for x in url_tags]
            outer_df = temp_df

        else:
            url_tags = soup.select('tbody > tr > td > a')
            temp_df['url'] = [base_url + x.attrs['href'].split(".")[-1] for x in url_tags]
            outer_df = pd.concat([outer_df, temp_df])

        if temp_df['예측일'].min() < start_dt.replace("-", "."):
            p += 1
            if p > 1:
                break
                
        cnt += 1

    data_dict = {x:[] for x in ['stock_code', '기업명']}

    for name, url in zip(outer_df['기업명'], outer_df['url']):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        overview_df = get_38df(soup, '기업개요')
        overview_df.columns = ["O" + str(x) for x in range(overview_df.shape[1])]

        # 종목 코드
        code = overview_df.loc[overview_df.O2 == '종목코드', 'O3'].values[0]

        data_dict['stock_code'].append(code)
        data_dict['기업명'].append(name)

    inner_df = pd.DataFrame.from_dict(data_dict)
    outer_df = pd.merge(outer_df, inner_df, on = '기업명', how = 'inner')
    
    select_cols = ['stock_code', '하단공모가액', '상단공모가액', '의무보유 확약', '기관 경쟁률']
    outer_df['하단공모가액'] = [cleansing(x.split("~")[0]) for x in outer_df['공모희망가(원)']]
    outer_df['상단공모가액'] = [cleansing(x.split("~")[1]) for x in outer_df['공모희망가(원)']]
    
    return outer_df.loc[:, select_cols]

######################
### DART 수집 관련 ###
######################
def get_table(xml_text, title):
    table_src = re.findall('{}</TITLE>.*?</TABLE-GROUP>'.format(title), xml_text)
    value = pd.read_html(change(table_src[0]))
    
    if len(value) > 1:
        value = value[1]
    else:
        value = value[0]
        
    return value

def get_dd(dart, second_df):
    dart_dict = {x:[] for x in ['대표주관회사', '인수회사', 'corp_code']}

    for corp_code in second_df.corp_code:
        temp_df = dart.regstate(corp_code, '지분증권')

        if temp_df.shape[0] == 0:
            dart_dict['대표주관회사'].append("-")
            dart_dict['인수회사'].append("-")
            dart_dict['corp_code'].append(corp_code)
        else:
            # 컬럼명 변경
            origin_feats = ['rcept_no', 'corp_cls', 'corp_code', 'corp_name', 'sbd', 'pymd', 'sband', 'asand', 'asstd', 'exstk', 'exprc', 'expd', 
                        'rpt_rcpn', 'title', 'stksen', 'stkcnt', 'fv', 'slprc', 'slta', 'slmthn', 'actsen',
                        'actnmn', 'udtcnt', 'udtamt', 'udtprc', 'udtmth', 'se', 'amt', 'hdr',
                        'rl_cmp', 'bfsl_hdstk', 'slstk', 'atsl_hdstk', 'grtrs', 'exavivr', 'grtcnt']

            change_feats = ['접수번호', '법인구분', '고유번호', '회사명', '청약기일', '납입기일', '청약공고일', '배정공고일', '배정기준일', '행사대상증권','행사가격', '행사기간' ,
                            '주요사항보고서(접수번호)', '그룹명칭', '증권의종류', '증권수량', '액면가액', '모집(매출)가액', '모집(매출)총액', '모집(매출)방법', '인수인구분', 
                            '인수인명', '인수수량', '인수금액', '인수대가', '인수방법', '구분', '금액', '보유자',
                            '회사와의관계', '매출전보유증권수', '매출증권수', '매출후보유증권수', '부여사유', '행사가능투자자', '부여수량']

            change_dict = {x:y for x, y in zip(origin_feats, change_feats)}

            temp_df.columns = [change_dict[x] for x in temp_df.columns]
            temp_df = temp_df.loc[temp_df['접수번호'] == np.max(temp_df['접수번호'].unique())]
            temp_df.index = [x for x in range(temp_df.shape[0])]

            # 증권사 이름 전처리
            temp_df['인수인명'] = [x if type(x) != str else change_corp(x) for x in temp_df['인수인명']]
            base_df = temp_df.loc[~temp_df['인수인명'].isna()]

            # IB1본부 양식 전처리
            df1 = temp_df.loc[[True if (type(x) != float) and ("대표" in x) else False for x in temp_df['인수인구분']], :]

            dart_dict['대표주관회사'].append(", ".join(df1['인수인명']))
            dart_dict['인수회사'].append(", ".join(base_df['인수인명']))
            dart_dict['corp_code'].append(corp_code)

            if (base_df.shape[0] == 1) and (base_df['인수인구분'].values[0] in ("주1)", "-", "")):
                dart_dict['대표주관회사'] = dart_dict['인수회사']

    dart_df = pd.DataFrame(dart_dict)
    third_df = pd.merge(second_df, dart_df, on = 'corp_code', how = 'inner')
    
    return third_df

def get_d_tables(dart, third_df):
    cnt = 0
    
    for rcept_no in third_df.rcept_no:
        xml_text = dart.document(rcept_no)
        xml_text = xml_text.replace("\n", "")

        try:
            temp_df = get_table(xml_text, '인수기관별 인수금액')
            temp_df.columns = ['인수기관', '인수수량', '인수금액', '비율', '비고']
        except:
            soup = BeautifulSoup(xml_text, 'html.parser')
            table_src = [str(x) for x in soup.find_all('table')]
            temp_df = [pd.read_html(x)[0] for x in table_src if ("인수기관" in x) and ("인수수량" in x)][0]
            temp_df.columns = ['인수기관', '인수수량', '인수금액', '비율', '비고']
        temp_df = temp_df.loc[~temp_df['인수기관'].isin(['합계', '계'])]
        temp_df['rcept_no'] = rcept_no

        if cnt == 0:
            corp_table = temp_df
        else:
            corp_table = pd.concat([corp_table, temp_df])

        cnt += 1

    corp_table['인수기관'] = [x if type(x) != str else change_corp(x) for x in corp_table['인수기관']]
    corp_table['비율'] = [float(re.sub("[^0-9.]", "", x))  if type(x) == str else x for x in corp_table['비율']]
    corp_table['인수수량'] = [cleansing(x) if type(x) == str else x for x in corp_table['인수수량']]
    corp_table['인수금액'] = [cleansing(x) if type(x) == str else x for x in corp_table['인수금액']]

    for no in corp_table.rcept_no:
        temp_df = corp_table.loc[corp_table.rcept_no == no]
        if temp_df.shape[0] == 1:
            corp_table.loc[corp_table.rcept_no == no, '비고'] = '대표주관회사'

    fourth_df = pd.merge(third_df, corp_table, on = 'rcept_no')
    
    # 후처리
    select_rows = [True if "리츠" in x else False for x in fourth_df.corp_name]

    if sum(select_rows) > 0:
        temp_df2 = fourth_df.loc[select_rows, :]

        for corp_name in temp_df2.corp_name.unique():
            temp_df3 = temp_df2.loc[temp_df2.corp_name == corp_name, :]
            df1 = temp_df3.loc[[True if (type(x) != float) and ("대표" in x) else False for x in temp_df3['비고']], :]

            fourth_df.loc[fourth_df['corp_name'] == corp_name, '대표주관회사'] = ", ".join(df1['인수기관'])
            fourth_df.loc[fourth_df['corp_name'] == corp_name, '인수회사'] = ", ".join(temp_df3['인수기관'])

            third_df.loc[third_df['corp_name'] == corp_name, '대표주관회사'] = ", ".join(df1['인수기관'])
            third_df.loc[third_df['corp_name'] == corp_name, '인수회사'] = ", ".join(temp_df3['인수기관'])

    if "" in list(fourth_df['대표주관회사']):
        fourth_df.loc[fourth_df['대표주관회사'] == '', ['대표주관회사']] = fourth_df['인수회사']

    if "" in list(third_df['대표주관회사']):
        third_df.loc[third_df['대표주관회사'] == '', ['대표주관회사']] = third_df['인수회사']
    
    return third_df, fourth_df

###########################
### IPO Stock 수집 관련 ###
###########################
def ipo_main(driver, info_df):
    # driver 실행
    url = 'http://www.ipostock.co.kr/sub03/ipo05.asp'

    col_names = [x+"매출액" + "({})".format(y) for x, y in zip(['당해연도', '직전연도', '전전연도'], ['T', 'T-1', 'T-2'])]
    col_names.extend([x+"영업이익" + "({})".format(y) for x, y in zip(['당해연도', '직전연도', '전전연도'], ['T', 'T-1', 'T-2'])])
    col_names.extend([x+"당기순이익" + "({})".format(y) for x, y in zip(['당해연도', '직전연도', '전전연도'], ['T', 'T-1', 'T-2'])])
    
    cnt = 0

    for idx, corp_name in enumerate(info_df.corp_name):
        driver.get(url)
        wait = WebDriverWait(driver, 10, poll_frequency=0.25)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                                                   'body > table:nth-child(1) > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(4) > td > table > tbody > tr:nth-child(1) > td > form > table > tbody > tr:nth-child(2) > td > input.GBOX')))

        search_element = driver.find_element(By.CSS_SELECTOR,
                                             'body > table:nth-child(1) > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(4) > td > table > tbody > tr:nth-child(1) > td > form > table > tbody > tr:nth-child(2) > td > input.GBOX')
        search_element.click()
        time.sleep(0.1)
        search_element.send_keys(corp_name)
        driver.find_element(By.CSS_SELECTOR, 
                       'body > table:nth-child(1) > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(4) > td > table > tbody > tr:nth-child(1) > td > form > table > tbody > tr:nth-child(2) > td > input[type=image]:nth-child(2)').click()

        td_values = driver.find_elements(By.CSS_SELECTOR, 
                                         '#print > table > tbody > tr:nth-child(4) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > a')

        if len(td_values) > 0:
            td_values[0].click()
        else:
            continue

        # 주주구성
        try:
            driver.find_element(By.CSS_SELECTOR, 'img[alt="주주구성"]').click()
            wait = WebDriverWait(driver, 5, poll_frequency=0.25)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="print"]/table/tbody/tr[8]/td/table[2]/tbody')))

            raw_tbls = pd.read_html(driver.page_source, header = 0)
            tbls1 = [x for x in raw_tbls if "보유주식" in x][0]
            u_cnt = tbls1.loc[tbls1['구 분'] == '공모후 상장주식수', ['보유주식']].values[0][0]
        except:
            u_cnt = 0

        try:
            # 재무정보
            driver.find_element(By.CSS_SELECTOR, 'img[alt="재무정보"]').click()

            wait = WebDriverWait(driver, 5, poll_frequency=0.25)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="print"]/table/tbody/tr[6]/td/table[2]')))

            raw_tbls = pd.read_html(driver.page_source, header = 0)
            tbls = [x for x in raw_tbls if "구분" in x][0]

            df = np.array(tbls.loc[tbls['구분'].isin(['매출액', '영업이익', '당기순이익'])].iloc[:, 1:]).reshape(1, -1)[0]

            t_year = tbls.loc[tbls['구분'] == '구분'].iloc[:, 1].values[0].split("년")[0]

            df_change = pd.DataFrame.from_dict({x:[y] for x,y in zip(col_names, df)})
            df_change['기준연도(T=)'] = t_year
            df_change.index = [0]
            df_change['유통가능주식수'] = u_cnt

        except:
            df_change = pd.DataFrame.from_dict({x:[0] for x in col_names})
            df_change.index = [0]
            df_change['기준연도(T=)'] = '-'
            df_change['유통가능주식수'] = u_cnt

        df_change['corp_name'] = corp_name

        if cnt == 0:
            ipo_df = df_change
            cnt += 1
        else:
            ipo_df = pd.concat([ipo_df, df_change])
            
    driver.close()
    ipo_df['유통가능주식수'] = [cleansing(x) for x in ipo_df['유통가능주식수']]
    ipo_df.loc[:, '당해연도매출액(T)':'전전연도당기순이익(T-2)'] = ipo_df.loc[:, '당해연도매출액(T)':'전전연도당기순이익(T-2)'].astype(float)
    
    return ipo_df

###########################
### 자료 형태 변환 관련 ###
###########################
def change_form(df, dept, opt = None):
    if dept == 'IB전략':
        select_cols = ['수요예측(시작일)', '수요예측(종료일)', '상장일', '대표주관회사', 'corp_name', '신주모집', '구주매출',
              '하단공모가액', '상단공모가액', '상장주식수', '유통가능주식수', '공모가', '기관 경쟁률', '의무보유 확약',
              '전전연도매출액(T-2)', '직전연도매출액(T-1)', '당해연도매출액(T)',
               '전전연도영업이익(T-2)', '직전연도영업이익(T-1)', '당해연도영업이익(T)', '전전연도당기순이익(T-2)',
               '직전연도당기순이익(T-1)', '당해연도당기순이익(T)', '기준연도(T=)', '주요제품']
        change_cols = {"corp_name": "회사명", "기관 경쟁률":"경쟁률"}

        output = df.loc[:, select_cols]
        output['공모주식수'] = output['신주모집'] + output['구주매출']
        output = output.rename(columns = change_cols)
        
        sorted_cols = ['수요예측(시작일)', '수요예측(종료일)', '상장일', '대표주관회사', '회사명', '공모주식수','신주모집', '구주매출',
                      '하단공모가액', '상단공모가액', '상장주식수', '유통가능주식수', '공모가', '경쟁률', '의무보유 확약',
                      '전전연도매출액(T-2)', '직전연도매출액(T-1)', '당해연도매출액(T)',
                       '전전연도영업이익(T-2)', '직전연도영업이익(T-1)', '당해연도영업이익(T)', '전전연도당기순이익(T-2)',
                       '직전연도당기순이익(T-1)', '당해연도당기순이익(T)', '기준연도(T=)', '주요제품']
        output = output.loc[:, sorted_cols]
        output['유통가능주식수'] = [0 for x in range(output.shape[0])]
        del output['기준연도(T=)']
        
    else:
        if opt == 1:
            select_cols = ['상장일', 'corp_name', 'corp_cls', '인수기관', '인수금액', '비고', '공모가', '비율', '기관배정수량', '청약일', '납입일']
            output = df.loc[:, select_cols]

            right_df = output.groupby('corp_name')[['인수금액', '기관배정수량']].sum().reset_index()
            right_df.columns = ['corp_name', '발행금액', '총기관배정수량']

            output = pd.merge(output.loc[:, ~output.columns.isin(['기관배정수량'])], right_df, on = 'corp_name')

            output['인수수수료'] = '-'
            output['청약수수료추정'] = '-'
            output['수수료합계'] = '-'
            output['건수'] = '-'
            output['상장트랙'] = '-'

            change_cols = {"corp_name":"업체", "corp_cls":"시장구분", "비고":"주관형태", "인수기관":"인수회사"}
            output.rename(columns = change_cols, inplace = True)

            select_cols = ['상장일', '업체', '시장구분', '발행금액', '인수회사', '인수금액', '인수수수료', '청약수수료추정', '수수료합계', '건수',
                           '주관형태', '상장트랙', '공모가', '비율', '청약일', '납입일', '총기관배정수량']
            output['주관형태'] = [x.replace("주관회사", "").replace("회사", "") for x in output['주관형태']]
            
            output = output.loc[:, select_cols]
            output['발행금액'] /= 100000000
            output['인수금액'] /= 100000000

            
        elif opt == 2:
            select_cols = ['청약일', 'corp_name', '대표주관회사', '납입일', '상장일', '신주모집', '구주매출', '공모가', '공모주식수',
                          '하단공모가액', '상단공모가액', '경쟁률']

            output = df.loc[:, select_cols]

            output['공모금액(천원)'] = (output['신주모집'] + output['구주매출']) * output['공모가'] / 1000
            output['구주매출비중'] = (output['구주매출']) / (output['신주모집'] + output['구주매출']) * 100
            output['기준가(평가가치)'] = '-'
            output['수요예측가중평균가'] = '-'
            output['결정비율'] = '-'
            output['코넥스여부'] = '-'
            output['공모비율'] = '-'
            output['상장요건'] = '-'
            output['인수수수료(천원)'] = '-'
            output['수수료율'] = '-'

            change_cols = {'corp_name':'회사명', "하단공모가액":'1차발행가액(하단)', "상단공모가액":"1차발행가액(상단)",
                          "공모주식수":"공모주수", "공모가":"확정발행가액"}
            output.rename(columns = change_cols, inplace = True)

            sorted_cols = ['청약일', '회사명', '대표주관회사', '납입일', '상장일', '공모금액(천원)', 
                           '공모주수',
                           '기준가(평가가치)','1차발행가액(하단)', '1차발행가액(상단)', '수요예측가중평균가',
                           '확정발행가액', 
                           '결정비율', '공모비율','구주매출비중', '상장요건','코넥스여부','경쟁률', '인수수수료(천원)', '수수료율']
            output = output.loc[:, sorted_cols]
            
        else:
            change_cols = {"corp_name": "회사명", "인수금액":"공모금액(백만원)", "비율":"인수비율"}
            select_cols = ['인수기관', '청약일', 'corp_name', '대표주관회사', '인수회사', '납입일', '상장일', '인수금액', '신주모집', '구주매출', '공모가', '비율']
            output = df.loc[:, select_cols]
            
            output['공모주수'] = output['신주모집'] + output['구주매출']
            output['인수수수료'] = 0
            
            output = output.rename(columns = change_cols)
            select_cols = ['인수기관', '청약일', '회사명', '대표주관회사', '인수회사', '납입일', '상장일', '공모금액(백만원)', '공모주수', '공모가', '인수수수료', '인수비율']
            output['공모금액(백만원)'] /= 1000000
            output = output.loc[:, select_cols].sort_values("인수기관")
            
    return output