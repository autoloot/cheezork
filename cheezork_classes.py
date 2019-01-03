import textwrap
import re
import json
import random
import math


class PersistentCollection:
    """A persistent list collection, size limited, can be printed."""
    def __init__(self, command, size):
        self.list = list()
        self.size = size
        self.command = command
        # maximum item string length
        self.maxlen = 100
        # default strings for replies
        self.string_dict = {
            'exception': "Unknown switch; switches are s, a, r, x."
            , 'empty_text': "You're not carrying anything."
            , 'no_add_text': 'You are overburdened.'
            , 'add_prefix': 'You picked up '
            , 'add_suffix': '.'
            , 'no_remove_text': "You can't find that item."
            , 'remove_prefix': 'You dropped '
            , 'remove_suffix': '.'
            , 'exchange_prefix': ''
            , 'exchange_mid': ' became '
            , 'exchange_suffix': '.'
            , 'list_header': 'You are carrying: '
        }

        # alias lists
        self.aliases = {
            '': self.show_items
            , 'list': self.show_items
            , 's': self.show_items
            , 'show': self.show_items
            , 'r': self.remove_item
            , 'remove': self.remove_item
            , 'a': self.add_item
            , 'add': self.add_item
            , 'x': self.exchange_item
            , 'exchange': self.exchange_item
        }

    def parse(self, text):
        print(self.command + ' parsing ' + "'" + text + "'")
        reply = self.string_dict['exception']
        match = re.split('\\s+', text.strip(' \t\n\r'))
        if len(match) == 1:
            cmd = ''
            remains = ''
        else:
            cmd = match[1]  # if text is an empty string, match[0] will also be an empty string
            remains = ' '.join(match[2:])
        if cmd in self.aliases:
            reply = self.aliases[cmd](remains)

        return reply

    def add_item(self, item):
        if len(item) > self.maxlen:
            item = item[0:self.maxlen]
        reply = self.string_dict['no_add_text']
        if len(self.list) < self.size:
            self.list.append(item)
            reply = '{}<b>{}</b>{}'.format(
                self.string_dict['add_prefix']
                , item
                , self.string_dict['add_suffix']
            )
        return reply

    def remove_item(self, text):
        print('removing item ' + text)
        if text.isnumeric():
            reply = self.remove_item_by_index(int(text)-1)  # player sees index from 1 on printout
        else:
            reply = self.remove_item_by_name(text)
        return reply

    def exchange_item(self, text):
        words = re.split('\s+', text)
        print('exchange: {}'.format(text))
        print(words)
        if len(words) >= 2:
            drop_item = words[0]
            add_item = ' '.join(words[1:])
            if not drop_item.isnumeric():
                reply = self.string_dict['no_remove_text']
            else:
                drop_index = int(drop_item)-1  # player counts from 1, not 0
                if drop_index >= len(self.list):
                    reply = self.string_dict['no_remove_text']
                else:
                    drop_item_string = self.list[drop_index]
                    self.list[drop_index] = add_item
                    reply = '{}<b>{}</b>{}<b>{}</b>{}'.format(
                        self.string_dict['exchange_prefix']
                        , drop_item_string
                        , self.string_dict['exchange_mid']
                        , add_item
                        , self.string_dict['exchange_suffix']
                    )
        else:
            reply = self.string_dict['no_remove_text']
        return reply

    def remove_item_by_name(self, text):
        reply = self.string_dict['no_remove_text']
        if text in self.list:
            self.list.remove(text)
            reply = '{}<b>{}</b>{}'.format(
                self.string_dict['remove_prefix']
                , text
                , self.string_dict['remove_suffix']
            )
        return reply

    def remove_item_by_index(self, index):
        reply = self.string_dict['no_remove_text']
        if index < len(self.list):
            item = self.list.pop(index)
            reply = '{}<b>{}</b>{}'.format(
                self.string_dict['remove_prefix']
                , item
                , self.string_dict['remove_suffix']
            )
        return reply

    def show_items(self, text):
        # text is unused at present
        reply = '({}/{})\n{}\n'.format(len(self.list), self.size, self.string_dict['list_header'])
        if len(self.list) > 0:
            i = 1
            for item in self.list:
                line = str(i) + '. ' + item + '.'
                reply += line
                if i < len(self.list):
                    reply += '\n'
                i += 1
        else:
            reply = self.string_dict['empty_text']
        return reply

    def to_file_string(self):
        file_string = json.dumps(self.list)
        return file_string

    def to_list(self):
        return self.list

    def from_file_string(self, file_string):
        self.list = json.loads(file_string)

    def from_list(self, saved_list):
        self.list = saved_list


class SaveHack:
    """A hack class to load save routines into cdict"""
    def parse(self, text):
        # savecollections()
        return 'Rest easy weary adventurer, your progress has been recorded.'

    def get_name(self):
        return '/save'


class HelpHack:
    """A hack class to print help on command"""
    def parse(self, text):
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


class WordsOfPower:

    def __init__(self):
        self.words = list()
        self.hidden = dict()
        self.current_word_index = 0

    def add_word(self, word):
        self.words.append(word)
        self.hidden[word] = list(range(0, len(word)))

    def add_clue(self):
        reply = None
        if self.current_word_index >= len(self.words):
            pass
        else:
            hidden = self.hidden[self.words[self.current_word_index]]
            hidden.remove(random.choice(hidden))
            if len(hidden) == 0:
                reply = f"As your insight into the world deepens, everything seems to fall into place. One of the words of power - '{self.words[self.current_word_index]}' is known to you now."
                self.next_word()
        return reply

    def next_word(self):
        if self.current_word_index < len(self.words):
            self.current_word_index = self.current_word_index + 1
            if self.current_word_index >= len(self.words):
                return
            hidden = self.hidden[self.words[self.current_word_index]]
            while len(hidden) == 0:
                self.current_word_index = self.current_word_index + 1
                if self.current_word_index >= len(self.words):
                    break
                hidden = self.hidden[self.words[self.current_word_index]]

    def print_words(self):
        text = 'The words of power:\n'
        word_number = 1
        for word in self.words:
            hidden = self.hidden[word]
            masked_list = list(word)
            for index in hidden:
                masked_list[index] = '?'
            masked_word = ''.join(masked_list)
            text += f'{word_number}. {masked_word}\n'
            word_number = word_number + 1
        return text

    def check_for_words(self, text):
        reply = None
        uttered = list()
        discovered = list()
        for word in self.words:
            if re.search(f'(^|[\s]){word}($|[\s.])', text):
                uttered.append(word)
                if len(self.hidden[word]) != 0:
                    discovered.append(word)
        discovery_prefix = '';
        if len(uttered) > 0:
            if len(uttered) == len(self.words):
                reply = ("As the final word of power leaves your lips a great calm comes over you. Your mastery of "
                         "Cheezork is unparalleled.\n\n"
                         "Congratulations - you may end this story as you see fit."
                         )
            elif len(uttered) / len(self.words) > 0.66:
                reply = "A searing white light lances through your thoughts as you utter most of the words of power."
            elif len(uttered) / len(self.words) > 0.33:
                reply = "The stories in your mind seem to burn as you utter some of the words of power."
            else:
                reply = "The very fabric of Cheezork shakes as you utter one of the words of power."
        for word in discovered:
            discovery_prefix += f"Your sharp mind has pierced the tales that hold this world together. One of the words of power - '{word}' is known to you now.\n\n"
            self.hidden[word] = []
            if self.words.index(word) == self.current_word_index:
                self.next_word()

        return discovery_prefix + reply

    def to_dict(self):
        save_dict = {
            'words': self.words
            , 'hidden': self.hidden
            , 'current_word_index': self.current_word_index
        }
        return save_dict

    def from_dict(self, save_dict):
        self.words = save_dict['words']
        self.hidden = save_dict['hidden']
        self.current_word_index = save_dict['current_word_index']

    def from_file(self, file):
        with open(file, 'r') as f:
            for line in f:
                self.add_word(line.strip())
