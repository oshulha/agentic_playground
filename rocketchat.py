# -*-coding:utf-8-*-
from APISections.channels import RocketChatChannels
from APISections.chat import RocketChatChat
from APISections.miscellaneous import RocketChatMiscellaneous
from APISections.rooms import RocketChatRooms
from APISections.users import RocketChatUsers

class RocketChat(
    RocketChatUsers,
    RocketChatChat,
    RocketChatChannels,
    RocketChatMiscellaneous,
    RocketChatRooms,
):
    pass