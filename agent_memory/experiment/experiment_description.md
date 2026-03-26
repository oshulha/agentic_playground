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

We embed each value separately (multi-vector).
4.1) Make three hybrid (0.7 * vector search + 0.3 * BM25) searches per each of the fields. Simply for each of the searches the query is user_query.

Does trajectory_summary, what_worked, what_to_avoid, context_tag_for_what_worked, context_tag_for_what_to_avoid have changed anything?

Results: 


4.2) The query will be like `what_worked` → the LLM selects from the set of all `what_worked` (stored in our “what_worked”); 
Same for `what_to_avoid` and `trajectory_summary`.
Again, there must be no duplicate tags across different sets;
— No duplicates within the sets themselves.

Results:


4.3) Generate each field according to query.

Results:


---

**2) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tags": "2-4 tags?"
}
```

We embed each value separately.

Does context_tags have changed anything?

4.1) Make four hybrid (0.7 * vector search + 0.3 * BM25) searches per each of the fields. Simply for each of the searches the query is user_query.

Results:


4.1.1) Only to embed context_tags and trajectory_summary

Results:


4.2) The query will be like `what_worked` → the LLM selects from the set of all `what_worked` (stored in our “what_worked”); 
Same for `what_to_avoid`, `trajectory_summary`, `context_tags`.
Again, there must be no duplicate tags across different sets;
— No duplicates within the sets themselves.

Results:


4.2.1) Only to select context_tags and trajectory_summary

Results:


4.3) Generate each field according to query.

Results:


4.3.1) Only to generate context_tags and trajectory_summary

Results:

4.4) Replace "_" to " " Or regenerate without "_"
(👉 *Tokenizer said that "_" symbol only makes embedding worse; for experiment too*)

---

**3) Dictionary:**

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

Does context_tag1, context_tag2, context_tag3 have changed anything?

4.1) Make six hybrid (0.7 * vector search + 0.3 * BM25) searches per each of the fields. Simply for each of the searches the query is user_query.

Result:

4.1.1) Only to embed context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:

4.2) The query will look something like `context_tag1` → the LLM selects from the set of all tags (stored in our “context_tag1”), same for `context_tag2` and `context_tag3`.
Again, there must be no duplicate tags across different sets;
— No duplicates within the sets themselves.

Results:


4.2.1) Only to select context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:


4.3) Generate each field according to query.

Results:


4.3.1) Only to generate context_tags and trajectory_summary

Results:

4.4) Replace "_" to " " Or regenerate without "_"
(👉 *Tokenizer said that "_" symbol only makes embedding worse; for experiment too*)

---

**4) Dictionary:**

```
{
  "trajectory_summary": 1-2 sent.,
  "what_worked": 1-2 sent.,
  "what_to_avoid": 1-2 sent.,
  "context_tag_for_what_worked": tag,
  "context_tag_for_what_to_avoid": tag
}
```

Does trajectory_summary, what_worked, what_to_avoid, context_tag_for_what_worked, context_tag_for_what_to_avoid have changed anything?

4.1) Make five hybrid (0.7 * vector search + 0.3 * BM25) searches per each of the fields. Simply for each of the searches the query is user_query.

Results:

4.1.1) Only to embed context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:

4.2) The query will be like `context_tag_for_what_worked` → the LLM selects from the set of all tags (stored in our “context_tag_for_what_worked”); 
Same for `context_tag_for_what_to_avoid`.
Again, there must be no duplicate tags across different sets;
— No duplicates within the sets themselves.

Results:


4.2.1) Only to select context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:

4.3) Generate each field according to query.

Results:

4.3.1) Only to generate context_tags and trajectory_summary

Results:

4.4) Replace "_" to " " Or regenerate without "_"
(👉 *Tokenizer said that "_" symbol only makes embedding worse; for experiment too*)

Results:

---

**5) Dictionary:**

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

4.1) Make six hybrid (0.7 * vector search + 0.3 * BM25) searches per each of the fields. Simply for each of the searches the query is user_query.

Results:

4.1.1) Only to embed context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:

4.2) The query will be like `context_tag_for_what_worked` → the LLM selects from the set of all tags (stored in our “context_tag_for_what_worked”); 
Same for `context_tag_for_what_to_avoid`.
Again, there must be no duplicate tags across different sets;
— No duplicates within the sets themselves.

Results:


4.2.1) Only to select context_tag1, context_tag2, context_tag3 and trajectory_summary

Results:

4.3) Generate each field according to query.

Results:

4.3.1) Only to generate context_tags and trajectory_summary

Results:

4.4) Replace "_" to " " Or regenerate without "_"
(👉 *Tokenizer said that "_" symbol only makes embedding worse; for experiment too*)

Results:
