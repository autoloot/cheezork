import sys
import time
import telepot
import re
import json
import textwrap
import pprint

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
    def __init__(self, command, modifiable, size):
        self.list = list()
        self.modifiable = modifiable
        self.size = size
        self.command = command
        #maximum item string length
        self.maxlen = 100
        #default strings for replies
        self.stringdict = dict()
        self.stringdict['exception'] = "Unknown switch, switches are s,a,r."
        self.stringdict['emptytext'] = "You're not carrying anything."
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
        print(self.command + ' parsing ' + "'" + text + "'")
        reply = self.stringdict['exception']
        match = re.split('\s+',text.strip(' \t\n\r'))
        cmd = match[0]  #if text is an empty string, match[0] will also be an empty string
        remains = text[len(cmd):len(text)].strip(' \t\n\r')
        if cmd in self.aliases:
            reply = self.aliases[cmd](remains)

        return reply

    def additem(self,item):
        if len(item) > self.maxlen:
            item = item[0:self.maxlen]
        reply = self.stringdict['noaddtext']
        if len(self.list) < self.size:
            self.list.append(item)
            reply = self.stringdict['addprefix'] + item + self.stringdict['addsuffix']
        return reply

    def removeitem(self,text):
        print('removing item ' + text)
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
        if len(self.list) > 0:
            i = 1
            for item in self.list:
                line = str(i) + '. ' + item
                reply += line
                if i < len(self.list):
                    reply += '\n'
                i += 1
        else:
            reply = self.stringdict['emptytext']
        return reply

    def setdictitem(self,name,value):
        oldvalue = ''
        if name in self.stringdict:
            oldname = self.stringdict[name]
            self.stringdict[name] = value
        return oldvalue

    def setsize(self,size):
        self.size = size

    def getcommand(self):
        return self.command

    def tofilestring(self):
        filestring = json.dumps(self.list)
        return filestring

    def fromfilestring(self,filestring):
        self.list = json.loads(filestring)

class SaveHack:
    """A hack class to load save routines into cdict"""
    def parse(self,text):
        savecollections()
        return 'Rest easy weary adventurer, your progress has been recorded.'

    def getname(self):
        return '/save'

class HelpHack:
    """A hack class to print help on command"""
    def parse(self,text):
        return textwrap.dedent("""
        /help - Show help for this bot.
        /rules - Show the rules of the game.
        /inventory - List the items in your inventory.
        /appearance - List the items that you are wearing.
        /titles - List the titles by which you are known.
        /songs - List the songs you have memorised.
        /signs - List the occult signs you know.
        /conditions - List any conditions affecting you.
        /allies - List your heroic companions!
        /enemies - List your nefarious rivals!
        """)

    def getname(self):
        return '/help'


def initcdict():
    global collectionlist

    cdict = dict()
    for collection in collectionlist:
        cdict[collection.getcommand()]=collection

    s = SaveHack()
    cdict[s.getname()] = s
    h = HelpHack()
    cdict[h.getname()] = h

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

def savecollections():
    global collectionlist
    f = open('cheez.log','w')
    for collection in collectionlist:
        f.write(collection.getcommand())
        f.write('\n')
        f.write(collection.tofilestring())
        f.write('\n')

    f.close()

def loadcollections():
    global cdict
    f = open('cheez.log','r')
    line = f.readline()
    while line != '':
        line = line.strip(' \t\n\r')
        if line in cdict:
            jsonline = f.readline().strip(' \t\n\r')
            print('Loading ' + line + ' with ' + jsonline)
            cdict[line].fromfilestring(jsonline)
        line = f.readline()

def update():
    savecollections()

def handle(msg):
    global cdict
    global BOTUSERNAME
    content_type, chat_type, chat_id = telepot.glance2(msg)
    if content_type == 'text':
        chat_id = msg['chat']['id']
        content = msg['text']

        content = content.replace('@'+BOTUSERNAME,'')

        split = commandsplitter(content)
        cmd = split['cmd']
        arg = split['arg']

        print('checking ' + content)

        if cmd in cdict :
            bot.sendMessage(chat_id,cdict[cmd].parse(arg))

# GO 8080
collectionlist = list()

rulescollection = PersistentCollection('/rules',False, 100)
rulescollection.additem('The player can not die.')
rulescollection.additem('Any actor may be the #DM or the #player.')
rulescollection.additem('An actor may not take two turns in a row.')
rulescollection.additem("Please don't abuse cheezorkbot :(")
collectionlist.append(rulescollection)

inventorycollection = PersistentCollection('/inventory', True, 10)
inventorycollection.additem('Longsword +1')
inventorycollection.additem('Cheese of Wounding')
collectionlist.append(inventorycollection)

songcollection = PersistentCollection('/songs', True, 5)
songcollection.setdictitem('addprefix', 'You learned ')
songcollection.setdictitem('removeprefix', 'You forgot ')
songcollection.setdictitem('noaddtext','You try to hum the tune but always end up at another.')
songcollection.setdictitem('emptytext',"You've really never been much of a musician.")
collectionlist.append(songcollection)

appearancecollection = PersistentCollection('/appearance',True,10)
appearancecollection.setdictitem('addprefix','You are now wearing ')
appearancecollection.setdictitem("removeprefix",'You remove your ')
appearancecollection.setdictitem('emptytext',"You're not wearing anything. Cheeky!")
collectionlist.append(appearancecollection)

conditioncollection = PersistentCollection('/conditions',True,5)
conditioncollection.setdictitem('addprefix','You are afflicted with ')
conditioncollection.setdictitem('removeprefix','You are no longer afflicted with ')
conditioncollection.setdictitem('noaddtext','You are already riddled with disease. You doubt another condition will make much difference.')
conditioncollection.setdictitem('emptytext',"Fit as a fiddle!")
collectionlist.append(conditioncollection)

titlecollection = PersistentCollection('/titles',True,3)
titlecollection.setdictitem('addprefix','You are now known as ')
titlecollection.setdictitem('removeprefix','You are no longer known as ')
titlecollection.setdictitem('noaddtext','You are known by too many names already. Any more would be confusing.')
titlecollection.setdictitem('emptytext',"Your name is known only to yourself... and you aim to keep it that way.")
collectionlist.append(titlecollection)

signcollection = PersistentCollection('/signs',True,5)
signcollection.setdictitem('addprefix','You learned how to make the sign of ')
signcollection.setdictitem('removeprefix','You forgot how to make the sign of ')
signcollection.setdictitem('removesuffix',"; Let's hope you don't need it later.")
signcollection.setdictitem('noaddtext','Your hands tire and the sign slips through your grasp.')
signcollection.setdictitem('emptytext',"The only signs you know are obscene; alas, there is no magic in them.")
collectionlist.append(signcollection)

allycollection = PersistentCollection('/allies',True,5)
allycollection.setdictitem('addprefix','You are now allied with ')
allycollection.setdictitem('removeprefix','')
allycollection.setdictitem('removesuffix'," is no longer your ally. It is a sad day.")
allycollection.setdictitem('noaddtext','Your legions of followers are endless. What good is one more?')
allycollection.setdictitem('emptytext',"You learned the hard way - the only person you can rely on is yourself.")
collectionlist.append(allycollection)

enemycollection = PersistentCollection('/enemies',True,5)
enemycollection.setdictitem('addprefix','You are instilled with a bitter hatred of ')
enemycollection.setdictitem('removeprefix','')
enemycollection.setdictitem('removesuffix'," is no longer your enemy.")
enemycollection.setdictitem('noaddtext','You should deal with your existing foes first.')
enemycollection.setdictitem('emptytext',"A man without enemies is a man who has not ventured far.")
collectionlist.append(enemycollection)

# must init CDICT *after* making the collections
cdict = initcdict()
# load collections from disk
print('Loading collections...')
loadcollections()
print('Loaded!')

# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]

bot = telepot.Bot(TOKEN)
BOTUSERNAME = bot.getMe()['username']
bot.notifyOnMessage(handle)
print('Running scripts for @' + BOTUSERNAME)
print('Listening ...')

# Keep the program running.
i = 0
while 1:
    time.sleep(100)
    #very rough 10m updates 600 * 100 = 60,000
    #don't try and clock anything with this
    i += 1
    if i == 600:
        update()
        i = 0