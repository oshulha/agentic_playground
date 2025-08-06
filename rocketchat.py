# -*-coding:utf-8-*-
import mimetypes
import os
from base import RocketChatBase
from wrap_response import WrapResponse
from typing import Literal

DEFAULT_LIMIT = 50

class RocketChat(RocketChatBase):
    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.call_api_get("channels.list", kwargs=kwargs)

    def channels_add_role(self, channel, user_name, role: Literal["owner", "moderator", "leader"], **kwargs): #Done
        """Gives the role of moderator/owner/leader for a user in the current channel. For this command user needs to be in a room/channel """
        list_us = self.users_list().json()
        user_id = None
        for i in range(len(list_us["users"])):
            if list_us["users"][i]["name"] == user_name:
                user_id = list_us["users"][i]["_id"]
                break
        
        if not user_id:
            return WrapResponse({"success": False, "error": "invalid-user_name"})

        list_ch = self.channels_list().json()

        for i in range(len(list_ch["channels"])):
            if list_ch["channels"][i]["name"] == channel:
                room_id = list_ch["channels"][i]["_id"]
                if role == "leader":
                    return self.call_api_post(
                        "channels.addLeader", roomId=room_id, userId=user_id, kwargs=kwargs
                    )
                elif role == "owner":
                    return self.call_api_post(
                        "channels.addOwner", roomId=room_id, userId=user_id, kwargs=kwargs
                    )
                elif role == "moderator":
                    return self.call_api_post(
                        "channels.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
                    )
                else:
                    return WrapResponse({
                        "success": False,
                        "error": "role must be owner, moderator or leader"
                    })
        return WrapResponse({"success": False, "error": "invalid-channel-name"})

    def channels_create(self, name, **kwargs):
        """Creates a new public channel, optionally including users."""
        return self.call_api_post("channels.create", name=name, kwargs=kwargs)

    def __channels_invite_one_user(self, channel, user_name, **kwargs): #Done
        """Adds a user to the channel."""
        list_us = self.users_list().json()
        user_id = None
        for i in range(len(list_us["users"])):
            if list_us["users"][i]["name"] == user_name:
                user_id = list_us["users"][i]["_id"]
                break

        if not user_id:
            return WrapResponse({"success": False, "error": "invalid-user_name"})

        list_ch = self.channels_list().json()

        for i in range(len(list_ch["channels"])):
            if list_ch["channels"][i]["name"] == channel:
                room_id = list_ch["channels"][i]["_id"]
                return self.call_api_post(
                    "channels.invite", roomId=room_id, userId=user_id, kwargs=kwargs
                )
        return WrapResponse({"success": False, "error": "invalid-channel-name"})

    def channels_invite(self, channel, user_names, **kwargs):
        """Adds an array of users to the channel."""
        invite_results = []
        for i in range(len(user_names)):
            output = self.__channels_invite_one_user(channel, user_names[i], **kwargs).json()
            
            result = {
                "success": output["success"],
                "user_name": user_names[i]
            }

            if not output.get("success", False):
                result["error"] = output.get("error", "unknown-error")

            invite_results.append(result)
        err = WrapResponse({"invite_results": invite_results})
        return err
            

    def channels_kick(self, channel, user_name, **kwargs): #Done
        """Removes a user from the channel."""
        list_us = self.users_list().json()
        user_id = None
        for i in range(len(list_us["users"])):
            if list_us["users"][i]["name"] == user_name:
                user_id = list_us["users"][i]["_id"]
                break

        if not user_id:
            return WrapResponse({"success": False, "error": "invalid-user_name"})    

        list_ch = self.channels_list().json()

        for i in range(len(list_ch["channels"])):
            if list_ch["channels"][i]["name"] == channel:
                room_id = list_ch["channels"][i]["_id"]
                return self.call_api_post(
                    "channels.kick", roomId=room_id, userId=user_id, kwargs=kwargs
                )
        return WrapResponse({"success": False, "error": "invalid-channel-name"})

    def channels_delete(self, channel, **kwargs): #Done
        """Delete a public channel."""
        return self.call_api_post(
            "channels.delete", roomName=channel, kwargs=kwargs
        )


    def channels_members(self, channel, **kwargs): #Done
        """Lists all channel users."""
        return self.call_api_get(
            "channels.members", roomName=channel, kwargs=kwargs
        )
    
    def __post_msg(self, text, user_name=None, channel=None, **kwargs):
        if user_name:
            list_us = self.users_list().json()
            user = None
            for i in range(len(list_us["users"])):
                if list_us["users"][i]["name"] == user_name:
                    user = "@" + list_us["users"][i]["username"]
                    break
            
            if not user:
                return WrapResponse({"success": False, "error": "invalid-user_name"})

            if text:
                return self.call_api_post(
                    "chat.postMessage", channel=user, text=text, kwargs=kwargs
                )
            return self.call_api_post("chat.postMessage", channel=user, kwargs=kwargs)
        
        if channel:
            if text:
                return self.call_api_post(
                    "chat.postMessage", channel=channel, text=text, kwargs=kwargs
                )
            return self.call_api_post(
                "chat.postMessage", channel=channel, kwargs=kwargs
            )
        return WrapResponse({"success": False, "error": "user_name or channel required"})
    
    def __rooms_upload(self, rid, file, **kwargs):
        """Post a message with attached file to a dedicated room."""
        files = {
            "file": (
                os.path.basename(file),
                open(file, "rb"),
                mimetypes.guess_type(file)[0],
            ),
        }
        return self.call_api_post(
            "rooms.upload/" + rid, kwargs=kwargs, use_json=False, files=files
        )

    def chat_post_message(self, text, user_name=None, channel=None, file=None, **kwargs): #Done
        """Posts a new chat message. Send messages to channels or users on your workspace.
        Example of using: output = client.chat_post_message(text="Hi!", user_name="Mike Chen")
        Example of using: output = client.chat_post_message(text="Hi!", channel="general")
        Example: output = client.chat_post_message(text="Hi! Look!", user_name="Mike Chen", file="/home/oleksandr/Pictures/ubuntu.jpg")
        Example: output = client.chat_post_message(text="Hi! Look!", channel="general", file="/home/oleksandr/Pictures/ubuntu.jpg")"""
        
        data = self.__post_msg(text, user_name=user_name, channel=channel, **kwargs)
        output = data.json()

        if file:
            if output.get("success"):
                rid = output["message"]["rid"]
                return self.__rooms_upload(rid, file)
            else:
                return data
        else:        
            return data

    def chat_list_messages(self, user_name=None, channel=None, lastUpdate="2023-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        if channel:
            list_ch = self.channels_list().json()
            for i in range(len(list_ch["channels"])):
                if list_ch["channels"][i]["name"] == channel:
                    room_id = list_ch["channels"][i]["_id"]
                    return self.call_api_get(
                        "chat.syncMessages", roomId=room_id, lastUpdate=lastUpdate, count=count, offset=offset
                    )
            return WrapResponse({"success": False, "error": "invalid-channel-name"})
        if user_name:
            list_us = self.users_list().json()
            user = None
            for i in range(len(list_us["users"])):
                if list_us["users"][i]["name"] == user_name:
                    user = list_us["users"][i]["username"]
                    break
            
            if not user:
                return WrapResponse({"success": False, "error": "invalid-user_name"})
            
            list_r = self.rooms_get().json()
            for i in range(len(list_r["update"])):
                if list_r["update"][i]["t"] == "d":
                    if list_r["update"][i]["usernames"][0] == user or list_r["update"][i]["usernames"][1] == user:
                        room_id = list_r["update"][i]["_id"]
                        return self.call_api_get(
                            "chat.syncMessages", roomId=room_id, lastUpdate=lastUpdate, count=count, offset=offset
                        )
            return WrapResponse({"success": False, "error": "No such room or no messages in a room you're trying to find"})
        return WrapResponse({"success": False, "error": "user_name or channel required"})
    
    def directory(self, query, **kwargs):
        """Search by users or channels on all server.
Field: text Recive type: string Description: The search term to be filtered Example: rocket
Field: type Receive type: string Description: It can be channels or users. When type is users you can send an additional workspace field, that can be local (default) or all. Workspace=all will work only if federation is enabled.
Example: users

Field: workspace
Receive type: string
Description: It can be local or all( if federation is enabled). It is local by default.
Example: local

Field: query Field is Required (will not query if not to fill it properly)
Description: The query to search the workspace directory. When type is users you can send an additional workspace field, that can be local (default) or all. Workspace=all will work only if federation is enabled.
Example: {"text": "rocket", "type": "users", "workspace": "local"}"""

        if isinstance(query, dict):
            query = str(query).replace("'", '"')

        return self.call_api_get("directory", query=query, kwargs=kwargs)

    def rooms_get(self, **kwargs):
        """Get all opened rooms for this user."""
        return self.call_api_get("rooms.get", kwargs=kwargs)
    
    def users_list(self, **kwargs):
        """All of the users and their information, limited to permissions."""
        return self.call_api_get("users.list", kwargs=kwargs)

    def users_create(self, email, name, password, username, **kwargs):
        """Creates a user"""
        return self.call_api_post(
            "users.create",
            email=email,
            name=name,
            password=password,
            username=username,
            kwargs=kwargs,
        )

    def users_delete(self, user_name, **kwargs):
        """Deletes a user"""
        list_us = self.users_list().json()
        user_id = None
        for i in range(len(list_us["users"])):
            if list_us["users"][i]["name"] == user_name:
                user_id = list_us["users"][i]["_id"]
                break
        if not user_id:
            return WrapResponse({"success": False, "error": "No such user_name"})
        return self.call_api_post("users.delete", userId=user_id, **kwargs)
    
    # def chat_post_message_with_image_url(self, text, channel, image_url=None, **kwargs):
    #     attachments = [
    #         {
    #         "image_url": image_url,
    #         }
    #     ]
        
    #     if image_url:
    #         if text:
    #             return self.call_api_post(
    #                 "chat.postMessage", channel=channel, text=text, attachments=attachments, kwargs=kwargs
    #             )
    #         return self.call_api_post(
    #             "chat.postMessage", channel=channel, attachments=attachments, kwargs=kwargs
    #         )
    #     else:
    #         if text:
    #             return self.call_api_post(
    #                 "chat.postMessage", channel=channel, text=text, kwargs=kwargs
    #             )
    #         return self.call_api_post(
    #             "chat.postMessage", channel=channel, kwargs=kwargs
    #         )