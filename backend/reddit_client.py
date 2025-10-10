import os
import praw
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

def fetch_comments(url: str) -> dict[int, dict[str, str]]:
    """
    Fetches Reddit comments from a post and returns a dictionary:
    {
        1: {"comment": "text", "label": "POSITIVE", "score": 0.998},
        2: {"comment": "text", "label": "NEGATIVE", "score": 0.975},
        ...
    }
    """
    submission = reddit.submission(url=url)

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