from praw import Reddit
from praw.models import MoreComments
import pandas as pd


class InstanceLogin:
    def __init__(self):
        self.reddit = Reddit(user_agent='Comment Extraction (by /u/sgdzhou5)',
                             client_id='zanmra52bp9GSg', client_secret='jrm-DL_IxEexh8WZbi1VduOmAFk')

    def extract_comment(self, forum):
        corpus = pd.DataFrame(columns=["Title", "Comments"])
        subreddit = self.reddit.subreddit(forum)
        for submission in subreddit.top('all'):
            title = submission.title
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


corpus = InstanceLogin().extract_comment('IoT')
corpus.to_csv("Corpus.csv")
