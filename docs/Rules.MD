[//]: # (This is a rough draft of the the proposed code stylings)

# Code Styles

### Naming Conventions


Naming should be consistent with the following rules:

    * short but descriptive names where possible
    * cogs start with `cog_`


### Structuring


Structuring should be consistent with the following rules:


    * if a cog is intended to be optional, togglable etc etc, then it should be placed in the cogs folder, if it is system specific and must always be running, then it belongs in the core_cogs folder
    * Files, modules, classes and functions should at best be single purpose, and if it requires several supporting files then the cog should be a package and NOT leave loose files in the cogs folders, while this will not effect the cogs functioning, it provides a cleaner codebase and shows what files belong to what cogs
    * Try to decouple your code, the more coupled your code the harder it becomes to update, refactor and test, so if you do require access to external functionality, try to use concepts like dependency injection. 


### Comments


Please attempt to keep your code comments consistent with the following rules:


    * Firstly, docstrings are preferable to comments, as these can be accessed as objects in the future for various helper functions.
    * Comments should be short, and should be placed at the top of the function, class, module, file, etc, unless explaining a particular line 
    * Make use of ToDo: at the beginning of a comment if you wish to flag something in particular for bug fixing, updates etc etc
    * Please keep your comments on topic, as this will make it easier for others to understand your code


### Approval


All code will be approved before it is added to the release by the senior developers.

There are come core things that will be used to measure the viability of proposed code:

    * Code readability
    * Code maintainability
    * Code testability
    * Code security
    * Code style
    * Code documentation
    * Code utility
    * Code efficiency

Do note, even after initial approval, the code may still not make it to final release.


### Community Standards

This project is community driven, and as such we have some ground rules for everyone to follow.

The community is built of real people with real lives, and as such please respect their time and energy and make considerations for their needs.
There are people with varying levels of experience, and as such please be respectful, everyone starts somewhere.
There are also people of varying ages, thus we ask people to keep conversations on topic, and not include NSFW content.
Be respectful of other peoples questions, and if you have the opportunity, please answer them.
Communication is important, and as such please try to be as open as possible about what you are currently working on, 
what help you are currently needing, and what you may be waiting on etc etc.
Keep everything legal, we will not condone any illegal activities, copyright infringement or any other content that could be considered damaging
