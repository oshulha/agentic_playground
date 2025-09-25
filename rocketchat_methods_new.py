# -*-coding:utf-8-*-
import json
import mimetypes
import os
from typing import Any, Dict, List, Literal, Optional

from .base import RocketChatBase

DEFAULT_LIMIT = 50

myid = "CZYWHd5bCmhj5YcFe"


class RocketChat(RocketChatBase):

    def __paginate(self, resource_fn, params=None, resource_type=None, resource_subtype=None, max_items=None, func_limit=DEFAULT_LIMIT, offset=0):
        """Pagination tool"""

        if params is None:
            params = {}

        params = {
            **params,
            "count": func_limit,
            "offset": offset,
        }

        if resource_fn == self.__chat_list_messages:
            resource_type = "result"
            resource_subtype = "updated"

            response = resource_fn(**params)
            items = response.get(resource_type, [])

            if resource_subtype and items:
                items = items.get(resource_subtype, [])

            results.extend(items)

            if max_items and len(results) >= max_items:
                results = results[:max_items]

            if offset:
                results = results[offset:]
            
            return results
            #Needs Another Paginate
        else:
            results = []
            total = None

            while True:
                response = resource_fn(**params)
                # with open("response.json", "w", encoding="utf-8") as f:
                #     f.write(json.dumps(response, ensure_ascii=False))
                items = response.get(resource_type, [])
                if resource_subtype and items:
                    items = items.get(resource_subtype, [])

                results.extend(items)

                if max_items and len(results) >= max_items:
                    return results[:max_items]

                total = len(items)
                params["offset"] += func_limit

                if total < func_limit:
                    break

            return results

    def __get_channel_by_name(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Get channel information (entire JSON) by its name.

        Returns:
            Optional[Dict[str, Any]]: The channel object if found; otherwise None.
        """
        list_ch = self.rocketchat_channels_list()

        for channel in list_ch["channels"]:
            if channel["name"] == channel_name:
                return channel

    def __get_user_by_name(self, user_name: Any) -> Optional[Dict[str, Any]]:
        """Get user information (entire json) by its username.

        Priority is by exact username match first, then by full name. A leading
        "@" in the provided user_name will be ignored.
        """
        list_us = self.rocketchat_users_list()
        found_user = None
        if user_name.startswith("@"):
            user_name = user_name[1:]
        for user in list_us["users"]:
            if user["username"] == user_name:
                return user
            if user["name"] == user_name:
                found_user = user
        return found_user

    def __post_msg(
        self,
        text: str,
        user_name: Optional[str] = None,
        channel: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Post a message to a channel or direct message.

        Exactly one of user_name or channel must be provided.
        """
        if not user_name and not channel:
            return {"success": False, "error": "user_name or channel required"}

        if user_name:
            user = self.__get_user_by_name(user_name)
            if not user:
                return {"success": False, "error": "invalid-user_name"}
            channel = "@" + user["username"]

        return self.call_api_post(
            "chat.postMessage", channel=channel, text=text, kwargs=kwargs
        ).json()

    def __rooms_upload(self, rid: str, file: str, **kwargs) -> Dict:
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

    def __channels_invite_one_user(
        self, channel: Any, user_name: str, **kwargs
    ) -> Dict:
        """Add a single user to a public channel.

        Args:
            channel (str): Channel name.
            user_name (str): Username of the user to invite.

        Returns:
            Dict: Rocket.Chat API response.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        channel = self.__get_channel_by_name(channel)

        if not channel:
            return {"success": False, "error": "invalid-channel-name"}

        return self.call_api_post(
            "channels.invite", roomId=channel["_id"], userId=user["_id"], kwargs=kwargs
        ).json()

    def __channels_list(self, offset=0, **kwargs):
        """Retrieves all of the channels from the server.

        Returns:
            Dict: A JSON-like dictionary containing the list of all channels and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get("channels.list", offset=offset, kwargs=kwargs).json()

    def rocketchat_channels_list(self, offset=0, count=None):
        """Retrieves all of the channels from the server.
        Args:
            count (int, optional): The maximum number of messages to return. Defaults to all. Be Cautious, if there is too many channels, output can be massive.
            offset (int, optional): The number of messages to skip (used for pagination). Defaults to 0.

        Returns:
            Dict: A JSON-like dictionary containing the list of all channels and metadata as provided by the Rocket.Chat API.
        """
        results = self.__paginate(
            resource_fn=self.__channels_list,
            resource_type="channels",
            func_limit=DEFAULT_LIMIT,
            offset=offset,
            max_items=count
        )
        return results

    def rocketchat_channels_add_role(
        self,
        channel: str,
        role: Literal["owner", "moderator", "leader"],
        user_name: str,
        **kwargs,
    ) -> Dict:
        """Assign a role (owner, moderator, or leader) to a user in a public channel.

        Args:
            channel (str): The name of the channel in which to assign the role.
            role (Literal["owner", "moderator", "leader"]): The role to assign to the user.
            user_name (str): The username of the user to assign the role to.

        Returns:
            dict: A JSON-like dictionary indicating success or failure, with details as provided by the Rocket.Chat API.

        Notes:
            The user must already be a member of the specified channel.
            If the user or channel cannot be found, the return value will include `"success": False` with an appropriate error message.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        channel = self.__get_channel_by_name(channel)

        if not channel:
            return {"success": False, "error": "invalid-channel-name"}

        if role == "leader":
            method = "addLeader"
        elif role == "owner":
            method = "addOwner"
        elif role == "moderator":
            method = "addModerator"
        else:
            return {
                "success": False,
                "error": "role must be owner, moderator or leader",
            }

        return self.call_api_post(
            f"channels.{method}",
            roomId=channel["_id"],
            userId=user["_id"],
            kwargs=kwargs,
        ).json()

    def rocketchat_channels_create(self, name: str, **kwargs) -> Dict:
        """Create a new public Rocket.Chat channel.

        Args:
            name (str): The name of the channel to create (e.g., "project_team").

        Returns:
            dict: A JSON-like dictionary containing details of the created channel and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_post("channels.create", name=name, kwargs=kwargs).json()

    def rocketchat_channels_invite(
        self, channel: str, user_names: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """Invite one or more users to a Rocket.Chat public channel.

        Args:
            channel (str): The name of the channel to which users will be invited.
            user_names (List[str]): A list of usernames of users to invite.

        Returns:
            List[Dict[str, Any]]: A list of per-user results with keys:
                - "success" (bool): Whether the invitation succeeded.
                - "user_name" (str): The username processed.
                - "error" (str, optional): Present when success is False.
        """
        invite_results = []
        for user_name in user_names:
            output = self.__channels_invite_one_user(
                channel=channel, user_name=user_name, **kwargs
            )
            result = {"success": output["success"], "user_name": user_name}
            if not output.get("success", False):
                result["error"] = output.get(
                    "error", "unknown-error"
                )  # Maybe It is better to say that somebody wasn't added
            invite_results.append(result)
        return invite_results

    def rocketchat_channels_kick(self, channel: str, user_name: str, **kwargs) -> Dict:
        """Remove a user from a Rocket.Chat public channel.

        Args:
            channel (str): The name of the channel from which to remove the user.
            user_name (str): Username of the user to remove.

        Returns:
            dict: A JSON-like dictionary indicating success or failure, with details as provided by the Rocket.Chat API.

        Notes:
            If the user or channel cannot be found, the return value will include `"success": False` with an appropriate error message.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        channel = self.__get_channel_by_name(channel)

        if not channel:
            return {"success": False, "error": "invalid-channel-name"}

        return self.call_api_post(
            "channels.kick", roomId=channel["_id"], userId=user["_id"], kwargs=kwargs
        ).json()

    def rocketchat_channels_delete(self, channel: str, **kwargs) -> Dict:
        """Delete a public Rocket.Chat channel.

        Args:
            channel (str): The name of the channel to delete (e.g., "general").

        Returns:
            dict: A JSON-like dictionary indicating success or failure, with details as provided by the Rocket.Chat API.

        Notes:
            Once deleted, the channel and its messages cannot be recovered.
        """
        return self.call_api_post(
            "channels.delete", roomName=channel, kwargs=kwargs
        ).json()

    def __channels_members(self, channel, offset=0, **kwargs): #Done
        """List all members of a Rocket.Chat channel.

        Args:
            channel (str): The name of the channel whose members should be listed (e.g., "general").

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get(
            "channels.members", roomName=channel, offset=offset, kwargs=kwargs
        ).json()

    def rocketchat_channels_members(self, channel, offset=0, count=None):
        """List all members of a Rocket.Chat channel.

        Args:
            channel (str): The name of the channel whose members should be listed (e.g., "general").

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        results = self.__paginate(
            resource_fn=self.__channels_members,
            params={"channel": channel},
            resource_type="members",
            func_limit=DEFAULT_LIMIT,
            offset=offset,
            max_items=count
        )
        return results

    def rocketchat_chat_post_message(
        self,
        text: str,
        user_name: Optional[str] = None,
        channel: Optional[str] = None,
        file: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Post a new chat message to a channel or direct chat.

        Args:
            text (str): The message text to send.
            user_name (str, optional): Username of the user to send a direct message to. Defaults to None.
            channel (str, optional): Channel name to send the message to (e.g., "general"). Defaults to None.
            file (str, optional): Path to a local file to upload along with the message. Defaults to None.

        Returns:
            dict: A JSON-like dictionary containing details of the posted message
            and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided.
        """
        output = self.__post_msg(text, user_name=user_name, channel=channel, **kwargs)

        if file:
            if output.get("success"):
                rid = output["message"]["rid"]
                return self.__rooms_upload(rid, file)
        return output

    def __chat_list_messages(self, user_name=None, channel=None, lastUpdate="2025-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        """Retrieve a list of messages from a Rocket.Chat channel or direct chat.

        Args:
            user_name (str, optional): The username of the user to fetch messages from. Defaults to None.
            channel (str, optional): The channel name from which to fetch messages. Defaults to None.
            lastUpdate (str, optional): Only messages updated after this time will be returned. It must strictly follow the format "YYYY-MM-DDTHH:MM:SS.000Z". Defaults to "2025-01-01T00:00:00.000Z".
            count (int, optional): The maximum number of messages to return.
            offset (int, optional): The number of messages to skip (used for pagination). Defaults to 0.

        Returns:
            dict: A JSON-like dictionary containing message objects and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided.
        """
        if not user_name and not channel:
            return {"success": False, "error": "user_name or channel required"}
        
        if channel:
            channel = self.__get_channel_by_name(channel)
            if not channel:
                return {"success": False, "error": "invalid-channel-name"}
            return self.call_api_get(
                "chat.syncMessages", roomId=channel["_id"], lastUpdate=lastUpdate, count=count, offset=offset
            ).json()
        
        if user_name:
            user = self.__get_user_by_name(user_name)
            if not user:
                return {"success": False, "error": "invalid-user_name"}
            
            output1 = self.call_api_get(
                "chat.syncMessages", roomId=myid + user["_id"], lastUpdate=lastUpdate, count=count, offset=offset
            ).json()

            output2 = self.call_api_get(
                "chat.syncMessages", roomId=user["_id"] + myid, lastUpdate=lastUpdate, count=count, offset=offset
            ).json()

            if output1.get("success"):
                return output1
            elif output2.get("success"):
                return output2
            else:
                return {"success": False, "error": f"Failed to find direct messages to {user_name}. There is may no direct message channel between you and {user_name}."}

    def rocketchat_chat_list_messages(self, user_name=None, channel=None, lastUpdate="2025-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        """Retrieve a list of messages from a Rocket.Chat channel or direct chat.

        Args:
            user_name (str, optional): The username of the user to fetch messages from. Defaults to None.
            channel (str, optional): The channel name from which to fetch messages. Defaults to None.
            lastUpdate (str, optional): Only messages updated after this time will be returned. It must strictly follow the format "YYYY-MM-DDTHH:MM:SS.000Z". Defaults to "2025-01-01T00:00:00.000Z".
            count (int, optional): The maximum number of messages to return.
            offset (int, optional): The number of messages to skip (used for pagination). Defaults to 0.

        Returns:
            dict: A JSON-like dictionary containing message objects and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided.
        """

        #Needs Another Paginate

        results = self.__paginate(
            resource_fn=self.__chat_list_messages,
            params={"user_name": user_name, "channel": channel, "lastUpdate": lastUpdate, "count": count, "offset": offset},
            resource_type="result",
            resource_subtype="updated",
            func_limit=DEFAULT_LIMIT
        )
        return results

    def __directory(self, query, offset=0, **kwargs):
        """Search by users or channels on all server."""

        return self.call_api_get("directory", query=query, offset=offset, kwargs=kwargs).json()

    def rocketchat_directory(
            self, text: str, type: Literal["users", "channels"], offset=0, count=None, **kwargs
        ) -> Dict:
            """Search for users or channels in the Rocket.Chat server directory.

            Args:
                text (str): The search text to look for in user names or channel names.
                type (Literal["users", "channels"]): The type of directory to search in.

            Returns:
                dict: A JSON-like dictionary containing the search results and metadata as provided by the Rocket.Chat API.
            """
            query = {"text": text, "type": type, "workspace": "local"}
            query = json.dumps(query)
            results = self.__paginate(
                resource_fn=self.__directory,
                params={"query": query},
                resource_type="result",
                func_limit=DEFAULT_LIMIT,
                offset=offset,
                max_items=count
            )
            return results
    
    def __users_list(self, offset=0, count=DEFAULT_LIMIT, **kwargs):
        """All of the users and their information, limited to permissions.

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get("users.list", offset=offset, count=count, kwargs=kwargs).json()

    def rocketchat_users_list(self, offset=0, count=None):
        """All of the users and their information, limited to permissions.

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        results = self.__paginate(
            resource_fn=self.__users_list,
            resource_type="users",
            func_limit=DEFAULT_LIMIT,
            offset=offset,
            max_items=count
        )
        return results
    
    def rocketchat_users_create(
        self, email: str, password: str, name: str, user_name: str, **kwargs
    ) -> Dict:
        """Create a new user in Rocket.Chat.

        Args:
            email (str): The email address of the new user.
            password (str): The password for the new user account.
            name (str): The full display name of the new user.
            user_name (str): The unique username for the new user.

        Returns:
            dict: A JSON-like dictionary containing details of the created user and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_post(
            "users.create",
            email=email,
            name=name,
            password=password,
            username=user_name,
            kwargs=kwargs,
        ).json()

    def rocketchat_users_delete(self, user_name: str, **kwargs) -> Dict:
        """Delete a user from Rocket.Chat.

        Args:
            user_name (str): The username of the user to delete.

        Returns:
            dict: A JSON-like dictionary indicating success or failure.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        return self.call_api_post("users.delete", userId=user["_id"], **kwargs).json()