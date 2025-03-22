import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

# Load environment variables at the start
load_dotenv()

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--browserstack", action="store_true", default=False)

@pytest.fixture
def config(request):
    return {
        "browser": request.config.getoption("--browser"),
        "browserstack": request.config.getoption("--browserstack")
    }

@pytest.fixture
def driver():
    if os.getenv('BROWSERSTACK_RUN', 'false').lower() == 'true':
        # Print for debugging
        print(f"Username: {os.getenv('BROWSERSTACK_USERNAME')}")
        print(f"Access Key: {'*' * len(os.getenv('BROWSERSTACK_ACCESS_KEY', ''))}")
        
        options = webdriver.ChromeOptions()
        bstack_options = {
            'userName': os.getenv('BROWSERSTACK_USERNAME'),
            'accessKey': os.getenv('BROWSERSTACK_ACCESS_KEY'),
            'os': 'Windows',
            'osVersion': '10',
            'browserName': 'Chrome',
            'browserVersion': 'latest',
            'projectName': 'El Pais Scraper',
            'buildName': 'El Pais Test',
            'debug': 'true',
            'networkLogs': 'true'
        }
        options.set_capability('bstack:options', bstack_options)
        
        driver = webdriver.Remote(
            command_executor='https://hub.browserstack.com/wd/hub',
            options=options
        )
    else:
        options = Options()
        options.add_argument('--lang=es')
        driver = webdriver.Chrome(options=options)
    
    driver.implicitly_wait(10)
    yield driver
    driver.quit() 