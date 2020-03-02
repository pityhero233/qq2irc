from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from multiprocessing.connection import Listener,Client
address = ('localhost',6240)
conn = Client(address, authkey=b'toirc_password')

@on_command('@rcvdword')
async def rcvdword(session: CommandSession):
    print(session.ctx["sender"]["nickname"])
    print("------\n"+session.current_arg+"\n")
    conn.send((session.ctx["sender"]["nickname"],session.current_arg))


@on_natural_language()
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    return IntentCommand(100.0, '@rcvdword', current_arg=stripped_msg)

