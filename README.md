# Sentdebot V2

Rework of original Setdebot to more modular form and using modern discord API. \
Except of reimplementing all the original features of the bot this bot implements some more features that will be described later.

## Table of contents
* [General info](#general-info)
* [Bot structure](#bot-structure)
* [Features](#features)
* [Deployment](#deployment)

## General info
Discord bot created in python using disnake library [Link](https://github.com/DisnakeDev/disnake). \
This project is no replacement for original Sentdebot. It was created only as programming practice and fun so there was no consultation between authors and original bot and me and because of this some features are implemented in my way and not exactly like in original bot and the code is not very clean.
Because original bot was ment to be used only for one specific server and some features are tightly related to it then this bot to share similar behaviour and simply some functions will be unavailable if invited to different guild for which was the bot configured.

## Bot structure
Main difference between this bot and the original one is the that this bot is split to modules with different subfunctions to be as modular as possible. \
This bot is divided to few main parts: main bot file, cogs, config, database, features, modals, static data and utils. \
Main bot file (sentdebot.py in root directory) is used as entrypoint of whole bot. \
Cogs is folder to store individual extensions of functionality. \
Config stores parser for configuration files and definitions for cooldowns, there is also template for configuration file that you want to copy, modify and rename to ``config.toml`` to be able to run this bot. \
Features is used to store extension of disnake functionality by wrappers, custom functional components and other things. \
Modals stores discord UI definitions for InApp forms. \
Static data folder is used to data that are not change in runtime, and it's desired to have them on one place to better access for editing. \
Utils is place for any other extensions, helper functions, etc.

## Features
1. Buildin robust error handling with option to log to file and log discord channel (in cases that are forgotten to handle or caused by bad manipulation of user) \
![1](media/error_sample1.jpg?raw=true)
2. Managing system for loading, unloading and reloading extensions on the fly
3. Guild statistics collector and displayer \
![2](media/community_report.jpg?raw=true)
4. Parametric random role giver
5. Custom help command with automatically generated help for individual message commands \
Help embed is send with button to list through help pages that outly author can control \
![3](media/help.jpg?raw=true)
6. System for managing help requests in help channel using threads and ticket system \
Help channel is locked by default to not allow users to write here directly, instead help requests are created using command that will bring this help request form. \
![7](media/help_req_create_form.jpg?raw=true) \
Help request is then created in help channel as thread by the bot and author is invited to that thread, this request is added to database too to track time of last activity. \
![8](media/help_req_created.jpg?raw=true) \
If then problem is solved user or mod can call `/help_request solve` in this thread to mark it as solved and lock it from future messages. \
![9](media/help_req_solved.jpg?raw=true)
7. Extension for storing project and information about them \
Mods can add projects using this form (ofcourse there is command to remove them too). \
![4](media/project_add_form.jpg?raw=true) \
User then can find project using command `/projects get <name>` and bot will show you all current projects as reference. \
![5](media/project_get_info.jpg?raw=true) \
And bot will then send information about the project in this form \
![6](media/project_get_info_result.jpg?raw=true)
8. Simple code evaluator for almost any language \
![10](media/code_evaluation.jpg?raw=true)
9. Bookmark feature, so you don't lose some important messages \
User can create bookmark of any message reacting to it by `🔖` or using rightclick on message -> Apps -> Bookmark \
Bot will then send to users bookmark like this \
![11](media/bookmark.jpg?raw=true)
10. Robust database using SQLAlchemy ORM
11. Centralized handling of added reaction because there is needed some more processing for non cached messages

And many other smaller things

## Deployment
Without any container (python version >= 3.8)
```
pip install -r requirements.txt
python sentdebot.py
```

Using docker compose
```py
docker-compose up --build

# After code modification rebuild using
docker-compose restart

## Special cleanup cases ##
# Teardown and remove volumes
docker-compose down -v

# Teardown and remove image
docker-compose down --rmi local

# Complete cleanup
docker-compose down -v --rmi local

# Dump of database
docker exec -t sentdebot-db-1 pg_dumpall -c -U postgres > database_dump.sql

# Restore database from dump
cat database_dump.sql | docker exec -i sentdebot-db-1 psql -U postgres
```

Using Heroku hosting only push to heroku project repository or link it to your copy of this repository

Any other deployment methods are up to you
