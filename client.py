import telethon
import datetime

class Client:
    def __init__(self, api_hash, api_id):
        self.client = telethon.TelegramClient(session="telegram_client_session", api_id=api_id, api_hash=api_hash)

    async def connect(self):
        await self.client.start()

    async def me(self):
        me = await self.client.get_me()
        return f"{me.username}"

    async def disconnect(self):
        await self.client.disconnect()

    async def all_chats(self):
        return await self.client.get_dialogs()
    
    async def chat_by_id(self, name):
        chats = await self.all_chats()
        for chat in chats:
            if chat.name == name:
                return chat.id
        return None
    
    async def all_messages_in_chat(self, chat_id, n):
        return await self.client.get_messages(chat_id, limit=n)
    
    async def my_messages_in_chat(self, chat_id, n):
        return await self.client.get_messages(chat_id, limit=n, from_user="me")
    
    # async def canc_all_messages(self, dialog_id, message_ids):
    #     await self.client.delete_messages(dialog_id, message_ids)
    
    async def all_users(self, chat_id):
        return await self.client.get_participants(chat_id)
    
    async def canc_all_messages(self, chat_id, message_ids):
        await self.client.delete_messages(chat_id, message_ids)

    async def messages_between_dates(self, chat_id,
        ts: datetime.datetime,
        te: datetime.datetime, limit: int = None):

        records = []
        async for m in self.client.iter_messages(chat_id, offset_date=te, reverse=False, limit=limit):
            print(f"[info]: processing message {m.id} in {chat_id} in date {m.date}")
            # print(m)
            # id        = m.id
            # date      = m.date
            # text      = m.message
            # sender    = m.from_id.user_id
            # reactions = m.reactions
            # reply_to  = m.reply_to.reply_to_msg_id if m.reply_to else None
            # if len(text) > 0:
            #     streak = ""
            #     if reactions:
            #         for r in reactions.results:
            #             streak += f"{r.reaction.emoticon}:{r.count} "
            #     print(id, date, text, sender, streak)
            if m.date < ts:
                break
            if ts <= m.date <= te:
                records.append(m)
            # print()
        return records
