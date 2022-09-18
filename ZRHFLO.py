from selenium import webdriver
url = 'https://www.google.com/travel/flights/search?tfs=CBwQAhojagwIAhIIL20vMDg5NjYSCjIwMjItMTEtMTFyBwgBEgNGTFIaI2oHCAESA0ZMUhIKMjAyMi0xMS0xM3IMCAISCC9tLzA4OTY2cAGCAQsI____________AUABSAGYAQE'
driver = webdriver.Chrome()
driver.get(url)
