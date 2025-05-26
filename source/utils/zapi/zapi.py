import aiohttp
import asyncio
import json
import requests
import requests.cookies
from pprint import pprint

import aiohttp.client_exceptions
from bs4 import BeautifulSoup
import requests.auth

from utils.zapi.tools import Output
from utils.logger import get_bot_logger
from config import CURRENT_CONFIG


config = CURRENT_CONFIG
logger = get_bot_logger()

class ZabbixAPI:
    _api_headers = {"Content-Type": "application/json"}
    _auth_postfix = '/index_http.php'
    _api_postfix = '/api_jsonrpc.php'
    _graph_postfix = '/chart.php'
    output = Output()
    
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
    
    def get_hosts_by_hostgroups_id(self, ids: list):
        url = self._url + self._api_postfix
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {"groupids": ids},
                "output": ["hostid", "host", "name"],
                "selectInterfaces": ["ip", "port", "dns"]
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
                    data = resp.json().get('result')
                    
                    for item in data:
                        interfaces = item.pop('interfaces')
                        item.update(*interfaces)
                    
                    return data
                raise requests.exceptions.ConnectionError(f'Error get result from {url}.')
    
    def get_availability_report(self):
        url = self._url + f"/report2.php?mode=1&from={config.availability_report_pediod}&to=now&filter_groupid=0&filter_templateid=10564&tpl_triggerid=23176&hostgroupid=0&filter_set=1"

        with requests.Session() as session:
            self._get_cookies(session)
            
            with session.get(url) as resp:
                if resp.ok:
                    soup = BeautifulSoup(resp.content, "html.parser")
                else:
                    logger.error(resp.status_code)
                    return

        table = soup.find("table", attrs={"class": "list-table"})

        t_headers_row = table.find("thead").find_all("th")
        t_headers_row = [
            head.string 
            for head in t_headers_row 
            if head.string in ('Host', 'Name', 'Ok')
        ]

        t_lines_rows = [row.find_all("td") for row in table.find("tbody")]

        for line_idx, line in enumerate(t_lines_rows[:]):
            line.pop(2)
            line.pop(-1)
        
            for el_idx, el in enumerate(line[:]):
                t_lines_rows[line_idx][el_idx] = el.string

        return [t_headers_row, *t_lines_rows]