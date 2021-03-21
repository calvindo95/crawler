import praw
import time
import os
import requests
import shutil
import youtube_dl
import config
import argparse

# Checks if OP account directory exists; creates account directory if directory does not exist
def Check_opAccount_Directory(account_Directory):
    if os.path.isdir(account_Directory): pass
    else: os.mkdir(account_Directory)

# Crawls through subreddit poster's account
def Crawl_opAccount(opAccount, my_Reddit, timePeriod):
    try:
        for submissionTitle in my_Reddit.redditor(f"{opAccount}").submissions.new():
            Search_Sumbissions(opAccount, submissionTitle)
        for submissionTitle in my_Reddit.redditor(f"{opAccount}").submissions.top(timePeriod):
            Search_Sumbissions(opAccount, submissionTitle)
    except Exception as e: print(e)

# Searches for submissions from poster
def Search_Sumbissions(opAccount, submissionTitle):
    fileTypes = [".jpg", "redgifs"]
    submissionURL = submissionTitle.url
    fileName = submissionURL.rsplit("/", 1)[1]
    filePath = os.path.join(account_Directory, f"{opAccount}-{fileName}")
    for i in range(len(fileTypes)):
        if fileTypes[i] in submissionURL:
            DownloadFile(filePath, fileTypes[i], submissionURL, opAccount)
        else: pass

# downloads images and videos
def DownloadFile(filePath, fileType, submissionURL, opAccount):
    if os.path.exists(filePath):
        print(f"{opAccount} {filePath} already exists")
    elif os.path.exists(filePath+'.mp4'):
        print(f"{opAccount} {filePath}.mp4 already exists")
    elif fileType == ".jpg":
        r = requests.get(submissionURL, stream=True)
        if r.status_code == 200:
            with open(filePath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f"{opAccount} {filePath} downloaded successfully")
        else:
            print(f"{opAccount} {filePath} failed to download")
    elif fileType == "redgifs":
        # sets ytdl options; outtmpl sets the file destination, name, and file type
        ytdlOpts = {'format': 'bestaudio/best', 'outtmpl': f'{filePath}.mp4', 'quiet': True}
        # actual ytdl download + exception handling
        with youtube_dl.YoutubeDL(ytdlOpts) as ytdl:
            try:
                ytdl.download([submissionURL])
                print(f"{opAccount} {filePath}.mp4 downloaded successfully")
            except Exception:
                print(f"{opAccount} {filePath}.mp4 failed to download")

parser = argparse.ArgumentParser()
parser.add_argument("sortType", nargs='?', help="Sort by 'hot', 'new', 'rising', 'controversial', 'top'; default='hot'", \
    default='hot')
args = parser.parse_args()
const_sortType = args.sortType
my_Reddit = praw.Reddit(client_id=config.client_id, \
                         client_secret=config.client_secret, \
                         user_agent=config.user_agent, \
                         username=config.username, \
                         password=config.password)

if __name__ == "__main__":
    subredditName = config.subredditURL.rsplit('/', 1)[1]
    print(f"searching for {args.sortType} authors in {subredditName}")
    timePeriods = ["hour", "day", "week", "month", "year", "all"]
    redditDictofMethods = {'hot':my_Reddit.subreddit(subredditName).hot(limit=None),        # dictionary of reddit methods
    'new':my_Reddit.subreddit(subredditName).new(limit=None), 
    'rising':my_Reddit.subreddit(subredditName).rising(limit=None), 
    'controversial':my_Reddit.subreddit(subredditName).controversial(limit=None),
    'top':my_Reddit.subreddit(subredditName).top(limit=None)}
    for i in range(len(timePeriods)):
        for const_sortType in redditDictofMethods:
            for submission in redditDictofMethods[const_sortType]:
                opAccount = submission.author
                account_Directory = os.path.join("./user/", f"{opAccount}")
                Check_opAccount_Directory(account_Directory)
                Crawl_opAccount(opAccount, my_Reddit, timePeriods[i])