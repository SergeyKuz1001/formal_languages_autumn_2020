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

FROM graphblas/pygraphblas-minimal:v3.3.3
RUN pip3 install pyformlang
RUN apt-get update;\
    apt-get install -y openjdk-11-jdk
RUN cd /usr/local/lib;\
    wget https://www.antlr.org/download/antlr-4.9-complete.jar
ENV CLASSPATH=".:/usr/local/lib/antlr-4.9-complete.jar:$CLASSPATH"
RUN pip3 install graphviz
RUN apt-get update;\
    apt-get install -y evince
RUN pip3 install antlr4-python3-runtime
RUN apt-get update;\
    apt-get install -y graphviz
WORKDIR /
COPY . .
