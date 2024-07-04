import os, json, time, random, sys, datetime, ast
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

load_dotenv()
username = os.environ.get("IG_USERNAME")
email = os.environ.get("IG_EMAIL")
password = os.environ.get("IG_PASSWORD")



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
    sleep_time = random.randint(30, 120)
    print(f"[{get_now()}] Timeout duration: {sleep_time} seconds.")

    for remaining_time in range(sleep_time, 0, -1):
        sys.stdout.write(f"\r[{get_now()}] Time remaining: {remaining_time} second(s).")
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\n")

def download_clip(client, clip_pk):
    print(f"[{get_now()}] Downloading reel {clip_pk}")

    # Get the current working directory
    cwd = os.getcwd()

    # Construct the path to the download folder
    download_path = os.path.join(cwd, "download")

    # Check if the download folder exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"[{get_now()}] Created {download_path}")

    client.video_download(clip_pk, "download")
    print(f"[{get_now()}] Downloaded {clip_pk}")
    client.delay_range = [1, 3]


def main():
    cl = Client()
    cl.delay_range = [1, 3]

    session_file = "session.json"
    seen_messages_file = "seen_messages.json"
    authenticate(cl, session_file)

    user_id = cl.user_id_from_username(username)
    print(f"[{get_now()}] Logged in as user ID {user_id}")


    seen_messages = load_seen_messages(seen_messages_file)
    print(f"[{get_now()}] Loaded seen messages.")

    while True:
        try:
            threads = cl.direct_threads()
            print(f"[{get_now()}] Retrieved direct threads.")
            cl.delay_range = [1, 3]

            for thread in threads:
                thread_id = thread.id
                messages = cl.direct_messages(thread_id)
                print(f"[{get_now()}] Retrieved messages.")
                cl.delay_range = [1, 3]

                for message in messages:
                    message_id = message.id
                    message_text = message.text if hasattr(message, 'text') else ""
                    message_caption = ""
                    if message.id not in seen_messages:
                        match message.item_type:
                            case "clip":
                                print(
                                    f"[{get_now()}] Downloading reel {message.clip.pk} from user {message.user_id} with caption {message.clip.caption_text}"

                                )
                                message_caption = message.clip.caption_text
                                try:
                                    download_clip(cl, message.clip.pk)
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
                        seen_messages[message_id] = {"message_text": message_text, "message_caption": message_caption}
                        save_seen_messages(seen_messages_file, seen_messages)

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
