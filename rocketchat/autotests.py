from rocketchat_methods_cleaned import RocketChat
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import os
import sys


if __name__ == "__main__":
    check = "2"
    client = RocketChat(server_url="http://157.230.77.20:3000/")
    #client = RocketChat(server_url="http://127.0.0.1:3000/")

    # postmsg = client.rocketchat_chat_post_message(text = "Hiu-hai!2222", user_name="mike_chen")
    # with open("test_results/rocketchat_channels_invite_result2222.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(postmsg, ensure_ascii=False))
    
    # sys.exit(0)

    # output = client.rocketchat_channels_list()
    # with open("test_results/_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_users_list(extra_fields=True) #channel="test_channel123456", user_names=["Sarah Johnson"]
    # with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # for u in output["users"]:
    #     postmsg = client.rocketcргиhat_chat_post_message(text = "Hiu-hai!", user_name=u["name"]) #channel="test_channel123456", user_names=["Sarah Johnson"]
    #     print(f"User {u["name"]}: postmsg['success'] {postmsg['success']}")
    #     with open("test_results/rocketchat_postmsg.json", "w", encoding="utf-8") as f:
    #         f.write(json.dumps(postmsg, ensure_ascii=False))

    # output = client.rocketchat_dms_list(offset = 100, extra_fields=True) #channel="test_channel123456", user_names=["Sarah Johnson"]
    # with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_channel_members(channel_name="general") #channel="test_channel123456", user_names=["Sarah Johnson"]
    # with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_users_list(extra_fields=True) #channel="test_channel123456", user_names=["Sarah Johnson"]
    # with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_rooms_get(extra_fields=True) #channel="test_channel123456", user_names=["Sarah Johnson"]
    # with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_channel_delete(channel="1test_channel1")
    # with open("test_results/rocketchat_channels_result.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_chat_list_messages(channel_name="general")
    # with open("test_results/_result1.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_chat_list_messages(user_name="sophia_rodriguez")
    # with open("test_results/_result2.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_chat_list_messages(user_name="huang_jie")
    # with open("test_results/_result3.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    # output = client.rocketchat_chat_list_messages(user_name="jessica_lee", extra_fields=False)
    # with open("test_results/_result4.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    output = client.rocketchat_chat_post_message(text="Hallo", user_name="chen_xinyi", file="/home/oleksandr/Pictures/ubuntu.jpg")
    with open("test_results/_result4.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(output, ensure_ascii=False))

    if check == "0":
        client = RocketChat(server_url="http://157.230.77.20:3000/")
        output = client.rocketchat_channel_add_role(channel="general", role="owner", full_name="Sarah Johnson")
        with open("test_results/rocketchat_channels_add_role_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_add_role(channel="general", role="moderator", user_name="sarah_johnson")
        with open("test_results/rocketchat_channels_add_role_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_add_role(channel="general", role="leader", user_name="@sarah_johnson")
        with open("test_results/rocketchat_channels_add_role_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_channel_invite(channel="general", full_names=["Sarah Johnson"])
        with open("test_results/rocketchat_channels_invite_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_invite(channel="general", user_names=["sarah_johnson"])
        with open("test_results/rocketchat_channels_invite_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_invite(channel="general", user_names=["@sarah_johnson"])
        with open("test_results/rocketchat_channels_invite_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_channel_kick(channel="general", full_name="David Wong")
        with open("test_results/rocketchat_channels_kick_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_kick(channel="general", user_name="jessica_chen")
        with open("test_results/rocketchat_channels_kick_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channel_kick(channel="general", user_name="@alex_turner")
        with open("test_results/rocketchat_channels_kick_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_chat_post_message(text="Hi!", full_name="David Wong")
        with open("test_results/rocketchat_chat_post_message_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_post_message(text="Privit!", user_name="jessica_chen")
        with open("test_results/rocketchat_chat_post_message_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_post_message(text="Bonjour!", user_name="@alex_turner")
        with open("test_results/rocketchat_chat_post_message_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_chat_list_messages(full_name="David Wong")
        with open("test_results/rocketchat_chat_list_messages_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_list_messages(user_name="jessica_chen")
        with open("test_results/rocketchat_chat_list_messages_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_list_messages(user_name="@alex_turner")
        with open("test_results/rocketchat_chat_list_messages_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_user_delete(full_name="David Wong")
        with open("test_results/rocketchat_users_delete_result1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_user_delete(user_name="jessica_chen")
        with open("test_results/rocketchat_users_delete_result2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_user_delete(user_name="@alex_turner")
        with open("test_results/rocketchat_users_delete_result3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))