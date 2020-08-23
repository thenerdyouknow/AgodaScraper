from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import json
import re
import os
# The place we will direct our WebDriver to
url = 'https://www.agoda.com/en-in/?cid=1844104'
# 'Kuala Lumpur'
# Singapore
cities_to_mine = ['Bangkok']
# Creating the WebDriver object using the ChromeDriver
driver = webdriver.Chrome(executable_path='/usr/local/share/chromedriver')

# Directing the driver to the defined url

def select_city(city_name,driver):
    
    inputElement = driver.find_elements_by_class_name("SearchBoxTextEditor")[0]
    inputElement.send_keys(city_name)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR , "div.Popup__content li")))
    time.sleep(10)
    auto_suggest_list = driver.find_elements_by_css_selector('div.Popup__content li > span.Suggestion__text')
    
    for item in auto_suggest_list:
        if(item.text.lower() == city_name.lower()):
            item.click()
            break
    
    date_element = driver.find_elements_by_css_selector('div.IconBox__wrapper')[1]
    date_element.click()
    submit_button = driver.find_elements_by_class_name("Searchbox__searchButton")[0]
    submit_button.click()
    return

def scrolling_to_load_hotels(driver):
    for i in range(0,7):
        driver.execute_script("window.scrollTo({}*document.body.scrollHeight/10,{}*document.body.scrollHeight/10)".format(i,i+1))
        time.sleep(5)
    return

def move_to_reviews(driver):
    element = driver.find_element_by_class_name("Review-comment-bodyTitle")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    return

def open_new_hotel_tab(driver,hotel_URL):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(hotel_URL)
    time.sleep(20)
    return

def select_most_recent(driver):
    select_most_recent_filter = Select(driver.find_element_by_id('review-sort-id'))
    select_most_recent_filter.select_by_visible_text('Most recent')
    time.sleep(10)
    return

def collecting_reviews(driver,hotel_URL,hotel_dict):
    hotel_dict['Reviews'] = []

    open_new_hotel_tab(driver,hotel_URL)
    move_to_reviews(driver)
    select_most_recent(driver)

    pagination_values = driver.find_elements_by_class_name("Review-paginator-number")

    number_of_verified_reviews = driver.find_element_by_class_name("Review__SummaryContainer__Text").text.split(" ")[1]
    print(int(number_of_verified_reviews))
    
    if(int(number_of_verified_reviews)<100):
        return None
    
    for i in range(0,5):
        all_current_reviews = driver.find_elements_by_class_name("Review-comment")
        for each_review in all_current_reviews:
            individual_review = {}
            individual_review['Review Score'] = each_review.find_element_by_class_name("Review-comment-leftScore").text
            individual_review['Review Title'] = re.sub('”','',each_review.find_element_by_class_name("Review-comment-bodyTitle").text)
            individual_review['Review Text'] = each_review.find_element_by_class_name("Review-comment-bodyText").text
            individual_review['Review Date'] = each_review.find_element_by_class_name('Review-statusBar-date').text
            hotel_dict['Reviews'].append(individual_review)
        if(i<3):
            i+=1
        pagination_values[i].click()
        time.sleep(5)
        move_to_reviews(driver)

    return hotel_dict

def collecting_hotels(driver):
    WebDriverWait(driver,40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div > ol.hotel-list-container")))
    scrolling_to_load_hotels(driver)
    all_hotels = driver.find_elements_by_class_name("property-card")
    return all_hotels

def writing_to_file(hotel_dict,i):
    with open(str(i)+'.json','w') as open_file:
        json.dump(hotel_dict,open_file)
    return

def make_and_change_dir(city_name):
    os.mkdir(each_city)
    os.chdir(each_city)
    return


if __name___ == '__main__':

    for each_city in cities_to_mine:

        make_and_change_dir()

        driver.get(url)
        select_city(each_city,driver)
        all_hotels = collecting_hotels(driver)

        counter = 0

        for i,each_hotel in enumerate(all_hotels):
            
            if(counter == 20):
                break
            
            try:
                hotel_dict = {}
                review_number = int(re.sub(',','',each_hotel.find_element_by_tag_name("strong").text))
                hotel_name = each_hotel.find_element_by_class_name("InfoBox__HotelTitle").text
                overall_rating = float(each_hotel.find_element_by_class_name("ReviewScore-Number").text)
                hotel_URL = each_hotel.get_attribute("href")
                if(review_number > 100):
                    hotel_dict['Hotel Name'] = hotel_name
                    hotel_dict['Number of reviews'] = review_number
                    hotel_dict['Overall Rating'] = overall_rating
                    hotel_dict['URL'] = hotel_URL
                    hotel_dict = collecting_reviews(driver,hotel_URL,hotel_dict)

                    if(hotel_dict is None):
                        driver.close()
                        driver.switch_to_window(driver.window_handles[0])
                        continue

                    writing_to_file(hotel_dict,counter)
                    counter += 1
                    driver.close()
                    driver.switch_to_window(driver.window_handles[0])
            except:
                raise
                
        os.chdir("..")
