# cheezork
A rudimentary telegram bot that manages lists of things for an adventure game.

Cheezork I uses telepot (deprecated)

Cheezork II uses python telegram bot (https://python-telegram-bot.org/)

## Installation
To install cheezork, you first need to install python telegram bot using any method. We suggest using pip:

`pip install telegram-bot`

Then copy this archive to anywhere you've got write access and you're good to go. That's all for the installation.

## Setup
To run a game of cheezork, you need two things - a bot token and a list of words of power.

To get a bot token, you'll need to create a bot by talking to the botfather. This process is described here: https://core.telegram.org/bots#6-botfather. Once the bot has been created, the botfather will give you a 'token' string that looks like a bunch of gibberish:

> Use this token to access the HTTP API:<br>
> 1273171144:agsuuyauytqwmnqwugaufikdgouigua

Next, you need to make some words of power. We recommend between five and ten words. More words will make for a longer game. Create a new text file with any name and type your words of power into it, with one per line. For example, you might create a text file 'words.txt' that contains:

> vacuous<br>
> love<br>
> gear

These would be the hidden words of power for your next game of cheezork.

Now, load these words of power into your game by calling the cheezork script with the following options:

`python3 cheezork_game.py <TOKEN> <path/to/save/file> --words <path/to/words/file> --exit`

This will make a new save file with your words of power. It will not run the bot.

To get the bot running, simply type:

`python3 cheezork_game.py <TOKEN> <path/to/save/file>`

Note that this will not inherently spawn as a background process so you'll have to do some additional scripting to get that to work!
