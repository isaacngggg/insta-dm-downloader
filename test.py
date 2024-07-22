import main

seen_messages =  main.load_seen_messages("seen_messages.json")

seen_messages["isaacNg"]["21029890138"] = {
    "transcribed_text": "This is a test",
}

main.save_seen_messages("seen_messages.json", seen_messages)

