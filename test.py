from rocketchat import RocketChat
import json

client = RocketChat("theagentcompany", "theagentcompany")
#output = client.users_list()
# output = client.chat_post_message("Hi! Testing post msg", channel="#general")

#output = client.rooms_get()

#output = client.chat_list_messages("GENERAL")

# output = client.users_list()

#Do Not Work Properly
# dict = {
#   "name": "Hai You Haikin",
# }
# output = client.users_update("7My8YbErQi3E7vd35", bio="here_we_go_again@gmail.com")

#output = client.users_create(name="TestUser", email="testuser@examle.com", password="testuser", username="testuser") #output.json gives id of created user

# output = client.users_delete("nHnpCA9fky98z54yS")

# output = client.channels_list()

#output = client.channels_invite(room_id="QYaq3NKio4oGgwvM3", user_id="PCYGvJCeb89Nk4dK8")

# output = client.channels_info(channel="product")

#output = client.directory(query={"text": "CTO", "type": "users", "workspace": "local"})

# output = client.directory(query={"text": "help-desk", "type": "channels", "workspace": "local"})

output = client.channels_invite(channel="test_channel", user_names=["Mike Chen", "Chen Xinyi1"])

# output = client.channels_add_moderator(room_id="PinWwfjHuqZzeCgcQ", user_id="GYMYHQKtWPAr47ZsE") 
# output = client.channels_remove_moderator(room_id="PinWwfjHuqZzeCgcQ", user_id="GYMYHQKtWPAr47ZsE") 
#output = client.channels_kick(room_id="PinWwfjHuqZzeCgcQ", user_id="GYMYHQKtWPAr47ZsE") 

# output = client.channels_members(channel="general")

# output = client.directory(query={"text": "general", "type": "channels", "workspace": "local"})

# output = client.channels_add_owner(room_id = "GENERAL", username="theagentcompany")

#output = client.directory(query={"text": "project-lowcode", "type": "channels", "workspace": "local"})

# output = client.chat_list_messages("HaDSGnNhFM6mCKHa6")

#output = client.chat_post_message(text="Hi, everyone!", channel="#project-lowcode")

# output = client.channels_create(name="literaturereview")

# output = client.channels_add_leader(room_id="GENERAL", user_id="hDhbakBmvM8WmraTA") #Emma Lewis is new leader

# output = client.chat_post_message(text="Hi, @sarah_johnson! Your task is to be polite and good girl!", channel="#project-lowcode")

# output = client.chat_post_message(text="Hi! Look!", user_name="Mike Chen", file="/home/oleksandr/Pictures/ubuntu.jpg")

# output = client.rooms_upload(rid="GENERAL", file="/home/oleksandr/Pictures/ubuntu.jpg")

# output = client.chat_list_messages(user_name="Sarah Johnson")

#output = client.users_delete("TestUser43")

data = output.json()

with open("output.json", "w") as file:
    json.dump(data, file)