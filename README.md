# flightdata

## Dependencies
- selenium
- click
- tqdm

As of now also requires Chrome webdriver to run. However, this will probably be changed soon (see here: https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python).

## Contents
### Test.ipynb
Notebook used for development and demonstration


### flight_prices.py
Main script to be called from CLI with options.

Example usage: 
'python flight_prices.py -i LHR BER -m 4'
checks prices for weekend flights from London Heathrow to Berlin Brandenburg over the next 4 months. If multiple flights are available, the cheapest flight is recorded.
Progress is logged and results are printed into terminal.

Days and times are not yet configurable (tb added).

