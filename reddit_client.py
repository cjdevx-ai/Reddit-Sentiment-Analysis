# reddit_client.py
import os
import praw
from dotenv import load_dotenv
from praw.models import MoreComments

# Load environment variables from .env
load_dotenv()

# Initialize the Reddit API client using PRAW
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "reddit-sentiment-analyzer")
)

def fetch_comments(url: str) -> list[str]:
    # get submission
    submission = reddit.submission(url=url)

    # list to hold comments
    list_comments = []

    # iterate through comments
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        list_comments.append(top_level_comment.body)

    if list_comments:
        list_comments.pop(0)

    list_comments = [comment.replace('\n', ' ') for comment in list_comments]
    comments_dict = {i: comment for i, comment in enumerate(list_comments, start=1)}
    return comments_dict

