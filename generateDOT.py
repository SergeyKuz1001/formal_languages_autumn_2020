#!/bin/python3

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

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from query_langLexer import query_langLexer
from query_langParser import query_langParser
from query_langDOTGenerator import query_langDOTGenerator

def main():
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
    else:
        input_stream = InputStream(sys.stdin.read())
    lexer = query_langLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = query_langParser(token_stream)
    generator = query_langDOTGenerator(parser)
    generator.generateDOT('Parse tree')

if __name__ == '__main__':
    main()