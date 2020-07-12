from praw import Reddit
from praw.models import MoreComments
import pandas as pd
import os


class InstanceLogin:
    def __init__(self):
        """Generate reddit instance"""
        self.reddit = Reddit(user_agent='Comment Extraction (by /u/sgdzhou5)',
                             client_id='zanmra52bp9GSg', client_secret='jrm-DL_IxEexh8WZbi1VduOmAFk')


    def extract_comment(self, forum, filter, corpora):
        """Harvest comment data from Reddit"""
        subreddit = ""
        corpus = pd.DataFrame(columns=["Title", "Comments"])
        if filter == "top":
            subreddit = self.reddit.subreddit(forum).top('all')
        elif filter == "new":
            subreddit = self.reddit.subreddit(forum).new()
        elif filter == "hot":
            subreddit = self.reddit.subreddit(forum).hot()
        for submission in subreddit:
            title = submission.title
            if title not in corpora['Title'].values:
                print(title)
                for top_level_comment in submission.comments:
                    if isinstance(top_level_comment, MoreComments):
                        comments = top_level_comment.comments()
                    else:
                        comments = [top_level_comment.body]
                    for i in comments:
                        d = {"Title": [title], "Comments": [i]}
                        corpus = pd.concat([corpus, pd.DataFrame(d)],
                                           ignore_index=True)
        return corpus


path = os.path.dirname(os.path.dirname(__file__)) + '/Corpora/'
for i in ["top", "hot", "new"]:
    corpora = pd.read_csv(path + "{}.csv".format(i))
    corpus = InstanceLogin().extract_comment('IoT', i, corpora)
    corpus.to_csv(path + "{}[0711].csv".format(i), index=False)
