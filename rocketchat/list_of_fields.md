### Remove from channels_list output
fname
customFields
topic
broadcast
encrypted
t (or rewrite to "type")
ts (for short "timestamp")
u
ro (for short "read-only"???)
default ("general" is a default channel)
sysMes (for short "system messages" -- like "user1 joined the channel")
_updatedAt (some update?)
lastMessage 
lm (lastmessage timestamp?)
federated

What left? Use It To Check (some of them may be missing):
name
msgs
usersCount
description

Remove from lastMessage -- Last is unnecessary because we have pagination
_id
rid
ts
_updatedAt
urls
mentions
channels
md
groupable
blocks


What left
msg
u (rename to user who send msg) -- name, username (remove: _id)

### channels_add_role has only success field

### Remove from channels_create
fname
customfields
t
ro
default
sysMes
_updatedAt

name
msgs
usersCount
ts (rewrite to timestamp)

What left? Use It To Check (some of them may be missing):


### channels_invite has only success field (and I don't think it needs more)

### channels_kick has only success field (and I don't think it needs more)

### channels_delete has only success field (and I don't think it needs more)

### Remove from members
_id
status
_updatedAt
nickname
avatarETag

What Left?
username
name


### Remove from users_list
_id
emails
type
status
active
lastLogin
nameInsensitive
avatarETag


What left?
username
roles
name

<!--NOT FINISHED ### Remove from get_rooms
_id
ts
t

What left?
name
usernames
msgs
usersCount -->

### Remove from dms_list
_id
t
usersCount
ts
uids
encrypted
default
ro
sysMes
_updatedAt
_USERNAMES
e2eKeyId
lastMessage
lm
topic

what left?
usernames
msgs

### Remove from post_msg
ts

What Left?
channel
success

In ["message"]
Remove
alias
parseUrls
groupable
ts
u
rid
_updatedAt
_id

What Left?
msg

### Remove from room.upload

Left:
["file"] ["name"] ["type"]

### Remove from chat_list_messages in ["result"]["updated"]
_id
rid
u
ts
_updatedAt
alias
token
unread
urls
mentions
channels
md
t
groupable

What Left?
msg
ts (timestamp)
u (username and name -- sender)

### I will leave Directory as is because it hasn't got a lot of fields and still it is Directory(dovidnyk and our agent is admin)

### Remove from create_user 
All info except success

### delete_user has only success field (and I don't think it needs more)

