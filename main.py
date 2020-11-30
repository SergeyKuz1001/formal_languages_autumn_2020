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

from src import Config
from src.algo import cyk

from argparse import ArgumentParser
from sys import stdin, exit

def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", metavar = "file", type = str,
                        dest = "config", help = "json configuration file")
    parser.add_argument("-g", "--grammar", metavar = "file", type = str,
                        dest = "pretty_context_free_query", required = True,
                        help = "file with CFG of query language")
    parser.add_argument("-p", "--program", metavar = "file", type = str,
                        dest = "word",
                        help = "file with program on query language")
    args = dict()
    for k, v in vars(parser.parse_args()).items():
        if not v is None:
            args[k] = v
    config = Config.from_args(args)
    if 'word' not in args:
        config._objs['word'] = stdin.read()
    if cyk(config):
        print('Correct')
        exit(0)
    else:
        print('Incorrect')
        exit(1)

if __name__ == "__main__":
    main()
