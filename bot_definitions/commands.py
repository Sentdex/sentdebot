import inspect

from definitions import Command

# module to hold definitions and functions pertaining to Discord commands ONLY

# PROPOSED COMMAND FORMAT:
# Command(
#   'register_as_command',
#   'description',
#   'function'
# )
#
# The 'register_as_command' should be formatted as `the_command_name(the_command_args)` with no prefix of sentdebot.
# The 'description' should be a short description of the register_as_command.
# The 'function' should be a Callable with arguments matching the register_as_command's arguments.
#    this can be either a function or a lambda.


# I have formatted out the existing register_as_command and have added some ideas for new ones, but I have not yet
# defined the functions as I wish to get some agreement on the format first.

# included is a function decorator that is used to make a function a Command

COMMAND_PREFIX = 'sentdebot.'


available_commands = [
    # TODO: replace the None lambdas with actual function calls or lambda expressions,
    #  replace these explicit entries with the decorator
    Command('member_count()',
            'Returns the number of members in the server.',
            lambda: None),

    Command('community_report()',
            'Get some stats on community',
            lambda: None),

    Command('search("QUERY")',
            'Search for a string',
            lambda query: None),

    Command('commands()',
            'Get commands',
            lambda: None),

    Command('logout()',
            'Sentdex-only register_as_command to log Sentdebot off',
            lambda: None),

    Command('user_activity()',
            'See some stats on top users',
            lambda: None),

    ##############################################################################################
    # New Proposed Commands
    ##############################################################################################

    Command('find_yt_video("QUERY")',
            'Searches for a Sentdex video',
            lambda query: None
            ),

    Command('find_documentation("QUERY")',
            'Try and find a link to documentation for a given query',
            lambda query: None
            ),

    Command('find_pseudo("QUERY")',
            'Try and find a link to a pseudo for a given query',
            lambda query: None
            ),

    Command('find_python_package("QUERY")',
            'Try and find a link to a python package for a given query',
            lambda query: None
            ),

    Command('find_github_repository("QUERY")',
            'Try and find a link to a github repository for a given query',
            lambda query: None
            ),
]


# a function/callable class decorator that has a description arg that is used to make a callable a Command
# the description is used to make the register_as_command's description if no description is provided
def register_as_command(description=None):
    """
    A function decorator that has a description arg that is used to make a callable a Command
    :param description: the description to use for the Command, if not provided the function's docstring is used
    :return: a function decorator
    """
    def decorator(function):
        func_name = function.__name__
        func_arg_names = ", ".join([
            f"{arg.capitalize()}"
            for arg
            in inspect.getfullargspec(function).args]) \
            if len(inspect.getfullargspec(function).args) > 0 \
            else ""
        command_name = f"{func_name}({func_arg_names})"
        command_description = description \
            if description is not None \
            else function.__doc__ \
            if function.__doc__ is not None \
            else ""
        available_commands.append(Command(command_name, command_description, function))
        return function

    return decorator


def build_commands_string(available_commands_list):
    """
    Builds a string of commands from a list of commands
    :param available_commands_list: List of Command objects
    :return: the command() output string
    """
    start = "```python\ndef commands():\n\treturn {\n"
    end = "\n\t}```"
    commands_string = "\t\t" + ",\n\t\t".join([
        f"{COMMAND_PREFIX}{command.name}: '{command.description}'"
        for command
        in available_commands_list
    ])
    return start + commands_string + end

if __name__ == '__main__':
    # test adding a new register_as_command using the decorator
    @register_as_command("This is a test register_as_command added using a decorator and the description arg")
    def test_command():
        print("This is a test register_as_command")

    @register_as_command()
    def test_command_2():
        """This is a test register_as_command added using a decorator and no description arg on a function with a docstring"""
        print("This is a test register_as_command")

    print(build_commands_string(available_commands))



