
import praw
import pandas as pd
import datetime as dt
import time
import argparse
import sys
import os
import requests
import shutil
from prawcore.exceptions import Forbidden
import youtube_dl
from urllib.error import URLError
import config


def Download(type):
    # finds redditor's top submissions for the type
    for submissionTitle in reddit.redditor("{}".format(redditor)).submissions.top("{}".format(type)):
        # finds .jpg images from top posts
        if ".jpg" in "{}".format(submissionTitle.url):
            print("top", type, "submissions of", submissionTitle.author)
            print(submissionTitle.subreddit, ":", submissionTitle.url)
            imgURL = submissionTitle.url
            imgFolder = os.path.join("{}/".format(authorPath), "{}".format(submissionTitle.subreddit))

            # checks if redditor's submission subreddit folder exists
            if not os.path.exists(imgFolder):
                print("creating folder", submissionTitle.subreddit)
                os.makedirs(imgFolder)
            else:
                pass
            # checks if image exists and downloads if file does not exist
            fileName = imgURL.rsplit('/', 1)[1]
            fullPathName = imgFolder + '/' + fileName
            if os.path.exists(fullPathName):
                print("File already exists")
            else:
                filename = submissionTitle.id
                # opens url image
                r = requests.get(imgURL, stream = True)
                # checks if image was retrieved
                if r.status_code == 200:
                    r.raw.decode_content == True
                    # saves image at fullPathName
                    with open(fullPathName, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    print('Image sucessfully Downloaded: ',filename)
                else:
                    print('Image Couldn\'t be retreived')

        if "redgifs" in "{}".format(submissionTitle.url):
            print("top", type, "submissions of", submissionTitle.author)
            print(submissionTitle.subreddit, ":", submissionTitle.url)
            imgURL = submissionTitle.url
            imgFolder = os.path.join("{}/".format(authorPath), "{}".format(submissionTitle.subreddit))
            # checks if redditor's submission subreddit folder exists
            if not os.path.exists(imgFolder):
                print("creating folder", submissionTitle.subreddit)
                os.makedirs(imgFolder)
            else:
                pass
            gifURL = submissionTitle.url
            gifName = gifURL.rsplit('/', 1)
            gifDest = os.path.join(imgFolder, gifName[1])
            ytdlOpts = {
            'format': 'bestaudio/best',
            'outtmpl': '{}'.format(gifDest+'.mp4'),
            'quiet': True}
            with youtube_dl.YoutubeDL(ytdlOpts) as ytdl:
                try:
                    ytdl.download([submissionTitle.url])
                except ConnectionRefusedError:
                    print("ConnectionRefusedError")
                    continue
                except youtube_dl.utils.DownloadError:
                    print("youtube_dl.utils.DownloadError")
                    continue
                except urllib.error.URLError:
                    print("urllib.error.URLError")
                    continue

        time.sleep(.1)

if __name__ == '__main__':
    subredditURL = config.subredditURL
    subredditName = subredditURL.rsplit('/', 1)[1]
    print("searching for authors in", subredditName)

    reddit = praw.Reddit(client_id=config.client_id, \
                         client_secret=config.client_secret, \
                         user_agent=config.user_agent, \
                         username=config.username, \
                         password=config.password)

    # finds subreddit's hot authors
    for submission in reddit.subreddit("{}".format(subredditName)).hot(limit=None):
        redditor = submission.author
        try:
            # creates author folder
            authorPath = os.path.join("./user/", "{}".format(submission.author))
            if os.path.isdir(authorPath) == False:
                os.makedirs(authorPath)
            else:
                pass
            timePeriods = ["hour", "day", "week", "month", "year", "all"]
            for i in range(len(timePeriods)):
                Download(timePeriods[i])

            time.sleep(5)
        except Forbidden:
            print("Forbidden error")
