import praw
import os
import requests
import shutil
import config
import argparse
import bs4
import threading
from datetime import datetime

class Author():
    def __init__(self,author):
        self.author = author
        self.authorDirectory = os.path.join("./user/", f"{author}")
        self.submissions = self.Get_AuthorSubmissions()
        self.submissionURLs = self.Search_URLs()
        self.fileNames = self.Search_FileNames()
        self.filePaths = self.Search_FilePaths()

    # returns a list of all submissions
    def Get_AuthorSubmissions(self):
        submissions = []
        sortType = [my_Reddit.redditor(f"{self.author}").submissions.hot(), 
                    my_Reddit.redditor(f"{self.author}").submissions.new(),
                    my_Reddit.redditor(f"{self.author}").submissions.top()]
        for i in range(len(sortType)):
            try:
                for submissionTitle in sortType[i]:
                    if submissionTitle in submissions:
                        pass
                    else:
                        submissions.append(submissionTitle)
            except Exception as e:
                print(f"Get_AuthorSubmissions {e}")
        return submissions

    # returns a list of URLS containing '.jpg' 'redgif' and 'gifv'
    def Search_URLs(self):
        submissionURLs = []
        submissions = self.submissions
        for submission in submissions:
            if '.jpg' in submission.url: # appends url with '.jpg'
                submissionURLs.append(submission.url)
            elif 'gifv' in submission.url: # appends url containing '.mp4'
                submissionURLs.append(submission.url.rsplit('.',1)[0]+'.mp4')
            elif 'redgif' in submission.url: # finds redgif source via html and appends with '.mp4'
                try:
                    res = requests.get(f'{submission.url}')
                    if res.status_code == 200:
                        soupHTML = bs4.BeautifulSoup(res.text, 'html.parser')
                        elems = soupHTML.select('meta[property="og:video"]')
                        redgifURL = elems[0].get('content')
                        submissionURLs.append(redgifURL)
                except Exception as e:
                    print(f"redgif Get_URLs {submission.url}: {e}")
                    print()
        return submissionURLs
    
    def Search_FileNames(self):
        submissionURLs = self.submissionURLs
        fileNames = []
        for i in range(len(submissionURLs)):
            if '.jpg' in submissionURLs[i]:
                fileName = submissionURLs[i].rsplit("/", 1)[1]
                fileNames.append(f"{self.author}-{fileName}")
            elif '.mp4' in submissionURLs[i]:
                fileName = submissionURLs[i].rsplit("/", 1)[1]
                fileNames.append(f"{self.author}-{fileName}")
            else:
                fileNames.append('')
        return fileNames

    def Search_FilePaths(self):
        fileNames = self.fileNames
        filePaths = []
        for i in range(len(fileNames)):
            if '.jpg' in fileNames[i]:
                filePaths.append(os.path.join(self.authorDirectory, fileNames[i]))
            elif '.mp4' in fileNames[i]:
                filePaths.append(os.path.join(self.authorDirectory, fileNames[i]))
            else:
                filePaths.append('')
        return filePaths

def download_file(author, url, file_path):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    if os.path.exists(file_path):
        print(f"{dt_string} {author} {file_path} already exists")
    else:
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                print(f"{dt_string} {author} {file_path} downloaded successfully")
            else:
                print(f"{dt_string} {author} {file_path} failed to download")
        except Exception:
            print(f"{dt_string} {author} {file_path} failed to download")

if __name__ == "__main__":
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

    subredditName = config.subreddit_Name
    print(f"searching for {args.sortType} authors in {subredditName}")
    redditDictofMethods = {'hot':my_Reddit.subreddit(subredditName).hot(limit=None),        # dictionary of reddit methods
                            'new':my_Reddit.subreddit(subredditName).new(limit=None), 
                            'rising':my_Reddit.subreddit(subredditName).rising(limit=None), 
                            'controversial':my_Reddit.subreddit(subredditName).controversial(limit=None),
                            'top':my_Reddit.subreddit(subredditName).top(limit=None)}
    for submission in redditDictofMethods[const_sortType]:
        print(f"Crawling through {submission.author}")
        author = Author(submission.author)
        submissionUrls = author.submissionURLs
        submissionFilePaths = author.filePaths

        # Checks of author directory exists
        if os.path.exists(author.authorDirectory):
            pass
        else: os.mkdir(author.authorDirectory)

        all_author_links = []
        for i in range(len(submissionUrls)):
            author_links = []
            author_links.append(author.author)
            author_links.append(submissionUrls[i])
            author_links.append(submissionFilePaths[i])
            all_author_links.append(author_links)
        
        n = 4 #number of parallel connections
        chunks = [all_author_links[i * n:(i + 1) * n] for i in range((len(all_author_links) + n - 1) // n )]

        for chunk in chunks:
            threads = []
            for data in chunk:
                author, url, file_path = data
                thread = threading.Thread(target=download_file, args=(author, url, file_path))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()