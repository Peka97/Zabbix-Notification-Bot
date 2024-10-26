#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import logging
import json
from pprint import pprint

import aiohttp
# import requests
# import requests.auth
# from requests.exceptions import JSONDecodeError
# from bs4 import BeautifulSoup
from aiogram.types import User
import aiohttp.client_exceptions
import aiohttp.http_exceptions
import aiohttp.web_exceptions

# from .tools import Output, parse_interfaces
# from config import PersonalConfig, ChannelConfig
from config import CURRENT_CONFIG


config = CURRENT_CONFIG


class ZabbixAPI:
    """Description
    ------
    Модель взаимодействия с API системы мониторинга Zabbix.
    Авторизация в системе проходит через специальный `token`, который можно
    получить после прохождения авторизации через `login` и `password`.

    Methods:
    ------
        * `get_host_interfaces`: Получение интерфейсов хоста через имя хоста;
        * `get_hosts_interfaces_by_group_id`: Получение интерфейсов хоста через ID группы;
        * `get_hosts_by_group_name`: Получение хостов через имя группы;
        * `get_group_id_by_group_name`: Получение ID группы через имя группы.
    """
    headers = {"Content-Type": "application/json"}
    auth_postfix = '/index_http.php'
    api_postfix = '/api_jsonrpc.php'
    graph_postfix = '/chart.php'
    # output = Output()

    def __init__(self):
        """Description
        ------
        Создание и возврат экземпляра `ZabbixAPI`.
        Проходит авторизацию в API системы мониторинга Zabbix.

        Args:
        ------
            * `url` (str): URL сервера Zabbix в формате "http://127.0.0.1/zabbix/";
            * `login` (str): Логин в системе мониторинга Zabbix;
            * `password` (str): Пароль в системе мониторинга Zabbix.
        """
        self._auth_url = f"http://{CURRENT_CONFIG.zabbix_api_internal_ip}/index_http.php"
        self._url = f"http://{CURRENT_CONFIG.zabbix_api_internal_ip}/api_jsonrpc.php"
        self._login = CURRENT_CONFIG.zabbix_bot_login
        self._password = CURRENT_CONFIG.zabbix_bot_pass
        self._auth()

    async def _auth(self) -> None:
        """Description
        ------
        Авторизация в системе мониторинга Zabbix средствами API.

        После отправки `login` и `password` возвращается `token`, который
        используется в дальнейших обращениях к API.

        Args:
        ------
            * `login` (str): _description_
            * `password` (str): _description_

        Raises:
        ------
            * ValueError: Неверный логин или пароль
        """

        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": self._login,
                "password": self._password,
            },
            "id": 1,
        }

        # Ask cookie
        async with aiohttp.ClientSession() as session:
            async with session.post(self._auth_url, data=json.dumps(data)) as resp:
                if resp.ok:
                    self._cookies = resp.cookies

    def get_group_id_by_group_name(
        self, group_name: str | list[str]
    ) -> list[str] | None:
        """Description
        ------
        Получение ID группы  по имени группы.
        Устройство API позволяет передать массив ID и получить массив имён.

        Args:
        ------
            * `group_name` (str | list[str]): имя группы или массив имён групп.

        Returns:
        ------
            * list[str] | None: список ID групп, удовлетворающих критериям запроса.
        """

        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "filter": {"name": group_name},
                "output": [
                    # Возможные значения: ["groupid", "name", "flags", "uuid"]
                    "groupid",
                    "name",
                ],
            },
            "auth": self._token,
            "id": 1,
        }

        res = requests.get(self._url, data=json.dumps(data), headers=self.headers)
        result = res.json().get("result")
        try:
            group_ids = [field["groupid"] for field in result]

            if not group_ids:
                return

        except Exception as err:
            logging.error(err)
            return

        return group_ids

    def get_hosts_interfaces_by_group_id(
        self, group_ids: str | list[str]
    ) -> list[dict] | None:
        """Description
        ------
        Получение данных хостов с инвентаризацией через ID групп.
        Инвентаризация распаковывается за счёт метода `ZabbitAPI`.

        Args:
        ------
            * `group_ids` (str | list[str]): ID группы или их массив.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        if not group_ids:
            return
        if isinstance(group_ids, str):
            group_ids = [
                group_ids,
            ]

        result = []

        for group_id in group_ids:
            data = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "groupids": [group_id],
                    "output": ["hostid", "host", "name"],
                    "selectInterfaces": ["ip", "port", "dns"],
                    "selectInventory": config.inventory_fields,
                },
                "auth": self._token,
                "id": 1,
            }

            res = requests.get(self._url, data=json.dumps(data), headers=self.headers)
            group_info = res.json().get("result")
            group_info = parse_interfaces(group_info)

            [
                result.append(host_info)
                for host_info in group_info
                if host_info not in result
            ]

        return result

    def get_host_interfaces(self, host_name: str | list[str]) -> list[dict] | None:
        """Description
        ------
        Получение инвентаризации хостов по их именам.
        Устройство API позволяет передать массив имён хостов и получить их инвентаризацию.

        Args:
        ------
            * `host_name` (str | list[str]): имя хоста или массив с именами хостов.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {"host": host_name},
                    "output": ["hostid", "host", "name"],
                    "selectInterfaces": ["ip", "port", "dns"],
                    "selectInventory": config.inventory_fields,
                },
                "auth": self._token,
                "id": 1,
            }
        )

        res = requests.get(self._url, data=data, headers=self.headers)
        info = res.json().get("result")
        info = parse_interfaces(info)

        return info

    def get_hosts_by_group_name(self, group_names: str | list[str]) -> list[dict]:
        """Description
        ------
        Получение хостов по имени группы.
        Не содержит данных инвентаризации и интерфейсов.

        Args:
        ------
            * `group_names` (str | list[str]): имя группы или массив имён групп.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        if isinstance(group_names, str):
            group_names = [
                group_names,
            ]

        if not group_names:
            return

        result = []

        for gr_name in group_names:
            data = {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "filter": {"name": gr_name},
                    "selectHosts": ["hostid", "host", "name", "description"],
                },
                "auth": self._token,
                "id": 1,
            }

            res = requests.get(self._url, data=json.dumps(data), headers=self.headers)

            try:
                res = res.json().get("result")[0].get("hosts")

            except Exception as err:
                logging.error(err)

            else:
                [
                    result.append(host_info)
                    for host_info in res
                    if host_info not in result
                ]

        return result

    async def get_graph(self, settings: dict) -> tuple[bytes, str, int]:
        """Description
        ------
        Функция получения графика по запросу к Zabbix.

        Структура возвращаемого кортежа:
            - content (bytes): График
            - url (str): Ссылка на график
            - status code (int): Код статуса запроса

        Args:
        ------
            * `settings` (dict): настройки из шаблона Zabbix

        Returns:
        ------
            * tuple[bytes, str, int]: контент по графику
        """

        url = self._url + self.graph_postfix
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url,params=params) as resp:
                return await resp.content

        # with requests.Session() as s:
        #     s.post(
        #         f"http://{config.zabbix_api_ip_or_dns}:{config.zabbix_api_port}/zabbix/",
        #         data,
        #     )

        #     resp = s.get(
        #         url,
        #         params=params,
        #         data={"auth": self._token},
        #         cookies=self._cookies,
        #     )

        #     if "You must login to view this page" in resp.text:
        #         return None, None, None

        #     return resp.content, resp.url, resp.status_code

    def confirm_problem(self, settings: dict, user: User) -> int:
        """Description
        ------
        Функция, подтверждающая проблему в Zabbix.

        Args:
        ------
            * `settings` (dict): cловарь с параметрами для поиска триггера в Zabbix;
            * `user` (User): экземпляр пользователя Telegram.

        Returns:
        ------
            * status code (int): Код статуса запроса
        """

        try:
            event_id = settings["eventid"]
            data = {
                "jsonrpc": "2.0",
                "method": "event.acknowledge",
                "params": {
                    "eventids": event_id,
                    "action": 6,
                    "message": f"Problem confirm by {user.last_name} {user.first_name} from Telegram",
                },
                "auth": self._token,
                "id": 1,
            }

            response = requests.post(
                self._url, data=json.dumps(data), headers=self.headers
            )

            if response.status_code == 200:
                logging.info(f"Problem confirmed: {response.content}")
            else:
                logging.error(
                    f"Problem NOT confirmed: Status Code: {response.status_code} | Content: {response.content}"
                )

            return response.status_code

        except Exception as err:
            logging.error(err)

    def get_templates(self):
        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                # 'selectGroups': 'extend',
                "selectTemplateGroups": "extend",
                "selectDiscoveryRule": "extend",
                "selectItems": "extend",
                "selectGraphs": "extend",
                "selectTriggers": "extend",
                "selectApplications": "extend",
                "selectMacros": "extend",
                "selectScreens": "extend",
                "selectTemplates": "extend",
            },
            "auth": self._token,
            "id": 1,
        }

        response = requests.post(self._url, data=json.dumps(data), headers=self.headers)

        if response.status_code == 200:
            pprint(response.json())
        else:
            raise ValueError(
                f"Status Code: {response.status_code} | Content: {response.content}"
            )

    def get_api_version(self):
        data = {"jsonrpc": "2.0", "method": "apiinfo.version", "params": [], "id": 1}
        response = requests.get(self._url, data=json.dumps(data), headers=self.headers)
        if response.status_code == 200:
            pprint(response.json())
        else:
            raise ValueError(
                f"Status Code: {response.status_code} | Content: {response.content}"
            )

    def get_availability_report(self):
        resp = requests.post(
            f"http://{config.zabbix_api_ip_or_dns}/zabbix/index.php?name={config.zabbix_api_login}&password={config.zabbix_api_pass}&enter=Sign%20in"
        )
        cookies = resp.cookies

        url = f"http://{config.zabbix_api_ip_or_dns}/zabbix/report2.php?mode=1&from=now-1h&to=now&filter_groupid=0&filter_templateid=10564&tpl_triggerid=23176&hostgroupid=0&filter_set=1"
        resp = requests.get(url, cookies=cookies)

        if resp.status_code != 200:
            logging.error(f"Status Code: {resp.status_code}")
            return None

        soup = BeautifulSoup(resp.content, "html.parser")

        table = soup.find("table", attrs={"class": "list-table"})

        t_headers_row = table.find("thead").find_all("th")
        t_headers_row.pop(2)
        t_headers_row.pop(3)
        t_headers_row = [head.string for head in t_headers_row]

        t_lines_rows = [row.find_all("td") for row in table.find("tbody")]

        for line_idx, line in enumerate(t_lines_rows[:]):
            line.pop(2)
            line.pop(3)

            for el_idx, el in enumerate(line[:]):
                t_lines_rows[line_idx][el_idx] = el.string

        data = []
        data.append(t_headers_row)
        data.extend(t_lines_rows)

        return data

    def test(self):
        print("Test")
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {"host": "verbalvoyager"},
                    "output": ["hostid", "host", "name"],
                    "selectInterfaces": ["ip", "port", "dns"],
                    "selectInventory": config.inventory_fields,
                },
                "auth": self._token,
                "id": 1,
            }
        )

        resp = requests.get(self._url, data=data, headers=self.headers)
        try:
            pprint(resp.json())
        except JSONDecodeError:
            pprint(resp.text)


if __name__ == "__main__":
    pass

    zapi = ZabbixAPI(
        config.zabbix_api_ip_or_dns,
        config.zabbix_api_port,
        config.zabbix_api_login,
        config.zabbix_api_pass,
    )

    ### Инвентаризация по имени хоста:
    # result = zapi.get_host_interfaces(["Zabbix server", "test"])
    # zapi.output.to_console(result)
    # zapi.output.to_csv(result)

    # print()

    ### Инвентаризация по группе хоста:
    # Ищем ID группы
    # ids = zapi.get_group_id_by_group_name(["Discovered hosts", "Zabbix servers", "qq"])
    # # Выводим все хосты внутри группы
    # result = zapi.get_hosts_interfaces_by_group_id(ids)
    # zapi.output.to_console(result)
    # # zapi.output.to_csv(result)
    # zapi.output.to_excel(result)

    # print()

    ### Пачка хостов по имени группы без инвентаризации
    # result = zapi.get_hosts_by_group_name(["Discovered hosts", "Zabbix servers", "qq"])
    # zapi.output.to_console(result)
    # zapi.output.to_csv(result)