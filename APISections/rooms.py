import mimetypes
import os

from RocketExceptions import RocketMissingParamException
from base import RocketChatBase


class RocketChatRooms(RocketChatBase):
    def rooms_upload(self, rid, file, **kwargs):
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

    def rooms_get(self, **kwargs):
        """Get all opened rooms for this user."""
        return self.call_api_get("rooms.get", kwargs=kwargs)