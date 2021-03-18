import praw
import time
import os
import requests
import shutil
import youtube_dl
import config
import multiprocessing
from prawcore.exceptions import Forbidden, NotFound
from urllib.error import URLError

'''
Check if author folder exists, creates folder if does not exist
'''
def AuthorCheck(redditor):
    try:
        # creates author folder
        authorPath = os.path.join("./user/", "{}".format(redditor))
        if os.path.isdir(authorPath):
            pass
        else:
            os.makedirs(authorPath)
        timePeriods = ["hour", "day", "week", "month", "year", "all"]
        for i in range(len(timePeriods)):
            Download(timePeriods[i], redditor, authorPath)
        time.sleep(.1)
    except Forbidden:
        print("Forbidden error")
    except NotFound:
        print("404 HTTP response")

def FileDownload(fullPathName, author, imgURL, fileName, timePeriod):
    if os.path.exists(fullPathName):
        print(f"{author} {fullPathName} already exists")
    else:
        # opens url image
        r = requests.get(imgURL, stream = True)
        # checks if image was retrieved
        if r.status_code == 200:
            r.raw.decode_content == True
            # saves image at fullPathName
            with open(fullPathName, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f"Downloaded {author}: {timePeriod} {fileName} at {fullPathName} ")
        else:
            print('Image Couldn\'t be retreived')

def Download(timePeriod, redditor, authorPath):
    # finds redditor's top submissions based on top submission type
    for submissionTitle in reddit.redditor("{}".format(redditor)).submissions.top("{}".format(timePeriod)):
        fileType = [".jpg", "redgifs", "gifv"]
        for x in range (len(fileType)):
            imgURL, fullPathName, fileName = CheckFile(fileType[x], submissionTitle, timePeriod, authorPath)
            author = submissionTitle.author
            if imgURL == None or fullPathName == None: continue
            else:
                if ".jpg" in fileType[x]:
                    FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
                if ".gifv" in fileType[x]:
                    FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
                if "redgifs" in fileType[x]:
                    # sets ytdl options; outtmpl sets the file destination, name, and file type
                    ytdlOpts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '{}'.format(fullPathName+'.mp4'),
                    'quiet': True}
                    # actual ytdl download + exception handling
                    if os.path.exists(fullPathName+'.mp4'):
                        print(f"{submissionTitle.author} {fullPathName} already exists")
                    else:
                        with youtube_dl.YoutubeDL(ytdlOpts) as ytdl:
                            try:
                                ytdl.download([imgURL])
                            except Exception:
                                print("Error")

def CheckFile(fileType,submissionTitle, timePeriod, authorPath):
    if fileType in "{}".format(submissionTitle.url):
        imgURL = submissionTitle.url
        fileName = imgURL.rsplit('/', 1)
        fullPathName = os.path.join(authorPath, f"{submissionTitle.author}-"+fileName[1])
#        print(submissionTitle.author, ": top", timePeriod, "of", submissionSubreddit, ":", imgURL)
        # checks if redditor's submission subreddit folder exists
        return imgURL, fullPathName, fileName[1]
    else: return None, None, None

if __name__ == "__main__":
    reddit = praw.Reddit(client_id=config.client_id, \
                         client_secret=config.client_secret, \
                         user_agent=config.user_agent, \
                         username=config.username, \
                         password=config.password)

    subredditName = config.subredditURL.rsplit('/', 1)[1]
    print("searching for authors in", subredditName)
    for submission in reddit.subreddit("{}".format(subredditName)).hot(limit=None):
        redditor = submission.author
        AuthorCheck(redditor)

   