import time
import datetime
import re
import logging
import click
from pprint import pprint
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager

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


def set_filters(driver, time_out, time_in, layovers):
    # stops
    if (layovers > -1) and (layovers < 3):
        WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div/div[1]/span/button"))).click()
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, f"/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div[{layovers+2}]/div/input"))).click()
    
    logging.debug(f"Set maximum layovers to {layovers}.")
    time.sleep(1)
    # outbound
    WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/div/div[5]/span/button"))).click()
    # departure time
    outbound_dep_time_drag = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[2]/span/div/div[2]/div/div[2]/div/div/input[1]")))
    for _ in range(time_out):
        outbound_dep_time_drag.send_keys(Keys.ARROW_RIGHT)
    logging.debug("Set outbound time")
    time.sleep(1)


    # inbound
    driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[1]/div/div/span/button[2]").click()
    # departure time
    inbound_dep_time_drag = driver.find_element(By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[4]/div/div[2]/div[3]/div/div[1]/section/div[2]/div[1]/div/div/div/div[3]/span/div/div[2]/div/div[2]/div/div/input[1]")
    for _ in range(time_in):
        inbound_dep_time_drag.send_keys(Keys.ARROW_RIGHT)
    logging.debug("Set inbound time")
    time.sleep(1)
    inbound_dep_time_drag.send_keys(Keys.ESCAPE)


def get_flight_dates(day_out,day_in,months=6):
    days = ["Mo","Tu","We","Th","Fr","Sa","Su"]
    nrs = [0,1,2,3,4,5,6]
    day_nrs = dict(zip(days,nrs))
    day_in, week_add = parse_inbound_day(day_in)
    days_delta = ((day_nrs[day_in]-day_nrs[day_out]) % 7) + 7*week_add
    day_date = datetime.date.today() + datetime.timedelta( (day_nrs[day_out]-datetime.date.today().weekday()) % 7 )
    format ="%a, %b %d"

    dates = [(day_date.strftime(format),(day_date + datetime.timedelta(days_delta)).strftime(format))]

    for _ in range((4*months)-1):
        day_date += datetime.timedelta(7)
        dates.append((day_date.strftime(format),(day_date+datetime.timedelta(days_delta)).strftime(format)))
    return dates

def get_currency(driver):
    currency_text = driver.find_element(By.XPATH,"/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[4]/c-wiz/footer/div[1]/c-wiz/button[3]/span/span[2]").text
    currencies = {"GBP":"£","EUR":"€","CHF":"CHF"}
    return currencies[currency_text]

def parse_inbound_day(t):
    """Auxiliary function that allows to specify day_in as 'Fr+1' for Friday the following week"""
    try:
        loc = t.find("+")
        r = int(t[loc+1:])
        t = t[:loc]
    except ValueError:
        r = 0
    return t,r

def fetch_prices(driver, dates):
    # TODO: write this as a method of a class
    prices = {}
    logging.info("Getting prices:")
    for date_out, date_in in tqdm(dates):
        logging.debug(f"Getting prices for {date_out}")
        time.sleep(1)
        from_time = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/div[1]")))
        from_time.click()
        time.sleep(1)
        from_time_w_calendar = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/input")))
        from_time_w_calendar.send_keys(date_out, Keys.TAB) # FIXME: this throws an element not interactible Exception!
        time.sleep(0.5)
        to_time = driver.switch_to.active_element
        to_time.send_keys(date_in)
        time.sleep(0.5)
        done_button = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div[3]/div[3]/div/button")))
        done_button.click()
        time.sleep(0.5)
        
        try:
            li_children = WebDriverWait(driver,2).until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li")))
        except TimeoutException:
            prices[date_out] = None
            continue
        
        currency_mask = get_currency(driver)

        if len(li_children):
            date_out_prices = []
            for li in li_children:
                try:
                    logging.debug(li.text)
                    price = re.search(rf'.*?{currency_mask}(.*?)\n.*', li.text).group(1).replace(",","")
                    date_out_prices.append(int(price))
                except:
                    continue
            itinerary = f"{date_out} -> {date_in}"
            prices[itinerary] = min(date_out_prices)
        else:
            prices[itinerary] = None
    logging.info("Prices fetched successfully.")
    return prices

@click.command()
@click.option("-i","--initiary", default=("ZRH","FLR"),nargs=2,show_default=True,type=(str,str),help="Departure and Destination.")
@click.option("-m","--months",default=6,type=int,show_default=True,help="Number of months into the future to scrape prices for.")
@click.option("-t","--times", default=(16,17),nargs=2, show_default=True, type=(int,int), help="Departure times for outbound and inbound flight.")
@click.option("-d","--days", default=("Fr","Su"),nargs=2, show_default=True, type=(str,str), help="Weekdays to select. For following week(s) do e.g. 'XX+1'.")
@click.option("-s","--stops", default=-1, show_default=False, type=int, help="Maximum number of layovers. 0 for non-stop only.")
@click.option("--debug",is_flag=True,default=False,show_default=True,help="Whether logger is set to DEBUG or INFO.")
def main(initiary,months,times,days,stops,debug):
    departure,destination = initiary
    t1,t2 = times
    day_out, day_in = days
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    

    logging.info(f"Checking weekly flight prices from {departure} to {destination} for {day_out} after {t1}:00 till {day_in} after {t2}:00 for the next {months} months.")

    # set up. handle deprecation at some point...
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get("https://www.google.com/travel/flights")

    # accept cookies
    driver.find_element(By.XPATH, "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button").click()

    try:
        navigate_to_main_search_mask(driver,departure=departure,destination=destination)
    except:
        logging.error("Encountered Error while navigating to main search mask.")
        raise

    try:
        set_filters(driver, time_out = t1, time_in = t2, layovers=stops)
    except:
        logging.error("Encountered error while setting filters.")
        raise

    flight_dates = get_flight_dates(day_out=day_out, day_in=day_in, months=months)

    try:
        prices = fetch_prices(driver,flight_dates)
    except:
        logging.error("Encountered Error while fetching prices.")
        raise
    
    # print to terminal or return?
    pprint(prices, width=30, sort_dicts=False)

    driver.close()



if __name__ == "__main__":
    main()