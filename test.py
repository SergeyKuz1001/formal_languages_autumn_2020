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

from src import Config, algo

import pytest
import os

MaxTime = 300
DataDir = "/DataForFLCourse"
GrammarDir = "grammars"
GraphDir = "graphs"

def config_factory():
    TestDir = "FullGraph" # from ['FullGraph', 'MemoryAliases', 'SparseGraph', 'WorstCase']
    for graph_file in os.listdir(os.path.join(DataDir, TestDir, GraphDir)):
        global_config = Config.from_args({'data_base': os.path.join(DataDir, TestDir, GraphDir, graph_file)})
        global_config['data_base']
        for grammar_file in os.listdir(os.path.join(DataDir, TestDir, GrammarDir)):
            local_config = global_config.copy()
            local_config._args['context_free_query_file'] = os.path.join(DataDir, TestDir, GrammarDir, grammar_file)
            local_config['context_free_query']
            yield local_config
            del local_config
        del global_config

@pytest.mark.timeout(MaxTime)
@pytest.mark.parametrize('config', config_factory())
def test(config):
    print(config._args['data_base_file'], config._args['context_free_query_file'])
    algo.cfpq(config) # from [algo.cfpq, algo.cfpq_bm, algo.cfpq_tp]
    assert True
