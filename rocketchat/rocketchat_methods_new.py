# -*-coding:utf-8-*-
import json
import mimetypes
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from base import RocketChatBase

DEFAULT_LIMIT = 50
USERS_LIMIT = 100


class RocketChat(RocketChatBase):
    CHAT_ACTIVITY_TIME: Dict[str, datetime] = {}  # Required for wait_for_message tool.
    # possible pairs: channel-datetime, @username-datetime

    def __get_channel_by_name(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Get channel information (entire JSON) by its name.

        Args:
            channel_name (str): The channel's name (without a leading #).

        Returns:
            Optional[Dict[str, Any]]: The channel object if found; otherwise None.
        """
        list_ch = self.rocketchat_channels_list()

        for channel in list_ch["channels"]:
            if channel["name"] == channel_name:
                return channel

    def __get_user_by_name(self, user_name: Any) -> Optional[Dict[str, Any]]:
        """Get user information (entire JSON) by username or full name.

        Priority is by exact username match first, then by full name. A leading
        "@" in the provided user_name will be ignored.

        Args:
            user_name (str): The user's username (with or without leading @) or the user's full name or even the user's userId.

        Returns:
            Optional[Dict[str, Any]]: The user object if found; otherwise None.
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
            if user["_id"] == user_name:
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

        At least one of `user_name` or `channel` must be provided. If both are
        provided, `user_name` takes precedence and a direct message will be sent
        to that user.

        Args:
            text (str): The message text to send.
            user_name (Optional[str]): Username for a direct message target.
            channel (Optional[str]): Channel name (e.g., "general").

        Returns:
            Dict: Rocket.Chat API response JSON.
        """
        if not user_name and not channel:
            return {"success": False, "error": "user_name or channel required"}

        if user_name:
            user = self.__get_user_by_name(user_name)
            if not user:
                return {"success": False, "error": "invalid-user_name"}
            channel = "@" + user["username"]

        response = self.call_api_post(
            "chat.postMessage", channel=channel, text=text, kwargs=kwargs
        ).json()
        message_time = response.get("message", {}).get("ts")
        if message_time:
            message_time = datetime.fromisoformat(message_time)
        else:
            message_time = datetime.now(UTC)
        message_time += timedelta(milliseconds=500)
        self.CHAT_ACTIVITY_TIME[str(channel)] = message_time

        return response

    def __rooms_upload(self, rid: str, file: str, **kwargs) -> Dict:
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

    def __channels_kick_one_user(self, channel: str, user_name: str, **kwargs) -> Dict:
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

        channel_info = self.__get_channel_by_name(channel)

        if not channel_info:
            return {"success": False, "error": "invalid-channel-name"}

        return self.call_api_post(
            "channels.kick",
            roomId=channel_info["_id"],
            userId=user["_id"],
            kwargs=kwargs,
        ).json()

    def rocketchat_channels_list(
        self, count: int = DEFAULT_LIMIT, offset: int = 0, **kwargs
    ) -> Dict:
        """Retrieve channels from the server.

        Args:
            count (int, optional): Maximum number of channels to return. Defaults to DEFAULT_LIMIT.
            offset (int, optional): Number of channels to skip (pagination). Defaults to 0.

        Returns:
            Dict: A JSON-like dictionary containing the list of channels and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get(
            "channels.list", count=count, offset=offset, kwargs=kwargs
        ).json()

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
            user_name (str): The username of the user (or full name of user or userId of user) to assign the role to.

        Returns:
            dict: A JSON-like dictionary indicating success or failure, with details as provided by the Rocket.Chat API.

        Notes:
            The user must already be a member of the specified channel.
            If the user or channel cannot be found, the return value will include `"success": False` with an appropriate error message.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        channel_info = self.__get_channel_by_name(channel)

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
            user_names (List[str]): A list of usernames (or full names or userIds) of users to invite.

        Returns:
            dict: A JSON-like dictionary that includes: 
                invite_results: A list of per-user results with keys: 
                    - "success" (bool): Whether the invitation succeeded. 
                    - "user_name" (str): The username processed. 
                    - "error" (str, optional): Present when success is False. 
                updated_member_list: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
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
                )
            invite_results.append(result)
        
        member_list = self.rocketchat_channels_members(channel=channel)
        dict = {"invite_results" : invite_results, "updated_member_list" : member_list}
        return dict

    def rocketchat_channels_kick(
        self, channel: str, user_names: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """Remove one or more users from a Rocket.Chat public channel.

        Args:
            channel (str): The name of the channel from which users will be removed.
            user_names (List[str]): A list of usernames (or full names or userIds) of users to remove.

        Returns:
            dict: A JSON-like dictionary that includes: 
                kick_results: A list of per-user results with keys: 
                    - "success" (bool): Whether the invitation succeeded. 
                    - "user_name" (str): The username processed. 
                    - "error" (str, optional): Present when success is False. 
                updated_member_list: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        kick_results = []
        for user_name in user_names:
            output = self.__channels_kick_one_user(
                channel=channel, user_name=user_name, **kwargs
            )
            result = {"success": output["success"], "user_name": user_name}
            if not output.get("success", False):
                result["error"] = output.get("error", "unknown-error")
            kick_results.append(result)
        
        member_list = self.rocketchat_channels_members(channel=channel)
        dict = {"kick_results" : kick_results, "updated_member_list" : member_list}
        return dict

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

    def rocketchat_channels_members(
        self, channel: str, count: int = USERS_LIMIT, offset: int = 0, **kwargs
    ) -> Dict:
        """List members of a Rocket.Chat channel.

        Args:
            channel (str): The name of the channel whose members should be listed (e.g., "general").
            count (int, optional): Maximum number of members to return. Defaults to USERS_LIMIT.
            offset (int, optional): Number of members to skip (pagination). Defaults to 0.

        Returns:
            dict: A JSON-like dictionary containing the list of channel members and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get(
            "channels.members",
            roomName=channel,
            count=count,
            offset=offset,
            kwargs=kwargs,
        ).json()

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
            user_name (str, optional): Username of the user (or full name of user or userId of user) to send a direct message to. Defaults to None.
            channel (str, optional): Channel name to send the message to (e.g., "general"). Defaults to None.
            file (str, optional): Path to a local file to upload along with the message. Defaults to None.

        Returns:
            dict: A JSON-like dictionary containing details of the posted message
            and metadata as provided by the Rocket.Chat API.

        Notes:
            Either `user_name` or `channel` must be provided. If both are provided, `user_name` takes precedence and a direct message will be sent.
            When `file` is provided and the message is posted successfully, the response will be that of the file upload (rooms.upload).
        """
        output = self.__post_msg(text, user_name=user_name, channel=channel, **kwargs)

        if file:
            if output.get("success"):
                rid = output["message"]["rid"]
                return self.__rooms_upload(rid, file)
        return output

    def rocketchat_wait_for_message(
        self, user_name: Optional[str] = None, channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Wait for a new message in a Rocket.Chat channel / direct message. Only use this tool if you need a response from the user to continue with the task.

        Args:
            user_name (str, optional): The username of the user (or full name of user or userId of user) to wait for a message from (in direct messages).
            channel (str, optional): The name of the channel to wait for a message in.

        Returns:
            Dict: status message of the tool execution.

        Notes:
            Either `user_name` or `channel` must be provided. `user_name` means direct messages from the user. Do not specify both at the same time.
        """
        TIMEOUT = 20  # seconds
        INTERVAL = 3  # seconds

        if not user_name and not channel:
            return {"success": False, "error": "user_name or channel required"}

        if user_name:
            user = self.__get_user_by_name(user_name)
            if not user:
                return {"success": False, "error": "invalid-user_name"}
            activity_channel = "@" + user["username"]
        if channel:
            activity_channel = channel

        last_checked_activity = self.CHAT_ACTIVITY_TIME.get(activity_channel)

        if not last_checked_activity:
            return self.rocketchat_chat_list_messages(
                user_name=user_name, channel=channel
            )

        for _ in range(0, TIMEOUT, INTERVAL):
            response = self.rocketchat_chat_list_messages(
                user_name=user_name,
                channel=channel,
                lastUpdate=last_checked_activity.isoformat().replace("+00:00", "Z"),
            )
            messages = response.get("result", {}).get("updated", [])
            if len(messages) > 0:
                self.CHAT_ACTIVITY_TIME[activity_channel] = max(
                    (
                        datetime.fromisoformat(m["_updatedAt"].replace("Z", "+00:00"))
                        for m in messages
                        if "_updatedAt" in m
                    ),
                    default=datetime.now(UTC),
                ) + timedelta(milliseconds=500)
                return response
            time.sleep(INTERVAL)

        return {"success": False, "error": "timeout-no-new-messages"}

    def rocketchat_chat_list_messages(
        self,
        user_name: Optional[str] = None,
        channel: Optional[str] = None,
        lastUpdate: str = "2025-01-01T00:00:00.000Z",
        count: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> Dict:
        """Retrieve a list of messages from a Rocket.Chat channel or direct chat.

        Args:
            user_name (str, optional): The username of the user (or full name of user or userId of user) to fetch messages from. Defaults to None.
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

        # Resolve roomId either from a channel name or a direct room with a user
        room_id = None
        if channel:
            channel_info = self.__get_channel_by_name(channel)
            if not channel_info:
                return {"success": False, "error": "invalid-channel-name"}
            room_id = channel_info.get("_id")
        else:
            user_info = self.__get_user_by_name(user_name)
            if not user_info:
                return {"success": False, "error": "invalid-user_name"}

            username = user_info["username"]
            rooms_resp = self.rocketchat_rooms_get()
            updates = (
                rooms_resp.get("update", [])
                if isinstance(rooms_resp, dict)
                else rooms_resp
            )
            for r in updates:
                if r.get("t") == "d" and username in r.get("usernames", []):
                    room_id = r.get("_id")
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
        return response

    def rocketchat_directory(
        self,
        text: str,
        type: Literal["users", "channels"],
        count: int = DEFAULT_LIMIT,
        offset: int = 0,
        **kwargs,
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
            "directory", query=query, count=count, offset=offset, kwargs=kwargs
        ).json()

    def rocketchat_rooms_get(self, **kwargs) -> Dict:
        """Get all opened rooms for this user.

        Returns:
            Dict: A JSON-like dictionary containing the user's opened rooms and related metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get("rooms.get", kwargs=kwargs).json()

    def rocketchat_users_list(
        self, count: int = USERS_LIMIT, offset: int = 0, **kwargs
    ) -> Dict:
        """Retrieve users and their information (permission-limited view).

        Args:
            count (int, optional): Maximum number of users to return. Defaults to USERS_LIMIT.
            offset (int, optional): Number of users to skip (pagination). Defaults to 0.

        Returns:
            dict: A JSON-like dictionary containing the list of users and metadata as provided by the Rocket.Chat API.
        """
        return self.call_api_get(
            "users.list", count=count, offset=offset, kwargs=kwargs
        ).json()

    def rocketchat_user_create(
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

    def rocketchat_user_delete(self, user_name: str, **kwargs) -> Dict:
        """Delete a user from Rocket.Chat.

        Args:
            user_name (str): The username of the user (or full name of user or userId of user) to delete.

        Returns:
            dict: A JSON-like dictionary indicating success or failure.
        """
        user = self.__get_user_by_name(user_name)

        if not user:
            return {"success": False, "error": "invalid-user_name"}

        return self.call_api_post("users.delete", userId=user["_id"], **kwargs).json()
