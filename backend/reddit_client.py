import os
import praw
import re
from dotenv import load_dotenv
from praw.models import MoreComments
from transformers import pipeline

# Load environment variables from .env
load_dotenv()

# Initialize the Reddit API client using PRAW
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "reddit-sentiment-analyzer")
)

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True
)

def is_valid_reddit_submission_url(url: str) -> bool:
    """
    Validates if the URL is a Reddit submission URL (not a subreddit URL).
    
    Valid submission URLs:
    - https://www.reddit.com/r/subreddit/comments/post_id/title/
    - https://redd.it/post_id
    
    Invalid URLs (subreddit URLs):
    - https://www.reddit.com/r/subreddit/
    - https://www.reddit.com/r/subreddit
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check for redd.it short URLs
    if re.match(r'https?://redd\.it/\w+', url):
        return True
    
    # Check for full Reddit submission URLs
    # Must contain /comments/ and have a post ID
    if re.match(r'https?://(www\.)?reddit\.com/r/\w+/comments/\w+/', url):
        return True
    
    return False

def fetch_comments(url: str) -> dict[int, dict[str, str]]:
    """
    Fetches Reddit comments from a post and returns a dictionary:
    {
        1: {"comment": "text", "label": "POSITIVE", "score": 0.998},
        2: {"comment": "text", "label": "NEGATIVE", "score": 0.975},
        ...
    }
    """
    # Validate that the URL is a Reddit submission URL, not a subreddit URL
    if not is_valid_reddit_submission_url(url):
        raise ValueError(f"Invalid Reddit submission URL: {url}. Please provide a URL to a specific Reddit post, not a subreddit.")
    
    try:
        submission = reddit.submission(url=url)
    except Exception as e:
        raise ValueError(f"Failed to fetch Reddit submission: {str(e)}")

    list_comments = []
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        list_comments.append(top_level_comment.body)

    if list_comments:
        list_comments.pop(0)

    # Clean up newlines
    list_comments = [comment.replace('\n', ' ') for comment in list_comments]

    # Run sentiment analysis
    sentiments = sentiment_pipeline(list_comments)

    # Combine comments + sentiment results into a dictionary
    comments_dict = {
        i: {
            "comment": comment,
            "label": result["label"],
            "score": round(result["score"], 4)
        }
        for i, (comment, result) in enumerate(zip(list_comments, sentiments), start=1)
    }

    return comments_dict

"""
# --------------------------
# Test block
# --------------------------
if __name__ == "__main__":
    test_url = "https://www.reddit.com/r/GigilAko/comments/1o22kh4/gigil_ako_caterer_no_show_tapos_ayaw_magrefund"

    print("🔍 Fetching comments and analyzing sentiment...")
    comments = fetch_comments(test_url)
    print(f"✅ Retrieved {len(comments)} analyzed comments.\n")

    # Preview first 5 comments with sentiment
    for i, data in list(comments.items())[:5]:
        print(f"{i}. [{data['label']} ({data['score']})] {data['comment']}\n")
"""