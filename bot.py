# coding: utf-8
import asyncio

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Friend, Group, Member, MiraiSession

import random
from tinydb import TinyDB
from tinydb.queries import Query

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="DreamRain",  # 填入 verifyKey
        account=2177895968,  # 你的机器人的 qq 号
    )
)

db = TinyDB('text.json')
table = db.table('Content')
query = Query()

atlist = ["我是梦雨正在开发MirAi机器人喔~","叫我干嘛","你是什么东西？","你叫我是想给我钱嘛","别叫了别叫了"]
admin_qq = 1430881243


def digit(text):
    """
    传入一个字符串，返回字符串中的数字
    """
    return int("".join(list(filter(lambda text:text.isdigit(), text))))


@bcc.receiver("GroupMessage")
async def group_message_handler(app: Ariadne, group: Group, member: Member, message: MessageChain):

    messageContent = None
    messageContentAt = None
    times = None
    adminList = []

    for i in table.search(query.name == 'adminqq'):
        adminList.append(i['cont'])

######################测试区域##########################


    # if "测试" in message.asDisplay():
    #     await app.sendMessage(
    #         group,
    #         MessageChain.create(str(digit(str(message.get(Plain)))))
    #     )

    if message.asDisplay().startswith('[At:(2177895968)]'):
        random.shuffle(atlist)
        await app.sendGroupMessage(
            group,
            MessageChain.create(
                Plain(atlist[0])
            )
        )

#####################权限部分开始#######################
    
    
    # 添加管理员
    if message.asDisplay().startswith("添加管理员[At"):
        if member.id == admin_qq:
            user_qq = message.getFirst(At).target
            if user_qq not in adminList:
                table.insert({'name':'adminqq','cont':user_qq}) # 往数据库加管理员QQ
                messageContent = "添加成功！祝贺新管理："
                messageContentAt = user_qq
            else:
                messageContent = "这个b已经是管理了喔~"
        else:
            messageContent = "你没有权限喔~"

    elif message.asDisplay().startswith("添加管理员"):
        if member.id == admin_qq:
            user_qq = digit(message.asDisplay())
            if user_qq not in adminList:
                table.insert({'name':'adminqq','cont':user_qq}) # 往数据库加管理员QQ
                messageContent = "添加成功！祝贺新管理："
                messageContentAt = user_qq
            else:
                messageContent = "这个b已经是管理了喔~"
        else:
            messageContent = "你没有权限喔~"

    # 删除管理员
    if message.asDisplay().startswith("删除管理员[At"):
        if member.id == admin_qq:
            user_qq = message.getFirst(At).target
            if user_qq in adminList:
                table.remove(query.cont == user_qq) # 删除数据库中指定QQ
                messageContent = "删除成功！被删除管理："
                messageContentAt = user_qq
            else:
                messageContent = "这个b不是是管理喔~"
        else:
            messageContent = "你没有权限喔~"
            
    elif message.asDisplay().startswith("删除管理员"):
        if member.id == admin_qq:
            user_qq = digit(message.asDisplay())
            if user_qq in adminList:
                table.remove(query.cont == user_qq) # 删除数据库中指定QQ
                messageContent = "删除成功！被删除管理："
                messageContentAt = user_qq
            else:
                messageContent = "这个b不是是管理喔~"
        else:
                messageContent = "你没有权限喔~"

    # 查看管理员
    if message.asDisplay() == "查看管理员":
        if member.id == admin_qq or member.id in adminList:
            messageContent = "管理员列表：" + str(adminList)
        else:
                messageContent = "你没有权限喔~"
        
#####################权限部分结束#######################


######################群管理结束########################

    # 禁言
    if message.asDisplay().startswith("禁言["):
        if member.id in adminList or member.id == admin_qq:
            user_qq = message.getFirst(At).target
            try:
                times = digit(str(message.get(Plain)))
            except: pass
            if times == None:
                await app.muteMember(
                    group,
                    user_qq,
                    5 * 60
                )
                messageContent = "被禁言5分钟"
            else:
                await app.muteMember(
                    group,
                    user_qq,
                    times * 60
                )
                messageContent = "被禁言" + str(times) + "分钟"
        else:
            messageContent = "你没有权限喔~"
    
    # 全体禁言
    if message.asDisplay() == "禁言全体":
        if member.id in adminList or member.id == admin_qq:
            await app.muteAll(
                group
            )
            messageContent = "已开启全体禁言！"
        else:
            messageContent = "你没有权限喔~"
    
    # 解除禁言
    if message.asDisplay().startswith("解除禁言"):
        if member.id in adminList or member.id == admin_qq:
            user_qq = message.getFirst(At).target
            await app.unmuteMember(
                group,
                user_qq
            )
            messageContent = "已解除禁言！"
        else:
            messageContent = "你没有权限喔~"
    
    # 解除全体禁言
    if message.asDisplay() == "解除全体":
        if member.id in adminList or member.id == admin_qq:
            await app.unmuteAll(
                group
            )
            messageContent = "已解除全体禁言！"
        else:
            messageContent = "你没有权限喔~"

    # 踢出某人
    if message.asDisplay().startswith("踢出"):
        if member.id in adminList or member.id == admin_qq:
            user_qq = message.getFirst(At).target
            await app.kickMember(
                group,
                user_qq,
                ""
            )
            messageContent = "已踢出" + str(user_qq)
        else:
            messageContent = "你没有权限喔~"

#######################群管理结束#########################


######################消息发送开始########################

    # 群消息事件消息发送出口
    if messageContent != None:
        if messageContentAt != None:
            await app.sendGroupMessage(
                            group,
                            MessageChain.create(
                                Plain(messageContent),
                                At(messageContentAt)
                            )
                        )
        else:
            await app.sendGroupMessage(
                            group,
                            MessageChain.create(
                                Plain(messageContent)
                            )
                        )
######################消息发送结束########################

@bcc.receiver("FriendMessage")
async def friend_message_listener(app: Ariadne, friend: Friend, message: MessageChain):
    if "你" in message.asDisplay() and "谁" in message.asDisplay():
        await app.sendMessage(
            friend, 
            MessageChain.create("我是梦雨正在开发的机器人鸭~")
        )
    else:
        await app.sendMessage(
            friend, 
            MessageChain.create("Hello " + friend.nickname + ",You said " + message.asDisplay())
        )

loop.run_until_complete(app.lifecycle())
