from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import os.path
import json
import telegram

# =========================================================================================
# function for telegram
# =========================================================================================
def send_telegram_alarm(bot, chat_id, msg):
    bot.send_message(chat_id=chat_id, parse_mode='HTML', text=msg)

# =========================================================================================
# MAIN
# =========================================================================================
if __name__ == '__main__':
    
    # load configuration
    with open("../coin_config.json", "r") as json_file:
        config_data = json.load(json_file)

    # binanace staking page url
    url = config_data["url"]["staking"]
    # staking condition monitor
    staking_monitor = config_data["coin_monitor"]
    # telegram token
    tele_token = config_data["telegram"]["token"]
    chat_id = config_data["telegram"]["chat_id"]

    # telegram alarm bot setting
    bot = telegram.Bot(token=tele_token)

    # selenium params
    CHECKBOX_CLICK_DELAY = 2
    INPUT_SEARCH_DELAY = 2

    # web driver setting
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)

    # page loading
    driver.get(url)

    driver.find_element_by_class_name("css-ou20q0").click() # click available checkbox
    time.sleep(CHECKBOX_CLICK_DELAY)

    for coin, due in staking_monitor.items():
        search_input = driver.find_element_by_xpath('//*[@id="__APP"]/div/main/div/div[3]/div/div[1]/div/input')
        search_input.clear()
        search_input.send_keys(coin) # search coin
        time.sleep(INPUT_SEARCH_DELAY)
        staking_coins = driver.find_elements_by_class_name("css-1lxsrr9")
        for due_item in due:
            print("- Check", coin, due_item)
            alarm_file_name = coin + "_" + due_item
            if len(staking_coins) > 0:
                # monitoring coin staking available
                staking_duration_div = driver.find_element_by_xpath('//*[@id="__APP"]/div/main/div/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]')
                button_tags = staking_duration_div.find_elements_by_xpath('./button')
                due_found = False
                for button_tag in button_tags:
                    if due_item == button_tag.text and due_found == False:
                        due_found = True
                        button_tag.click()
                        staking_earn_rate = driver.find_element_by_class_name("css-1v55uij")
                        msg = "Duration: " + button_tag.text + ", Est. APY: " + staking_earn_rate.text
                        print(msg)
                        if not os.path.isfile(alarm_file_name):
                            f = open(alarm_file_name, "x") # create alarm file
                            f.close()
                            alarm_msg_new_staking = "New staking available!\n" + coin + "\n" + msg
                            send_telegram_alarm(bot, chat_id, alarm_msg_new_staking)
                if due_found is False:
                    print(coin, due_item, "sold out")
                    if os.path.exists(alarm_file_name):
                        os.remove(alarm_file_name) # delete alarm file
                        send_telegram_alarm(bot, chat_id, coin + " " + due_item + " staking sold out!")
            else:
                # monitoring coin staking available, no search result
                # need to check other duration, no exit at here
                print(coin, due_item, "sold out")
                if os.path.exists(alarm_file_name):
                    os.remove(alarm_file_name) # delete alarm file
                    send_telegram_alarm(bot, chat_id, coin + " " + due_item + " staking sold out!")
                

