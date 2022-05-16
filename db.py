# Maintenance Bot
# Copyright Reeshu (@reeshuxd)

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

from vars import Var
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

try:
    mongo_client = MongoClient(Var.MONGODB_URL)
    db = mongo_client.Hoster
except BaseException as be:
    print(f"Something went wrong with MongoDB Url - {be}")

""" Tokens DataBase """
tdb = db.Tokens

async def check_token(token: str, user_id: int) -> bool:
 check = await tdb.find_one({"user_id": user_id})
 if check:
  kk = check["tokens"]
  for a in kk:
    if a["token"] == token:
        return True
 return False

async def add_token(user_id: int, token: str, uname: str):
    tok = await tdb.find_one({'user_id': user_id})
    tokens = []
    if tok != None:
      tokens = tok['tokens']
    tokens.append({"token": token, "uname": uname})
    tdb.update_one({'user_id': user_id}, {'$set': {'tokens': tokens}}, upsert=True)

async def rm_token(user_id: int):
    check = await check_token(user_id)
    if not check:
        return
    await tdb.delete_one({"user_id": user_id})

async def get_bot(user_id: int):
    get = await tdb.find_one({"user_id": user_id})
    if not get:
        return False
    sed = get["tokens"]
    return sed

async def get_tokens():
    users = tdb.find({"user_id": {"$gt": 0}})
    if not users:
        return []
    users_list = []
    for user in await users.to_list(length=1000000000):
        users_list.append(user)
    return users_list