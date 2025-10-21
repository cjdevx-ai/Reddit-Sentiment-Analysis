from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reddit_client import fetch_comments  # your Reddit scraper function

app = FastAPI()

origins = [
    "http://127.0.0.1:8123",   # Frontend dev server port (from vite.config.js)
    "http://127.0.0.1:5173",   # Vite default dev server port
    "http://127.0.0.1:3000",   # Alternative React dev server port
    "http://localhost:8123",   # Frontend dev server port (localhost)
    "http://localhost:5173",   # Vite default dev server port (localhost)
    "http://localhost:3000",   # Alternative React dev server port (localhost)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    try:
        comments = fetch_comments(url) 
        return {"comments": comments, "success": True}
    except ValueError as e:
        return {"error": str(e), "success": False}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "success": False}
