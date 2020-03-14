from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand, get_bot, CQHttpError
from multiprocessing.connection import Listener,Client
import asyncio
import threading



address = ('localhost',6240)
addForUserComm = ('localhost',6241)
bot = get_bot()
conn = Client(address, authkey=b'toirc_password')
revsck = Listener(addForUserComm, authkey=b'toirc_password')
revconn = revsck.accept()
print("Mutual Connection established.")

# <Event, {'font': 1605664, 'message': [{'type': 'text', 'data': {'text': 'noob'}}], 'message_id': 70, 'message_type': 'private', 'post_type': 'message', 'raw_message': 'noob', 'self_id': 2357913729, 'sender': {'age': 34, 'nickname': 'O晖O', 'sex': 'male', 'user_id': 1171548839}, 'sub_type': 'friend', 'time': 1583396768, 'user_id': 1171548839, 'to_me': True}>

def ircListener():
    while True:
        (comm, arg1, arg2) = revconn.recv()
        if comm == "DEBUGSEND":
            print("Debug Send Activated.")
            try:
                print(asyncio.run(bot.send_private_msg(user_id=1019508714,message="test")))
            except CQHttpError:
                print("Error.")
                conn.send(("err", "", ""))
            print("send done.")
        if comm=="SEND":
            print("Send Activated")
            try:
                print(asyncio.run(bot.send_private_msg(user_id=int(arg1),message=arg2)))
            except CQHttpError:
                print("Error.")
                conn.send(("err","",""))
            print("send done.")
t = threading.Thread(target=ircListener,args=())
t.start()

@on_command('@rcvdword')
async def rcvdword(session: CommandSession):
    print(session.ctx["sender"]["nickname"])
    print("------\n"+session.current_arg+"\n")
    if session.ctx["message_type"]== "private":
        conn.send(("msg", session.ctx["sender"]["nickname"],session.current_arg))
    else:
        conn.send(("msg", session.ctx["sender"]["nickname"],"NONPRIV"))


@on_natural_language()
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    return IntentCommand(100.0, '@rcvdword', current_arg=stripped_msg)

