# markdown wiki builder that walks through a directory structure and builds a markdown wiki
# every module having its own page in the wiki
# if a module is part of a package, the module is placed in the package's page
# when we read a python file we need to walk through the ast and find what was imported, and then recursively walk through the module functions and classes to gather the doc strings

import aiopath
import re
import json
import ast
import inspect
import textwrap
import collections
import itertools
import functools
import typing
import asyncio


class MarkdownWikiBuilder:
    def __init__(self, directory):
        self.directory = directory
        self.wiki_directory = 'wiki'

    # us asyncio to generate a wiki file for each module following the directory structure
    async def generate_wiki(self):


