from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st
import os, sys

import subprocess
st.write(subprocess.call("whereis firefox", shell=True))
st.write(a)

_ = installff()
st.write("finish-install")

#opts = FirefoxOptions()
#opts.add_argument("--headless")
#firefox_binary = FirefoxBinary('/home/appuser/venv/bin/firefox.exe')
#st.write("set-binary")

#opts.binary = firefox_binary
#opts.binary_location = '/home/appuser/venv/bin/geckodriver'
#opts.binary_location = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver.exe'
#opts.binary_location = '/home/appuser/venv/bin/firefox.exe'

#service = Service(GeckoDriverManager().install())
st.write("set-service")
#browser = webdriver.Firefox(service = service, options=opts)
st.write("run-browser")
#browser = webdriver.Firefox(options=opts)
options = Options()
options.add_argument("--headless")
options.binary_location("/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver")

#browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

#browser = webdriver.Chrome(service = Service(excutable_path = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver'), options = options)
browser = webdriver.Chrome(options = options)

#browser.get('http://naver.com')
st.write(browser.page_source)