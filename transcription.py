from moviepy.editor import VideoFileClip
import os


def get_transcription(message_id):
    # for each video file in the download folder, extract the audio and save it as an mp3 file in a new folder called audio

    for folder in os.listdir("download"):
        if folder == message_id:
            for clip in os.listdir(f"download/{folder}"):
                if clip.endswith(".mp4"):
                    video = VideoFileClip(f"download/{folder}/{clip}")
                    audio = video.audio
                    # create the audio folder if it doesn't exist
                    if not os.path.exists("audio"):
                        os.makedirs("audio")
                    if not os.path.exists(f"audio/{folder}.mp3"):
                        audio.write_audiofile(f"audio/{folder}.mp3")

            # call open ai's speech to text api to transcribe the audio files in the audio folder

            from openai import OpenAI
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            from pathlib import Path

            audio = message_id+".mp3"

            if audio in os.listdir('audio'):
                file_path_str = f"audio/{audio}"
                file_path = Path(file_path_str)
                with open(file_path, 'rb') as file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=file_path, 
                        response_format="text"
                    )
                    
                    # save the transcribed text to the seen_messages.json file as new property called "transcribed_text"

                    # with open("seen_messages.json", "r") as file:
                    #     seen_messages = json.load(file)
                    #     clipPk = audio.split(".")[0]
                    #     seen_messages[clipPk]["transcribed_text"] = transcription
                    # with open("seen_messages.json", "w") as file:
                    #     json.dump(seen_messages, file)

                    return transcription

