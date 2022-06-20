## Style Guide for Sentdebot

### Commands:
Commands should be short and pythonic in appearance, placing queries between parenthes (implementation in progress).
The sentdebot. prefix is handled automatically, and does not need to be included.

Commands without arguments is named like this:
`command_name()`
and can be called like this:
`sentdebot.commands()`'

Commands with arguments are named like this:
`command_name('arg1', 'arg2')`
and can be called like this:
`sentdebot.command_name('arg1', 'arg2')`


### Cogs
cog filenames must be structures as such:
`cog_camel_case_name.py`
and must only contain a single cog class with its associated setup function, other non cog classes can be included if they are used within the script.
A cog can have supporting sub packages and cogs, but try and keep them in a single root package, structured like
* cog.py
* /cog_data
    * some_supporting_file.py
making sure sensibly name the files so it's clear which cog they belong to.

The class name must omit the cog_ prefix and be written in PascalCase like thus:
`class CogName(Cog)`
 
the setup function must be named setup. and look like this:
```python
def setup(bot):
    bot.add_cog(CogName(bot))
```
