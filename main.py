#!/usr/bin/python3.7
import nonebot
import config
import os
import asyncio

nonebot.init(config)
nonebot.load_builtin_plugins()
nonebot.load_plugins(os.path.join(os.path.dirname(__file__), "genebot", "plugins"), 'genebot.plugins')

try:
    nonebot.run(host='127.0.0.1', port=6238) # start main event loop
finally:
    pass
