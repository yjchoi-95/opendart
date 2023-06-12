from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager.firefox import GeckoDriverManager
import streamlit as st
import os, sys

import subprocess
#st.write(subprocess.call("whereis firefox", shell=True))
#st.write(a)

@st.cache_resource
def installff():
    #os.system('/home/appuser/venv/bin/python -m pip install --upgrade pip')
    os.system('cd . add-apt-repository ppa:ubuntu-mozilla-security/ppa')
    os.system('sbase install geckodriver')
    #os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/geckodriver')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/firefox')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/firefox.exe')
    #os.system('export PATH=$PATH:/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
    
_ = installff()
st.write("finish-install")

opts = FirefoxOptions()
opts.add_argument("--headless")
#firefox_binary = FirefoxBinary('/home/appuser/venv/bin/firefox.exe')
#st.write("set-binary")

#opts.binary = firefox_binary
#opts.binary_location = '/home/appuser/venv/bin/geckodriver'
#opts.binary_location = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver.exe'
opts.binary_location = '/home/appuser/venv/bin/firefox.exe'

#service = Service(GeckoDriverManager().install())
st.write("set-service")
#browser = webdriver.Firefox(service = service, options=opts)
st.write("run-browser")
browser = webdriver.Firefox(options=opts)


browser.get('http://naver.com')
st.write(browser.page_source)