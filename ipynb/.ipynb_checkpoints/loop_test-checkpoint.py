'''
import streamlit as st
from streamlit_modal import Modal
import time
import streamlit.components.v1 as components

year = 2022
r_code = '사업보고서'

modal = Modal(key="Demo Key", title="※ 데이터 존재".format(year, r_code))

#open_modal = st.button("Open")

#if open_modal:
#    modal.open()

open_modal = False
time.sleep(5)
open_modal = True

if open_modal:
    modal.open()

if modal.is_open():
    with modal.container():
        st.write("ECM_타법인출자-단순투자-{}-{} 파일이 존재합니다. 재수집하시겠습니까?".format(year,r_code))
        st.write("(아니오 선택 시 기존 파일을 불러옵니다)".format(year,r_code))
        inside_c1, inside_c2 = st.columns(2)
        with inside_c1:
            btn1 = st.button('예')
        with inside_c2:
            btn2 = st.button('아니오')
        
        if btn1 or btn2:
            modal.close()
'''

'''
import streamlit as st

year = 2022
r_code = '사업보고서'

st.warning("""ECM_타법인출자-단순투자-{}-{} 파일이 저장소에 존재합니다. 
\n 재수집하시겠습니까?""".format(year,r_code), icon="⚠️")
inside_c1, inside_c2 = st.columns(2)
with inside_c1:
    btn1 = st.button('예')
with inside_c2:
    btn2 = st.button('아니오')

if btn1:
    st.write("hi")
elif btn2:
    st.write("hello")
'''

'''
import streamlit as st

form1_bt = st.button('조회')

if st.session_state.get('button') != True:
    st.session_state['button'] = form1_bt

if st.session_state['button'] == True:
    inside_c1, inside_c2 = st.columns(2)
    
    with inside_c1:
        btn1 = st.button('예')
    with inside_c2:
        btn2 = st.button('아니오')
    
    if btn1:
        st.write("btn1")
    elif btn2:
        st.write("btn2")
    else:
        st.write("btn3")
'''


import streamlit as st
import numpy as np
import pandas as pd

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('CP949')    


array = np.array([1,2,3])
array = pd.DataFrame(array)
save_df = convert_df(array)
            

form1_bt = st.button('조회')
        
if st.session_state.get('button') != True:
    st.session_state['button'] = form1_bt

if st.session_state['button'] == True:
    genre = st.radio(
        "What\'s your favorite movie genre",
        ('Comedy', 'Drama', 'Documentary'), horizontal =True)

    if genre == 'Documentary':
        st.write('You selected comedy.')
        st.download_button(label="Download", data=save_df, file_name='test', mime='text/csv')
    elif genre == "Drama":
        st.write("You didn\'t select comedy.")
        st.download_button(label="Download", data=save_df, file_name='test', mime='text/csv')
    else:
        st.write("hi")