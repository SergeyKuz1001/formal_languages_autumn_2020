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

from src import Request, DataBase, Query

from typing import Tuple
from functools import reduce
import pytest
import os
import json
import random
import operator

TEST_DIR = os.path.join(os.path.dirname(
        os.path.abspath(__file__)),
        'refinedDataForRPQ'
    )
# uncomment one of this string
# I had tested really so because didn't want to take much memory
#DATA_BASE_SETS = ['LUBM300']
#DATA_BASE_SETS = ['LUBM500']
#DATA_BASE_SETS = ['LUBM1M']
#DATA_BASE_SETS = ['LUBM1.5M']
#DATA_BASE_SETS = ['LUBM1.9M']
DATA_BASE_DIRS = [os.path.join(TEST_DIR, data_base_set)
        for data_base_set in DATA_BASE_SETS]
DATA_BASE_FILES = [os.path.join(DATA_BASE_DIRS[i], DATA_BASE_SETS[i] + '.txt')
        for i in range(len(DATA_BASE_SETS))]
DATA_BASES = list(map(DataBase.from_file, DATA_BASE_FILES))
DATA_BASE_QUERIES = [os.path.join(data_base_dir, 'regexes')
        for data_base_dir in DATA_BASE_DIRS]
TEST_SETS = reduce(operator.add,
        [
            list(enumerate(map(
                lambda query_file:
                    (
                        DATA_BASES[i],
                        os.path.join(DATA_BASE_QUERIES[i], query_file)
                    ),
                os.listdir(DATA_BASE_QUERIES[i])
            )))
            for i in range(len(DATA_BASE_SETS))
        ]
    )

@pytest.mark.parametrize('test_set', TEST_SETS)
def test(test_set):
    test_num, (data_base, query_file) = test_set
    request = Request()
    request.data_base = data_base
    request.query = Query.from_file(query_file)
    print(test_num, query_file, request.count_reachable_pairs())
    assert True
