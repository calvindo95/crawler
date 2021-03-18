import praw
import time
import os
import requests
import shutil
import youtube_dl
import config
import multiprocessing
import argparse

def SortSubmissionType(subredditName, reddit):
    timePeriods = ["hour", "day", "week", "month", "year", "all"]
    if const_sortType == 'hot':
        for submission in reddit.subreddit(f"{subredditName}").hot(limit=None):
            originalPoster = submission.author
            authorPath = AuthorCheck(originalPoster)
            for i in range(len(timePeriods)):
                Download(timePeriods[i], originalPoster, authorPath)
    if const_sortType == 'new':
        for submission in reddit.subreddit(f"{subredditName}").new(limit=None):
            originalPoster = submission.author
            authorPath = AuthorCheck(originalPoster)
            for i in range(len(timePeriods)):
                Download(timePeriods[i], originalPoster, authorPath)
    if const_sortType == 'rising':
        for submission in reddit.subreddit(f"{subredditName}").rising(limit=None):
            originalPoster = submission.author
            authorPath = AuthorCheck(originalPoster)
            for i in range(len(timePeriods)):
                Download(timePeriods[i], originalPoster, authorPath)
    if const_sortType == 'controversial':
        for submission in reddit.subreddit(f"{subredditName}").controversial(limit=None):
            originalPoster = submission.author
            authorPath = AuthorCheck(originalPoster)
            for i in range(len(timePeriods)):
                Download(timePeriods[i], originalPoster, authorPath)
    if const_sortType == 'top':
        for submission in reddit.subreddit(f"{subredditName}").top(limit=None):
            originalPoster = submission.author
            authorPath = AuthorCheck(originalPoster)
            for i in range(len(timePeriods)):
                Download(timePeriods[i], originalPoster, authorPath)

'''
Check if author folder exists, creates folder if does not exist
Returns relative authorPath directory
'''
def AuthorCheck(originalPoster):
    try:
        # creates author folder
        authorPath = os.path.join("./user/", f"{originalPoster}")
        if os.path.isdir(authorPath):
            pass
        else:
            os.makedirs(authorPath)
        return authorPath
    except Exception: 
        print("Error")

def Download(timePeriod, originalPoster, authorPath):
    for submissionTitle in reddit.redditor(f"{originalPoster}").submissions.new():
        fileType = [".jpg", "redgifs", "gifv"]
        for x in range (len(fileType)):
            imgURL, fullPathName, fileName = CheckFile(fileType[x], submissionTitle, timePeriod, authorPath)
            author = submissionTitle.author
            if imgURL == None or fullPathName == None: continue
            elif ".jpg" in fileType[x]:
                FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
            elif ".gifv" in fileType[x]:
                FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
            elif "redgifs" in fileType[x]:
                    # sets ytdl options; outtmpl sets the file destination, name, and file type
                    ytdlOpts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{fullPathName}.mp4',
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
            else: pass
    # finds redditor's top submissions based on top submission type
    for submissionTitle in reddit.redditor(f"{originalPoster}").submissions.top(f"{timePeriod}"):
        fileType = [".jpg", "redgifs", "gifv"]
        for x in range (len(fileType)):
            imgURL, fullPathName, fileName = CheckFile(fileType[x], submissionTitle, timePeriod, authorPath)
            author = submissionTitle.author
            if imgURL == None or fullPathName == None: continue
            elif ".jpg" in fileType[x]:
                FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
            elif ".gifv" in fileType[x]:
                FileDownload(fullPathName, author, imgURL, fileName, timePeriod)
            elif "redgifs" in fileType[x]:
                    # sets ytdl options; outtmpl sets the file destination, name, and file type
                    ytdlOpts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{fullPathName}.mp4',
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
            else: pass

def AuthorSubmissions():
    pass

def CheckFile(fileType,submissionTitle, timePeriod, authorPath):
    if fileType in f"{submissionTitle.url}":
        imgURL = submissionTitle.url
        fileName = imgURL.rsplit('/', 1)
        fullPathName = os.path.join(authorPath, f"{submissionTitle.author}-{fileName[1]}")
        # checks if redditor's submission subreddit folder exists
        return imgURL, fullPathName, fileName[1]
    else: return None, None, None

def FileDownload(fullPathName, author, imgURL, fileName, timePeriod):
    if os.path.exists(fullPathName):
        print(f"{author} {fullPathName} already exists")
    else:
        try:
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
        except Exception as e:
            print(e)

parser = argparse.ArgumentParser()
parser.add_argument("sortType", nargs='?', help="Sort by 'hot', 'new', 'rising', 'controversial', 'top'; default='hot'", default='hot')
args = parser.parse_args()
const_sortType = args.sortType

if __name__ == "__main__":
    reddit = praw.Reddit(client_id=config.client_id, \
                         client_secret=config.client_secret, \
                         user_agent=config.user_agent, \
                         username=config.username, \
                         password=config.password)
    subredditName = config.subredditURL.rsplit('/', 1)[1]
    print(f"searching for {args.sortType} authors in {subredditName}")
    SortSubmissionType(subredditName, reddit)
   