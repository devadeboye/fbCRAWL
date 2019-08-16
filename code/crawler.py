# import all necessary libary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
from bs4 import BeautifulSoup
import sqlite3
import json
from selenium.common.exceptions import NoSuchElementException
import random

class PostCrawler:
    """fetches friend's posts on facebook"""

    def __init__(self):
        """constructor of the PostCrawler class"""
        # open text file containing login details
        f = open('./login_details.txt', 'r')
        login_details = (line for line in f)
        # unpack details
        self.username, self.password = login_details
        # remove end of line character from username
        self.username = self.username[:-1]

        # define other useful variables
        self.posts = []
        self.post_container = dict()

        # gecko driver path
        gecko = './geckodriver.exe'
        # firefox profile
        ff_prof = webdriver.FirefoxProfile()
        # block images from loading
        ff_prof.set_preference('permissions.default.image', 2)
        # activate incognito mode
        ff_prof.set_preference('browser.privatebrowsing.autostart', True)
        # block all notifications
        ff_prof.set_preference('dom.webnotifications.enabled', False)
        # instantiate the browser
        self.driver = webdriver.Firefox(firefox_profile=ff_prof, executable_path=gecko)


    def go_fb(self):
        # go to facebook
        self.driver.get('http://www.facebook.com/login')
        # check if title contains facebook
        assert ('Facebook') in self.driver.title


    def get_cookies(self):
        """get cookies for the current session"""
        return(self.driver.get_cookies())


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
            # name
            n = post.find_element_by_css_selector('div[data-testid="fbfeed_story"] h5').text
            # paragraph
            try:
                p = post.find_element_by_css_selector('p')
            except NoSuchElementException:
                print('there is no p tag, so i\'m using span')
                # use span if there is no p tag
                p = post.find_element_by_css_selector('div > span:nth-child(2) > span:nth-child(1)') 
            #print(p.text, '\n\n')
            # check for repetition of posts
            if n in self.post_container.keys():
                if p not in self.post_container[n]:
                    self.post_container[n].append(p.text)
            else:
                if p is not '':
                    # store post in a dict
                    self.post_container[n] = [p.text]
            

    def scroll_page(self):
        """scrolls down the page to load fresh content"""
        # Scroll down to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


    def commit_post(self):
        """
        write the crawled result to json and
        save it to db
        """
        # convert to json format before saving in db
        js_format = json.dumps(self.post_container)
        
        #create a db
        db = sqlite3.connect('facebook.db')
        # get a cursor object
        cur = db.cursor()
        # create a table if it doesn't exist
        cur.execute(""" CREATE TABLE IF NOT EXISTS 
        fb_posts(posts TEXT )""")
        # add to db
        cur.execute("""INSERT INTO fb_posts(posts) VALUES
        (?)""", (js_format,))
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


    def run(self, no_of_users):
        """runs and controls the activity of the crawler""" 
        self.go_fb() # visit facebook
        time.sleep(5) # wait       
        self.login() # login
        # wait for the page to load
        self.driver.implicitly_wait(90)
        # harvest the post of some users
        while len(self.post_container) <= no_of_users:
            try:
                # grab users posts
                self.get_posts()
                # scroll page downward
                self.scroll_page()
                # wait... i use randint to vary the wait time
                time.sleep(random.randint(6,10))    
            except NoSuchElementException as error:
                print(error)
                # scroll page downward
                self.scroll_page()
        print(f'successfully gathered the posts of {len(self.post_container)} of your facebook friends.')
        time.sleep(2)
        print('Here they are:- \n\n')
        self.commit_post() # save post to db
        for k,v in self.post_container.items():
            print(f"""{k}:\n{v}\n\n""")
            





# test
if __name__ == "__main__":
    c = PostCrawler()
    c.run(5)