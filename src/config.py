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

from typing import Any, Dict
import json

class Config:
    def __init__(self):
        self._dict: Dict[str, Any] = dict()

    def __contains__(self, key: str) -> bool:
        return key in self._dict

    def __getitem__(self, key: str) -> Any:
        return self._dict.get(key)

    @classmethod
    def from_args(cls, args) -> "Config":
        res = Config()
        if args.config != None:
            res._dict = json.load(args.config)
        if args.data_base != None:
            res._dict['data_base_file'] = args.data_base
        if args.query != None:
            res._dict['query_file'] = args.query
        return res
