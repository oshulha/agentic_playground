**Experiment:**

There are several approaches to embedding memories.

The task is to determine which of these approaches yields the best results. We will compare them against each other.

**1) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.
}
```

We simply embed the entire dictionary into the Vector Store.

---

**2) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.
}
```

We embed each value separately (multi-vector).

---

**3) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tags": "2-4 tags?"
}
```

We embed the entire dictionary.

**3.2)** We embed each value separately.

---

**4) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tag1": tag (2-4 keywords),
  "context_tag2": tag,
  "context_tag3": tag
}
```

👉 *4.1)*

*Tokenizer said that "_" symbol only makes embedding worse; for experiment too*

Here, the query will look something like `context_tag1` → the LLM selects from the set of all tags (stored in our “context_tag1”), same for `context_tag2` and `context_tag3`.

— There must be no duplicate tags across different sets;

— No duplicates within the sets themselves.

---

**5) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tag_for_what_worked": tag,
  "context_tag_for_what_to_avoid": tag
}
```

Here, the query will be like `context_tag_for_what_worked` → the LLM selects from the set of all tags (stored in our “context_tag_for_what_worked”);

Same for `context_tag_for_what_to_avoid`.

Again, there must be no duplicate tags across different sets;

— No duplicates within the sets themselves.

---

**5.1)** + also include `trajectory_summary` in the query and select from the available ones (only one nuance — number of memories, but ignore for now)

5.2) + generate `trajectory_summary` based on the `user_input`

5.3) Dictionary:

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tag_for_what_worked": tag,
  "context_tag_for_what_to_avoid": tag,
  "context_tag_for_trajectory_summary": tag
}
```

The LLM selects from the available context tags for each field.