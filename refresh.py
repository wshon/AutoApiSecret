# -*- coding: UTF-8 -*-
import logging
import os
import sys

import requests as req

# 先注册azure应用,确保应用有以下权限:
# files: Files.Read.All、Files.ReadWrite.All、Sites.Read.All、Sites.ReadWrite.All
# user:  User.Read.All、User.ReadWrite.All、Directory.Read.All、Directory.ReadWrite.All
# mail:  Mail.Read、Mail.ReadWrite、MailboxSettings.Read、MailboxSettings.ReadWrite
# 注册后一定要再点代表xxx授予管理员同意,否则outlook api无法调用

LOGIN_URI = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
REFRESH_TOKEN_PATH = sys.path[0] + r'/refresh_token.txt'
TRY_COUNT_MAX = 3

# ENV
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')


class Refresh:
    logger = logging.getLogger(__name__)

    @property
    def refresh_token(self):
        try:
            self.logger.info(f'read refresh_token from file: {REFRESH_TOKEN_PATH}')
            with open(REFRESH_TOKEN_PATH, "r+") as f:
                refresh_token = f.read()
            self.logger.debug(f'refresh_token: {refresh_token}')
        except FileNotFoundError:
            self.logger.exception(f'file {REFRESH_TOKEN_PATH} not found')
            refresh_token = REFRESH_TOKEN
        return refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        self.logger.info(f'save refresh_token to file: {REFRESH_TOKEN_PATH}')
        with open(REFRESH_TOKEN_PATH, 'w+') as f:
            f.write(value)

    @property
    def access_token(self):
        for _ in range(TRY_COUNT_MAX):
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': 'http://localhost:53682/'
            }
            self.logger.debug(data)
            for _ in range(TRY_COUNT_MAX):
                self.logger.info(f'request access_token')
                try:
                    rsp = req.post(LOGIN_URI, data=data, headers=headers)
                except Exception:
                    self.logger.exception(f'access_token request error')
                    continue
                if rsp.status_code == 200:
                    self.logger.info(f'access_token request success')
                    content = rsp.json()
                    self.logger.debug(content)
                    new_refresh_token = content['refresh_token']
                    access_token = content['access_token']
                    self.logger.debug(f'access_token: {access_token}')
                    self.logger.debug(f'refresh_token: {new_refresh_token}')
                    self.refresh_token = new_refresh_token
                    return access_token
                elif rsp.status_code == 400:
                    self.logger.info(f'access_token request false')
                    self.logger.error(rsp.json())
                    content = rsp.json()
                    if content['error'] == 'invalid_grant':
                        self.refresh_token = REFRESH_TOKEN
                        break
                    return None

    def run(self):
        headers = {
            'Authorization': self.access_token,
            'Content-Type': 'application/json'
        }
        with open("api_list", encoding='UTF-8') as fp:
            for line in fp.readlines():
                api_path = line.strip()
                if api_path.startswith('#'):
                    continue
                for _ in range(TRY_COUNT_MAX):
                    # noinspection PyBroadException
                    try:
                        self.logger.info(f'start request api: {api_path}')
                        if req.get(api_path, headers=headers).status_code == 200:
                            self.logger.info(f'api request：{api_path} success')
                            break
                        else:
                            self.logger.warning(f'api request：{api_path} fail')
                    except Exception:
                        self.logger.exception(f'api request：{api_path} error')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
        level=logging.NOTSET
    )
    # noinspection PyBroadException
    try:
        refresh = Refresh()
        refresh.run()
    except Exception:
        logging.exception('system error')
