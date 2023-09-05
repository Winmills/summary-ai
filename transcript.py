import os
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

class YoutubeAPI:

    def __init__(self):
        """
        Initialize the YouTube API client and load the API key from the environment variable.
        """
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("You need to set the YOUTUBE_API_KEY environment variable.")
        
        # Initialize the YouTube Data API v3 client
        self.youtube = self.initialize_youtube_api()

    def initialize_youtube_api(self):
        """
        Initialize the YouTube Data API v3 client.
        """
        return build("youtube", "v3", developerKey=self.api_key)

    def get_video_id(self, link):
        """
        Extract the video ID from a YouTube video link.

        Args:
            link (str): The YouTube video link.

        Returns:
            dict: A dictionary with information about the video link.
                - 'fullLink': The full link.
                - 'videoId': The video ID.
                - 'hasExtraText': True if there is extra text in the link, False otherwise.
        """
        text = link.strip()
        youtube_regexp = r'http(s?)://(?:m\.|www\.)?(?:m\.)?youtu(?:be\.com/(?:watch\?v=|embed/|shorts/)|\.be/)([\w\-\_]*)(&(amp;)?[\w\?\=]*)?'
        match = re.match(youtube_regexp, text)
        
        if match:
            full_link = match.group(0)
            video_id = match.group(2)
            has_extra_text = len(text.replace(full_link, '').strip()) > 0
            return {'fullLink': full_link, 'videoId': video_id, 'hasExtraText': has_extra_text}
        else:
            return {'fullLink': None, 'videoId': None, 'hasExtraText': True}

    def get_transcripts(self, links):
        """
        Get transcripts for a list of YouTube video links.

        Args:
            links (list): A list of YouTube video links.

        Returns:
            tuple: A tuple containing video IDs and transcripts.
        """
        video_ids = [self.get_video_id(link)['videoId'] for link in links]
        transcripts, errors = YouTubeTranscriptApi.get_transcripts(video_ids=video_ids)
        return video_ids, transcripts

    def extract_text(self, data):
        """
        Extract text from transcript data.

        Args:
            data (list): A list of transcript data.

        Returns:
            str: The extracted text.
        """
        if isinstance(data, list):
            text_list = [entry["text"] for entry in data]
            return " ".join(text_list)
        else:
            return "Invalid input data."

    def get_transcript_as_text(self, video_link):
        """
        Get the transcript of a YouTube video as text.

        Args:
            video_link (str): The YouTube video link.

        Returns:
            str: The transcript text.
        """
        video_ids, transcripts = self.get_transcripts([video_link])
        result = self.extract_text(transcripts[video_ids[0]])
        return result

    def get_youtuber_id(self, youtuber_username):
        """
        Get the channel ID for a YouTuber's username.

        Args:
            youtuber_username (str): The username of the YouTuber.

        Returns:
            str: The channel ID or None if not found.
        """
        search_response = self.youtube.search().list(
            q=youtuber_username,
            type="channel",
            part="id"
        ).execute()
        
        if 'items' in search_response and len(search_response['items']) > 0:
            return search_response['items'][0]['id']['channelId']
            
        print(f"No channel found for the YouTuber: {youtuber_username}")
        return None

    def get_youtuber_videos(self, channel_id, days_ago):
        """
        Get the newest videos from a channel published in the last X days.

        Args:
            channel_id (str): The channel ID of the YouTuber.
            days_ago (int): The number of days to consider for recent videos.

        Returns:
            list: A list of dictionaries with video details.
        """
        published_after_date = (datetime.now() - timedelta(days=days_ago)).isoformat() + "Z"
        
        try:
            channel_response = self.youtube.search().list(
                channelId=channel_id,
                type="video",
                part="snippet",
                order="date",
                maxResults=5,
                publishedAfter=published_after_date
            ).execute()

            video_ids = [item['id']['videoId'] for item in channel_response['items']]

            videos = []
            for video_id in video_ids:
                video_info = self.youtube.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                if 'items' in video_info and len(video_info['items']) > 0:
                    item = video_info['items'][0]
                    video_title = item['snippet']['title']
                    video_description = item['snippet']['description']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    videos.append({
                        "title": video_title,
                        "url": video_url,
                        "description": video_description
                    })

            return videos
        
        except Exception as e:
            print(f"An error occurred while fetching videos: {str(e)}")
            return []

# Example usage:
# youtube_api = YoutubeAPI()
# videos = youtube_api.get_youtuber_videos("CHANNEL_ID", 7)  # Replace with channel ID and desired number of days
# for video in videos:
#     print(f"Title: {video['title']}")
#     print(f"Description: {video['description']}")
#     print(f"URL: {video['url']}")

if __name__ == "__main__":
    days_ago = 2
    youtube = YoutubeAPI()
    videos = youtube.get_youtuber_videos(youtube.get_youtuber_id("SamWitteveen"),days_ago)
        # Print the newest videos
    for video in videos:
        print(f"Title: {video['title']}")
        print(f"Description: {video['description']}")
        print(f"URL: {video['url']}")
        print()

    # video_links = ["https://www.youtube.com/watch?v=TIZRskDMyA4&ab_channel=DataScienceGarage", "https://www.youtube.com/watch?v=qo_fUjb02ns&ab_channel=BeyondFireship"]  # Replace with your extracted video IDs
    # video_ids,transcripts = get_youtube_transcripts(video_links)

    # for id in video_ids:
    #     text = extract_text(transcripts[id])
    #     print(text)
    #     print("-----------------------")
