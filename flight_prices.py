import time
import datetime
import re
import logging
import click
from pprint import pprint
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def navigate_to_main_search_mask(driver, departure="ZRH",destination="FLR"):
    # TODO: write this as a method of a class
    input_from = driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input")
    input_from.click()
    input_w_dropdown_from = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div[2]/div[1]/div/input")))
    time.sleep(0.5)
    input_w_dropdown_from.clear()
    input_w_dropdown_from.send_keys(departure)
    time.sleep(0.8) # load js
    input_w_dropdown_from.send_keys(Keys.RETURN)

    # entering destination
    input_to = driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input")
    input_to.click()
    input_w_dropdown_to = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[2]/div[2]/div[1]/div/input")))
    input_w_dropdown_to.send_keys(destination)
    time.sleep(0.8) # load js
    input_w_dropdown_to.send_keys(Keys.RETURN)

    # press search
    driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button").click()


def set_filters(driver):
    # stops
    WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div/div[1]/span/button"))).click()
    non_stop_option = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div[2]/div/input")))
    non_stop_option.click()
    logging.debug("Set nonstop.")
    time.sleep(1)

    # outbound 
    driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div/div[5]/span/button").click()
    # departure time
    outbound_dep_time_drag = driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[2]/span/div/div[2]/div/div[2]/div/div/input[1]")
    for _ in range(16):
        outbound_dep_time_drag.send_keys(Keys.ARROW_RIGHT)
    logging.debug("Set outbund time")
    time.sleep(1)


    # inbound
    driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[1]/div/div/span/button[2]").click()
    # departure time
    inbound_dep_time_drag = driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[3]/span/div/div[2]/div/div[2]/div/div/input[1]")
    for _ in range(17):
        inbound_dep_time_drag.send_keys(Keys.ARROW_RIGHT)
    logging.debug("Set inbound time")
    time.sleep(1)
    inbound_dep_time_drag.send_keys(Keys.ESCAPE)


def get_fridays(start_date = datetime.date.today(),months=6):
    friday = start_date + datetime.timedelta( (4-start_date.weekday()) % 7 )
    format ="%a, %b %d"

    fridays = [(friday.strftime(format),(friday + datetime.timedelta(2)).strftime(format))]

    for _ in range((4*months)-1):
        friday += datetime.timedelta(7)
        fridays.append((friday.strftime(format),(friday+datetime.timedelta(2)).strftime(format)))
    return fridays

def fetch_prices(driver, fridays,currency_mask="€"):
    # TODO: write this as a method of a class
    prices = {}
    logging.info("Getting prices:")
    for fr, su in tqdm(fridays):
        logging.debug(f"Getting prices for {fr}")
        time.sleep(1)
        from_time = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/div[1]")))
        from_time.click()
        time.sleep(1)
        from_time_w_calendar = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/input")))
        from_time_w_calendar.send_keys(fr, Keys.TAB) # FIXME: this throws an element not interactible Exception!
        time.sleep(0.5)
        to_time = driver.switch_to.active_element
        to_time.send_keys(su)
        time.sleep(0.5)
        done_button = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div[3]/div[3]/div/button")))
        done_button.click()
        time.sleep(0.5)
        # if there are no li - i.e. no flights for the times and filters, the WebDriverWait will throw an exception. TODO: wrap into according except.
        try:
            li_children = WebDriverWait(driver,2).until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li")))
        except TimeoutException:
            prices[fr] = None
            continue

        if len(li_children):
            all_prices = []
            for i in li_children:
                # NOTE: This is for CHF - adjust for different settings, with more sophisticated reg ex matching
                price = re.search(rf'.*?{currency_mask}(.*?)\n.*', i.text).group(1)
                all_prices.append(int(price))
            prices[fr] = min(all_prices)
    logging.info("Prices fetched successfully.")
    return prices

@click.command()
@click.option("-i","--initiary", default=("ZRH","FLR"),nargs=2,show_default=True,type=(str,str),help="Departure and Destination.")
@click.option("-m","--months",default=6,type=int,show_default=True,help="Number of months into the future to scrape prices for")
@click.option("--debug",is_flag=True,default=False,show_default=True,help="Whether logger is set to DEBUG or INFO")
def main(initiary,months,debug):
    departure,destination = initiary
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    

    logging.info(f"Checking weekly flight prices from {departure} to {destination} for the next {months} months.")

    # set up. handle deprecation at some point...
    driver = webdriver.Chrome("/Applications/chromedriver")

    driver.get("https://www.google.com/travel/flights")

    # accept cookies
    driver.find_element(By.XPATH, "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button").click()

    try:
        navigate_to_main_search_mask(driver,departure=departure,destination=destination)
    except:
        logging.error("Encountered Error while navigating to main search mask.")
        raise

    try:
        set_filters(driver)
    except:
        logging.error("Encountered error while setting filters.")
        raise

    fridays = get_fridays(months=months)

    try:
        prices = fetch_prices(driver,fridays, "€")
    except:
        logging.error("Encountered Error while fetching prices.")
        raise
    
    # print to terminal or return?
    pprint(prices, width=30, sort_dicts=False)

    driver.close()



if __name__ == "__main__":
    main()