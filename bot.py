# Maintenance Bot
# Copyright Reeshu (@reeshuxd)

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

import asyncio
import logging
import requests
from db import *
from vars import Var
from os import remove
from sys import version
from telethon import __version__ as tv
from telethon import TelegramClient, events, Button

logging.basicConfig(level=logging.INFO)
main_client = TelegramClient(
    "main_bot",
    api_hash="06dac184e959d99b293294328aacb47d",
    api_id=16214771
).start(
    bot_token=Var.TOKEN
)

clients = []
client_dict = {}
plist = []

async def start_clients():
    q = 0
    ok = await get_tokens()
    tokens = []
    for k in ok:
        for y in k["tokens"]:
            tokens.append(y["token"])
    for x in tokens:
        q += 1
        clientt = TelegramClient("bot_{}".format(q), api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e", api_id=6)
        try:
                await clientt.start(bot_token=x)
        except BaseException as be:
            print(f"{be}")
            continue # user revokes token 
        clients.append(clientt)


loop = asyncio.get_event_loop()
loop.run_until_complete(start_clients())

def client(**args):
    pattern = args.get("pattern", None)
    args["incoming"] = args.get("incoming", True)
    args["outgoing"] = False
    if bool(args["outgoing"]) == False:
        args["incoming"] = True
    r_pattern = r'^[/!]'
    try:
        if pattern is not None and not pattern.startswith('(?i)'):
                args['pattern'] = '(?i)' + pattern
        args['pattern'] = pattern.replace('^/', r_pattern, 1)
    except BaseException:
        pass
    try:
        def decorator(func):
            plist.append(func)
            for cli in clients:
                     cli.add_event_handler(func, events.NewMessage(**args))
            return func
        return decorator
    except BaseException as be:
        print(f"{be}")
    


@main_client.on(events.NewMessage(pattern="/start"))
async def start(event):
    text = """
**Hello, I can keep your bot working while they are inactive.**
🔗 @Userchatroom
    """
    await event.client.send_message(
        event.chat.id,
        text,
        buttons=[
            [Button.inline(" 🤖 Add Your Bot", data="conv"), Button.inline(" 📃 My Bots ", data="bots")],
            [Button.inline(" 💎 About ", data="about"), Button.inline(" 👨🏻‍💻 Contact Support", data="contact")],
            [Button.url("Source Code", url="https://github.com/Reeshuxd/MaintenanceBot")],
        ],
    )

@main_client.on(events.NewMessage(pattern="/disconnect"))
async def disconnect(event):
    msg = await main_client.send_message(event.chat.id, "`Processing....`")
    tokens = []
    try:
        token = event.text.split(None, 1)[1]
    except IndexError:
        return await msg.edit("**⚠️ No token found in message!**")
    check = await check_token(str(token), int(event.sender.id))
    if not check:
        return await msg.edit("No bot has been added with this token!")
    gemt = await get_bot(int(event.sender.id))
    for uname in gemt:
        username = uname["uname"]
    tokens.append({"token": str(token), "uname": str(username)})
    try:
        await tdb.delete_one({"user_id": int(event.sender.id)})
    except BaseException as be:
        return await msg.edit(f"`{be}`")
    await msg.edit("Sucessfully disconnected this bot!")

@main_client.on(events.CallbackQuery(data="contact"))
async def contact(event):
    await event.edit("**👨‍💻 You can go to @userchatroom for help and support regarding this bot!**", buttons=[Button.inline(" Back ", data="back")])

@main_client.on(events.CallbackQuery(data="back"))
async def back(event):
    await event.edit(
        """
**Hello, I can keep your bot working while they are inactive.**
🔗 @Userchatroom
        """,  
        buttons=[
            [Button.inline(" 🤖 Add Your Bot", data="conv"), Button.inline(" 📃 My Bots ", data="bots")],
            [Button.inline(" 💎 About ", data="about"), Button.inline(" 👨🏻‍💻 Contact Support", data="contact")],
            [Button.url("Source Code", url="https://github.com/Reeshuxd/MaintenanceBot")],
        ]
    )

@main_client.on(events.CallbackQuery(data="about"))
async def about(event):
    text = """
<b>🤖 About this Bot:</b>

<i>If any of your bot is inactive or under-development,
you can put it on maintenance and keep it active.
As there is a risk that it can be reserved ny someome 
via @BotSupport, if it's inactive.
Also it will tell the users interacting with bot that,
it is currently under maintainenance.</i>

🔗 @Userchatroom
    """
    await event.answer()
    await event.edit(text, parse_mode="html", buttons=[Button.inline("Back", data="back")])

@main_client.on(events.NewMessage(pattern="/bots"))
async def bots(event):
    if event.sender.id != Var.OWNER_ID:
        return
    ok = await get_tokens()
    usernames = []
    for k in ok:
        for y in k["tokens"]:
            usernames.append(y["uname"])
    with open("bots.txt", "w") as file:
        for uname in usernames:
            file.write(f"- @{uname}\n")
    await main_client.send_file(
        event.chat.id,
        file="bots.txt",
        caption="Bots currently connected: {}".format(len(usernames))
    )
    remove("bots.txt")

@main_client.on(events.CallbackQuery(data="bots"))
async def get_bots(event):
    await event.answer()
    bots = await get_bot(int(event.sender.id))
    text = "<b>Bots connected by you:</b>\n\n"
    if bots == False:
        return await event.edit("No bots has been connected by  you!", buttons=[Button.inline("Back", data="back")])
    for uname in bots:
        username = uname["uname"]
        text += f"<b>-</b> @{username}\n"
    text += "\n<b>⚠️ Note -</b> Use the command <code>/disconnect {token}</code> to disconnect your bot!"
    await event.edit(text, parse_mode="html", buttons=[Button.inline(" Back ", data="back")])


@main_client.on(events.CallbackQuery(data="conv"))
async def conv(event):
    text = """
**Steps to connect a bot:**

1. Start @BotFather and create a new bot.
2. You'll get a token like `123456:ABCDEFG`, forward that to me or copy paste that token here.

__Send /cancel to cancel the process!__
    """
    await event.delete()
    async with main_client.conversation(event.chat.id) as con:
        mmsg = await con.send_message(text, buttons=[Button.inline(" Back ", data="back")])
        resp = await con.get_response()
        if resp.message == "/cancel":
            return await main_client.send_message(event.chat.id, "**🏃‍♂️ Process Cancelled successfully!**")
        #print(f"{req}")
        if resp.fwd_from:
            if resp.fwd_from.from_id.user_id != 93372553:
              return await main_client.send_message(event.chat.id, "**⚠️ Forward a valid message from @BotFather!**")
            if not resp.message.startswith("Done"):
               return await main_client.send_message(event.chat.id, "Couldn't find a valid token in this message!")
            text1 = resp.message.split("Done! Congratulations on your new bot. You will find it at", 1)[1]
            tee = text1.split("You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.", 1)[1]
            text2 = tee.split("Keep your token secure and store it safely, it can be used by anyone to control your bot.\n\nFor a description of the Bot API, see this page: https://core.telegram.org/bots/api", 1)[0]
            to = text2.split("Use this token to access the HTTP API:")[1]
            tt = to.split("\n")[1]
        else:
            reqs = requests.get("https://api.telegram.org/bot{}/getMe".format(resp.message)).json()
            if reqs["ok"] == False:
                 return await main_client.send_message(event.chat.id, "❌ **Look's like this is an invalid token!**")
            tt = resp.message
    req = requests.get("https://api.telegram.org/bot{}/getMe".format(tt)).json()
    await mmsg.delete()
    sed = await main_client.send_message(event.chat.id, f"__Wait, this may take a few moments....__")
    if await check_token(str(tt), int(event.sender.id)) == True:
            return await sed.edit("**⚠️This bot is already added!**")
    uname = req["result"]["username"]
    await add_token(int(event.sender.id), str(tt), str(uname))
    ok = await get_tokens()
    tokens = []
    for k in ok:
        for y in k["tokens"]:
            tokens.append(y["token"])
    tok = len(tokens) + 1
    client = TelegramClient("bott_{}".format(tok), api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e", api_id=6)
    try:
        await client.start(bot_token=str(tt))
    except BaseException as be:
        pass
    clients.append(client)  
    for func in plist: 
         for cli in clients:
            cli.add_event_handler(func, events.NewMessage(incoming=True))
    success = f"""
**🔗 Succesfully connected @{uname}!**

__⚠️ Do not share this token with anyone as they can control your bot with it.__
**Note:** Bot will stop working if you revoke it's token.
    """
    await sed.edit(success)

@main_client.on(events.NewMessage(pattern="/stats"))
async def stats(event):
    if event.sender.id != Var.OWNER_ID:
        return
    tokens = []
    me = (await main_client.get_me()).username
    ok = await get_tokens()
    for k in ok:
        for y in k["tokens"]:
            tokens.append(y["token"])
    text = """
<b>@{} Status:</b>

<b>Bots connected:</b> <code>{}</code>
<b>Python version:</b> <code>{}</code>
<b>Telethon version:</b> <code>{}</code>
    """
    await main_client.send_message(event.chat.id, text.format(me, len(tokens), version.split()[0], tv), parse_mode="html")

@client(incoming=True)
async def start(event):
    text = """
**🌟 This bot is currently under maintenance and not able to work!**    
__Check again after sometime!__

**🔗 By - @SafeGuardingBot**
    """
    await event.client.send_message(
        event.chat.id,
        text
    )

main_client.run_until_disconnected()
