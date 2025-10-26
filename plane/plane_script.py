from methods import Plane
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import os

if __name__ == "__main__":
    check = "2"
    i = 0
    #client = Plane(server_url="http://157.230.77.20:8091/")
    client = Plane(api_key="plane_api_83f868352c6f490aba59b869ffdae1cf", server_url="http://127.0.0.1:8091/")
    output = client.list_projects()
    with open(f"result_list{i}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(output, ensure_ascii=False))
    i+=1
    #output = client.create_project(name="", identifier="", description="") #I need to come out with id that is unique
    #output = client.create_issue()
