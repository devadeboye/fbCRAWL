# import all necessary libary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import sqlite3
import json
from selenium.common.exceptions import NoSuchElementException

class PostCrawler:
    """fetches friend's posts on facebook"""

    def __init__(self):
        """constructor of the PostCrawler class"""
        # open text file containing login details
        f = open('login_details.txt', 'r')
        login_details = (line for line in f)
        # unpack details
        self.username, self.password = login_details
        # remove end of line character from username
        self.username = self.username[:-1]

        # define other useful variables
        self.posts = self.prev_cook = None
        self.post_container = dict()

        # gecko driver path
        gecko = 'E:/documents/myWorks/python/python source/Data Science/geckodriver.exe'
        # firefox profile
        ff_prof = webdriver.FirefoxProfile()
        # block images from loading
        ff_prof.set_preference('permissions.default.image', 2)
        # block all notifications
        ff_prof.set_preference('dom.webnotifications.enabled', False)
        # instantiate the browser
        self.driver = webdriver.Firefox(firefox_profile=ff_prof, executable_path=gecko)
        
    def go_fb(self):
        # go to facebook
        self.driver.get('http://www.facebook.com/login')
        # check if title contains facebook
        assert ('Facebook') in self.driver.title

    def man_cookies(self):
        """manage everything that has to do with cookies"""
        # open file containing cookies
        fr = open('cookies.json', 'r')
        self.prev_cook = json.load(fr)
        self.driver.add_cookie(self.prev_cook[0])

    def login(self):
        """log on to facebook"""
        # find the username and password field
        username = self.driver.find_element_by_id('email')
        password = self.driver.find_element_by_id('pass')
        # find the login button
        login_butt = self.driver.find_element_by_css_selector('#loginbutton')
        # wait before filling the form
        time.sleep(8)
        # fill in the username and password
        username.send_keys(self.username)
        time.sleep(9)
        password.send_keys(self.password)
        time.sleep(10)
        # click to login
        login_butt.click()
        

        

    def get_posts(self):
        """fetches the posts"""
        # list of posts
        self.posts = self.driver.find_elements_by_css_selector('div[data-testid="fbfeed_story"]')
        # iterate post
        for post in self.posts:
            try:
                # name
                n = post.find_element_by_css_selector('div[data-testid="fbfeed_story"] h5').text
                # paragraph
                #p = post.find_element_by_css_selector('div[data-testid="post_message"]')
                p = post.find_element_by_css_selector('p') 
                #print(p.text, '\n\n')
                # check for repetition of posts
                if n in self.post_container.keys():
                    self.post_container[n].add(p.text)
                else:
                    # store post in a dict
                    self.post_container[n] = {p.text}
            except NoSuchElementException:
                print('element not found')
            

    def scroll_page(self):
        """scrolls down the page to load fresh content"""
        # Get scroll height
    #    last_height = self.driver.execute_script("return document.body.scrollHeight")

        #while len(self.post_container) < 20:
    #    SCROLL_PAUSE_TIME = 6
        # Scroll down to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
    #    time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
    #    new_height = self.driver.execute_script("return document.body.scrollHeight")
    #    if new_height == last_height:
    #        break
    #    last_height = new_height


    def commit_post(self):
        """collect and save posts to db"""
        #create a db
        db = sqlite3.connect('facebook.db')

        # get a cursor object
        cur = db.cursor()

        # create a table if it doesn't exist
        cur.execute(""" CREATE TABLE IF NOT EXISTS 
        posts(id INTEGER PRIMARY KEY, name TEXT, post TEXT )""")
        db.commit()



    def logout(self):
        """sign out of facebook"""
        # click the dropdown menu to reveal the logout button
        dd = self.driver.find_element_by_css_selector('a[id="pageLoginAnchor"]')
        dd.click()
        # wait for the dailog box to show
        time.sleep(5)
        # find the logout button
        css_attr = """data-gt='{"ref":"async_menu","logout_menu_click":"menu_logout"}'"""
        # select the logout
        logout = self.driver.find_element_by_css_selector(f'li[{css_attr}]')
        # click the logout button
        logout.click()
        # rest
        time.sleep(4)
        # close the browser
        self.driver.quit()


    def controller(self):
        """controls the activity of the crawler"""
        pass





# test
if __name__ == "__main__":
    c = PostCrawler()