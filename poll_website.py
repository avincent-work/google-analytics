"""
Poll pages on my test web app, for generating Google analytics data.
Uses Selenium with Chromedriver to generate the hits, randomly
selecting one of the pages in the app. Pauses between hits, to stop
the site thinking it's a DOS.

Notes:
- Sadly, simply making HTTP GET requests to the page doesn't work;
Google Analytics doesn't register the hits.
- Similarly, running Chromedriver headlessly doesn't register any hits;
it *MUST* use an actual browser window.
"""

#======================================================================
# Import libraries
#======================================================================
import argparse
import os
import random
import time

from selenium import webdriver

import config as cfg

#======================================================================
# Module-level constants
#======================================================================
MAX_CLICKS = 1      # max number of clicks to use
NUM_REQUESTS = 10   # number of requests (for Heroku page)
WAIT_TIME = 2       # set poling parameters (seconds)

click_count = {
    cfg.INDEX["RED_BTN_ID"]: 0,
    cfg.INDEX["YELLOW_BTN_ID"]: 0,
    cfg.INDEX["GREEN_BTN_ID"]: 0,
    cfg.GRAPHS["ID"]: 0,
    cfg.MAPS["ID"]: 0,
    cfg.CAROUSEL["ID"]: 0
}

#======================================================================
# Functions
#======================================================================
def click_element(driver, elem_id):
    elem = driver.find_element_by_id(elem_id)
    elem.click()

def index_button_clicks(driver):
    btn_id = random.choice(list(cfg.INDEX.values()))
    click_element(driver, btn_id)
    click_count[btn_id] += 1

def graphs_button_clicks(driver):
    btn_id = cfg.GRAPHS["ID"]
    click_element(driver, btn_id)
    click_count[btn_id] += 1

def maps_button_clicks(driver):
    btn_id = cfg.MAPS["ID"]
    click_element(driver, btn_id)
    click_count[btn_id] += 1

def carousel_button_clicks(driver):
    btn_id = cfg.CAROUSEL["ID"]
    click_element(driver, btn_id)
    click_count[btn_id] += 1

def page_interactions(url, driver):
    # navigate to page    
    driver.get(url)

    # split the URL into two components; the base, and the page-name
    split_url = url.rsplit(sep="/", maxsplit=1)
    suffix = split_url[1] if len(split_url) != 1 else ""
    
    # decide how many clicks there are going 
    num_clicks = random.randint(1, MAX_CLICKS)
    for _ in range(num_clicks):
        # home page
        if suffix == "":
            index_button_clicks(driver)
        # home page, but using a referral URL
        elif suffix[0] == "?":
            index_button_clicks(driver)
        # graphs page
        elif suffix == "graphs":
            graphs_button_clicks(driver)
        # maps page
        elif suffix == "maps":
            maps_button_clicks(driver)
        # carousel page
        elif suffix == "carousel":
            carousel_button_clicks(driver)
        # about page
        elif suffix == "about":
            pass
        # otherwise: unexpected page, debugging required
        else:            
            print(f"{'*'*53}\n*** ERROR: identify_page(), unexpected URL suffix ***\n{'*'*53}")
        time.sleep(WAIT_TIME)

def get_urls(base_url):
    return [
        base_url,
        f"{base_url}graphs",
        f"{base_url}maps",
        f"{base_url}carousel",
        f"{base_url}about"
    ]

def poll_site(urls, num_requests, wait_time, chromedrive_path):
    for i in range(num_requests):              
        # spin up the browser, point to a randomly-chosen URL, wait a
        # few seconds, then kill the browser. Wait for next iteration
        driver = webdriver.Chrome(executable_path=chromedrive_path)
        url = random.choice(urls)
        # driver.get(url)
        page_interactions(url, driver)

        time.sleep(wait_time)
        driver.quit()
        print(f"> Request {i+1} completed")
        time.sleep(wait_time)

def poll_heroku(num_requests, wait_time, chromedriver_path):
    # set URL parameters
    BASE_URL = "https://ggl-analytics-test.herokuapp.com/"    
    URLS = get_urls(BASE_URL)
    URLS.append(f"{BASE_URL}?utm_source=wix%2Fal-net&utm_medium=referral&utm_campaign=link_test&utm_term=bumbling")
    
    poll_site(URLS, num_requests, wait_time, chromedriver_path)

def poll_azure(num_requests, wait_time, chromedriver_path):
    # set URL parameters
    BASE_URL = "https://ga4-test.azurewebsites.net/"
    URLS = get_urls(BASE_URL)
    
    poll_site(URLS, num_requests, wait_time, chromedriver_path)

#======================================================================
# Drivers
#======================================================================
def parse_arguments():
    """Parse command-line arguments / flags, to change the default
    behaviour of the processor.
    
    Returns:
        - argparse ArgumentParser object, containing all the arguments
        provided in the namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--azure",
                        help=("Poll the Azure deployment, instead of "
                              " the Heroku deployment (default)."),
                        action="store_true")
    return parser.parse_args()


def main():        

    # chromedriver is in the same directory as this script
    CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "chromedriver.exe")

    args = parse_arguments()    
    if args.azure:
        print(f"\n{'*'*32}\n*** Polling Azure Deployment ***\n{'*'*32}\n")
        num_requests = 10
        poll_azure(num_requests, WAIT_TIME, CHROMEDRIVER_PATH)
    else:
        poll_heroku(NUM_REQUESTS, WAIT_TIME, CHROMEDRIVER_PATH)
    
    print(f"\nClick events generated:\n{'-'*22}")
    for id, count in click_count.items():
        print(f"{id}: count")
    print(f"{'-'*22}\n")

if __name__ == "__main__":
    main()