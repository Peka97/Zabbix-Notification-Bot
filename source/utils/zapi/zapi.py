import aiohttp
import asyncio
import json
import requests
import requests.cookies

import aiohttp.client_exceptions
import requests.auth

from config import CURRENT_CONFIG


config = CURRENT_CONFIG

class ZabbixAPI:
    _api_headers = {"Content-Type": "application/json"}
    _auth_postfix = '/index_http.php'
    _api_postfix = '/api_jsonrpc.php'
    _graph_postfix = '/chart.php'
    
    def __init__(self):
        self._url = f"http://{CURRENT_CONFIG.zabbix_api_internal_ip}"
        self._login = CURRENT_CONFIG.zabbix_bot_login
        self._password = CURRENT_CONFIG.zabbix_bot_pass
    
    def _get_cookies(self, session: requests.Session):
        auth = requests.auth.HTTPBasicAuth(
            self._login, self._password
        )
        with session.post(
            self._url + self._auth_postfix,
            auth=auth
        ) as resp:
            if resp.ok:
                session.cookies.set('zbx_session', resp.cookies.get('zbx_session'))
                return session
            raise requests.exceptions.ConnectionError("Wrong login or password.")

    def get_graph(self, settings: dict) -> tuple[bytes, str, int]:
        url = self._url + self._graph_postfix
        headers = {
        "Content-Type": "image/png"
        }
        params = {
            "from": f"now-{config.period}",
            "to": "now",
            "width": f"{config.graph_width}",
            "height": f"{config.graph_height}",
            "itemids[0]": f"{settings['itemid']}",
            "profileIdx": "web.item.graph.filter",
            "legend": "1",
            "showtriggers": "1",
            "showworkperiod": "1",
        }
        
        with requests.Session() as session:
            self._get_cookies(session)
            
            with session.get(
                url,
                headers=headers,
                params=params
            ) as resp:
                if resp.ok:
                    return resp.content
                
                raise requests.exceptions.ConnectionError(f'Graph for "item ID {settings['itemid']}" not found.')
    
    def get_all_hostgroups(self):
        url = self._url + self._api_postfix
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend"
                # "filter": {
                #     "name": "karasev/verbalvoyager"
                # }
            },
            "id": 1
        }
        with requests.Session() as session:
            self._get_cookies(session)
            with session.get(
                url,
                headers=self._api_headers,
                data=json.dumps(data)
            ) as resp:
                if resp.ok:
                    return resp.json().get('result')
                raise requests.exceptions.ConnectionError(f'Error get result from {url}.')