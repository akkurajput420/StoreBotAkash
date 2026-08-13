import asyncio, logging
from telethon import TelegramClient
from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from bot.config import Settings

logger = logging.getLogger("bot")

class AccountSetupService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def setup_account(self, client: TelegramClient):
        r = {"profile_ok":False,"channel_ok":False,"spam_free":False,"spam_note":""}
        try:
            await client(UpdateProfileRequest(
                first_name=self.settings.account_display_name[:64], last_name="",
                about=self.settings.account_bio[:70]))
            r["profile_ok"]=True
        except Exception as e:
            logger.warning("profile: %s", e)
        link=self.settings.required_channel_link
        if "+" in link:
            h=link.split("+",1)[-1].strip()
            try:
                await client(ImportChatInviteRequest(h))
                r["channel_ok"]=True
            except UserAlreadyParticipantError:
                r["channel_ok"]=True
            except Exception as e:
                logger.warning("channel: %s", e)
        sf, note = await self.check_spam_bot(client)
        r["spam_free"], r["spam_note"] = sf, note
        return r

    async def check_spam_bot(self, client):
        try:
            e=await client.get_entity(self.settings.spambot_username.lstrip("@"))
            await client.send_message(e,"/start")
            await asyncio.sleep(2.5)
            msgs=await client.get_messages(e, limit=3)
            text=" ".join(m.text.lower() for m in msgs if m.text)
            ok="good news" in text and "free as a bird" in text
            return ok, (msgs[0].text[:200] if msgs and msgs[0].text else "")
        except Exception as ex:
            return False, str(ex)[:200]
