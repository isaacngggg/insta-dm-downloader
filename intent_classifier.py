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

        categories = ["travel", "restaurant", "activities","recipes", "film & shows", "thoughts","other"]

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


        category_properties = {
            "travel": ['title','city/province', 'country', 'category','things_to_know','offers','last_date_of_offer','tags'],
            "restaurant": ['restaurant_name', 'address', 'cuisine', 'city/province', 'country','things_to_know','offers','last_date_of_offer','tags'],
            "activities": ['activity_name', 'address', 'city/province', 'country', 'category','things_to_know','offers','last_date_of_offer','tags'],
            "recipes": ['dish_name', 'cuisine', 'recipe', 'ingredients', 'effort_level','tags'],
            "film & shows": ['film_name', 'genre', 'director', 'actors', 'plot_summary','tags'],
            "ideas & thoughts": ['thought', 'type','tags'],
        }

        enums = {
            "category": ['adventure', 'beach', 'city', 'countryside', 'culture', 'family', 'food', 'history', 'nature', 'nightlife', 'outdoor', 'relaxing', 'shopping', 'sightseeing', 'sports', 'wellness'],
            "cuisine": ['african', 'american', 'asian', 'caribbean', 'chinese', 'european', 'french', 'indian', 'italian', 'japanese', 'korean', 'latin american', 'mediterranean', 'middle eastern', 'thai', 'vietnamese'],
            "activities": ['adventure', 'beach', 'city', 'countryside', 'culture', 'family', 'food', 'history', 'nature', 'nightlife', 'outdoor', 'relaxing', 'shopping', 'sightseeing', 'sports', 'wellness'],
            "effort_level": ['easy', 'medium', 'hard'],
            "genre": ['action', 'adventure', 'comedy', 'crime', 'drama', 'fantasy', 'historical', 'horror', 'mystery', 'romance', 'science fiction', 'thriller', 'western'],
            "type": ['philosophical', 'political', 'religious', 'scientific', 'social', 'spiritual','business', 'other']
        }

        example_response = {
            "travel": "{'title':'Bali Travel Guide', 'city/province':'Bali', 'country':'Indonesia', 'category':'beach', 'things_to_know':'Bali is a popular tourist destination', 'offers':'10% off on hotels', 'last_date_of_offer':'2022-12-31', 'tags':'beach, travel'}",
            "restaurant": "{'restaurant_name':'The Rock', 'address':'232 Bhanna Street', 'cuisine':'seafood', 'city':'Bali', 'country':'Indonesia', 'things_to_know':'The Rock is a popular seafood restaurant', 'offers':'10% off on seafood', 'last_date_of_offer':'2022-12-31', 'tags':'seafood, restaurant'}",
            "activities": "{'activity_name':'Surfing', 'address':'Kuta Beach', 'city':'Bali', 'country':'Indonesia', 'category':'beach', 'things_to_know':'Surfing is a popular activity in Bali', 'offers':'10% off on surfing lessons', 'last_date_of_offer':'2022-12-31', 'tags':'surfing, beach'}",
            "recipes": "{'dish_name':'Spaghetti Carbonara', 'cuisine':'Italian', 'recipe':'Boil pasta, fry bacon, mix with eggs and cheese', 'ingredients':'pasta, bacon, eggs, cheese', 'effort_level':'easy', 'tags':'pasta, italian'}",
            "film & shows": "{'film_name':'Inception', 'genre':'science fiction', 'director':'Christopher Nolan', 'actors':'Leonardo DiCaprio, Ellen Page', 'plot_summary':'A thief who enters the dreams of others to steal secrets', 'tags':'science fiction, thriller'}",
            "ideas & thoughts": "{'thought':'The world is a book and those who do not travel read only one page', 'type':'philosophical', 'tags':'travel, philosophy'}"
        }

        if response in categories:
            classifier_value = response

            
            rules = ""
            for cat  in category_properties[response]:
                if cat in enums.keys():
                    rule =f" For the property {cat}, please use the following values: {enums[cat]} \n"
                    rules += rule


            prompt = ("This is a short video from instagram. "
                +transcription+caption+video_frame_summary+
                " the video is about (and it's classifier) " + classifier_value + ". \n"
                f" Can you return a json object with the following properties: {category_properties[response]} ,? If it is not applicable, please return the value as an empty string (i.e. '') and not 'None'. \n"
                " For recipe, please return in step by step guide, for last_date on offer always provide in the formate: 'yyyy-mm-dd'\n" +
                rules +
                " Please not add any description or title 'json' to the json object. \n\n Just return the json object alone as a string in a single line & use double quotation whenever possible to avoid single quotations affecting the json formating, "
                "an example response is shown here: " + example_response[classifier_value]
            )
            messages = [{"role": "user", "content": prompt}]
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
            )
            json_response = completion.choices[0].message.content.strip().lower()
            print(f"[{get_now()}] Json Response from chatgpt: {json_response}")
            
            try:
                json_dict = eval(json_response)
                update_response = supabase.table("clips").update(json_dict).eq("message_id", message_id).execute()
            except Exception as e:
                print(f"[{get_now()}] Error updating supabase: {e}")
                # Retry logic
                for _ in range(3):
                    try:
                        # Check if response starts and ends with "json" or "```"
                        while not json_response.startswith("{"):
                            json_response = json_response[1:].strip()
                        while not json_response.endswith("}"):
                            json_response = json_response[:-1].strip()
                        json_dict = eval(json_response)
                        update_response = supabase.table("clips").update(json_dict).eq("message_id", message_id).execute()
                        break
                    except Exception as e:
                        print(f"[{get_now()}] Error updating supabase on retry: {e}")
                else:
                    print(f"[{get_now()}] Failed to update supabase after 3 retries")
                
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
    classify_intent("31759772573669580872611577441812480")

