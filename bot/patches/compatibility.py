from discord.ext.commands.view import _quotes

# WARNING:: [The commented code is important please don't remove it
# unless absolutely neccesary]
# TODO:: [Optimise this function more,
# and discard invalid commands to make up for lost cpu time.]

# Every conversion has a non-unique conversion ID
# The ID corresponds to the code that was exceuted
# Example:
#   Id of sentdebot.oof("\", 5) is 163456
#   Id of sentdebot.oof("\", 5, 888) is 16345645666
#   Id of "Hello, how are you?" does not exist
# Similar strings will have similar IDs
# The IDs Can be very useful for debugging
# But i have not implemented this, this could be made easily when bugs
# will be found

__all__ = ("clean_string",)

# we do not do any validation in here, we just convert and pass it ahead
# for validation and processing
def clean_string(content: str, prefix: str = "sentdebot "):
    """Cleans the string so that we are compat with ext

    Parameters
    ----------
    content : str
        The string wich is going to be cleaned
    prefix : str


    Returns
    -------
    str
        The clean string
    """
    try:
        try:
            _argstrt = content.index('(')
        except ValueError:
            return content # Not a valid command
        cleaned = content[0:_argstrt].replace(".", " ") # This is the base of the command
        if cleaned.lower() == "help":
            cleaned = prefix + cleaned
        cleaned += " "
        args = content[_argstrt:].lstrip("(").rstrip(") ") # Remaining has to be the arguments

        # Now we need to build a tuple a of strings from a string which is similar to a tuple's repr
        # eval is not an option since even without builtins it is dangerous
        # we could just split with a comma,
        # but the args might have commas inside quotes (aka comma inside the command args)!

        closer = ""
        inquotes = False
        on_backslash = False
        for i in args:
            if i == "\\" and inquotes:
                on_backslash = True
            elif i in _quotes and not on_backslash and i != closer:
                closer = _quotes[i]
                inquotes = True
                cleaned += i
                # print(i, 1, closer, inquotes, on_backslash)
            elif i in _quotes and on_backslash:
                on_backslash = False
                cleaned += f"\\{i}"
                # print(i, 2, closer, inquotes, on_backslash)
            elif inquotes and i == closer and not on_backslash:
                inquotes = False
                cleaned += i
                closer = ""
                # print(i, 3, closer, inquotes, on_backslash)
            elif i == "," and not inquotes:
                cleaned += " "
                # print(i, 4, closer, inquotes, on_backslash)
            elif i == " " and not inquotes and cleaned[-1] == " ":
                # We are not in an arg and the space shows up twice
                # so we ignore the second space
                # print(i, 5, closer, inquotes, on_backslash)
                pass
            else:
                cleaned += i
                # print(i, 6, closer, inquotes, on_backslash)
        return cleaned
    except Exception:
        return content

# Testing the conversion layer
if __name__ == "__main__":
    while True:
        if not (In := input("clean_string test >>>")):
            break
        print(clean_string(In))