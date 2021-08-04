from selenium import webdriver
from bs4 import BeautifulSoup, Comment
import pandas as pd

URL = 'https://www.adcreview.com/adc-drugmap/'

def get_chrome_data(url, driver):
	driver.get(url)
	return driver.page_source

def new_driver():
	chrome_options = webdriver.ChromeOptions()  
	chrome_options.add_argument("--headless")
	return webdriver.Chrome(options = chrome_options)

def get_compounds(driver):
	compounds = {}
	data = get_chrome_data(URL, driver)
	soup = BeautifulSoup(data, 'html.parser').find('ul', {'id':'drugmap-items'})
	for element in soup(text = lambda x: isinstance(x, Comment)):
		element.extract()
	items = soup.find_all('li')
	for item in items:
		compounds[item.find('a').find(text = True, recursive = False)] = item.find('a').get('href')
	return compounds

def scrape_compound(driver, name, link):
	info = {'name': name}
	data = get_chrome_data(link, driver)
	soup = BeautifulSoup(data, 'html.parser').find('ul', {'class':'data'})
	lines = soup.find_all('li')
	for line in lines:
		info[line.find('p').text] = line.find('em').text
	print(len(info), link)
	return pd.DataFrame(info, index = [0])

def main():
	driver = new_driver()
	compounds_dict = get_compounds(driver)
	output = pd.DataFrame()
	dfs = []
	for c in sorted(compounds_dict):
		dfs.append(scrape_compound(driver, c, compounds_dict[c]))
	output = pd.concat(dfs, ignore_index = True)
	output.to_csv('all_data.csv', index = False)
	driver.quit()

if __name__ == '__main__':
	main()