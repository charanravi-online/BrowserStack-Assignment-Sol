import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

# Load environment variables at the start
# This loads variables from .env file into environment variables
# Used to access BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY, RAPIDAPI_KEY, etc.
load_dotenv()

# This fixture is used in test_elpais_scraper.py for test functions
# The fixture provides a configured WebDriver instance that connects to BrowserStack
# for remote testing on real devices and browsers
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # BrowserStack configuration options
    # These settings determine which device/browser to use for testing
    bstack_options = {
        'userName': os.getenv('BROWSERSTACK_USERNAME'),
        'accessKey': os.getenv('BROWSERSTACK_ACCESS_KEY'),
        'deviceName': 'iPhone 13',
        'osVersion': '15',
        'browserName': 'safari',
        'deviceOrientation': 'portrait',
        'projectName': 'El Pais Scraper',
        'buildName': 'El Pais Test',
        'debug': 'true',
        'networkLogs': 'true',
        'realMobile': 'true'
    }
    options.set_capability('bstack:options', bstack_options)
    
    # Print capabilities for debugging
    print("Setting up with capabilities:", bstack_options)
    
    # Create a remote WebDriver that connects to BrowserStack's Selenium grid
    driver = webdriver.Remote(
        command_executor='https://hub.browserstack.com/wd/hub',
        options=options
    )
    
    # Set implicit wait to avoid immediate failures when elements aren't instantly available
    driver.implicitly_wait(10)
    # Yield the driver to the test function
    yield driver
    # After the test completes, quit the driver to clean up resources
    driver.quit() 