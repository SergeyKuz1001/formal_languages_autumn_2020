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

from src import Config

import json
import os
from typing import List, Tuple, Any, Callable

def simple_test(test_dir: str,
                test_files: List[Tuple[str, str]],
                algo: Callable[[Config], Any],
                answer_from_json: Callable[[Any], Any]
               ) -> bool:
    args = dict()
    for file_name, arg_name in test_files:
        full_file_name = os.path.join(test_dir, file_name)
        if os.path.exists(full_file_name):
            args[arg_name] = full_file_name
    config = Config.from_args(args)
    result = algo(config)
    with open(os.path.join(test_dir, 'answer.json'), 'r') as answer_file:
        answer = answer_from_json(json.load(answer_file))
    return result == answer

