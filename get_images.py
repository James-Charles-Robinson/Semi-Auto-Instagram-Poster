#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import requests
import urlopen
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import json
import time

'''
This program takes images from instagram with posts containing a cirtain hastag.
It then saves the images and the accounts that own them
'''
def LoadPreviousPosts(): #gets previous image urls
    with open("postIDs.txt", "r+") as f:
        lines = f.readlines()
    newLines = []
    for line in lines:
        line = line.strip()
        newLines.append(line)
        
    return newLines

def GetPostLinks(stalkHashtags, amount): #gets the post link from the hashtag page from the file
    newPostIDs = []
    for account in stalkHashtags:
        if len(newPostIDs) < amount*5:
            url = "https://www.instagram.com/explore/tags/" + account + "/"
            html = urllib.request.urlopen(url,).read()
            soup = BeautifulSoup(html, 'html.parser')
            script = soup.find('script', text=lambda t: \
                               t.startswith('window._sharedData'))
            page_json = script.text.split(' = ', 1)[1].rstrip(';')
            data = json.loads(page_json)
            for post in data['entry_data']['TagPage'][0]['graphql'
                    ]['hashtag']['edge_hashtag_to_media']['edges']:
                if len(newPostIDs) < amount*5:
                    postCode = post['node']['shortcode']
                    newPostIDs.append(postCode)
    print(len(newPostIDs))
    return newPostIDs


def CheckUnused(newPostIDs, oldPostIDs): #checks the post hasnt already been saved
    postsIDs = []
    for ID in newPostIDs:
        if ID not in oldPostIDs:
            postsIDs.append(ID)    
    return postsIDs
    

def Write(IDs, amount): #writes the used pasts to the file, how every removes some.
    print(IDs)
    try:
        newIDs = [IDs[random.randint(0, len(IDs)-1)] for i in range(amount)]
    except:
        try:
            newIDs = [IDs[random.randint(0, len(IDs)-1)] for i in range(int(amount/1.5))]
        except:
            try:
                newIDs = [IDs[random.randint(0, len(IDs)-1)] for i in range(15)]
            except:
                try:
                    newIDs = [IDs[random.randint(0, len(IDs)-1)] for i in range(3)]
                except:
                    newIDs = [IDs[random.randint(0, len(IDs)-1)] for i in range(1)]
    with open("postIDs.txt", "a") as f:
        for ID in newIDs:
            f.write(ID + "\n")
    return newIDs

def GetPhotoScontent(IDs): #gets the image link from the post
    imageUrls = []
    usernames = []
    for ID in IDs:
        try:
            url = "https://www.instagram.com/p/" + ID + "/"
            html = urllib.request.urlopen(url,).read()
            time.sleep(random.random()+1)
            soup = BeautifulSoup(html, 'html.parser')
            script = soup.find('script', text=lambda t: \
                               t.startswith('window._sharedData'))
            page_json = script.text.split(' = ', 1)[1].rstrip(';')
            data = json.loads(page_json)
            for post in data['entry_data']['PostPage']:
                username = post['graphql']['shortcode_media']['owner']['username']
                imageUrl = post['graphql']['shortcode_media']['display_resources'][-1]['src']
                if post['graphql']['shortcode_media']['__typename'] == "GraphImage":
                    imageUrls.append(imageUrl)
                    usernames.append(username)
        except:
            pass
    return imageUrls, usernames


def SavePhoto(urls): #saves the image from the link
    urls = Remove(urls)
    for i in range(len(urls)):
        try:
            url = urls[i]
            name = "pic" + str(random.randint(100, 999)) + ".jpg"
            with open(name, 'wb') as handle:
                    response = requests.get(url, stream=True)

                    if not response.ok:
                        print (response)

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)  

        except:
            pass
        
def Remove(duplicate): #removes duplicates
    final_list = [] 
    for thing in duplicate: 
        if thing not in final_list: 
            final_list.append(thing) 
    return final_list 

def GetHashtags(): #gets the hastags from the file
    stalkHashtags = []
    with open("hashtags.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        stalkHashtags.append(line.replace("\n", ""))
    return stalkHashtags

def Main(): #main loop
    amount = int(input("Aproxitmatly how many images: "))
    for i in range(1):
        oldPostUrls = LoadPreviousPosts()
        stalkHashtags = GetHashtags()
        print("Getting post links")
        newPostIDs = GetPostLinks(stalkHashtags, amount)
        print("Getting image links")
        imageUrls, usernames = GetPhotoScontent(newPostIDs)
        imageUrls = CheckUnused(imageUrls, oldPostUrls)
        imageUrls = Write(imageUrls, amount)
        print("Saving photos")
        SavePhoto(imageUrls)
        usernames = Remove(usernames)
        with open("accountstofollow.txt", "w") as f:
            for username in usernames:
                f.write(username + ",")
    print("Delete any images you dont want to post")

Main()
