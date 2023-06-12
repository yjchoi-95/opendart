from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import streamlit as st
import os, sys

@st.experimental_singleton
def installff():
    os.system('/home/appuser/venv/bin/python -m pip install --upgrade pip')
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    options.binary_location = '/home/appuser/venv/bin/geckodriver'
    
_ = installff()

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
opts = FirefoxOptions()
opts.add_argument("--headless")
service = Service(GeckoDriverManager().install())
browser = webdriver.Firefox(service = service, options=opts)


browser.get('http://naver.com')
st.write(browser.page_source)