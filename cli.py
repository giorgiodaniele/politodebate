import asyncio
import shlex
import json
import os
import datetime

class Cli:
    def __init__(self, limit, client):
        self.running = True
        self.current = None
        self.limit   = limit if limit else 1000
        self.client  = client

    async def run(self):
        while self.running:
            line = await asyncio.to_thread(input, "> ")

            if not line:
                continue

            try:
                parts = shlex.split(line)
            except ValueError as e:
                print(f"Parse error: {e}")
                continue

            cmd  = parts[0].lower()
            args = parts[1:]

            if cmd == "select":
                await self.cmd_sel(args)
            elif cmd == "list":
                await self.cmd_list(args)
            elif cmd == "save":
                await self.cmd_save(args)
            elif cmd == "delete":
                await self.cmd_delete(args)
            elif cmd == "exit":
                self.running = False
            elif cmd == "help":
                self.cmd_help()
            else:
                print("Unknown command. Type 'help'.")

    async def cmd_sel(self, args):
        if not args:
            print("Usage: select <chat-name>")
            return

        name = " ".join(args)
        chat_id = await self.client.get_chat_id(name)

        if chat_id is None:
            print("Chat not found.")
            return

        self.current = chat_id
        print(f"Chat selected: {name}")

    def parse_limit(self, args):
        if not args:
            return None, None

        target = args[0].lower()

        if len(args) == 1:
            return target, self.limit

        try:
            return target, int(args[1])
        except:
            return None, None

    # ---------------------------
    # LIST
    # ---------------------------
    async def cmd_list(self, args):
        target, count = self.parse_limit(args)

        if not target:
            print("Usage: list messages|users [N]")
            return

        if not self.current:
            print("No chat selected")
            return

        if target in ("m", "msg", "message", "messages"):
            await self.list_messages(self.current, count)
        elif target in ("u", "user", "users"):
            await self.list_users(self.current)
        else:
            print("Unknown list target. Use messages|users.")

    # ---------------------------
    # SAVE
    # ---------------------------
    async def cmd_save(self, args):
        target, count = self.parse_limit(args)

        if not target:
            print("Usage: save messages|users [N]")
            return

        if not self.current:
            print("No chat selected")
            return

        if target in ("m", "msg", "message", "messages"):
            await self.save_messages(self.current, count)
        elif target in ("u", "user", "users"):
            await self.save_users(self.current)
        else:
            print("Unknown save target. Use messages|users.")

    # ---------------------------
    # DELETE
    # ---------------------------
    async def cmd_delete(self, args):
        target, count = self.parse_limit(args)

        if not target:
            print("Usage: delete messages [N]")
            return

        if not self.current:
            print("No chat selected")
            return

        if target in ("m", "msg", "message", "messages"):
            await self.delete_messages(self.current, count)
        else:
            print("Unknown delete target. Only 'messages' is supported.")

    # ---------------------------
    # OPERATIONS
    # ---------------------------
    async def list_messages(self, chat_id, n):
        msgs = await self.client.get_all_messages(chat_id, n)
        for m in msgs:
            print(f"[id={m.id}] sender={m.sender_id} text={m.text}")

    async def list_users(self, chat_id):
        users = await self.client.get_users(chat_id)
        for u in users:
            print(f"[id={u.id}] username={u.username} first_name={u.first_name} last_name={u.last_name}")

    async def save_messages(self, chat_id, n):
        msgs = await self.client.get_all_messages(chat_id, n)

        data = [{
            "id": m.id,
            "from": m.sender_id,
            "text": m.text,
            "date": m.date.isoformat() if m.date else None
        } for m in msgs]

        os.makedirs("out", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        path = f"out/messages_{ts}.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Saved {len(data)} messages to {path}")

    async def save_users(self, chat_id):
        users = await self.client.get_users(chat_id)

        data = [{
            "id":         u.id,
            "username":   u.username,
            "first_name": u.first_name,
            "last_name":  u.last_name
        } for u in users]

        os.makedirs("out", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        path = f"out/users_{ts}.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Saved {len(data)} users to {path}")

    async def delete_messages(self, chat_id, n):
        msgs = await self.client.get_all_messages(chat_id, n)
        ids = [m.id for m in msgs]

        if not ids:
            print("No messages to delete.")
            return

        deleted = await self.client.delete_messages(chat_id, ids)
        print(f"Deleted {deleted} messages")

    # ---------------------------
    # HELP
    # ---------------------------
    def cmd_help(self):
        print("""
Commands:
  select <chat-name>

  list messages [N]
  list users [N]

  save messages [N]
  save users [N]

  delete messages [N]

  help
  exit
""")
