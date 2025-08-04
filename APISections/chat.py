from RocketExceptions import RocketMissingParamException
from base import RocketChatBase

DEFAULT_LIMIT = 50

class RocketChatChat(RocketChatBase):

    def chat_post_message(self, text, room_id=None, channel=None, image_url=None, **kwargs):
        """Posts a new chat message.Send messages to channels or users on your workspace. The room ID or an array of room IDs where the message is to be sent. 
        You can use channel name or username. The channel name must have the # prefix. @ refers to username.
        Example of using: output = client.chat_post_message("Hi!", channel="@mike_chen")
        Example of using: output = client.chat_post_message("Hi!", channel="#general")
        Example: output = client.chat_post_message(text="Logo:", channel="#project-lowcode", image_url="https://upload.wikimedia.org/wikipedia/commons/7/78/Image.jpg")"""
        
        attachments = [
            {
            "image_url": image_url,
            }
        ]
        if not room_id and not channel:
            raise RocketMissingParamException("roomId or channel required")
        
        if image_url:
            if room_id:
                if text:
                    return self.call_api_post(
                        "chat.postMessage", roomId=room_id, text=text, attachments=attachments, kwargs=kwargs
                    )
                return self.call_api_post("chat.postMessage", roomId=room_id, attachments=attachments, kwargs=kwargs)
            if channel:
                if text:
                    return self.call_api_post(
                        "chat.postMessage", channel=channel, text=text, attachments=attachments, kwargs=kwargs
                    )
                return self.call_api_post(
                    "chat.postMessage", channel=channel, attachments=attachments, kwargs=kwargs
                )
        else:
            if room_id:
                if text:
                    return self.call_api_post(
                        "chat.postMessage", roomId=room_id, text=text, kwargs=kwargs
                    )
                return self.call_api_post("chat.postMessage", roomId=room_id, kwargs=kwargs)
            if channel:
                if text:
                    return self.call_api_post(
                        "chat.postMessage", channel=channel, text=text, kwargs=kwargs
                    )
                return self.call_api_post(
                    "chat.postMessage", channel=channel, kwargs=kwargs
                )
    
    def chat_list_messages(self, roomId, lastUpdate="2020-01-01T00:00:00.000Z", count=DEFAULT_LIMIT, offset=0):
        return self.call_api_get(
            "chat.syncMessages", roomId=roomId, lastUpdate=lastUpdate, count=count, offset=offset
        )