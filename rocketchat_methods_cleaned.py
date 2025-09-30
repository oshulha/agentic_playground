# -*-coding:utf-8-*-
import json
import mimetypes
import os
from typing import Any, Dict, List, Literal, Optional

from langchain_core.tools import tool

from .base import RocketChatBase

DEFAULT_LIMIT = 50
USERS_LIMIT = 100


class RocketChat(RocketChatBase):
    def __get_channel_by_name(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Get channel information (entire JSON) by its name.

        Args:
            channel_name (str): The channel's name (without a leading #).

        Returns:
            Optional[Dict[str, Any]]: The channel object if found; otherwise None.
        """
        list_ch = self.rocketchat_channels_list(extra_fields=True)

        for channel_info in list_ch["channels"]:
            if channel_info["name"] == channel_name:
                return channel_info

    def __get_user_by_name(self, user_name: Any) -> Optional[Dict[str, Any]]:
        """Get user information (entire JSON) by username or full name.

        Priority is by exact username match first, then by full name. A leading
        "@" in the provided user_name will be ignored.

        Args:
            user_name (str): The user's username (with or without leading @) or the user's full name.

        Returns:
            Optional[Dict[str, Any]]: The user object if found; otherwise None.
        """
        list_us = self.rocketchat_users_list(extra_fields=True)
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
        channel_name: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Post a message to a channel or direct message.

        At least one of `user_name` or `channel_name` must be provided. If both are
        provided, `user_name` takes precedence and a direct message will be sent
        to that user.

        Args:
            text (str): The message text to send.
            user_name (Optional[str]): Username for a direct message target.
            channel_name (Optional[str]): Channel name (e.g., "general").

        Returns:
            Dict: Rocket.Chat API response JSON.
        """
        if not user_name and not channel_name:
            return {"success": False, "error": "user_name or channel_name required"}

        if user_name:
            user = self.__get_user_by_name(user_name)
            if not user:
                return {"success": False, "error": "invalid-user_name"}
            channel_name = "@" + user["username"]

        return self.call_api_post(
            "chat.postMessage", channel=channel_name, text=text
        ).json()

    def __rooms_upload(self, rid: str, file: str) -> Dict:
        """Upload a file to a room.

        Args:
            rid (str): The room ID to upload the file to.
            file (str): Path to the local file to upload. The content type is
                inferred via ``mimetypes.guess_type``.

        Returns:
            Dict: Rocket.Chat API response JSON for the upload.
        """
        files = {
            "file": (
                os.path.basename(file),
                open(file, "rb"),
                mimetypes.guess_type(file)[0],
            ),
        }
        return self.call_api_post(
            "rooms.upload/" + rid, use_json=False, files=files
        ).json()

    def __channels_invite_one_user(
        self, channel_name: Any, user_name: str
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

        channel_info = self.__get_channel_by_name(channel_name)

        if not channel_info:
            return {"success": False, "error": "invalid-channel-name"}

        return self.call_api_post(
            "channels.invite", roomId=channel_info["_id"], userId=user["_id"]
        ).json()

    def __channels_kick_one_user(self, channel_name: str, user_name: str) -> Dict:
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

        channel_info = self.__get_channel_by_name(channel_name)

        if not channel_info:
            return {"success": False, "error": "invalid-channel-name"}

        return self.call_api_post(
            "channels.kick",
            roomId=channel_info["_id"],
            userId=user["_id"]
        ).json()

    def __clean_channels_list(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's channels.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """

        def clean_channel(channel_info: dict) -> dict:
            cleaned = {}

            if "name" in channel_info:
                cleaned["name"] = channel_info["name"]

            if "msgs" in channel_info:
                cleaned["msgs"] = channel_info["msgs"]
            if "usersCount" in channel_info:
                cleaned["usersCount"] = channel_info["usersCount"]

            if "description" in channel_info:
                cleaned["description"] = channel_info["description"]

            return cleaned

        # If output has "channels" list
        if "channels" in output:
            output["channels"] = [clean_channel(c) for c in output["channels"]]

        return output

    def rocketchat_channels_list(
        self, count: int = DEFAULT_LIMIT, offset: int = 0, extra_fields : bool = False
    ) -> Dict:
        """Retrieve channels from the server.

        Args:
            count (int, optional): Maximum number of channels to return. Defaults to DEFAULT_LIMIT.
            offset (int, optional): Number of channels to skip (pagination). Defaults to 0.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            Dict: A JSON-like dictionary containing the list of channels and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_get(
            "channels.list", count=count, offset=offset
        ).json()

        if extra_fields and output["success"]:
            return output
        else:
            return self.__clean_channels_list(output)

    def rocketchat_channel_add_role(
        self,
        channel_name: str,
        role: Literal["owner", "moderator", "leader"],
        user_name: str
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

        channel_info = self.__get_channel_by_name(channel_name)

        if not channel_info:
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
            roomId=channel_info["_id"],
            userId=user["_id"]
        ).json()

    def rocketchat_channel_create(self, channel_name: str, extra_fields: bool = False) -> Dict:
        """Create a new public Rocket.Chat channel.

        Args:
            channel_name (str): The name of the channel to create (e.g., "project_team").
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing details of the created channel and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_post("channels.create", name=channel_name).json()

        if extra_fields and output["success"]:
            return output
        else:
            #Clean information about a channel that was created
            cleaned = {}
            cleaned["success"] = output["success"]
            return cleaned

    def rocketchat_channel_invite(
        self, channel_name: str, user_names: List[str]
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
                channel_name=channel_name, user_name=user_name
            )
            result = {"success": output["success"], "user_name": user_name}
            if not output.get("success", False):
                result["error"] = output.get(
                    "error", "unknown-error"
                )  # Maybe It is better to say that somebody wasn't added
            invite_results.append(result)
        return invite_results

    def rocketchat_channel_kick(
        self, channel_name: str, user_names: List[str]
    ) -> List[Dict[str, Any]]:
        """Remove one or more users from a Rocket.Chat public channel.

        Args:
            channel (str): The name of the channel from which users will be removed.
            user_names (List[str]): A list of usernames of users to remove.

        Returns:
            List[Dict[str, Any]]: A list of per-user results with keys:
                - "success" (bool): Whether the removal succeeded.
                - "user_name" (str): The username processed.
                - "error" (str, optional): Present when success is False.
        """
        kick_results = []
        for user_name in user_names:
            output = self.__channels_kick_one_user(
                channel_name=channel_name, user_name=user_name
            )
            result = {"success": output["success"], "user_name": user_name}
            if not output.get("success", False):
                result["error"] = output.get("error", "unknown-error")
            kick_results.append(result)
        return kick_results

    def rocketchat_channel_delete(self, channel_name: str) -> Dict:
        """Delete a public Rocket.Chat channel.

        Args:
            channel (str): The name of the channel to delete (e.g., "general").

        Returns:
            dict: A JSON-like dictionary indicating success or failure, with details as provided by the Rocket.Chat API.

        Notes:
            Once deleted, the channel and its messages cannot be recovered.
        """
        return self.call_api_post(
            "channels.delete", roomName=channel_name
        ).json()
    
    def __clean_channel_members(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's channels.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """

        def clean_member(member_info: dict) -> dict:
            cleaned = {}

            if "name" in member_info:
                cleaned["name"] = member_info["name"]

            if "username" in member_info:
                cleaned["username"] = member_info["username"]

            return cleaned

        # If output has "members" list
        if "members" in output:
            output["members"] = [clean_member(c) for c in output["members"]]

        return output

    def rocketchat_channel_members(
        self, channel_name: str, count: int = USERS_LIMIT, offset: int = 0, extra_fields: bool = False
    ) -> Dict:
        """List members of a Rocket.Chat channel.

        Args:
            channel (str): The name of the channel whose members should be listed (e.g., "general").
            count (int, optional): Maximum number of members to return. Defaults to USERS_LIMIT.
            offset (int, optional): Number of members to skip (pagination). Defaults to 0.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_get(
            "channels.members",
            roomName=channel_name,
            count=count,
            offset=offset
        ).json()

        if extra_fields and output["success"]:
            return output
        else:
            return self.__clean_channel_members(output)

    def __clean_chat_post_message(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's channels.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """

        cleaned = {}
        if "messages" in output:
            cleaned["messages"] = output["message"].get("msg", [])
        if "channel" in output:
            cleaned["channel"] = output["channel"]
        if "success" in output:
            cleaned["success"] = output["success"]
        if "message" in output:
            if "file" in output["message"]: 
                cleaned["file"] = {}
                cleaned["file"]["name"] = output["message"]["file"]["name"]
                cleaned["file"]["type"] = output["message"]["file"]["type"]

        return cleaned

    def rocketchat_chat_post_message(
        self,
        text: str,
        user_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        file: Optional[str] = None,
        extra_fields: bool = False
    ) -> Dict:
        """Post a new chat message to a channel or direct chat.

        Args:
            text (str): The message text to send.
            user_name (str, optional): Username of the user to send a direct message to. Defaults to None.
            channel (str, optional): Channel name to send the message to (e.g., "general"). Defaults to None.
            file (str, optional): Path to a local file to upload along with the message. Defaults to None.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing details of the posted message
            and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided. If both are provided, `user_name` takes precedence and a direct message will be sent.
            When `file` is provided and the message is posted successfully, the response will be that of the file upload (rooms.upload).
        """
        output = self.__post_msg(text, user_name=user_name, channel_name=channel_name)

        if file:
            if output.get("success"):
                rid = output["message"]["rid"]
                output = self.__rooms_upload(rid, file)
            
        if extra_fields and output["success"]:
            return output
        else: 
            return self.__clean_chat_post_message(output)
    
    def __clean_chat_list_messages(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's channels.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """

        def clean_messages(message_info: dict) -> dict:
            cleaned = {}

            if "msg" in message_info:
                cleaned["msg"] = message_info["msg"]

            if "ts" in message_info:
                cleaned["timestamp"] = message_info["ts"]

            if "u" in message_info:
                cleaned["sender"] = {}
                if "username" in message_info["u"]:
                    cleaned["sender"]["username"] = message_info["u"]["username"]
                if "name" in message_info["u"]:
                    cleaned["sender"]["name"] = message_info["u"]["name"]

            return cleaned

        # If output has "members" list
        if "result" in output and "updated" in output["result"]:
            output["result"]["updated"] = [clean_messages(c) for c in output["result"]["updated"]]

        if "result" in output and "deleted" in output["result"]:
            output["result"]["deleted"] = {}

        return output
            
    def rocketchat_chat_list_messages(
        self,
        user_name: Optional[str] = None,
        channel_name: Optional[str] = None,
        lastUpdate: str = "2025-01-01T00:00:00.000Z",
        count: int = DEFAULT_LIMIT,
        offset: int = 0,
        extra_fields: bool = False
    ) -> Dict:
        """Retrieve a list of messages from a Rocket.Chat channel or direct chat.

        Args:
            user_name (str, optional): The username of the user to fetch messages from. Defaults to None.
            channel (str, optional): The channel name from which to fetch messages. Defaults to None.
            lastUpdate (str, optional): Only messages updated after this time will be returned. It must strictly follow the format "YYYY-MM-DDTHH:MM:SS.000Z". Defaults to "2025-01-01T00:00:00.000Z".
            count (int, optional): The maximum number of messages to return.
            offset (int, optional): The number of messages to skip (used for pagination). Defaults to 0.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing message objects and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided.
        """
        if not user_name and not channel_name:
            return {"success": False, "error": "user_name or channel required"}

        # Resolve roomId either from a channel name or a direct room with a user
        room_id = None
        if channel_name:
            channel_info = self.__get_channel_by_name(channel_name)
            if not channel_info:
                return {"success": False, "error": "invalid-channel-name"}
            room_id = channel_info.get("_id")
        else:
            user_info = self.__get_user_by_name(user_name)
            if not user_info:
                return {"success": False, "error": "invalid-user_name"}

            username = user_info["username"]
            dms_resp = self.rocketchat_dms_list(extra_fields=True)
            dms_list = dms_resp.get("ims", [])
            for dm in dms_list:
                if username in dm.get("usernames", []):
                    room_id = dm.get("_id")
                    break

        if not room_id:
            return {
                "success": False,
                "error": "No such room or no messages in a room you're trying to find",
            }

        response = self.call_api_get(
            "chat.syncMessages",
            roomId=room_id,
            lastUpdate=lastUpdate,
            count=count,
            offset=offset,
        ).json()
        response["result"]["updated"] = response["result"]["updated"][
            offset : offset + count
        ]
        response["result"]["deleted"] = response["result"]["deleted"][
            offset : offset + count
        ]

        if extra_fields:
            return response
        else:
            return self.__clean_chat_list_messages(response)


    def rocketchat_directory(
        self,
        text: str,
        type: Literal["users", "channels"],
        count: int = DEFAULT_LIMIT,
        offset: int = 0
    ) -> Dict:
        """Search for users or channels in the Rocket.Chat server directory.

        Args:
            text (str): The search text to look for in user names or channel names.
            type (Literal["users", "channels"]): The type of directory to search in.
            count (int, optional): Maximum number of results to return. Defaults to DEFAULT_LIMIT.
            offset (int, optional): Number of results to skip (pagination). Defaults to 0.

        Returns:
            dict: A JSON-like dictionary containing the search results and metadata as provided by the Rocket.Chat API.
        """
        query = {"text": text, "type": type, "workspace": "local"}
        query = json.dumps(query)
        return self.call_api_get(
            "directory", query=query, count=count, offset=offset
        ).json()

    def __clean_users_list(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's users.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """
        def clean_user(user_info: dict) -> dict:
            cleaned = {}

            if "name" in user_info:
                cleaned["name"] = user_info["name"]

            if "username" in user_info:
                cleaned["username"] = user_info["username"]
            if "roles" in user_info:
                cleaned["roles"] = user_info["roles"]

            return cleaned

        if "users" in output:
            output["users"] = [clean_user(user) for user in output["users"]]

        return output

    def rocketchat_users_list(
        self, count: int = USERS_LIMIT, offset: int = 0, extra_fields: bool = False
    ) -> Dict:
        """Retrieve users and their information (permission-limited view).

        Args:
            count (int, optional): Maximum number of users to return. Defaults to USERS_LIMIT.
            offset (int, optional): Number of users to skip (pagination). Defaults to 0.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing the list of users and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_get(
            "users.list", count=count, offset=offset
        ).json()

        if extra_fields:
            return output
        else:
            return self.__clean_users_list(output)
        
    def __clean_dms_list(self, output: dict) -> dict:
        """
        Clean the JSON returned by Rocket.Chat's users.list API.
        Removes unnecessary fields and renames some keys for clarity.
        """
        def clean_dm(user_info: dict) -> dict:
            cleaned = {}

            if "usernames" in user_info:
                cleaned["usernames"] = user_info["usernames"]
            if "msgs" in user_info:
                cleaned["msgs"] = user_info["msgs"]

            return cleaned

        if "ims" in output:
            output["ims"] = [clean_dm(user) for user in output["ims"]]

        return output
        
    def rocketchat_dms_list(
        self, count: int = USERS_LIMIT, offset: int = 0, extra_fields: bool = False
    ) -> Dict:
        """Retrieve users and their information (permission-limited view).

        Args:
            count (int, optional): Maximum number of users to return. Defaults to USERS_LIMIT.
            offset (int, optional): Number of users to skip (pagination). Defaults to 0.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.

        Returns:
            dict: A JSON-like dictionary containing the list of users and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_get(
            "dm.list", count=count, offset=offset
        ).json()

        if extra_fields:
            return output
        else:
            return self.__clean_dms_list(output)

    def rocketchat_user_create(
        self, email: str, password: str, name: str, user_name: str, extra_fields: bool = False
    ) -> Dict:
        """Create a new user in Rocket.Chat.

        Args:
            email (str): The email address of the new user.
            password (str): The password for the new user account.
            name (str): The full display name of the new user.
            user_name (str): The unique username for the new user.
            extra_fields (bool, optional): If True, includes additional information about each channel as raw JSON from the RocketChat API, which is often unnecessary. Defaults to False.


        Returns:
            dict: A JSON-like dictionary containing details of the created user and metadata as provided by the Rocket.Chat API.
        """
        output = self.call_api_post(
            "users.create",
            email=email,
            name=name,
            password=password,
            username=user_name
        ).json()

        if extra_fields:
            return output
        else:
            cleaned = {}
            cleaned["success"] = output["success"]
            return cleaned


    def rocketchat_user_delete(self, user_name: str) -> Dict:
        """Delete a user from Rocket.Chat.

        Args:
            user_name (str): The username of the user to delete.

        Returns:
            dict: A JSON-like dictionary indicating success or failure.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        return self.call_api_post("users.delete", userId=user["_id"]).json()