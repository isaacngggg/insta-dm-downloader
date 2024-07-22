import json
from openai import OpenAI
import os

from supabase import create_client, Client

import datetime


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def classify_intent(message_id):
    
    response = supabase.table("clips").select("*").eq("message_id", message_id).execute()

    if response.data:

        seen_message = response.data[0]

        # print (seen_message)

        if seen_message['clip_transcription'] != None:
                transcription = "Here is the transcribed text: " + seen_message["clip_transcription"]
        else:
            transcription = "For this video, I was not able to get a transcription"

        if seen_message['clip_caption']!= None:
            caption = " the caption is " + seen_message["clip_caption"]
        else:
            caption = "For this video, I was not able to get a caption"

        if seen_message['clip_frame_summary']!= None:
            video_frame_summary = " the video summary is " + seen_message["clip_frame_summary"]
        else: 
            video_frame_summary = "For this video, I was not able to get a video frame summary"


        # if it is return the json object
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # using the transcription, caption and message text, determine the intent of the message using openai's intent classifier
        # check whether the video is video about travel, food or entertainment

        categories = ["travel", "restaurant", "entertainment","recipes", "other"]

        options_str = " ".join(categories)

        
    

        first_prompt = ("Based on the transcribed text and caption, "
            "please categorize this video as either " + options_str + ". "
                "please just respond with the category, no need to provide a reason."
            +transcription+caption)

        messages = [{"role": "user", "content": first_prompt}]


        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=10,
        )
        response = completion.choices[0].message.content.strip().lower()

        options_str = " ".join(categories)

        if response in categories:
            classifier_value = response

            prompt = ("This is a short video from instagram. "
                +transcription+caption+video_frame_summary+
                " the classifier value is " + classifier_value +
                " Can you return a json object with the following properties:  'restaurant_name', 'location', 'cusinie', 'city', 'country', 'dish_name', 'things_to_know', 'activity_name', 'recipe', 'ingredients',? If it is not applicable, please return the value as an empty string (i.e. '') and not 'None' because that will not work. For recipe, please return in step by step guide" +
                " Please not add any description or title 'json' to the json object. \n\n Just return the json object alone as a string in a single line, an example response is shown here: {'restaurant_name':'Wing Wah', 'location':'', 'cusinie':'chinese', 'city':'kowloon', 'country':'hong kong', 'dish_name':'', 'things_to_know':'', 'activity_name':'', 'recipe':'1. Boil water 2. Add noodles 3. Add seasoning 4. Serve', 'ingredients':'noodles, seasoning'}"
            )
            messages = [{"role": "user", "content": prompt}]
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
            )
            json_response = completion.choices[0].message.content.strip().lower()
            print(f"[{get_now()}] Json Response from chatgpt: {json_response}")
            json_dict = eval(json_response)
            
            update_response = supabase.table("clips").update(json_dict).eq("message_id", message_id).execute()

                
        else:
            classifier_value = "other"

        # seen_message["classifier"] = classifier_value

        response = supabase.table("clips").update({"classifier":classifier_value}).eq("message_id", message_id).execute()


    else:
        # if it isn't return None
        print("Cannot find message")


# classify_intent("31737217669174158506072675312467968")

# get_transcription('31737217669174158506072675312467968')

if __name__ == "__main__":
    classify_intent("31757843032829550901368753752113152")

