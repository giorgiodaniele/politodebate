import asyncio
import dotenv
import os
import argparse
import telethon

from client import Client
from cli    import Cli

    
async def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--api_hash", type=str, required=False,  help="API Hash (You can get it from https://my.telegram.org)")
    parser.add_argument("--api_id",   type=int, required=False,  help="API ID (You can get it from https://my.telegram.org)")
    parser.add_argument("--limit",    type=int, required=False,  help="Number of messages to fetch")
    args = parser.parse_args()

    api_hash = None
    api_id   = None

    # Derive from command line arguments
    # both the HASH and the ID for using
    # the Telegram API
    if args.api_hash and args.api_id:
        api_hash = args.api_hash
        api_id   = args.api_id
    # Derive from .env file (if it exists)
    # both the HASH and the ID for using
    # the Telegram API
    else:
        dotenv.load_dotenv()
        api_hash = os.getenv("API_HASH")
        api_id   = os.getenv("API_ID")

    if api_hash is None or api_id is None:
        print("!!! ERROR !!!")
        print("You need to specify either the API_HASH and the API_ID or the --api_hash and --api_id parameters")
        exit(1)

    # Have a client and run it
    client = Client(api_id=api_id, api_hash=api_hash)
    await client.connect()

    # Say Hello
    me = await client.get_me()
    print("######## TGRAM (v.0.0.1) ########")
    # print(f"   Welcome back [{me}]")
    
    # Hava a CLI and run it
    cli = Cli(limit=args.limit, client=client)
    await cli.run()

    # Exit
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
