# -*-coding:utf-8-*-
import mimetypes
import os
from base import RocketChatBase
from typing import Literal
import json

DEFAULT_LIMIT = 50
USERS_LIMIT = 100

myid = "CZYWHd5bCmhj5YcFe"

class RocketChat(RocketChatBase):
    def __paginate(self, resource_fn, params=None, resource_type=None, resource_subtype=None, max_items=None, limit=100):
        if params is None:
            params = {}

        params = {
            **params,
            "count": limit,
            "offset": 0,
        }

        results = []
        total = None

        while True:
            response = resource_fn(**params)
            with open("response.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(response, ensure_ascii=False))
            items = response.get(resource_type, [])
            if resource_subtype and items:
                items = items.get(resource_subtype, [])

            results.extend(items)

            if max_items and len(results) >= max_items:
                return results[:max_items]

            total = len(items)
            params["offset"] += limit

            if total < limit:
                break

        return results

    def __channels_list(self, offset=0, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.call_api_get("channels.list", offset=offset, kwargs=kwargs).json()

    def rocketchat_channels_list(self):
        """Retrieves all of the channels from the server."""
        results = self.__paginate(
            resource_fn=self.__channels_list,
            resource_type="channels",
            limit=50
        )
        return results

    def rocketchat_channels_add_role(self, channel, user_name, role: Literal["owner", "moderator", "leader"], **kwargs): #Done
        """Gives the role of moderator/owner/leader for a user in the current channel. For this command user needs to be in a room/channel """
        list_us = self.rocketchat_users_list()
        user_id = None
        for i in range(len(list_us)):
            if list_us[i]["name"] == user_name:
                user_id = list_us[i]["_id"]
                break
        
        if not user_id:
            return {"success": False, "error": "invalid-user_name"}

        list_ch = self.rocketchat_channels_list()

        for i in range(len(list_ch)):
            if list_ch[i]["name"] == channel:
                room_id = list_ch[i]["_id"]
                if role == "leader":
                    return self.call_api_post(
                        "channels.addLeader", roomId=room_id, userId=user_id, kwargs=kwargs
                    ).json()
                elif role == "owner":
                    return self.call_api_post(
                        "channels.addOwner", roomId=room_id, userId=user_id, kwargs=kwargs
                    ).json()
                elif role == "moderator":
                    return self.call_api_post(
                        "channels.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
                    ).json()
                else:
                    return {
                        "success": False,
                        "error": "role must be owner, moderator or leader",
                    }
        return {"success": False, "error": "invalid-channel-name"}

    def rocketchat_channels_create(self, name, **kwargs):
        """Creates a new public channel, optionally including users."""
        return self.call_api_post("channels.create", name=name, kwargs=kwargs).json()

    def __channels_invite_one_user(self, channel, user_name, **kwargs): #Done
        """Adds a user to the channel."""
        list_us = self.rocketchat_users_list()
        user_id = None
        with open("users_list.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(list_us, ensure_ascii=False))
        size = len(list_us)
        for i in range(size):
            name = list_us[i]["name"]
            if name == user_name:
                user_id = list_us[i]["_id"]
                break

        if not user_id:
            return {"success": False, "error": "invalid-user_name"}

        list_ch = self.rocketchat_channels_list()

        for i in range(len(list_ch)):
            if list_ch[i]["name"] == channel:
                room_id = list_ch[i]["_id"]
                return self.call_api_post(
                    "channels.invite", roomId=room_id, userId=user_id, kwargs=kwargs
                ).json()
        return {"success": False, "error": "invalid-channel-name"}

    def rocketchat_channels_invite(self, channel, user_names, **kwargs):
        """Adds an array of users to the channel."""
        invite_results = []
        for i in range(len(user_names)):
            output = self.__channels_invite_one_user(channel, user_names[i], **kwargs)

            result = {
                "success": output["success"],
                "user_name": user_names[i]
            }

            if not output.get("success", False):
                result["error"] = output.get("error", "unknown-error")

            invite_results.append(result)
        err = {"invite_results": invite_results}
        return err
            

    def rocketchat_channels_kick(self, channel, user_name, **kwargs): #Done
        """Removes a user from the channel."""
        list_us = self.rocketchat_users_list()
        user_id = None
        for i in range(len(list_us)):
            if list_us[i]["name"] == user_name:
                user_id = list_us[i]["_id"]
                break

        if not user_id:
            return {"success": False, "error": "invalid-user_name"}

        list_ch = self.rocketchat_channels_list()

        for i in range(len(list_ch)):
            if list_ch[i]["name"] == channel:
                room_id = list_ch[i]["_id"]
                return self.call_api_post(
                    "channels.kick", roomId=room_id, userId=user_id, kwargs=kwargs
                ).json()
        return {"success": False, "error": "invalid-channel-name"}

    def rocketchat_channels_delete(self, channel, **kwargs): #Done
        """Delete a public channel."""
        return self.call_api_post(
            "channels.delete", roomName=channel, kwargs=kwargs
        ).json()


    def __channels_members(self, channel, offset=0, **kwargs): #Done
        """Lists all channel users."""
        return self.call_api_get(
            "channels.members", roomName=channel, offset=offset, kwargs=kwargs
        ).json()

    def rocketchat_channels_members(self, channel):
        """Lists all channel users."""
        results = self.__paginate(
            resource_fn=self.__channels_members,
            params={"channel": channel},
            resource_type="members",
            limit=50
        )
        return results
    
    def __post_msg(self, text, user_name=None, channel=None, **kwargs):
        if user_name:
            list_us = self.rocketchat_users_list()
            user = None
            for i in range(len(list_us)):
                if list_us[i]["name"] == user_name:
                    user = "@" + list_us[i]["username"]
                    break
            
            if not user:
                return {"success": False, "error": "invalid-user_name"}

            if text and text != "":
                return self.call_api_post(
                    "chat.postMessage", channel=user, text=text, kwargs=kwargs
                ).json()
            return self.call_api_post("chat.postMessage", channel=user, kwargs=kwargs).json()
        
        if channel:
            if text and text != "":
                return self.call_api_post(
                    "chat.postMessage", channel=channel, text=text, kwargs=kwargs
                ).json()
            return self.call_api_post(
                "chat.postMessage", channel=channel, kwargs=kwargs
            ).json()
        return {"success": False, "error": "user_name or channel required"}

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
        ).json()

    def rocketchat_chat_post_message(self, text, user_name=None, channel=None, file=None, **kwargs): #Done
        """Posts a new chat message. Send messages to channels or users on your workspace. Optionally can attach files to the message.
        Example of using: output = client.chat_post_message(text="Hi!", user_name="Mike Chen")
        Example of using: output = client.chat_post_message(text="Hi!", channel="general")
        Example: output = client.chat_post_message(text="Hi! Look!", user_name="Mike Chen", file="/home/oleksandr/Pictures/ubuntu.jpg")
        Example: output = client.chat_post_message(text="Hi! Look!", channel="general", file="/home/oleksandr/Pictures/ubuntu.jpg")"""
        
        output = self.__post_msg(text, user_name=user_name, channel=channel, **kwargs)

        if file:
            if output.get("success"):
                rid = output["message"]["rid"]
                return self.__rooms_upload(rid, file)
            else:
                return output
        else:
            return output

    def __chat_list_messages(self, user_name=None, channel=None, lastUpdate="2025-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        if channel:
            list_ch = self.rocketchat_channels_list()
            for i in range(len(list_ch)):
                if list_ch[i]["name"] == channel:
                    room_id = list_ch[i]["_id"]
                    return self.call_api_get(
                        "chat.syncMessages", roomId=room_id, lastUpdate=lastUpdate, count=count, offset=offset
                    ).json()
            return {"success": False, "error": "invalid-channel-name"}
        if user_name:
            list_us = self.rocketchat_users_list()
            userid = None
            for i in range(len(list_us)):
                if list_us[i]["name"] == user_name:
                    userid = list_us[i]["_id"]
                    break
            
            if not userid:
                return {"success": False, "error": "invalid-user_name"}

            output1 = self.call_api_get(
                "chat.syncMessages", roomId=myid + userid, lastUpdate=lastUpdate, count=count, offset=offset
            ).json()

            output2 = self.call_api_get(
                "chat.syncMessages", roomId=userid + myid, lastUpdate=lastUpdate, count=count, offset=offset
            ).json()

            if output1.get("success"):
                return output1
            elif output2.get("success"):
                return output2
            else:
                return {"success": False, "error": f"Failed to find direct messages to {user_name}. There is may no direct message channel between you and {user_name}."}

            # list_r = self.rocketchat_rooms_get()#
            # for i in range(len(list_r["update"])):
            #     if list_r["update"][i]["t"] == "d":
            #         if list_r["update"][i]["usernames"][0] == user or list_r["update"][i]["usernames"][1] == user:
            #             room_id = list_r["update"][i]["_id"]
            #             return self.call_api_get(
            #                 "chat.syncMessages", roomId=room_id, lastUpdate=lastUpdate, count=count, offset=offset
            #             ).json()
            # return {"success": False, "error": "No such room or no messages in a room you're trying to find"}
        return {"success": False, "error": "user_name or channel required"}

    def rocketchat_chat_list_messages(self, user_name=None, channel=None, lastUpdate="2025-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        """Lists all messages in a chat."""
        results = self.__paginate(
            resource_fn=self.__chat_list_messages,
            params={"user_name": user_name, "channel": channel, "lastUpdate": lastUpdate, "count": count, "offset": offset},
            resource_type="result",
            resource_subtype="updated",
            limit=50
        )
        return results

    def __directory(self, query, offset=0, **kwargs):
        """Search by users or channels on all server."""

        if isinstance(query, dict):
            query = str(query).replace("'", '"')

        return self.call_api_get("directory", query=query, offset=offset, kwargs=kwargs).json()

    def rocketchat_directory(self, query: dict[str, str]):
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
        results = self.__paginate(
            resource_fn=self.__directory,
            params={"query": query},
            resource_type="result",
            limit=50
        )
        return results

    def rocketchat_rooms_get(self, **kwargs):
        """Get all opened rooms for this user."""
        return self.call_api_get("rooms.get", kwargs=kwargs).json()

    def __paginated_rocketchat_rooms_get(self): #Do not work -- No offset parameter for this method in RocketChat API 
        all_rooms = self.__paginate(
            resource_fn=self.__rooms_get,
            resource_type="update",
            limit=50
        )
        return all_rooms
    
    def __users_list(self, offset=0, **kwargs):
        """All of the users and their information, limited to permissions."""
        return self.call_api_get("users.list", count=USERS_LIMIT, offset=offset, kwargs=kwargs).json()

    def rocketchat_users_list(self):
        """All of the users and their information, limited to permissions."""
        all_users = self.__paginate(
            resource_fn=self.__users_list,
            resource_type="users",
            limit=50
        )
        return all_users

    def rocketchat_users_create(self, email, name, password, username, **kwargs):
        """Creates a user"""
        return self.call_api_post(
            "users.create",
            email=email,
            name=name,
            password=password,
            username=username,
            kwargs=kwargs,
        ).json()

    def rocketchat_users_delete(self, user_name, **kwargs):
        """Deletes a user"""
        list_us = self.rocketchat_users_list()
        user_id = None
        for i in range(len(list_us)):
            if list_us[i]["name"] == user_name:
                user_id = list_us[i]["_id"]
                break
        if not user_id:
            return {"success": False, "error": "No such user_name"}
        return self.call_api_post("users.delete", userId=user_id, **kwargs).json()