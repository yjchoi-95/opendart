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

st.write("set-service")
st.write("run-browser")
