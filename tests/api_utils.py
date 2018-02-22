import requests

def api_clear(baseUrl):
    r = requests.post(baseUrl+"/data/clear/")
    return r


def api_add(baseUrl, compound):
    r = requests.post(baseUrl+"/data/add/", json=compound)
    return r


def api_batchadd(baseUrl, compounds):
    r = requests.post(baseUrl+"/data/batchadd/", json=compounds)
    return r


def api_search(baseUrl, filter_dict):
    r = requests.post(baseUrl+"/data/search/", json=filter_dict)
    return r

