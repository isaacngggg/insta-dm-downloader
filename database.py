
import os
from supabase import create_client, Client



url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# response = (
#     supabase.table("clips")
#     .insert({ "message_username": "Denmark", "message_text": "Copenhagen is the capital of Denmark", "clip_caption": "Copenhagen is the capital of Denmark", "message_id": "31735206860605345065691649314652160", "clip_transcription": "Copenhagen is the capital of Denmark", "classifier": "travel", "location": "Denmark", "clip_creator_username":"isaacngggg","play_count":2000})
#     .execute()
# )

# response = supabase.table("clips").select("message_id").execute()

# message_ids = []

# for row in response.data:
#     message_ids.append(row['message_id'])

# print(message_ids)

# response = supabase.table("clips").update({"message_text":"updated data"}).eq("message_id", "31737217669174158506072675312467968").execute()

response = supabase.table("clips").select("message_id").execute()

message_ids = []

for row in response.data:
    message_ids.append(row['message_id'])

print (message_ids)

if "31745101559634278647046145539309568" not in message_ids:
    print("yes")