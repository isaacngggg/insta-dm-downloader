import csv

import intent_classifier

# Path to the clips_rows.csv file
csv_file = 'clips_rows.csv'

# List to store the message_ids
message_ids = []

# Read the CSV file
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        message_id = row['message_id']
        message_ids.append(message_id)

# Process each message_id
for message_id in message_ids:

    intent = intent_classifier.classify_intent(message_id)

    print(f"Message ID: {message_id}, Intent: {intent}")