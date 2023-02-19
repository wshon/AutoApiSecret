# -*- coding: UTF-8 -*-
import json
import os
import sys
import urllib.request

from api_list import API_LIST

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]

REQUEST_COUNT_MAX = 3

# Cache
REFRESH_TOKEN_PATH = CURRENT_PATH + r'/refresh_token.txt'

# Env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

def load_refresh_token():
    try:
        print(f'read refresh_token from file: {REFRESH_TOKEN_PATH}')
        with open(REFRESH_TOKEN_PATH, "r+") as f:
            refresh_token = f.read()
        print(f'refresh_token: {refresh_token}')
    except FileNotFoundError:
        print(f'file {REFRESH_TOKEN_PATH} not found, load from env')
        refresh_token = REFRESH_TOKEN
        print(f'refresh_token: {refresh_token}')
    return refresh_token

def save_refresh_token(refresh_token):
    print(f'save refresh_token to file: {REFRESH_TOKEN_PATH}')
    with open(REFRESH_TOKEN_PATH, 'w+') as f:
        f.write(refresh_token)

def request_token(client_id, client_secret, refresh_token):
    url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    headers = {
        'Content-Type':'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret':client_secret,
        'refresh_token': refresh_token,
        'redirect_uri':'http://localhost:53682/'
    }
    print(f'request url: {url}')
    data = urllib.parse.urlencode(data).encode('utf8')
    req = urllib.request.Request(url, data, headers)
    try:
        rsp_c = urllib.request.urlopen(req).read()
        try:
            rsp_json = json.loads(rsp_c)
            refresh_token = rsp_json['refresh_token']
            access_token = rsp_json['access_token']
            return refresh_token, access_token
        except json.decoder.JSONDecodeError:
            print(f'rsp json error: {rsp_c.decode()}')
            return None, None
    except urllib.error.HTTPError as e:
        err_c = e.read()
        try:
            err_json = json.loads(err_c)
            print(f'request error: [{err_json["error"]}] {err_json["error_description"]}')
        except json.decoder.JSONDecodeError:
            print(f'request error: {e.code} {e.reason}')
        return None, None
    pass

def request_api(url, access_token):
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }
    print(f'api {url} request...')
    req = urllib.request.Request(url, headers=headers)
    try:
        rsp = urllib.request.urlopen(req)
        print(f'api success: {rsp.reason}')
    except urllib.error.HTTPError as e:
        err_c = e.read()
        try:
            err_json = json.loads(err_c)
            print(f'api error: {err_json["error"]["message"]}')
        except json.decoder.JSONDecodeError:
            print(f'api error: {e.code} {e.reason}')
    pass

def main():
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    refresh_token = load_refresh_token()
    refresh_token, access_token = request_token(client_id, client_secret, refresh_token)
    print(f'client_id {client_id}')
    print(f'client_secret {client_secret}')
    print(f'refresh_token {refresh_token}')
    if access_token is None:
        return
    save_refresh_token(refresh_token)
    for round in range(REQUEST_COUNT_MAX):
        print(f'# api request round {round+1} start...')
        for api in API_LIST:
            request_api(api, access_token)
            pass
        print(f'# api request round {round+1} done.')

if __name__ == '__main__':
    main()
