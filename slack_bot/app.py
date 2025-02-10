from fastapi import FastAPI, BackgroundTasks
import httpx
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = FastAPI()

# Read environment variables
CALENDAR_BOT_URL = os.getenv("CALENDAR_BOT_URL", "http://calendar-bot:8000")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")  # adjust as needed

# Initialize Slack client
slack_client = WebClient(token=SLACK_BOT_TOKEN)

@app.get("/")
async def read_root():
    return {"message": "Slack Bot is running."}

@app.get("/post_events")
async def post_events(background_tasks: BackgroundTasks):
    """
    Retrieve events from the calendar bot and post a message to Slack.
    """
    background_tasks.add_task(process_and_post_events)
    return {"status": "Processing events and posting to Slack"}

async def process_and_post_events():
    # Retrieve events from the calendar bot
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CALENDAR_BOT_URL}/events")
            response.raise_for_status()
            events = response.json()
        except Exception as e:
            print(f"Error fetching events: {e}")
            events = {}

    message = ""
    # Process events here
    for event in events.get('events', []):
        message += f"ID: {event['id']}, \nSummary: {event['summary']}, \nStart: {event['start']}, \nEnd: {event['end']}\n"
    message = message.strip('\n')
    
    # Post the message to Slack
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Message posted to Slack")
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")
