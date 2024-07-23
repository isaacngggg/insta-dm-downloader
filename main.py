import os, json, time, random, sys, datetime, ast
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
# from videoGPT import get_video_summary
from intent_classifier import classify_intent
from transcription import get_transcription
import os
from supabase import create_client, Client as SupabaseClient
from skyscraper import get_preferred_date
import shutil

load_dotenv()

username = os.environ.get("IG_USERNAME")
email = os.environ.get("IG_EMAIL")
password = os.environ.get("IG_PASSWORD")


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")
else:
    supabase: SupabaseClient = create_client(url, key)


def authenticate(client, session_file):
    if os.path.exists(session_file):
        client.load_settings(session_file)
        try:
            client.login(username, password)
            client.get_timeline_feed()  # check if the session is valid
        except LoginRequired:
            # session is invalid, re-login and save the new session
            client.login(username, password)
            client.dump_settings(session_file)
    else:
        client.login(username, password)
        client.dump_settings(session_file)


def load_seen_messages(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    else:
        return {}


def save_seen_messages(file, messages):
    with open(file, "w") as f:
        json.dump(messages, f)


def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sleep_countdown():
    # check for new messages every random seconds
    sleep_time = random.randint(30*60, 60*60)
    print(f"[{get_now()}] Timeout duration: {sleep_time} seconds.")

    for remaining_time in range(sleep_time, 0, -1):
        sys.stdout.write(f"\r[{get_now()}] Time remaining: {remaining_time} second(s).")
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\n")

def download_clip(client, clip_pk, message_id):
    print(f"[{get_now()}] Downloading reel {clip_pk}")

    # Get the current working directory
    cwd = os.getcwd()

    # Construct the path to the download folder
    download_path = os.path.join(cwd, "download", str(message_id))

    # Check if the download folder exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"[{get_now()}] Created {download_path}")

    client.video_download(clip_pk, f"{download_path}")
    print(f"[{get_now()}] Downloaded {clip_pk}")
    client.delay_range = [1, 3]

def send_message(cl, message_id, thread_ids):
    try:
        response = supabase.table("clips").select("*").eq("message_id", message_id).execute()
        if response.data:
            seen_message = response.data[0]
            if seen_message['classifier'] == 'travel':
                today = datetime.date.today().strftime("%Y-%m-%d")
                location = seen_message['location']
                city = seen_message['city'] 
                country = seen_message['country']

                if seen_message['city'] != None:
                    cheapest_months,average_prices = get_preferred_date(city, today)
                    message = f"Based on the location {city}, the cheapest months to travel from London are {cheapest_months[0]}, {cheapest_months[1]} and {cheapest_months[2]}. The average prices for these months are {average_prices[cheapest_months[0]]:.2f}, {average_prices[cheapest_months[1]]:.2f} and {average_prices[cheapest_months[2]]:.2f} respectively."
                elif seen_message['country'] != None:
                    cheapest_months,average_prices = get_preferred_date(country, today)
                    message = f"Based on the location {country}, the cheapest months to travel from London are {cheapest_months[0]}, {cheapest_months[1]} and {cheapest_months[2]}. The average prices for these months are {average_prices[cheapest_months[0]]:.2f}, {average_prices[cheapest_months[1]]:.2f} and {average_prices[cheapest_months[2]]:.2f} respectively."
                    
                elif seen_message['location'] != None:
                    cheapest_months,average_prices = get_preferred_date(location, today)
                    message = f"Based on the location {location}, the cheapest months to travel from London are {cheapest_months[0]}, {cheapest_months[1]} and {cheapest_months[2]}. The average prices for these months are {average_prices[cheapest_months[0]]:.2f}, {average_prices[cheapest_months[1]]:.2f} and {average_prices[cheapest_months[2]]:.2f} respectively."
                
                cl.direct_send(message, [],thread_ids)
                print(f"[{get_now()}] Sent message to user {seen_message['message_username']} with the cheapest months and average prices.")

                

    
    except Exception as e:
        print(f"[{get_now()}] An exception occurred: {e}")    



def main():
    cl = Client()
    cl.delay_range = [1, 3]

    session_file = "session.json"
    seen_messages_file = "seen_messages.json"
    authenticate(cl, session_file)

    user_id = cl.user_id_from_username(username)
    print(f"[{get_now()}] Logged in as user ID {user_id}")


    while True:
        try:
            response = supabase.table("clips").select("message_id").execute()

            message_ids = []

            for row in response.data:
                message_ids.append(row['message_id'])

            threads = cl.direct_threads()
            print(f"[{get_now()}] Retrieved direct threads.")
            cl.delay_range = [1, 3]

            for thread in threads:
                thread_id = thread.id
                messages = cl.direct_messages(thread_id)
                print(f"[{get_now()}] Retrieved messages.")
                cl.delay_range = [1, 3]
                sender_user_id = ""
                if thread.is_group == False:
                    sender_user_id = thread.inviter.username
                    
                for message in messages:
                    message_id = message.id
                    message_text = message.text if hasattr(message, 'text') else ""
                    message_timestamp = str(message.timestamp)
                    message_caption = ""
                    clip_url = ""
                    play_count = 0
                    like_count = 0
                    clip_creator_username = ""
                    if message.id not in message_ids:
                        if message.item_type == None or message.is_sent_by_viewer == True:
                            print(
                            f"[{get_now()}] Ignoring message in {thread_id}: {message.text}"
                        )
                        else:
                            match message.item_type:
                                case "clip":
                                    print(
                                        f"[{get_now()}] Downloading reel {message.clip.pk} from user {message.user_id} with caption {message.clip.caption_text}"

                                    )
                                    message_caption = message.clip.caption_text
                                    clip_url = str(message.clip.thumbnail_url)
                                    play_count = message.clip.play_count
                                    like_count = message.clip.like_count
                                    clip_creator_username = message.clip.user.username
                                    try:
                                        download_clip(cl, message.clip.pk,message_id)
                                    except Exception as e:
                                        print ('Error Downloading...')
                                        print(e)
                                case "xma_story_share":
                                    print(
                                        f"[{get_now()}] New story video in thread {thread_id}: {message.id}"
                                    )
                                case _:
                                    print(
                                        f"[{get_now()}] New message in thread {thread_id}: {message.text}"
                                    )
                            transcription = get_transcription(message_id)
                            # video_summary = get_video_summary(message_id)
                            # Delete the video and audio files from the folder
                            shutil.rmtree('download')
                            shutil.rmtree('audio')
                            response = (
                                supabase.table("clips")
                                .insert({
                                        "message_username": sender_user_id, 
                                        "message_text": message_text, 
                                        "message_timestamp": message_timestamp,
                                        "clip_caption": message_caption, 
                                        "message_id": message_id, 
                                        "clip_transcription": transcription, 
                                        "clip_creator_username": clip_creator_username,
                                        "clip_url": clip_url,
                                        "play_count": play_count,
                                            "like_count": like_count,
                                            "thread_id": thread_id,
                                        })
                                .execute()
                            )
                            classify_intent(message_id)
                            # save_seen_messages(seen_messages_file, seen_messages)
                            send_message(cl, message_id, [thread_id])




        except Exception as e:
            print(f"[{get_now()}] An exception occurred: {e}")
            print(f"[{get_now()}] Deleting the session file and restarting the script.")
            if os.path.exists(session_file):
                os.remove(session_file)
            sleep_countdown()
            print(f"[{get_now()}] Restarting the script now.")
            os.execv(sys.executable, ["python"] + sys.argv)
            

        sleep_countdown()

if __name__ == "__main__":
    main()
