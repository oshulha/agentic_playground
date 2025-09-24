# RocketChat Documentation – Insights and Notes

Below are some observations and suggestions based on my testing and review of the RocketChat methods.

---

## 1. `channels_invite` and `channels_kick` Parameters
- **`channels_invite`** accepts an **array** of users to add to a channel.  
- **`channels_kick`** accepts **only one** user.  
This inconsistency is not very logical. Ideally, both should accept an array.

---

## 2. `directory` Method – Workspace Parameter
- The `directory` method takes a **dictionary** as a parameter, one of its fields being `workspace`.  
- The `workspace` field can have two values:
  - `"local"` → works fine.
  - `"all"` → does **not** work without additional configuration.  
Should always be set `workspace` to `"local"` and should make this parameter unchangeable (inaccessible to the LLM).

---

## 3. Poorly Written Docstrings
- Many docstrings are short and sometimes contain unnecessary text.  
- Parameter descriptions are often unclear — it’s not always obvious what values should be passed.
  - Example: The parameter `user_name` in all methods refers to **First and Last name** (with a space and capitalized), **not** the username or user ID. This is not explained in the current docstrings, and the variable name could be improved.

(need to check how it takes user_name as input (as First and Last Name or not) -- gives it error or not -- and write name in various variants)

---

## 4. Optimization Idea
It might be better to define and return the `StructuredTool` objects directly in `rocketchat_methods.py` instead of generating them dynamically via code.

---

## 5. Large and Complex JSON Responses
- Methods often return **very large** JSON objects containing unnecessary data. Also, JSON maybe is not the best format for LLMs to analyze 
- Large JSONs are not very understandable, and many key names are not intuitive.
  - Example: The `chat_list_messages` method returns a key `"t"`(means type of message) whose values can be:
    - `"au"` → add user
    - `"ru"` → remove user
  - These abbreviations should be explained or rewritten at least. So it needs to filter or simplify responses before returning them to the LLM.

Should Docstrings provide an example of how to use tool?
---

## 6. Exception Handling
There may still be exceptions. These should be rewritten so that errors are returned in a format understandable by the LLM. And it could be 

---

## 7. More Tools Needed?
At the moment we have 14 tools. This tools must be enough to do tasks in TAC for Do node. However, it can be not enough for Check node. 
Example: Do node made a mistake and made wrong user a moderator in chat/channel. Check node noticed this mistake, but Check or Do node can't remove moderator because there is no tool for that.

## Testing
I tested the RocketChat MCP using the `test.py` script:  
```bash
# Run from the `src` directory
python test.py