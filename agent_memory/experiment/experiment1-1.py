import weaviate
from weaviate.classes.config import Property, DataType, Configure
import time
from episodic_memory_thoughts import episodic_memories
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

queries_list = [
    "How to find a reputable car detailing service and select the best paint protection (wax or sealant) for a long road trip, considering budget and specific vehicle needs?",
    "What are the best car rental and insurance options for a trip to Maui, and what essential travel gear should I pack to ensure my devices stay charged while managing the total cost of my travel budget?",
    "How can I organize a community food event that combines a charity drive with a menu featuring slow cooker chicken tacos (rich in peppers and onions) and coffee crème brûlée with a perfectly caramelized crust?",
    "How can I properly clean and maintain the breathability of waterproof membranes like Keen.Dry or Merrell's technology in hiking boots, and what are the best actionable steps for drying and storing running shoes to prevent moisture buildup?",
    "What is the total cost of ownership for a 2018 Ford Mustang GT if I upgrade it with high-performance tires and track-ready suspension, and how do these modifications, along with track-day usage, impact insurance rates and long-term maintenance costs?",
    "What are the best car rental and insurance options for a trip to Hawaii, including essential travel gear for electronics and ways to get involved with local coral reef protection or marine debris projects during my visit?",
    "What are the best online courses and platforms for mastering statistical visualization with Seaborn and Python integration, and how can I incorporate self-awareness practices like reflective journaling into my learning routine to improve my professional communication?",
    "What is the best routine for cleaning and maintaining the lifespan of both running shoes and hiking boots, and how should I properly break in new footwear while also preparing leather dress shoes for a professional cobbler visit?",
    "How can I effectively organize a faith-based charity food drive, secure microloans or grants for the initiative through organizations like Catholic Charities, and implement a social media promotion strategy to maximize community engagement and donations?",
    "How can I leverage microloans or grants from organizations like Catholic Charities to improve my financial standing for a home purchase in family-friendly Irvine neighborhoods, and what are the best strategies for submitting a strong offer with an inspection contingency and pre-approval letter through my agent, Rachel?"
]

answers_list = [
    [2, 3, 4],
    [9, 10, 8],
    [28, 29, 13],
    [27, 24, 25],
    [21, 22, 8],
    [9, 10, 30],
    [6, 11, 5],
    [27, 23, 26],
    [13, 14, 19],
    [16, 15, 14]
]

vdb_client = weaviate.connect_to_local()
print("Connected to Weviate: ", vdb_client.is_ready())

if vdb_client.collections.exists("episodic_memory"):
    vdb_client.collections.delete("episodic_memory")
    print("Deleted old collection")

vdb_client.collections.create(
    name="episodic_memory",

    vectorizer_config=[
        Configure.NamedVectors.text2vec_openai(
            name="conversation_summary_vector",
            model="text-embedding-3-large",
            source_properties=["conversation_summary"]
        ),
        # Configure.NamedVectors.text2vec_openai(
        #     name="what_worked_vector",
        #     model="text-embedding-3-large",
        #     source_properties=["what_worked"]
        # ),
        # Configure.NamedVectors.text2vec_openai(
        #     name="what_to_avoid_vector",
        #     model="text-embedding-3-large",
        #     source_properties=["what_to_avoid"]
        # )
    ],

    properties=[
        Property(name="memory_id", data_type=DataType.INT),
        Property(name="conversation_summary", data_type=DataType.TEXT),
        Property(name="what_worked", data_type=DataType.TEXT),
        Property(name="what_to_avoid", data_type=DataType.TEXT)
    ]
)

print("Started load...")
start_load = time.time()

collection = vdb_client.collections.get("episodic_memory")

episodic_memories_dicts = episodic_memories["episodic_memories"]

for i in range(0, 30, 1):
    collection.data.insert(
        episodic_memories_dicts[i]
    )

start_fetch = time.time()
print(f"Loading took {start_fetch - start_load}")
# print("Started fetch...")

final_score = 0

for i, query in enumerate(queries_list):
    conversation_summary_memories = collection.query.hybrid(
        query=query,
        alpha=0.7,
        limit=3,
        target_vector="conversation_summary_vector",
        return_metadata=["score"]
    )

    # what_worked_memories = collection.query.hybrid(
    #     query=query,
    #     alpha=0.7,
    #     limit=3,
    #     target_vector="what_worked_vector",
    #     return_metadata=["score"]
    # )

    # what_to_avoid_memories = collection.query.hybrid(
    #     query=query,
    #     alpha=0.7,
    #     limit=3,
    #     target_vector="what_to_avoid_vector",
    #     return_metadata=["score"]
    # )

# end_fetch = time.time()
# print(f"Скільки часу зайняв retrieve: {end_fetch - start_fetch}")

    # scores = {}

    # def add_scores(results, weight):
    #     for obj in results.objects:
    #         id = obj.uuid
    #         score = obj.metadata.score
    #         if score is None:
    #             continue

    #         if id not in scores:
    #             scores[id] = 0

    #         scores[id] += weight * score

    # add_scores(what_to_avoid_memories, 0.3)
    # add_scores(what_worked_memories, 0.3)
    # add_scores(conversation_summary_memories, 0.4)

    # print(f"len(scores.items()): {len(scores.items())}")
    # top_k = 3
    # best = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    with open("exp1-1_results.txt", "a", encoding="utf-8") as f:
        f.write(f"Query is: {query}\n\n")
        f.write(f"The answers are: {answers_list[i]}\n\n")
        for obj in sorted(conversation_summary_memories.objects, key=lambda x: x.metadata.score, reverse=True):
            score = obj.metadata.score
            props = obj.properties
            
            f.write(f"Score: {score}\n")
            f.write(f"Memory_id: {props['memory_id']}\n")
            f.write(f"Conversation summary: {props['conversation_summary']}\n")
            f.write(f"What worked: {props['what_worked']}\n")
            f.write(f"What to avoid: {props['what_to_avoid']}\n")
            f.write("-" * 50 + "\n")

            if props['memory_id'] in answers_list[i]:
                final_score += 1

with open("exp1-1_results.txt", "a", encoding="utf-8") as f:
    f.write(f"Final score: {final_score}/30")
    print(f"Final score: {final_score}/30")

vdb_client.close()