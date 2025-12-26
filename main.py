import asyncio
import pandas as pd
import datetime
import dotenv
import sys
import os
from   client import Client

# Define API_ID and API_HASH
dotenv.load_dotenv()
API_ID   = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    raise RuntimeError(print("[error]: API_ID or API_HASH not defined"))

async def main():

    client = Client(API_HASH, API_ID)
    await client.connect()

    # Get the chat ID
    name = "Polito Debate"
    chat = await client.chat_by_id(name=name)
    if chat is None:
        print(f"[error]: chat named {name} not found, exiting with 1")
        sys.exit(1)

    #
    # Get all users in chat and write a CSV
    # containing basic info: the id Telegram
    # has assigned to the user, the username,
    # the first name, the last name, the phone
    # if the user is a bot
    #

    users = await client.all_users(chat)
    print(f"[info]: there are {len(users)} users in the chat named {name}")
    pd.DataFrame([{
        "id"         : user.id,
        "username"   : user.username,
        "first_name" : user.first_name,
        "last_name"  : user.last_name,
        "phone"      : user.phone,
        "bot"        : user.bot,
    } for user in users]).to_csv(f"{name.replace(" ", "_")}_users.csv", index=False)


    #
    # Get all messages in chat between two dates
    # For each message, save the id, the date, the
    # sender, any reaction and if it is a reply to
    # someone else
    #

    ts       = datetime.datetime(2025, 12, 1,  tzinfo=datetime.timezone.utc)
    te       = datetime.datetime(2025, 12, 25, tzinfo=datetime.timezone.utc)
    messages = await client.messages_between_dates(chat, ts, te)
    print(f"[info]: there are {len(messages)} messages in the chat named {name}")

    records = []
    columns = ["id", "date", "text", "sender", "reactions"]
    for m in messages:
        id        = m.id
        date      = m.date
        text      = m.message
        sender    = m.from_id.user_id
        reactions = m.reactions
        if len(text) > 0:
            streak = ""
            if reactions:
                for r in reactions.results:
                    streak += f"{r.reaction.emoticon}:{r.count} "
            records.append([id, date, text, sender, reactions])
    pd.DataFrame(records, columns=columns).to_csv(f"{name.replace(' ', '_')}_messages.csv", index=False)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
