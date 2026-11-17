# © By Waste shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import os
import sys
from pyrogram import Client

def restart():
    os.execvp(sys.executable, [sys.executable, "-m", "Waste"])

async def join(client):
    try:
        await client.join_chat("itszShukla")
    except BaseException:
        pass
