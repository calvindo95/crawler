import praw
import time
import os
import requests
import shutil
import youtube_dl
import config
from prawcore.exceptions import Forbidden, NotFound
from urllib.error import URLError

# checks if subreddit folder exists and returns submissionTitle's imgURL, fullPathName, and fileName
def checkFile(fileType,submissionTitle, topType):
    if fileType in "{}".format(submissionTitle.url):
        print(submissionTitle.author, ": top", topType, "of", submissionTitle.subreddit, ":", submissionTitle.url)
        imgURL = submissionTitle.url
        imgFolder = os.path.join("{}/".format(authorPath), "{}".format(submissionTitle.subreddit))
        fileName = imgURL.rsplit('/', 1)
        fullPathName = os.path.join(imgFolder, fileName[1])
        # checks if redditor's submission subreddit folder exists
        if not os.path.exists(imgFolder):
            print("creating folder", submissionTitle.subreddit)
            os.makedirs(imgFolder)
        else: pass
        return imgURL, fullPathName, fileName[1]
    else: return None, None, None

def Download(topType):
    # finds redditor's top submissions based on top submission type
    for submissionTitle in reddit.redditor("{}".format(redditor)).submissions.top("{}".format(topType)):
        fileType = [".jpg", "redgifs"]
        for x in range (len(fileType)):
            imgURL, fullPathName, fileName = checkFile(fileType[x], submissionTitle, topType)
            if imgURL == None or fullPathName == None: continue
            else:
                if ".jpg" in fileType[x]:
                    if os.path.exists(fullPathName):
                        print("File already exists")
                    else:
                        # opens url image
                        r = requests.get(imgURL, stream = True)
                        # checks if image was retrieved
                        if r.status_code == 200:
                            r.raw.decode_content == True
                            # saves image at fullPathName
                            with open(fullPathName, 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                            print('Image sucessfully Downloaded: ',fileName)
                        else:
                            print('Image Couldn\'t be retreived')
                if "redgifs" in fileType[x]:
                    # sets ytdl options; outtmpl sets the file destination, name, and file type
                    ytdlOpts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '{}'.format(fullPathName+'.mp4'),
                    'quiet': True}
                    # actual ytdl download + exception handling
                    if os.path.exists(fullPathName+'.mp4'):
                        print("File already exists")
                    else:
                        with youtube_dl.YoutubeDL(ytdlOpts) as ytdl:
                            try:
                                ytdl.download([imgURL])
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

            time.sleep(1)
        except Forbidden:
            print("Forbidden error")
        except NotFound:
            print("404 HTTP response")
