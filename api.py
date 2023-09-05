from fastapi import FastAPI
from pydantic import BaseModel
from transcript import YoutubeAPI
from summarizer import SummarizerAI

from dotenv import load_dotenv

youtubers = ["AIJason","MatthewBerman"]

app = FastAPI()
load_dotenv()

class Youtuber(BaseModel):
    content:str

@app.get("/")
def read_root():
    return {"Hello","World"}

@app.post("/")
def get_latest_youtuber_summarize(youtuber:Youtuber):
    content = youtuber.content 
    summarizer = SummarizerAI()
    days_ago = 2
    youtube = YoutubeAPI()
    videoslist = [(youtuber,youtube.get_youtuber_videos(youtube.get_youtuber_id(youtuber),days_ago)) for youtuber in youtubers]
    transcripts = []
    
    #Loop through all the youtubers and their videos and get a transcript for each video
    for youtuber,videos in videoslist:
        for video in videos:
            print(video['url'])
            transcripts.append((youtuber,{"transcript": youtube.get_transcript_as_text(video['url']), 'url':video['url'], 'title':video['title']}))

    # Add youtuber and each youtube video url, title and summary to list
    Summaries = [(yt,{"url": video['url'],"title": video['title'],"summary":summarizer.text_to_summary(video['transcript'])}) for yt,video in transcripts]
    result = {}
    for yt,summary in Summaries:
        if yt in result:
            result[yt].append(summary)
        else:
            result[yt] = [summary]

    return result
    

