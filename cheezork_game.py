from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ParseMode
import re
import json
import logging
import sys
import os
import datetime
import argparse
from cheezork_classes import PersistentCollection
from cheezork_classes import WordsOfPower
from pidfile import PIDFile


class Cheezork:

    def __init__(self, file_name):
        self.item_collection = PersistentCollection('/items', 10)
        self.min_words = 10
        self.clue_count = 0
        self.file_name = file_name
        self.words_of_power = WordsOfPower()
        self.words_of_power.add_word('foo')
        self.words_of_power.add_word('bar')
        self.words_of_power.add_word('cheezork')

        # check if log file exists
        if not os.path.isfile(f'{self.file_name}.log'):
            with open(f'{self.file_name}.log', 'w+') as f:
                f.write("Cheezork II - The Words of Power\n")
                f.write("Started {:%d/%b/%Y %H:%M:%S}\n".format(datetime.datetime.now()))

        # check if save file exists (and load)
        if os.path.isfile(f'{self.file_name}.save'):
            with open(f'{self.file_name}.save', 'r') as f:
                text = f.read()
                save_dict = json.loads(text)
                print('Loading words of power progress...')
                self.words_of_power.from_dict(save_dict['words_of_power'])
                print('Loading inventory...')
                self.item_collection.from_list(save_dict['inventory'])

    def help(self, bot, update):
        help_message = [
            '<b>Instruction Manual for CHEEZORK II - The Words of Power</b>\n\n'
            , 'Welcome to CHEEZORK, an interactive fiction story in which your group chat is the main character and '
            , 'the storyteller. Group members take turns setting a scene and then interacting with it in classic '
            , 'text adventure game style.\n\n'
            , 'Take <i>player</i> actions by starting a line with the tag #player.\n\n'
            , 'Take <i>dungeon master</i> actions by starting a line with the tag #dm.\n\n'
            , 'Text without a tag is not considered to be part of the adventure, and is never recorded.\n\n'
            , 'Have a look at the rules of the game with the /rules command.\n\n'
            , 'Access your inventory with the /inventory command. For example, you could add a brass lantern to the '
            , "player's inventory with the command:\n\n"
            , '<b>/inventory add brass lantern</b>\n\n'
            , 'You could remove the brass lantern using the command:\n\n'
            , '<b>/inventory remove brass lantern</b>\n\n'
            , 'or, if the lantern occupied slot number 1. in the inventory, you could also write:\n\n'
            , '<b>/inventory remove 1</b>\n\n'
            , 'Finally, a common pattern in CHEEZORK is to modify an item in the inventory, perhaps, in the case of '
            , 'the lantern, by lighting it. The fastest way to do this is to use the exchange command. This command '
            , 'only works with the numeric index of an item, for example, if the brass lantern was in slot number '
            , '1.:\n\n'
            , '<b>/inventory exchange 1 lit brass lantern</b>\n\n'
            , 'replaces the brass lantern with a lit brass lantern.\n\n'
            , 'As the <i>dungeon master</i> try to give the player fun items to work with!\n'
            , 'As the <i>player</i>, try to think of ways to use your items with the current scene.\n'
            , '\n'
            , '<i>Note, a, r, x, l, are shortcuts for add, remove, exchange, and list respectively</i>.\n\n'
            , "If you want to check your inventory before taking an action, but don't want to spam the main "
            , 'channel, you can use all of the CHEEZORK commands in a private conversation with your bot host. Be '
            , 'careful though, anything you type in private messages will also progress the game! Try to keep as much '
            , 'of your conversation with CHEEZORK to the main channel as possible!'
        ]
        bot.send_message(chat_id=update.message.chat_id, text=''.join(help_message), parse_mode=ParseMode.HTML)

    def about(self, bot, update):
        about_message = [
            '<b>CHEEZORK II - The Words of Power</b>\n\n'
            , 'CHEEZORK is a game of adventure, danger, and low cunning. In it you will explore some of the most '
            , 'amazing territory ever seen by mortals.\n\n'
            , 'Discover the /words of power!\n'
            , 'Bend the forces of creativity to your will!\n'
            , 'Remake the universe as you desire!\n\n'
            , 'The original CHEEZORK was created by Zach Benitez, with input from Lachlan Coles, Ryan Thomas, '
            , 'Sam Duyker, Ashnil Kumar, Bogdan Constantinescu, Liviu Constantinescu, Dane Murray, Luke Rasborsek, '
            , 'and Peter Budd. It was inspired by the adventure game ZORK, and the fighting fantasy book DEATHTRAP '
            , 'DUNGEON.\n\n'
            , '<i>(c) Copyright 2018 & 2019 PUNCHOUSE, inc. all rights reserved.</i>'
        ]
        bot.send_message(chat_id=update.message.chat_id, text=''.join(about_message), parse_mode=ParseMode.HTML)

    def rules(self, bot, update):
        rules_message = [
            '<b>Rules</b>\n'
            , '1. The player can not die.\n'
            , '2. You may not answer your own messages.\n'
            , '3. You may take multiple actions in a row as the <i>player</i> or the <i>dungeon master</i>, but you '
            , 'are encouraged to share these roles with other participants.\n'
            , '4. Tag <i>player</i> messages with #player and <i>dungeon master</i> messages with #dm.\n'
            , '5. Speak all of the /words of power in the same #player text to end the game.'
        ]
        bot.send_message(chat_id=update.message.chat_id, text=''.join(rules_message), parse_mode=ParseMode.HTML)

    def inventory(self, bot, update):
        text = update.message.text
        reply_text = self.item_collection.parse(text)
        bot.send_message(chat_id=update.message.chat_id
                         , text=reply_text
                         , parse_mode=ParseMode.HTML
                         )
        self.log(reply_text)
        self.save()

    def text_parser(self, bot, update):
        text = update.message.text
        player_pattern = '^\s*#player'
        dm_pattern = '^\s*#dm'
        player_match = re.match(player_pattern, text.lower())
        dm_match = re.match(dm_pattern, text.lower())
        if player_match:
            self.log(text)
            player_words = self.words_of_power.check_for_words(text)
            print('Logging player note...')
            if player_words:
                bot.send_message(chat_id=update.message.chat_id
                                 , text=player_words
                                 , parse_mode=ParseMode.HTML
                                 )
                self.save()
        if dm_match:
            self.log(text)
            print('Logging DM note...')
            words = re.split('\s+', text)
            if len(words) > self.min_words:
                self.clue_count = self.clue_count + 1;
                word_found = self.words_of_power.add_clue()
                print(f'Clues increased to {self.clue_count}.')
                if word_found:
                    bot.send_message(chat_id=update.message.chat_id
                                     , text=word_found
                                     , parse_mode=ParseMode.HTML
                                     )
                self.save()

    def log(self, text):
        with open(f'{self.file_name}.log', 'a+') as f:
            f.write(text)
            f.write('\n\n')

    def save(self):
        with open(f'{self.file_name}.save', 'w') as f:
            save_dict = {
                'words_of_power': self.words_of_power.to_dict()
                , 'inventory': self.item_collection.to_list()
            }
            f.write(json.dumps(save_dict))

    def words(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id
                         , text=self.words_of_power.print_words()
                         , parse_mode=ParseMode.HTML
                         )

    def register_dispatcher(self, dispatcher):
        dispatcher.add_handler(CommandHandler('inventory', self.inventory))
        dispatcher.add_handler(CommandHandler('about', self.about))
        dispatcher.add_handler(CommandHandler('help', self.help))
        dispatcher.add_handler(CommandHandler('rules', self.rules))
        dispatcher.add_handler(CommandHandler('words', self.words))

        # Non command handler
        dispatcher.add_handler(MessageHandler(Filters.text, self.text_parser))


def main():
    print(os.path.dirname(os.path.realpath(__file__)))
    parser = argparse.ArgumentParser(
        description='Interactive telegram text adventure server.'
        , prog='cheezork'
    )
    parser.add_argument('token', help='Telegram bot token for the target bot.')
    parser.add_argument('save', help='Name of save file. Will load if exists.')
    parser.add_argument('--words', help='Words file to load. Clears words progress.')
    parser.add_argument('--exit', action='store_const', const=True
                        , help='Exits the game immediately. Will still load words.')

    args = parser.parse_args()

    cheezork = Cheezork(args.save)
    if args.words:
        cheezork.words_of_power = WordsOfPower()
        cheezork.words_of_power.from_file(args.words)
        cheezork.save()

    if args.exit:
        sys.exit(0)

    TOKEN = args.token
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        , level=logging.INFO)

    cheezork.register_dispatcher(dispatcher)

    updater.start_polling()


if __name__ == "__main__":
    with PIDFile(os.getcwd() + "/cheezork.pid"):
        main()

