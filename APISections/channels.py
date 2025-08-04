import json
import logging

from RocketExceptions import RocketMissingParamException
from base import RocketChatBase


class RocketChatChannels(RocketChatBase):
    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.call_api_get("channels.list", kwargs=kwargs)

    # def expr_channels_add_moderator(self, room_name, user_name, **kwargs):
    #     """Gives the role of moderator for a user in the current channel. For this command user needs to be in a room/channel """
    #     self.users_list
    #     list_ch = self.channels_list().json()
    #     for i in range(len(list_ch["channels"])):
    #         if list_ch["channels"][i]["name"] == room_name:
    #             room_id = list_ch["channels"][i]["_id"]
    #             return self.call_api_post(
    #                 "channels.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
    #             )

    def channels_add_moderator(self, room_id, user_id, **kwargs):
        """Gives the role of moderator for a user in the current channel. For this command user needs to be in a room/channel """
        return self.call_api_post(
            "channels.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_add_owner(self, room_id, user_id=None, username=None, **kwargs):
        """Gives the role of owner for a user in the current channel."""
        if user_id:
            return self.call_api_post(
                "channels.addOwner", roomId=room_id, userId=user_id, kwargs=kwargs
            )
        if username:
            return self.call_api_post(
                "channels.addOwner", roomId=room_id, username=username, kwargs=kwargs
            )
        raise RocketMissingParamException("userID or username required")

    def channels_add_leader(self, room_id, user_id, **kwargs):
        """Gives the role of Leader for a user in the current channel."""
        return self.call_api_post(
            "channels.addLeader", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_create(self, name, **kwargs):
        """Creates a new public channel, optionally including users."""
        return self.call_api_post("channels.create", name=name, kwargs=kwargs)

    def channels_invite(self, room_id, user_id, **kwargs):
        """Adds a user to the channel."""
        return self.call_api_post(
            "channels.invite", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_kick(self, room_id, user_id, **kwargs):
        """Removes a user from the channel."""
        return self.call_api_post(
            "channels.kick", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_delete(self, room_id=None, channel=None, **kwargs):
        """Delete a public channel."""
        if room_id:
            return self.call_api_post("channels.delete", roomId=room_id, kwargs=kwargs)
        if channel:
            return self.call_api_post(
                "channels.delete", roomName=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or channel required")

    def channels_members(self, room_id=None, channel=None, **kwargs):
        """Lists all channel users."""
        if room_id:
            return self.call_api_get("channels.members", roomId=room_id, kwargs=kwargs)
        if channel:
            return self.call_api_get(
                "channels.members", roomName=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or channel required")