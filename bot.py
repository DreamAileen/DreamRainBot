# coding: utf-8
import asyncio
import json
from os import replace

from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source
from graia.ariadne.model import Friend, Group, Member, MiraiSession

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models

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

admin_qq = 1430881243

def digit(text):
    """
    传入一个字符串，返回字符串中的数字
    """
    return int("".join(list(filter(lambda text:text.isdigit(), text))))


if table.search(query.name == 'adminqq') == []:
    table.insert({'name':'adminqq','cont':admin_qq})
if table.search(query.name == 'illegalBool') == []:
    table.insert({'name':'illegalBool','cont':False})
if table.search(query.name == 'nlpBool') == []:
    table.insert({'name':'nlpBool','cont':False})

@bcc.receiver("GroupMessage")
async def group_message_handler(app: Ariadne, group: Group, member: Member, message: MessageChain):

    messageContent = None
    messageContentAt = None
    times = None
    adminList = []
    illList = []
    illBool = table.search(query.name == 'illegalBool')[0]['cont']
    nlpBool = table.search(query.name == 'nlpBool')[0]['cont']

    for i in table.search(query.name == 'adminqq'):
        adminList.append(i['cont'])
    
    for i in table.search(query.name == 'Illegal'):
        illList.append(i['cont'])

######################测试区域##########################


    # if "测试" in message.asDisplay():
    #     await app.sendMessage(
    #         group,
    #         MessageChain.create(str(digit(str(message.get(Plain)))))
    #     )

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



######################违禁词撤回开始######################

    # 开启违禁词
    if message.asDisplay() == "开启违禁检测":
        if member.id in adminList or member.id == admin_qq:
            table.update({'cont':True},query.name == 'illegalBool')
            messageContent = '已开启违禁词检测！请注意发言喔~'

    # 关闭违禁词
    if message.asDisplay() == "关闭违禁检测":
        if member.id in adminList or member.id == admin_qq:
            table.update({'cont':False},query.name == 'illegalBool')
            messageContent = '已关闭违禁词检测！大家畅所欲言吧~'

    # 违禁词添加
    if message.asDisplay().startswith('添加违禁词'):
        if member.id in adminList or member.id == admin_qq:
            illegal = message.asDisplay().replace("添加违禁词","").replace(" ","")
            table.insert({'name':'Illegal','cont': illegal})
            messageContent = '添加成功，新增违禁词：' + illegal

    # 违禁词删除
    if message.asDisplay().startswith('删除违禁词'):
        if member.id in adminList or member.id == admin_qq:
            illegal = message.asDisplay().replace("删除违禁词","").replace(" ","")
            table.remove(query.cont == illegal)
            messageContent = '删除成功，被删除违禁词：' + illegal

    # 查看违禁词
    if message.asDisplay() == "查看违禁词":
        if illBool:
            messageContent = "当前违禁词状态：开启\n违禁词列表：" + str(illList)
        else:
            messageContent = "当前违禁词状态：关闭\n违禁词列表：" + str(illList)

    # 违禁词撤回
    if illBool:
        for illegal in illList:
            if illegal in message.asDisplay():
                text = message.asDisplay()
                await app.recallMessage(
                    message.get(Source)[0].id
                )
                await app.sendGroupMessage(
                    group,
                    MessageChain.create(
                        Plain("发现违禁词！已经撤回违禁消息！\n触发者："),
                        At(member.id),
                        Plain("\n违禁内容：" + text.replace(illegal,len(illegal) * '*'))
                    )
                )

######################违禁词撤回结束######################


######################智能聊天开始########################

    # 开启智能聊天
    if message.asDisplay() == '开启智能聊天':
        if member.id in adminList or member.id == admin_qq:
            table.update({'cont':True},query.name == 'nlpBool')
            messageContent = '已开启智能聊天！快来一起和机器人玩耍吧~'

    # 关闭智能聊天
    if message.asDisplay() == '关闭智能聊天':
        if member.id in adminList or member.id == admin_qq:
            table.update({'cont':False},query.name == 'nlpBool')
            messageContent = '已关闭智能聊天！机器人不能和大家愉快的聊天了~'

    # 腾讯NLP智能聊天调用模块
    
    if nlpBool:
        try:
            if message.asDisplay().startswith('[At:(2177895968)]') and '谁' not in  message.asDisplay():
                cred = credential.Credential("腾讯云开发接口ID", "腾讯云开放接口Key")
                httpProfile = HttpProfile()
                httpProfile.endpoint = "nlp.tencentcloudapi.com"

                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

                req = models.ChatBotRequest()
                params = {
                    "Query": message.asDisplay().replace('[At:(2177895968)]','').replace(' ','')
                }
                req.from_json_string(json.dumps(params))

                resp = client.ChatBot(req)
                messageContent = json.loads(resp.to_json_string())["Reply"]
            elif  message.asDisplay().startswith('[At:(2177895968)]') and '谁' in  message.asDisplay():
                messageContent = '我是梦雨正在开发的MirAi机器人喔~'
            

        except TencentCloudSDKException as err:
            print(err)


######################智能聊天结束########################




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
