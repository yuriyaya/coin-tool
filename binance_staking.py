from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import os.path

url = "https://www.binance.com/en/pos"

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.maximize_window()
driver.implicitly_wait(10)

# staking condition monitor
staking_monitor = {"TRX" : ["30", "60", "90"], "ADA" : ["60", "90"]}

driver.get(url)

CHECKBOX_CLICK_DELAY = 2
INPUT_SEARCH_DELAY = 2
driver.find_element_by_class_name("css-ou20q0").click() # available checkbox
time.sleep(CHECKBOX_CLICK_DELAY)

for coin, due in staking_monitor.items():
    search_input = driver.find_element_by_xpath('//*[@id="__APP"]/div/main/div/div[3]/div/div[1]/div/input')
    search_input.clear()
    search_input.send_keys(coin)
    time.sleep(INPUT_SEARCH_DELAY)
    staking_coins = driver.find_elements_by_class_name("css-1lxsrr9")
    for due_item in due:
        print("- Check", coin, due_item)
        alarm_file_name = coin + "_" + due_item
        if len(staking_coins) > 0:
            # staking available
            staking_duration_div = driver.find_element_by_xpath('//*[@id="__APP"]/div/main/div/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]')
            button_tags = staking_duration_div.find_elements_by_xpath('./button')
            due_found = False
            for button_tag in button_tags:
                if due_item == button_tag.text and due_found == False:
                    due_found = True
                    button_tag.click()
                    staking_earn_rate = driver.find_element_by_class_name("css-1v55uij")
                    print("Duration:", button_tag.text, ", Est. APY:", staking_earn_rate.text)
                    if not os.path.isfile(alarm_file_name):
                        f = open(alarm_file_name, "x") # create alarm file
                        f.close()
            if due_found is False:
                print(coin, due_item, "sold out")
                if os.path.exists(alarm_file_name):
                    os.remove(alarm_file_name) # delete alarm file
        else:
            print(coin, "staking sold out")
            if os.path.exists(alarm_file_name):
                os.remove(alarm_file_name) # delete alarm file
            exit

