"""
Programmer: TheCrzyDoctor
Description: This script enables you to have a battle royale in your chat.
Date: 05/5/2018
Version: 1
"""

import datetime

timer = None
sentStartMessage = False
attacker = None
target = None
participants = {}
hasLooted = []
started = False
allowJoin = False
allowLoot = False
allowAttack = False
