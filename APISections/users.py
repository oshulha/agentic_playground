import mimetypes
import os

from RocketExceptions import RocketMissingParamException
from base import RocketChatBase


class RocketChatUsers(RocketChatBase):
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

    def users_delete(self, user_id, **kwargs):
        """Deletes a user"""
        return self.call_api_post("users.delete", userId=user_id, **kwargs)