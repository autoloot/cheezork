import sys
import time
import telepot
import re

# Done! Congratulations on your new bot.
# You will find it at telegram.me/NAMEOFBOT.
# You can now add a description, about section
# and profile picture for your bot, see
#     /help for a list of commands.
#
# Use this token to access the HTTP API:
# This token is HIDDEN! Write it down somewhere because you
# need to pass it in as arg 1
#
# For a description of the Bot API, see this page: https://core.telegram.org/bots/api

# Bot commands should be
# /rules
# /inventory
# /appearance
# /titles
# /songs

# rules - Show the rules of the game.
# inventory - List the items in your inventory.
# appearance - List the items that you are wearing, and any identifying features you may have.
# titles - List the titles by which you are known.
# songs - List the songs you have memorised.
# conditions - List any conditions affecting you.

class PersistentCollection:
    """A persistent list collection, size limited, can be printed."""
    def __init__(self,name,modifiable,size):
        self.list = list()
        self.modifiable = modifiable
        self.size = size
        self.name = name
        #default strings for replies
        self.stringdict = dict()
        self.stringdict['exception'] = "Unknown switch, switches are s,a,r."
        self.stringdict['noaddtext'] = 'I am overburdened.'
        self.stringdict['addprefix'] = 'Got '
        self.stringdict['addsuffix'] = '.'
        self.stringdict['noremovetext'] = "I can't find that item."
        self.stringdict['removeprefix'] = 'Dropped '
        self.stringdict['removesuffix'] = '.'

        #alias lists
        self.aliases = dict()
        self.aliases[''] = self.showitems
        self.aliases['s'] = self.showitems
        self.aliases['show'] = self.showitems

        if self.modifiable:
            self.aliases['r'] = self.removeitem
            self.aliases['remove'] = self.removeitem
            self.aliases['a'] = self.additem
            self.aliases['add'] = self.additem

    def parse(self,text):
        print self.name + ' parsing ' + "'" + text + "'"
        reply = self.stringdict['exception']
        match = re.split('\s+',text.strip(' \t\n\r'))
        cmd = match[0]  #if text is an empty string, match[0] will also be an empty string
        remains = text[len(cmd):len(text)].strip(' \t\n\r')
        if cmd in self.aliases:
            reply = self.aliases[cmd](remains)

        return reply

    def additem(self,item):
        reply = self.stringdict['noaddtext']
        if len(self.list) < self.size:
            self.list.append(item)
            reply = self.stringdict['addprefix'] + item + self.stringdict['addsuffix']
        return reply

    def removeitem(self,text):
        print 'removing item ' + text
        if text.isnumeric():
            reply = self.removeitembyindex(int(text)-1) #player sees index from 1 on printout
        else:
            reply = self.removeitembyname(text)
        return reply

    def removeitembyname(self,text):
        reply = self.stringdict['noremovetext']
        if text in self.list:
            self.list.remove(text)
            reply = self.stringdict['removeprefix'] + text + self.stringdict['removesuffix']
        return reply

    def removeitembyindex(self,index):
        reply = self.stringdict['noremovetext']
        if index < len(self.list):
            item = self.list.pop(index)
            reply = self.stringdict['removeprefix'] + item + self.stringdict['removesuffix']
        return reply

    def showitems(self,text):
        #text is unused at present
        reply = ''
        i = 1;
        for item in self.list:
            line = str(i) + '. ' + item
            reply += line
            if i < len(self.list):
                reply += '\n'
            i += 1
        return reply

    def setdictitem(self,name,value):
        oldvalue = ''
        if name in self.stringdict:
            oldname = self.stringdict[name]
            self.stringdict[name] = value
        return oldvalue

    def setsize(self,size):
        self.size = size


def rules(text):
    global rulescollection
    return rulescollection.parse(text)

def inventory(text):
    global inventorycollection
    return inventorycollection.parse(text)

def diplo(text):
    return "Chips! (Some chips may fail if contrary to the eater's values)."

def echo(text):
    return 'All you can hear is the echo of your own voice - ' + text

def initcdict():
    cdict = dict()
    cdict['/rules'] = rules
    cdict['/echo'] = echo
    cdict['/inventory'] = inventory
    cdict['/diplomacy'] = diplo
    return cdict


def commandsplitter(text):
    match = re.search('(^/[\w]+)',text)
    cmd = ''
    arg = ''
    if match:
        cmd = match.group(1)
        if len(text) > len(cmd)+1:
            arg = text[len(cmd)+1 : len(text)]
    return {'cmd':cmd,'arg':arg}


def handle(msg):
    global cdict
    content_type, chat_type, chat_id = telepot.glance2(msg)
    if content_type == 'text':
        chat_id = msg['chat']['id']
        content = msg['text']
        split = commandsplitter(content)
        cmd = split['cmd']
        arg = split['arg']

        print 'checking ' + content

        if cmd in cdict :
            bot.sendMessage(chat_id,cdict[cmd](arg))

# GO 8080
rulescollection = PersistentCollection('Rules',False, 100)
rulescollection.additem('The player can not die.')
rulescollection.additem('Any actor may be the #DM or the #player.')
rulescollection.additem('An actor may not take two turns in a row.')
rulescollection.additem("Please don't abuse cheezorkbot :(")

inventorycollection = PersistentCollection('Inventory', True, 10)
inventorycollection.additem('Longsword +1')
inventorycollection.additem('Cheese of Wounding')

cdict = initcdict()
# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]



bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(100)