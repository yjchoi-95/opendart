from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import streamlit as st
import os, sys

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


import subprocess

st.write(subprocess.call("whereis firefox", shell=True))
#st.write(a)

@st.cache_resource
def installff():
    os.system('/home/appuser/venv/bin/python -m pip install --upgrade pip')
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    os.system('export PATH=$PATH:/home/appuser/venv/bin/geckodriver')
    
_ = installff()

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
opts = FirefoxOptions()
opts.add_argument("--headless")
firefox_binary = FirefoxBinary('/home/appuser/venv/bin/firefox.exe')
opts.binary = firefox_binary
#opts.binary_location = '/home/appuser/venv/bin/geckodriver'

service = Service(GeckoDriverManager().install())
browser = webdriver.Firefox(service = service, options=opts)
#browser = webdriver.Firefox(service = service, options=opts)


browser.get('http://naver.com')
st.write(browser.page_source)