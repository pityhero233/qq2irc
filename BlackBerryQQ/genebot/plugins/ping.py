from nonebot import on_command, CommandSession

@on_command('@ping')
async def ping(session: CommandSession):
    await session.send("pong "+session.get("word"))

@ping.args_parser
async def _(session: CommandSession):
    trimmed = session.current_arg_text.strip()
    if session.is_first_run:
        if trimmed:
            session.state["word"] = trimmed
            return
        else:
            session.pause(".... at least tell me something")
    session.state[session.current_key]=trimmed #?
