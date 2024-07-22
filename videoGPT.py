from openai import OpenAI
from moviepy.editor import VideoFileClip
import os
import json
from IPython.display import display, Image, Audio, DisplayObject, DisplayHandle
import asyncio


import cv2  # We're using OpenCV to read video frames
import base64
import time
import requests



def get_video_summary(message_id):


    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    download_path = "download"
    video_path = None

    for folder in os.listdir(download_path):
        if folder == message_id:
            for clip in os.listdir(f"{download_path}/{folder}"):
                if clip.endswith(".mp4"):
                    video_path = f"{download_path}/{folder}/{clip}"
                    break
            if video_path:
                break

    video = cv2.VideoCapture(video_path)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")

    display_handle = DisplayHandle(display_id=True)

    # display_handle = display(Image(data=b''), display_id=True)

    for img in base64Frames:
        display_handle.update(Image(data=base64.b64decode(img.encode("utf-8"))))
        # img_data = base64.b64decode(img.encode("utf-8"))
        # display_handle.display(Image(data=img_data))

        time.sleep(0.025)

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "These are frames from a video that I want to upload. Generate a summary of what the video is about and I can upload along with transcription. Try to use the caption as much as possible to help with understanding the video content.",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)

    video_summary = result.choices[0].message.content

    return video_summary



#test the function

# message_id = "31735206860605345065691649314652160"
# get_video_summary(message_id)