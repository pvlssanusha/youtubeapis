from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_cors import CORS  # Optional: for handling Cross-Origin Resource Sharing

app = Flask(__name__)
CORS(app)  # Optional: Enable CORS for all routes
from dotenv import load_dotenv
load_dotenv()
import os
import json
# Replace 'YOUR_YOUTUBE_API_KEY' with your actual YouTube API key
API_KEY = os.getenv("GEMINI_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

@app.route('/', methods=['GET'])
def search_videos():
    try:
        # Get the search topic from the request's query parameters
        search_topic = request.get_json().get('topic')
        #print(search_topic)
        if not search_topic:
            return jsonify({"error": "Please provide a search keyword."}), 400

        max_results = 10  # Number of videos to retrieve

        # Execute the search request
        search_response = youtube.search().list(
            q=search_topic,
            type='video',
            part='id',
            maxResults=max_results
        ).execute()
        #print(search_response)
        # Extract video IDs from the search results
        video_ids = [search_result['id']['videoId'] for search_result in search_response.get('items', [])]

        # Fetch video details using the video IDs
        video_details = []
        for video_id in video_ids:
            video_response = youtube.videos().list(
                id=video_id,
                part='snippet'
            ).execute()
            video_details.append(video_response)

        # Organize the video details into a JSON response
        response_data = []
        for video in video_details:
            title = video['items'][0]['snippet']['title']
            # description = video['items'][0]['snippet']['description']
            video_url = f"https://www.youtube.com/watch?v={video['items'][0]['id']}"
            response_data.append({
                "title": title,
                # "description": description,
                "video_url": video_url
            })

        return jsonify(response_data)

    except HttpError as e:
        error_message = json.loads(e.content)['error']['message']
        return jsonify({"error": f"An error occurred: {error_message}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
