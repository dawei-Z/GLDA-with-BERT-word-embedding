from praw import Reddit
from praw.models import MoreComments
import json
from datetime import datetime
import requests
import time
from urllib.request import urlopen
import pandas as pd
import os


class InstanceLogin:
    def __init__(self):
        """Generate reddit instance"""
        self.reddit = Reddit(user_agent='Comment Extraction (by /u/sgdzhou5)',
                             client_id='zanmra52bp9GSg', client_secret='jrm-DL_IxEexh8WZbi1VduOmAFk')
        self.start_time = datetime.utcnow()

    def submission_extraction(self):
        url = "https://api.pushshift.io/reddit/submission/search?subreddit=iot&before={}&sort=desc&size=1000"
        count = 0
        id_ls = []
        previous_epoch = int(self.start_time.timestamp())
        while True:
            new_url = url.format(str(previous_epoch))
            json = requests.get(new_url, headers={'User-Agent': 'Comment Extraction (by /u/sgdzhou5)'})
            time.sleep(1)
            json_data = json.json()
            if 'data' not in json_data:
                break
            objects = json_data['data']
            if len(objects) == 0:
                break
            for object in objects:
                previous_epoch = object['created_utc'] - 1
                count += 1
                if object['is_self']:
                    if 'selftext' not in object:
                        continue
                    try:
                         id_ls.append(object['id'])
                    except Exception as err:
                        print(f"Couldn't print post: {object['url']}")
                print("Saved {} submissions through {}.".format(count, datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d")))
        print(f"Saved {count}")
        return id_ls

    def extract_comment(self, id_ls):
        """Harvest comment data from Reddit"""
        corpus = pd.DataFrame(columns=["Title", "Comment"])
        for i in id_ls:
            submission = self.reddit.submission(id=i)
            submission.comments.replace_more(limit=None)
            title = submission.title
            comment_queue = submission.comments[:]
            while comment_queue:
                comment = comment_queue.pop(0)
                print(title)
                temp = comment.body
                d = {"Title": title, "Comment": temp}
                corpus = corpus.append(d, ignore_index=True)
                comment_queue.extend(comment.replies)
        return corpus


path = os.path.dirname(os.path.dirname(__file__)) + '/Corpora/'
# for i in ["top", "hot", "new"]:
#     corpora = pd.read_csv(path + "{}.csv".format(i))
reddit = InstanceLogin()
id_ls = reddit.submission_extraction()
corpus = InstanceLogin().extract_comment(id_ls)
corpus.to_csv(path + "new_corpus.csv", index=False)

