#!/bin/python3.8

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

from src import Request, Config

from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", metavar = "file", type = str,
                        dest = "config", help = "json configuration file")
    parser.add_argument("--rq", "--regular-query", metavar = "file",
                        type = str, dest = "regular_query",
                        help = "file with query as regular expression")
    parser.add_argument("--cfq", "--context-free-query", metavar = "file",
                        type = str, dest = "context_free_query",
                        help = "file with query as context free grammar")
    parser.add_argument("-d", "--data-base", metavar = "file", type = str,
                        dest = "data_base",
                        help = "file with description of data base")
    args = vars(parser.parse_args())
    config = Config.from_args(args)
    request = Request.from_config(config)
    print(request.execute())

if __name__ == "__main__":
    main()
