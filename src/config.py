#  Copyright 2020 Sergey Kuzivanov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Any, Dict, Optional
import json
import os

class Config:
    def __init__(self):
        self._dict: Dict[str, Any] = dict()
        self._path: Optional[str] = None

    def __contains__(self, key: str) -> bool:
        return key in self._dict

    def __getitem__(self, key: str) -> Any:
        return self._dict.get(key)

    @property
    def path(self):
        return self._path

    @classmethod
    def from_dict(cls, _dict: Dict[str, Any]) -> "Config":
        res = Config()
        if 'config' in _dict:
            res._path = os.path.dirname(os.path.abspath(_dict['config']))
            with open(_dict['config'], 'r') as config_file:
                res._dict = json.load(config_file)
        if 'data_base' in _dict:
            res._dict['data_base_file'] = _dict['data_base']
        if 'query' in _dict:
            res._dict['query_file'] = _dict['query']
        return res

    @classmethod
    def from_args(cls, args) -> "Config":
        return cls.from_dict(vars(args))
