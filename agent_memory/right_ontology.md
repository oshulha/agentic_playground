Developing Ontology

Current Ontology (+ Upgraded): 
```
# Table Of Contents

# Actors(Microservices)

## Brains

## Memory Controller
### Episodic Memory Responsibilities (Memory Controller-level and Store Interaction-level)
#### recall_episodic
#### store_episodic
#### forget_episodic*
### Tool-level Memory Responsibilities (Memory Controller-level and Store Interaction-level)
#### recall_tool_level
#### store_tool_level
#### forget_tool_level*

## Vector Store
### Episodic Memory Responsibilities
#### Initialization*
?#### Saving Memories 
?#### Retrieving Memories 
?#### Deleting Memories* 
### Tool-level Memory Responsibilities
#### Initialization*
?#### Saving Memories 
?#### Retrieving Memories 
?#### Deleting Memories* 

## Graph Store*
### Semantic Memory Responsibilities*
#### Initialization*

# Types Of Memory

## Explicit & Implicit Memory

## Working Memory

## Tool-Level Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### Memory Storage After Post-Think -- #minimalTODO (Memory Controller-level) need to rewrite in ReAct level and add this section to Memory Controller 
### How To Forget
#### Classical Forgetting?[To_Do]
#### Tool-Level Memory Rewriting -- #minimalTODO (Memory Controller-level) need to rewrite in ReAct level and add this section to Memory Controller section
### Commit Mechanism
### Accept Mechanism

## Episodic Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### How To Forget

## Semantic Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### How To Forget

## Procedural Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### How To Forget

## Autobiographical / User-Personalized Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### How To Forget

## Priming & Classical Conditioning & Non-Associative Memory (Tools and ReAct-level)
### Sequence Diagram*
### Intro*
### How To Retrieve
### How To Update
### How To Forget

# Other
...
?#### - seems like it will be more appropriate to be in Memory Controller endpoint logic
* - no section (I need to add it)
at the moment current ontology of my spec has troubles having almost the same naming in Types Of Memory and Memory Controller (ontology 2 solves it)
```

Ontology 2: 
```
# Table Of Contents

# Brains(ReAct) Python harness

## Tools
### recall_episodic
### recall_tool_level

## Functions
### update_episodic
### forget_episodic
### update_tool_level
### forget_tool_level

## Start of ReAct 
### Episodic Memory 
### Tool-level Memory

## End of ReAct
### Episodic Memory
### Tool-level Memory

## Mechanisms(?)
### Commit Mechanism
### Accept Mechanism

# Memory Controller (code-only microservice)

## Tool-level Memory
### recall() 
### update()
### forget() 

## Episodic Memory
### recall()
### update()
### forget()

## Semantic Memory
### recall()
### update()
### forget()

## Procedural Memory
### recall()
### update()
### forget()

## Autobiographical / User-Personalized Memory
### recall()
### update()
### forget()

## Priming & Classical Conditioning & Non-Associative Memory
### recall()
### update()
### forget()

# Initialization of DBs

## Vector Store
### Tool-level Memory config
### Episodic Memory config
### *Procedural Memory config
### *Autobiographical / User-Personalized Memory config
### *Priming & Classical Conditioning & Non-Associative Memory config

## Graph Store
### Semantic Memory config

* - still don't know if paragraph will be in Vector Store section
? - still don't know if section will be in Brains(ReAct) Python harness section
```

**Sprint Plan (almost 2 weeks — [19 Mar - 31 Mar]):**

Goal: Completed Memory Subsystem Spec

5 Global Tasks (Epics) Left: (well, maybe 4, since Priming & … is not guaranteed to be included)

Episodic Memory, Semantic Memory, Procedural Memory, Autobiographical / User-Personalized Memory, Priming & Classical Conditioning & Non-Associative Memory

This means that 13 days / 5 Epics = 2.6 days per Epic (in the worst case: 13 days / 4 Epics = 3.25 days per Epic). That is, this means that with weekends it’s about 2–3 days per subsystem. If we consider that Episodic is almost done, then 13 days / 3 Epics = 4.3(3) days per Epic. And if we include weekends, then 9 / 3 = 3 days per Epic, which seems unrealistic. So, roughly 2–4 days. 4 days at least sounds somewhat like “rushing through everything at full speed.”