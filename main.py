import yaml
import requests
from urllib.parse import urljoin
import json

files = dict()


def ensure_url(url):
    if url not in files:
        files[url] = yaml.load(requests.get(url).text, Loader=yaml.CLoader)

def resolve_path(current_path, new_path):
    result = list()
    if new_path.startswith("#/"):
        result.append(current_path[0])
        result.extend(new_path[2:].split("/"))
    if new_path.startswith("../"):
        if "#/" in new_path:
            result = [urljoin(current_path[0], new_path.split("#/")[0])] + new_path.split("#/")[1]
        else:
            result = [urljoin(current_path[0], new_path)]
    return result
        

def check_references(data, path):
    if isinstance(data, dict):
        for key, value in tuple(data.items()):
            if key == "$ref":
                new_path = resolve_path(path, value)
                return crawler(new_path)


def crawler(path):
    ensure_url(path[0])
    data = files[path[0]]
    for index, item in enumerate(path[1:]):
        new_data = check_references(data[item], path[:index])
        if new_data:
            data[item] = new_data
        data = data[item]
    if isinstance(data, list):
        for index in range(len(data)):
            crawler(path + [index])
    elif isinstance(data, dict):
        for key, value in tuple(data.items()):
            crawler(path + [key])
    return data


url = "https://developer.spotify.com/reference/web-api/open-api-schema.yaml"

with open("result.json", "w") as fobj:
    json.dump(crawler([url]), fobj)
