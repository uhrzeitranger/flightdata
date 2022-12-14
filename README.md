# flightdata

Simple CLI tool to scrape flight prices for a given route from Google Flights through Chrome.

## Dependencies
- selenium
- click
- tqdm
- webdriver-manager

## Contents
### flight_prices.py
Main script to be called from CLI with options.

Example usage: 
`python flight_prices.py -i LHR BER -d We Su -t 15 18 -m 4 -s 1`
checks prices for flights from London Heathrow to Berlin Brandenburg, outbound Wednesday and inbound Sunday, each week over the next 4 months and enforces a maximum of 1 layover. If multiple flights are available, the cheapest flight is recorded.
Progress is logged and results are printed into Terminal.

For a full list of options and usage, use
`python flight_prices.py --help`

### Test.ipynb
Notebook used for development and demonstration

