from fastapi import FastAPI
from pydantic import BaseModel
from reddit_client import fetch_comments  # your Reddit scraper function

app = FastAPI()

class Post(BaseModel):
    url: str

# initialize as None
latest_post: Post | None = None


@app.get("/")
def root():
    return {"message": "Reddit Sentiment Analysis API is running!"}


@app.post("/posturl")
def post_url(new_post: Post):
    global latest_post
    latest_post = new_post
    print("Stored post:", latest_post.url)
    return {"message": "Post stored successfully", "stored_url": latest_post.url}


@app.get("/latestpost")
def get_post():
    if not latest_post:
        return {"message": "No post stored yet."}
    return {"latest_post": latest_post.url}


@app.get("/latestpost/comments")
def get_latest_post_comments():
    """Fetch and return comments for the latest stored Reddit post."""
    if not latest_post:
        return {"message": "No post stored yet."}

    url = latest_post.url
    comments = fetch_comments(url) 
    return comments
