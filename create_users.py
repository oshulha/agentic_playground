from rocketchat_methods import RocketChat
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import os

users = ["Alex Evans", "Jordan Collins", "Taylor Stewart", "Morgan Perez", "Casey Mitchell", "Riley Wright", "Skyler Sanchez", "Parker Rogers", "Avery Reed", "Quinn Cook", "Cameron Morgan", "Drew Bell", "Bailey Barnes", "Rowan Gray", "Reese James", "Finley Wood", "Kai Kelly", "Sage Patterson", "Remy Price", "Elliot Bennett", "Noel Gray", "Adrian Watson", "Blake Brooks", "Blair Kelly", "Daryl Rivera", "Emerson Cox", "Hayden Howard", "Jules Ward", "Kendall Torres", "Lane Peterson", "Marin Gray", "Micah James", "Nico Watson", "Oakley Barnes", "Rhett Wood", "Shawn Edwards", "Terry Collins", "Val Stewart", "Wesley Sanchez", "Zane Morris", "Hannah Rogers", "Maya Clark", "Nina Lewis", "Lena Robinson", "Ivy Walker", "Chloe Rivera", "Amelia Cooper", "Olivia Richardson", "Sophia Cox", "Isabella Howard", "Mila Ward", "Aria Torres", "Ella Peterson", "Charlotte Gray", "Grace Martinez", "Emily Lopez", "Emma Gonzalez", "Abigail Hernandez", "Ava Lopez", "Sofia Gonzalez", "Olivia Flores", "Sophia Green", "Isabella Adams", "Mila Nelson", "Aria Carter", "Ella Mitchell", "Grace Perez", "Emily Roberts", "Emma Turner", "Abigail Phillips", "Ava Evans", "Sofia Turner", "Olivia Diaz", "Sophia Murphy", "Isabella Bailey", "Mila Rivera", "Eric Cooper", "Ella Richardson", "Greg Cox", "Emily Howard", "Egor Ward", "Abigail Sanchez", "Ivan Martin", "Sofia Lee", "Oleh Young", "Sophia Allen", "Tim Nelson", "Mila Baker", "Chris Carter", "Ella Ramirez", "Kas Clark", "Emily Rodriguez", "Volodymyr Martinez", "Daria Hernandez", "Ivan Lopezenko", "Sofia Dorozhna", "Oleh Flores", "Sophia Pustovoit", "Illya Adams", "Barbora Kreichik", "John Carter", "Tereza Mitkell", "George Perez", "Maya Sherif", "Erica Temina", "Elina Phillips", "Clark Evans", "Varvar Macnelly", "Lloyd Diaz", "Rebeka Madarova", "Lewis Bailey", "Bernarda Pivera", "Endrick Cooper", "Katarzyna Fardson", "Charles Foxer", "Simona Walterod", "Tony Wordic", "Rafael Sanchez", "Gael Martinelli", "Stefania Lacrazo", "Dexter Young", "Sophia Allenelli", "Terry Neliro", "Whitney Houston", "Ariana Grandera", "Lesya Parmizano", "Juliet Clarken", "Emily Rodrine", "Charles Leclercas", "Antonina Hernandez", "Aryna Lopez", "Sonya Gonza", "David Floresyan", "Sophia Greeneri", "Roger Adamsian", "Milana Neliwo", "Eric Mapanelli", "Scharma Astra", "Greg Schwartz", "Emily Robertson", "Karen Mhitaryan", "Katerina Phillips", "Christian Evanson", "Sofia Turnerolli", "Oleksandr Diaz", "Tamara Zinda", "Danylo Bailey", "Linda Chirico", "Vsevolod Cooperoni", "Jana Inglis", "George Coxoli", "Edward Howard-Pyrohova", "Rick Wardlo", "Casper Rodero", "Lorenzo Marcusoni", "Sofia Leeson", "Jack Youngeston", "Sophia Alleno", "Fabrizio Capuchini", "Mila Bakeronment", "Dmytro Carterto", "Ella Mitchelliki", "Greg Perezenolli", "Emily Robertswaten", "Timoti Shaturner", "Serena Williamson", "Venus Willino", "Sofia Cage", "Diego Delpotro", "Sophia Murcuri", "Anastasia Bailiro", "Mila Kunicova", "Christian Cooperbale", "Ella Hommason", "Ben Folo", "Jessica Pegularico", "Querantino Wardico", "Casey Sanchez", "Terry Martinok", "Serena Winasion", "Iga Schwentec", "Sora Alalo", "John Belson", "Miia Tunder", "Ariana Cartero", "Ella Mitell", "Andrii Perezot", "Jack Robertsaw", "Emilio Tero", "Mira Andreka", "Mariia Fastop", "Karolina Tsibulkova", "Coco Dazo", "Paula Dasoda", "Jannik Carlsen", "Errica Rivera", "Sonya Bladen", "Veronica Richaso", "Antonina Coxino", "Jasmine Hohoko", "Peter Parcer", "Leyla Lecleric", "Lando Mart", "Marta Lewa", "Justin Timberl", "Dmytro Augustino", "Toni Naval", "Magdalena Babadon", "Carlos Alcatraz", "Scarlett Mi", "Christiano Pessi", "Jack Jacksori", "Marcus Tele", "Ugo Neydar", "Artem Nemi", "Angelina Trygub", "Maksym Didenko", "Olga Marpha", "Terry Baibai", "Yulia Riv", "Son Hyuro", "Polina Richar", "Maksym Cohorta", "Renata Zaraward", "Ons Jager", "Karolina Santa", "Eliza Cocciretto", "Sarah Lolo", "Roger Erono", "Denis Petlik", "Oleksandr Makedon", "Serhii Nalbandian", "Alejandro Torres", "Carmen Lopez", "Javier Morales", "Lucia Fernandez", "Diego Castillo", "Sofia Alvarez", "Martin Reyes", "Elena Vargas", "Ricardo Ortega", "Natalia Pena", "Andres Ramos", "Mariana Cruz", "Francisco Navarro", "Daniela Romero", "Juan Garcia", "Laura Herrera", "Pablo Serrano", "Valeria Molina", "Santiago Delgado", "Adriana Campos", "Tomas Aguilar", "Clara Ibanez", "Miguel Esteban", "Teresa Suarez", "Alvaro Santos", "Patricia Mendez", "Ignacio Paredes", "Beatriz Cabrera", "Esteban Rojas", "Ines Bravo", "Mateo Fuentes", "Paula Dominguez", "Rodrigo Leon", "Angela Marin", "Rafael Solis", "Isabel Cortes", "Oscar Varela", "Jimena Salazar", "Manuel Prieto", "Nuria Carrasco", "Guillermo Montoya", "Alicia Ponce", "Sergio Hidalgo", "Amalia Godoy", "Cristian Lozano", "Veronica Ferrer", "Felipe Cuevas", "Marta Benitez", "Ivan Petrov", "Natalia Sokolova", "Sergey Mikhailov", "Elena Ivanova", "Dmitry Orlov", "Marina Kovalenko", "Oleg Smirnov", "Anastasia Moroz", "Viktor Lebedev", "Irina Pavlova", "Mikhail Kuznetsov", "Tatiana Volkova", "Yuri Antonov", "Galina Nikitina", "Alexei Denisov", "Svetlana Fedorova", "Igor Tarasov", "Katerina Zaitseva", "Pavel Korneev", "Alina Melnik", "Andrey Bondarenko", "Olga Markova", "Nikolai Egorov", "Daria Ivanenko", "Boris Voronin", "Lidia Polyakova", "Roman Stepanov", "Yana Gavrilova", "Vadim Cherevko", "Milena Sorokina", "Alex Tarasenko", "Kristina Pavlenko", "Maksim Levchenko", "Oksana Drobysheva", "Viktor Shevchenko", "Marina Belyaeva", "Denis Kravchenko", "Yulia Karpova", "Leonid Bogdanov", "Inna Novikova", "Artem Popov", "Polina Mirova", "Nikita Kalinin", "Zoya Cherkasova", "Kirill Grigorenko", "Sofia Martynova", "Dmitry Vasiliev", "Larisa Rogova", "Ahmed Al-Masri", "Fatima El-Sayed", "Omar Al-Hassan", "Layla Al-Farouq", "Karim Nasser", "Noor Abbas", "Youssef Khalil", "Hanan Mansour", "Tariq Al-Mutairi", "Samira Haddad", "Nabil Barakat", "Zainab Darwish", "Khalid Al-Salem", "Rania Fadel", "Walid Hamdan", "Maha Bitar", "Fadi Al-Khatib", "Hana Abu-Salem", "Jamal Ameen", "Salma Qadri", "Mustafa Zahran", "Aisha Rahman", "Bassam Younis", "Lina Saeed", "Farid Jalal", "Dalia Shoukry", "Yasin Abdelrahman", "Mariam Naji", "Hassan Al-Badawi", "Rasha Ibrahim", "Samir Fawzi", "Amal Zahra", "Majid Al-Rifai", "Yasmin Abu-Nasr", "Nader Ismail", "Leila Kamal", "Firas Bahjat", "Noura Hijazi", "Adnan Khoury", "Huda Saleh", "Basel Qassem", "Rawan Mahfouz", "Tareq Shami", "Sahar Awad", "Imran Ghazi", "Yara Abdelaziz", "Sami Haddad", "Rami Maktoum", "Iman Saqr", "Ziad Marwan", "Chen Liang", "Zhao Mei", "Sun Hao", "Liu Yan", "Wang Rui", "Zhang Ping", "Ma Bo", "Xu Lei", "Guo Hui", "Zhou Lan", "Deng Min", "Qian Jun", "He Ying", "Gao Peng", "Shi Qiao", "Fang Xin", "Liang Jie", "Pan Ming", "Zhong Wei", "Bai Chen", "Tang Xiu", "Luo Fei", "Du Wen", "Jin Kai", "Xie Hui", "Cai Rong", "Zhu Li", "Han Yu", "Pei Qian", "Hou Bo", "Kong Mei", "Deng Jie", "Ran Li", "Lin Peng", "Meng Fang", "Yao Ming", "Zhuang Hui", "Shao Bin", "Yin Yue", "Ke Hong", "Mo Feng", "Tan Li", "Xun Wei", "Qiu Ling", "Ren Hao", "Fei Lan", "Bao Zhen", "Niu Yong", "Shou Ping", "Lian Shu", "Adebayo Okonkwo", "Fatima Abiola", "Kwame Boateng", "Zanele Ncube", "Thabo Mokoena", "Aisha Diallo", "Mohamed Jallow", "Chiamaka Eze", "Daniel Banda", "Halima Yusuf", "Sibusiso Dlamini", "Mariam Bah", "Peter Kimani", "Nomusa Khumalo", "Emmanuel Chike", "Awa Sarr", "Lebo Maseko", "Kofi Mensah", "Zuri Muthoni", "Tendai Chirwa", "Salma Benali", "Oumar Kane", "Lindiwe Moyo", "Juma Hassan", "Nana Adom", "Aminata Keita", "Ahmed Osman", "Yara Fadel", "Sipho Maduna", "Ibrahim Sow", "Naima Warsame", "Joseph Muriithi", "Grace Nanziri", "Musa Abubakar", "Blessing Okafor", "Jamal Diouf", "Olabisi Fashola", "Pascal Mba", "Zanele Mthethwa", "Hamza Belkacem", "Phumzile Shongwe", "Saidou Bah", "Adjoa Owusu", "Youssef Moustafa", "Amina Kone", "Samuel Njoroge", "Rahma Idris", "Omar Elamin", "Kemi Balogun", "Ismail Hassan", "Linda Adeyemi", "Hassan Olatunji", "Chipo Mutasa", "Andreas Pappas", "Eleni Markou", "Nikos Dimitriou", "Sophia Laskari", "Ioannis Kyrkos", "Maria Katsaros", "Leonidas Petrakis", "Chrysoula Mavros", "Thanos Georgiou", "Alexandra Voulgaris", "Petros Anagnostou", "Christina Rallis", "Antonis Kouris", "Despina Karalis", "Stavros Galanis", "Nefeli Xanthopoulos", "Dimitra Ioannou", "Andreas Tsoukalas", "Panagiota Frangou", "Nikolas Stavridis", "Konstantinos Lemos", "Katerina Psarros", "Ilias Marinos", "Myrto Christodoulou", "Georgios Spanos", "Theodora Kyriakou", "Christos Loukas", "Melina Papadakis", "Vasilis Triantafyllos", "Charis Oikonomou", "Fotis Argyros", "Athina Skarlatos", "Panos Deligiannis", "Spyros Mandrakis", "Eirini Alexiou", "Michalis Chatzis", "Lampros Sotiropoulos", "Artemis Roussos", "Evangelos Nanos", "Calliope Anastos", "Nikolaos Prokopis", "Ioanna Vrettos", "Themis Charalambous", "Persephone Kalivas", "Alexandros Xenakis", "Panagiotis Manos", "Zoi Gerasimos", "Georgina Stylianou", "Andreas Christakis", "Kleon Konstantinou", "Ahmet Demir", "Elif Yildirim", "Burak Kaya", "Merve Aksu", "Caner Arslan", "Derya Korkmaz", "Hakan Ozcan", "Melis Kantar", "Cem Yaman", "Aylin Kurt", "Onur Bas", "Ece Polat", "Yusuf Akman", "Zeynep Tunca", "Mehmet Ersoy", "Aslihan Yuce", "Selim Karaca", "Gulcin Ozdemir", "Tuncay Alp", "Nihan Ulusoy", "Serkan Usta", "Ceyda Aydin", "Levent Sari", "Pelin Erol", "Emre Dogan", "Ayse Tekin", "Murat Dincer", "Selda Kaplan", "Kadir Ince", "Ipek Cimen", "Volkan Acar", "Fatma Sezer", "Baris Can", "Pinar Gunes", "Sinan Bulut", "Deniz Yalcin", "Ozan Cetin", "Gokce Bal", "Haluk Tan", "Sibel Guler", "Ferhat Altun", "Dilan Kurtoglu", "Koray Oz", "Yasemin Er", "Eray Turan", "Cansu Gok", "Eren Aksoy", "Sema Bayrak", "Tolga Celik", "Nuray Topal", "Haruto Tanaka"]

#new channels with channels that are orginally from TAC (TACchannels)
new_channels = ["ai-ml", "alliances", "analytics", "appsec", "backend", "brand", "community", "compliance", "content", "controller", "customer-success", "databases", "deal-desk", "dei", "demand-gen", "design-ux", "detections", "devrel", "docs", "ecosystem", "education", "emea", "engineering", "enterprise", "events", "exec", "field-marketing", "finance", "finops", "fpa", "frontend", "general", "growth", "gtm", "hr", "hr-announcements", "hr-emea", "hr-ops", "i18n", "incident", "it-helpdesk", "it-networks", "it-tools", "learning-development", "legal", "marketing", "marketing-ops", "ml", "observability", "observability-marketing", "oltp", "onboarding", "ops", "orchestration", "people-analytics", "people-ops", "platform", "pmo", "pr", "privacy", "procurement", "product", "product-marketing", "project-ai", "project-airflow", "project-arangodb", "project-argo", "project-bentoml", "project-clickhouse", "project-cockroachdb", "project-dask", "project-druid", "project-ecommerce", "project-elasticsearch", "project-flink", "project-grafana", "project-graphdb", "project-hasura", "project-iceberg", "project-influxdb", "project-kafka", "project-loki", "project-lowcode", "project-meilisearch", "project-metabase", "project-milvus", "project-mlflow", "project-nebulagraph", "project-onnxrt", "project-pinot", "project-presto", "project-prestodb", "project-prometheus", "project-qdrant", "project-questdb", "project-ray", "project-redpanda", "project-search", "project-solr", "project-spark", "project-streamdb", "project-supabase", "project-superset", "project-temporal", "project-tgi", "project-tidb", "project-trino", "project-triton", "project-vald", "project-vespa", "project-victoriametrics", "project-vllm", "project-weaviate", "project-webcrawler", "project-yugabytedb", "qa", "rag", "recruiting", "redteam", "reliability", "revops", "revrec", "saas-admin", "sales", "sales-amer", "sales-apac", "sales-emea", "sales-marketing", "sales-sdr", "sales-se", "search", "secops", "security", "security-awareness", "security-grc", "security-tooling", "solutions", "sre", "streaming", "support", "support-escalations", "support-ops", "support-tier1", "support-tier2", "support-tier3", "systems", "tam", "tax", "tech-talk", "timeseries", "total-rewards", "training", "treasury", "video", "web", "workplace"]

#old channels without channels that are originally from TAC (TACchannels)
old_channels = ["community", "compliance", "design", "devops", "devportal", "finance", "frontend", "legal", "ops", "people-ops", "project-ab-testing", "project-alerting", "project-auth", "project-billing", "project-cachelayer", "project-cdnservice", "project-chatops", "project-compliance", "project-crm", "project-datalake", "project-desktopclient", "project-devportal", "project-docsgenerator", "project-documentation", "project-ecommerce", "project-edgecompute", "project-erp", "project-etl", "project-featurestore", "project-imagepipeline", "project-internaltools", "project-janusgraph", "project-legacyadapters", "project-legal", "project-licenseserver", "project-localization", "project-mobileapp", "project-modelhub", "project-monitoring", "project-notification", "project-onboarding", "project-orchestration", "project-paymentgateway", "project-pluginmarketplace", "project-realtimeanalytics", "project-recommendationengine", "project-rnd-sandbox", "project-searchbackend", "project-securityscanner", "project-simulator", "project-telemetry", "project-uxlab", "project-videotranscoder", "qa", "recruiting", "rnd", "security", "sre", "support"]

def extract_channels(xml_file):
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Dictionary: channel -> list of members
    channels_map = defaultdict(list)
    # everybody_set = set()

    # Loop over all members
    channels_map["everybody_channel"]
    for member in root.findall("member"):
        name_tag = member.find("name")
        member_name = name_tag.text.strip() if name_tag is not None else None

        channels_tag = member.find("channels")
        if member_name and channels_tag is not None and channels_tag.text:
            # Split by comma, remove '#'
            channels = [ch.strip()[1:] if ch.strip().startswith("#") else ch.strip()
                        for ch in channels_tag.text.split(",")]

            for ch in channels:
                if member_name not in channels_map[ch]:
                    channels_map[ch].append(member_name)

            # everybody_set.add(member_name)
    
    # channels_map["everybody_channel"] = list(everybody_set)

    return channels_map

if __name__ == "__main__":
    check = "2"
    client = RocketChat(server_url="http://157.230.77.20:3000/")

    output = client.rocketchat_channels_add_role(channel="general", role="owner", full_name="Sarah Johnson")
    with open("result_list1.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(output, ensure_ascii=False))

    

    # output = client.rocketchat_chat_list_messages(user_name="Huang Jie", 
    #                                               lastUpdate="2025-09-19T18:32:25")
    # with open("result_list3.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    if check == "0":
        client = RocketChat(server_url="http://157.230.77.20:3000/")
        output = client.rocketchat_channels_add_role(channel="general", role="owner", full_name="Sarah Johnson")
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channels_add_role(channel="general", role="moderator", user_name="sarah_johnson")
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channels_add_role(channel="general", role="leader", user_name="@sarah_johnson")
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_channels_invite(channel="general", full_names=["Sarah Johnson"])
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channels_invite(channel="general", user_names=["sarah_johnson"])
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channels_invite(channel="general", user_names=["@sarah_johnson"])
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_channels_kick(channel="general", full_name="David Wong")
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_channels_kick(channel="general", user_name="jessica_chen")
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
            output = client.rocketchat_channels_kick(channel="general", user_name="@alex_turner")
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_chat_post_message(text="Hi!", full_name="David Wong")
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_post_message(text="Privit!", user_name="jessica_chen")
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_post_message(text="Bonjour!", user_name="@alex_turner")
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_chat_list_messages(full_name="David Wong")
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_list_messages(user_name="jessica_chen")
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_chat_list_messages(user_name="@alex_turner")
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        output = client.rocketchat_users_delete(full_name="David Wong")
        with open("result_list1.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_users_delete(user_name="jessica_chen")
        with open("result_list2.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))
        output = client.rocketchat_users_delete(user_name="@alex_turner")
        with open("result_list3.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

    # client = RocketChat(server_url="http://157.230.77.20:3000/")
    # output = client.rocketchat_users_list()
    # with open("users_list.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(output, ensure_ascii=False))

    if check == "1":
        TACchannels = ["engineering", "hr-announcements", "product", "project-ai", "project-graphdb", "project-lowcode", "project-search", "project-streamdb", "project-webcrawler",
                    "sales-marketing", "tech-talk"]

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xml_file_path = os.path.join(script_dir, "members_full.xml")
        
        channels_map = extract_channels(xml_file_path)
        client = RocketChat(server_url="http://127.0.0.1:3000")

        # for channel in old_channels: #Delete Old Channels
        #     output = client.rocketchat_channels_delete(channel)

        #add new channels
        for channel in new_channels:
            output = client.rocketchat_channels_create(channel)

        # output = client.rocketchat_channels_delete("everybody_channel")

        for channel in TACchannels:
            output = client.rocketchat_channels_delete(channel)
            output = client.rocketchat_channels_create(channel)

        # output = client.rocketchat_channels_create("everybody_channel")

        for ch, members in channels_map.items():
            if ch == "engineering":
                members_list = ", ".join(f'"{m}"' for m in members)
                print(f'{ch} = [{members_list}]')
                print(f"number of members is {len(members)}")
            if ch == "everybody_channel":
                members_list = ", ".join(f'"{m}"' for m in members)
                print(f'{ch} = [{members_list}]')
                print(f"number of members is {len(members)}")
            output = client.rocketchat_channels_invite(ch, members)
        output = client.rocketchat_channels_list()
        with open("users_list.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False))

        # print(output)

        # output = client.rocketchat_users_list()
        # with open("users_list.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(output, ensure_ascii=False))

        # client = RocketChat(server_url="http://127.0.0.1:3000")
        # channel_users = ["Noel Gray", "Charlotte Gray", "Ella Richardson", "Sonya Gonza", "Iga Schwentec", "Mateo Fuentes", "Alex Tarasenko", "Samir Fawzi", "Kong Mei", "Naima Warsame", "Fotis Argyros", "Volkan Acar"]
        # output = client.rocketchat_channels_invite("community", channel_users)
        # with open("channels_invite_result.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(output, ensure_ascii=False))