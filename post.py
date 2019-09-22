#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from pathlib import Path
import autoit
from PIL import Image

'''
This program follows accounts and posts images over time
'''
def Login(username, password, driver): #logs into instagram
    login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]")
    login_button.click()
    time.sleep(2)
    username_input = driver.find_element_by_xpath("//input[@name='username']")
    username_input.send_keys(username)
    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.send_keys(password)
    password_input.submit()
    time.sleep(1)

def close_add_to_home(driver): #gets rid of pop up
    try:
        time.sleep(3) 
        close_addHome_btn = driver.find_element_by_xpath("//button[contains(text(),'Cancel')]")
        close_addHome_btn.click()
        time.sleep(4)
    except:
        time.sleep(2)

def close_notification(driver): #gets rid of notification
    try: 
        time.sleep(2)
        close_noti_btn = driver.find_element_by_xpath("//button[contains(text(),'Not Now')]")
        close_noti_btn.click()
        time.sleep(2)
    except:
        pass

def close_reactivated(driver): #closes pop up
    try:
        time.sleep(2)
        not_now_btn = driver.find_element_by_xpath("//a[contains(text(),'Not Now')]")
        not_now_btn.click()
    except:
        pass

def removeImages(): #delets all images
    files = os.listdir()
    imageFiles = [file for file in files if ".jpg" in file]
    for file in imageFiles:
        os.remove(file)

def follow(usernames, driver): #follows people from list
    usernames = Remove(usernames)
    print(len(usernames))
    usernames = [usernames[random.randint(0, int(len(usernames)/2))] for i in range(int(len(usernames)/3))]
    print(len(usernames))
    for name in usernames:
        try:
            time.sleep(1)
            url  = "https://www.instagram.com/" + name + "/"
            driver.get(url)
            time.sleep(3)
            follow_button = driver.find_element_by_xpath("//button[contains(text(),'Follow')]")
            follow_button.click()
        except:
            time.sleep(3)
    with open("followedAccounts.txt", "a") as f: #adds them to this file to be later unfollowed
        for name in usernames:
            f.write(name + "\n")
            
def Remove(duplicate): #removes duplicates from list
    final_list = [] 
    for thing in duplicate: 
        if thing not in final_list: 
            final_list.append(thing) 
    return final_list 

def unfollow(driver): #unfollows followed accounts
    with open("followedAccounts.txt", "r") as f:
        lines = f.readlines()
    lines = Remove(lines)
    if len(lines) > 40:
        print("Starting to unfollow")
        for i in range(int(len(lines)/5)):
            try:
                name = lines[random.randint(0, len(lines)-1)].replace("\n", "")
                time.sleep(1)
                url  = "https://www.instagram.com/" + name + "/"
                driver.get(url)
                time.sleep(4)
                unfollow_button = driver.find_element_by_css_selector("button._5f5mN.-fzfL._6VtSN.yZn4P")
                unfollow_button.click()
                time.sleep(random.randint(1, 2))
                unfollow_button_confirm = driver.find_element_by_css_selector("button.aOOlW.-Cab_")
                unfollow_button_confirm.click()
                lines.remove(lines[i])
            except:
                pass
    with open("followedAccounts.txt", "w") as f:
        for line in lines:
            f.write(line)


def make_square(im, image_path): #takes saved image and adds white buffer to make sure its squre
    min_size=256
    fill_color=(255, 255, 255, 0)
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    new_im.save((image_path.split("/")[-1]))


def Post(username, password, timer, usernames): #posts the image
    files = os.listdir()
    imageFiles = [file for file in files if ".jpg" in file]

    
    user_agent = "Mozilla/4.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

    profile = webdriver.FirefoxProfile() #starts webbrowser emulating as a phone
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(profile)
    driver.set_window_size(360,640)
    
    url = "https://www.instagram.com"
    driver.get(url)
    time.sleep(4)
    Login(username, password, driver) #logs in
    close_reactivated(driver)
    close_notification(driver)
    close_add_to_home(driver)
    close_notification(driver)
    print("Starting following")
    follow(usernames, driver)
    for i in range(len(imageFiles)): #starts posting
        print("Posting " + imageFiles[i])
        image_path = (str(Path(__file__).parent.absolute()) + "\\" + imageFiles[i])

        opened_image = Image.open(image_path)
        make_square(opened_image, image_path)
        
        new_post_btn = driver.find_element_by_xpath("//div[@role='menuitem']").click()
        time.sleep(1.5)
        autoit.win_active("File Upload") 
        time.sleep(2)
        autoit.control_send("File Upload","Edit1",image_path) 
        time.sleep(1.5)
        autoit.control_send("File Upload","Edit1","{ENTER}")
        try:
            time.sleep(1.5)
            autoit.control_send("File Upload","Edit1","{ENTER}")
        except:
            pass
        time.sleep(2)
        
        next_btn = driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
        time.sleep(1.5)
        share_btn = driver.find_element_by_xpath("//button[contains(text(),'Share')]").click()
        time.sleep(2)
        print("Unfollwing some people")
        unfollow(driver)
        time.sleep(timer)

        
    driver.close() #ends driver
    

def Main(): #main loop
    timer = int(input("Time between posts in minutes: "))
    timer = timer*60
    username = input("Instagram Username: ")
    password = input("Instagram password: ")
    with open("accountstofollow.txt", "r") as f:
        line = f.readline()
        usernames = line.split(",")
    Post(username, password, timer, usernames)
    removeImages()
Main()
