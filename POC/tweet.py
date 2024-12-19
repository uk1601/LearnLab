import requests
import markdown
from requests_oauthlib import OAuth1
from html.parser import HTMLParser
import subprocess
import boto3
import os
from dotenv import load_dotenv

class HTMLStripper(HTMLParser):
    """
    A utility class to strip HTML tags from content.
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

class XPlatformClient:
    """
    A client to interact with the X (formerly Twitter) platform.
    Supports posting, updating, and deleting tweets, including media uploads.
    """
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        self.auth = OAuth1(api_key, api_secret_key, access_token, access_token_secret)
        self.post_url = "https://api.x.com/2/tweets"
        self.media_upload_url = "https://upload.x.com/1.1/media/upload.json"

    @staticmethod
    def strip_html_tags(html_content):
        """
        Strip HTML tags from the given content and return plain text.
        """
        stripper = HTMLStripper()
        stripper.feed(html_content)
        return stripper.get_data()

    def parse_markdown(self, markdown_content):
        """
        Convert Markdown content to plain text by stripping HTML tags.
        """
        html_content = markdown.markdown(markdown_content)
        return self.strip_html_tags(html_content)

    def split_text_into_chunks(self, content, max_length=280):
        """
        Split the content into logical chunks without cutting off sentences.
        """
        chunks = []
        while len(content) > max_length:
            split_index = content[:max_length].rfind(' ')
            if split_index == -1:
                split_index = max_length
            chunks.append(content[:split_index].strip())
            content = content[split_index:].strip()
        if content:
            chunks.append(content)
        return chunks

    def convert_audio_to_video(self, audio_path, image_path, output_path):
        """
        Converts an audio file to a video by combining it with a static image.
        """
        command = [
            "ffmpeg",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
        subprocess.run(command, check=True)
        print(f"Video created successfully: {output_path}")

    def upload_to_s3(self, file_path, bucket_name, s3_key):
        """
        Upload a file to an AWS S3 bucket.
        """
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          region_name=os.getenv('AWS_REGION'))
        try:
            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"File uploaded to S3: s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"Failed to upload to S3: {e}")

    def upload_media(self, file_path):
        """
        Upload a media file (image, GIF, or video) to the X platform.
        """
        with open(file_path, 'rb') as media_file:
            files = {"media": media_file}
            data = {"media_category": "tweet_video"}  # Specify video category
            response = requests.post(self.media_upload_url, auth=self.auth, files=files, data=data)

        if response.status_code == 200:
            media_id = response.json().get("media_id_string")
            print(f"Media uploaded successfully. Media ID: {media_id}")
            return media_id
        else:
            print(f"Failed to upload media: {response.status_code}, {response.text}")
            return None

    def post_tweet_thread(self, content, media_file_path=None):
        """
        Post a new tweet thread. Automatically splits content into logical chunks and posts as a thread.
        If a media file path is provided, the media is attached to the first tweet in the thread.
        """
        chunks = self.split_text_into_chunks(content)

        thread_ids = []
        in_reply_to_id = None
        media_id = None

        if media_file_path:
            media_id = self.upload_media(media_file_path)

        for i, chunk in enumerate(chunks):
            payload = {"text": chunk}
            if in_reply_to_id:
                payload["reply"] = {"in_reply_to_tweet_id": in_reply_to_id}
            if i == 0 and media_id:
                payload["media"] = {"media_ids": [media_id]}

            response = requests.post(
                self.post_url,
                auth=self.auth,
                json=payload
            )

            if response.status_code in (200, 201):
                response_data = response.json()
                tweet_id = response_data["data"]["id"]
                thread_ids.append(tweet_id)
                in_reply_to_id = tweet_id
                print("Post successful:", response_data)
            else:
                print("Failed to post:", response.status_code, response.text)
                break

        return thread_ids

    def delete_tweet(self, tweet_id):
        """
        Delete an existing tweet by its ID.
        """
        delete_url = f"https://api.x.com/2/tweets/{tweet_id}"
        response = requests.delete(delete_url, auth=self.auth)
        if response.status_code == 200:
            print(f"Tweet {tweet_id} deleted successfully.")
        else:
            print(f"Failed to delete tweet {tweet_id}:", response.status_code, response.text)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # X API credentials
    API_KEY = os.getenv('X_API_KEY')
    API_SECRET_KEY = os.getenv('X_API_SECRET_KEY')
    ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

    # Instantiate the client
    client = XPlatformClient(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Read and parse the markdown file
    with open("post.md", "r") as md_file:
        md_content = md_file.read()

    # Convert Markdown to plain text
    plain_text = client.parse_markdown(md_content)

    # Paths for audio, image, and output video
    #audio_path = "audio.mp3"  # Replace with the path to your audio file
    #image_path = "https://learnlab-files.s3.us-east-1.amazonaws.com/audio_video_files/audio_image.jpg"  # Static image URL
    #output_video_path = "output_video.mp4"

    # S3 bucket details
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    s3_key = "audio_video_files/output_video.mp4"

    # Convert audio to video
    #client.convert_audio_to_video(audio_path, image_path, output_video_path)

    # Upload the video to S3
    #client.upload_to_s3(output_video_path, bucket_name, s3_key)

    # Post the tweet thread with the generated video
    #client.post_tweet_thread(plain_text, media_file_path=output_video_path)
    client.post_tweet_thread(plain_text)