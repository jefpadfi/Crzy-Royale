"""
Programmer: TheCrzyDoctor
Description: This script enables you to have a battle royale in your chat.
Date: 02/19/2017
Version: 1
"""

# ---------------------------------------
# Import Libraries
# ---------------------------------------

import clr
import os
import codecs
import json
import random
import datetime
import sys


clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------------------
# [Required] Script Information
# ---------------------------------------
ScriptName = "Crzy Royale"
Website = "https://www.twitch.tv/thecrzydoc"
Description = "This script enables you to have a battle royale in your chat."
Creator = "TheCrzyDoctor"
Version = "1.0.0"

# ---------------------------------------
# Settings file setup
# ---------------------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

# global vars that dont need to be saved
users_in_cr = {}


class Settings:
    def __init__(self, settingsFile=None):
        if settingsFile is not None and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        else:
            self.OnlyLive = False
            self.Command = '!crstart'
            self.cmdJoin = '!crjoin'
            self.cmdLoot = '!crloot'
            self.cmdAttack = '!crattack'
            self.Usage = 'Stream Chat'
            self.Permission = 'Everyone'
            self.PermissionInfo = ''
            self.PermissionResp = '{0} -> only {1} and higher can use this command'
            self.CRCreatedMsg = 'The Crzy Royale has been started. Use !crjoin to join the Crzy Royale'
            self.CRErrorMsg = 'There was an issue with creating the Crzy Royale'
            self.CRLoser = 10
            self.CRWinner = 50
            self.UseCD = True
            self.CoolDown = 5
            self.OnCoolDown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCoolDown = 10
            self.OnUserCoolDown = "{0} the command is still on user cooldown for {1} seconds!"
            self.CasterCD = True
            self.NoCurrency = "{0} -> You don't have any currency to create a giphy!"
            self.InfoResponse = 'To create a giphy use !giphy keyword. At this time the giphy command only accepts' \
                                'two keyword. Future versions will allow a full string of keywords.'

    def ReloadSettings(self, data):
        """ Reload settings file. """
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    def SaveSettings(self, settingsFile):
        """ Saves settings File """
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))


def ReloadSettings(jsonData):
    """ Reload Settings on Save """
    global CGSettings
    CGSettings.ReloadSettings(jsonData)
    return


# ---------------------------------------
# 	[Required] Functions
# ---------------------------------------
def Init():
    """ Intialize Data (only called on load) """
    global CGSettings
    CGSettings = Settings(settingsFile)
    return


def Execute(data):
    """ Executes data and processes the message. """

    if data.IsChatMessage():
        # check what command is being used.
        if data.GetParam(0).lower() == CGSettings.Command.lower():
            SendResp(data, CGSettings.Usage, 'Start command used.')
        elif data.GetParam(0).lower() == CGSettings.cmdJoin.lower():
            SendResp(data, CGSettings.Usage, 'Join command used.')
        elif data.GetParam(0).lower() == CGSettings.cmdLoot.lower():
            SendResp(data, CGSettings.Usage, 'Loot command used.')
        elif data.GetParam(0).lower() == CGSettings.cmdAttack.lower() and data.GetParamCount() == 2:
            SendResp(data, CGSettings.Usage, 'Attack command used {0}.'.format(data.GetParam(1)))


def Tick():
    """Required tick function"""
    pass


# ---------------------------------------
# 	[Optional] Usage functions
# ---------------------------------------

def SendResp(data, rUsage, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    # Set a list with all possible usage options that would trigger Stream chat message
    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]

    # check if message is from Stream, from chat and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and (rUsage in l) and not data.IsWhisper():
        # send Stream message
        Parent.SendStreamMessage(sendMessage)

    # Set a list with all possible usage options that would trigger Stream whisper
    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]

    # check if message is from Stream, from whisper and if chosen usage is in the list above
    if (data.IsFromTwitch() or data.IsFromYoutube()) and data.IsWhisper() and (rUsage in l):
        # send Stream whisper
        Parent.SendStreamWhisper(data.User, sendMessage)

    # Set a list with all possible usage options that would trigger discord message
    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]

    # check if message is from discord
    if data.IsFromDiscord() and not data.IsWhisper() and (rUsage in l):
        # send Discord message
        Parent.SendDiscordMessage(sendMessage)

    # Set a list with all possible usage options that would trigger discord DM
    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]

    # check if message is from discord, from DM and if chosen usage is in the list above
    if data.IsFromDiscord() and data.IsWhisper() and (rUsage in l):
        # send Discord whisper
        Parent.SendDiscordDM(data.User, sendMessage)

    return


"""
Required custom fucntions needed for plugin.
"""


def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return


def haspermission(data):
    """ CHecks to see if the user hs the correct permission.  Based on Castorr91's Gamble"""
    if not Parent.HasPermission(data.User, CGSettings.Permission, CGSettings.PermissionInfo):
        message = CGSettings.PermissionResp.format(data.UserName, CGSettings.Permission, CGSettings.PermissionInfo)
        SendResp(data, CGSettings.Usage, message)
        return False
    return True


def is_on_cooldown(data):
    """ Checks to see if user is on cooldown. Based on Castorr91's Gamble"""
    # check if command is on cooldown
    cooldown = Parent.IsOnCooldown(ScriptName, CGSettings.Command)
    user_cool_down = Parent.IsOnUserCooldown(ScriptName, CGSettings.Command, data.User)
    caster = Parent.HasPermission(data.User, "Caster", "")

    if (cooldown or user_cool_down) and caster is False and not CGSettings.CasterCD:

        if CGSettings.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CGSettings.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CGSettings.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CGSettings.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CGSettings.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)
        return True
    elif (cooldown or user_cool_down) and CGSettings.CasterCD:
        if CGSettings.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, CGSettings.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, CGSettings.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = CGSettings.OnCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)

            else:
                m_CooldownRemaining = userCDD

                message = CGSettings.OnUserCoolDown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, CGSettings.Usage, message)
        return True
    return False


def addcooldown(data):
    """Create Cooldowns Based on Castorr91's Gamble"""
    if Parent.HasPermission(data.User, "Caster", "") and CGSettings.CasterCD:
        Parent.AddCooldown(ScriptName, CGSettings.Command, CGSettings.CoolDown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, CGSettings.Command, data.User, CGSettings.UserCoolDown)
        Parent.AddCooldown(ScriptName, CGSettings.Command, CGSettings.CoolDown)
