import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def setup_browser():
    """invisible and safe chrome browser setup"""
    options = uc.ChromeOptions()

    # '--headless' means the browser will run in the background, not pop up on the screen. 
    options.add_argument('--headless')

    #undertected_chromedriver is automatically remove bot-flags
    driver = uc.Chrome(options=options, version_main=145)
    return driver

def verify_bio_code(platform_link, expected_code):
    #this funtion will go to the given link & find the bio code.
    driver = None
    try:
        #1. hey mine novo lets start browser
        driver = setup_browser()

        #2. hey mine novo open the user social media link
        driver.get(platform_link)

        #3. now pretend just like (human behavior) random delay process bro
        delay_time = random.uniform(6.0, 10.0) # thambaa-thanbaa browser here 4 - 8 seconds 
        time.sleep(delay_time) #so that social platform thinks a real human is reading the page! u got it bro?

        #4. retive all the text from this page brother ji
        #remove body tag's inside of text
        page_text = driver.page_source

        #5. now check our code is in that text? 
        if expected_code in page_text:
            return True, "Verified Successfully! Code found."
        else:
            return False, "Code not found in bio. Please check and try again."

    except Exception as e:
        #if any technical error ouccer, so mine dear computer insted of crashing, return an error message.
        return False, f"Verification failed due to technical error: {str(e)}"

    finally:
        #. very important: after complete work then close the browser
        # warning: (RAM) will full
        if driver:
            driver.quit()
