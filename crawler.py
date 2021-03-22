import praw
import os
import requests
import shutil
import config
import argparse
import bs4
class Author():
    def __init__(self,author):
        self.author = author
        self.authorDirectory = os.path.join("./user/", f"{author}")

    def Get_Author(self):
        return self.author

    def Get_AuthorDirectory(self):
        return self.authorDirectory

    # returns a list of URLS, list of file names, and lists of file paths
    def Get_URLs(self):  # make this private??
        submissionsURLs = []
        sortType = [my_Reddit.redditor(f"{self.Get_Author()}").submissions.hot(), 
                    my_Reddit.redditor(f"{self.Get_Author()}").submissions.new(),
                    my_Reddit.redditor(f"{self.Get_Author()}").submissions.top()]
        for i in range(len(sortType)):
            for submissionTitle in sortType[i]:
                try:
                    if '.jpg' in submissionTitle.url:
                        submissionsURLs.append(submissionTitle.url)
                    elif 'redgif' in submissionTitle.url:
                        submissionsURLs.append(submissionTitle.url)
                    elif 'gifv' in submissionTitle.url: # returns url containing '.mp4'
                        submissionsURLs.append(submissionTitle.url.rsplit('.',1)[0]+'.mp4')
                except Exception as e:
                    print(e)
            return submissionsURLs
    
    def Get_FileNames(self):
        submissionsURLs = self.Get_URLs()
        fileNames = []
        for i in range(len(submissionsURLs)):
            if '.jpg' in submissionsURLs[i]:
                fileName = submissionsURLs[i].rsplit("/", 1)[1]
                fileNames.append(f"{self.Get_Author()}-{fileName}")
            elif 'redgif' in submissionsURLs[i]:
                fileName = submissionsURLs[i].rsplit("/", 1)[1]+'.mp4'
                fileNames.append(f"{self.Get_Author()}-{fileName}")
            elif '.mp4' in submissionsURLs[i]:
                fileName = submissionsURLs[i].rsplit("/", 1)[1]
                fileNames.append(f"{self.Get_Author()}-{fileName}")
        return fileNames

    def Get_FilePaths(self):
        fileNames = self.Get_FileNames()
        filePaths = []
        for i in range(len(fileNames)):
            if '.jpg' in fileNames[i]:
                filePaths.append(os.path.join(self.Get_AuthorDirectory(), fileNames[i]))
            elif '.mp4' in fileNames[i]:
                filePaths.append(os.path.join(self.Get_AuthorDirectory(), fileNames[i]))
        return filePaths

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
    redditDictofMethods = {'hot':my_Reddit.subreddit(subredditName).hot(limit=None),        # dictionary of reddit methods
                            'new':my_Reddit.subreddit(subredditName).new(limit=None), 
                            'rising':my_Reddit.subreddit(subredditName).rising(limit=None), 
                            'controversial':my_Reddit.subreddit(subredditName).controversial(limit=None),
                            'top':my_Reddit.subreddit(subredditName).top(limit=None)}
    for submission in redditDictofMethods[const_sortType]:
        author = Author(submission.author)
        submissionUrls = author.Get_URLs()
        submissionFileNames = author.Get_FileNames()
        submissionFilePaths = author.Get_FilePaths()

        # Checks of author directory exists
        if os.path.exists(author.Get_AuthorDirectory()):
            pass
        else: os.mkdir(author.Get_AuthorDirectory())

        for i in range(len(submissionUrls)):
            if os.path.exists(submissionFilePaths[i]):
                print(f"{author.Get_Author()} {submissionFilePaths[i]} already exists")
            elif '.jpg' in submissionUrls[i]:
                try:
                    r = requests.get(submissionUrls[i], stream=True)
                    if r.status_code == 200:
                        with open(submissionFilePaths[i], 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                        print(f"{author.Get_Author()} {submissionFilePaths[i]} downloaded successfully")
                    else:
                        print(f"{author.Get_Author()} {submissionFilePaths[i]} failed to download")
                except Exception:
                    print(f"{author.Get_Author()} {submissionFilePaths[i]} failed to download")
            elif '.mp4' in submissionUrls[i]:
                if 'redgif' in submissionUrls[i]:
                    res = requests.get(f'{submissionUrls[i]}')
                    res.raise_for_status()
                    exampleSoup = bs4.BeautifulSoup(res.text, 'html.parser')
                    elems = exampleSoup.select('#root source')
                    redgifURL = elems[2].get('src')
                    r = requests.get(redgifURL, stream=True)
                    if r.status_code == 200:
                        with open(submissionFilePaths[i], 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                        print(f"{author.Get_Author()} {submissionFilePaths[i]} downloaded successfully")
                    else:
                        print(f"{author.Get_Author()} {submissionFilePaths[i]} failed to download")
                else:
                    try:
                        r = requests.get(submissionUrls[i], stream=True)
                        if r.status_code == 200:
                            with open(submissionFilePaths[i], 'wb') as f:
                                shutil.copyfileobj(r.raw, f)
                            print(f"{author.Get_Author()} {submissionFilePaths[i]} downloaded successfully")
                        else:
                            print(f"{author.Get_Author()} {submissionFilePaths[i]} failed to download")
                    except Exception:
                        print(f"{author.Get_Author()} {submissionFilePaths[i]} failed to download")