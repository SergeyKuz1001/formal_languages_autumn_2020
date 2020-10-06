# Formal Languages Autumn 2020

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FSergeyKuz1001%2Fformal_languages_autumn_2020%2Fbadge%3Fref%3Dmaster&style=flat)](https://actions-badge.atrox.dev/SergeyKuz1001/formal_languages_autumn_2020/goto?ref=master)

Repository for hometasks of the cource "Formal Languages"

## Task5

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FSergeyKuz1001%2Fformal_languages_autumn_2020%2Fbadge%3Fref%3Dtask5&style=flat)](https://actions-badge.atrox.dev/SergeyKuz1001/formal_languages_autumn_2020/goto?ref=task5)

## Task4

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FSergeyKuz1001%2Fformal_languages_autumn_2020%2Fbadge%3Fref%3Dtask4&style=flat)](https://actions-badge.atrox.dev/SergeyKuz1001/formal_languages_autumn_2020/goto?ref=task4)

Fourth hometask of the cource "Formal Languages"

### Description

I have united in this task previous tasks and add CYK and CFPQ. I have also updated
old tests from previous tasks, so they can testing into updated program.

### `main.py`

```
usage: main.py [-h] [-c file] [--rq file] [--cfq file] [-d file]

optional arguments:
  -h, --help            show this help message and exit
  -c file, --config file
                        json configuration file
  --rq file, --regular-query file
                        file with query as regular expression
  --cfq file, --context-free-query file
                        file with query as context free grammar
  -d file, --data-base file
                        file with description of data base
```

### Configuration file

It is json file with such possible fields:

 * `data_base_lists` - list of `V_from`s, `S`s and `V_to`s lists
 * `data_base_file` - name of file with data base in the same directory as this configuration file
 * `regular_query_regex` - string of regular expression
 * `regular_query_file` - name of file with regular expression in the same directory as this
configuration file
 * `context_free_query_text` - string of productions `{head} -> {body}`, joined by '\n'
 * `context_free_query_file` - name of file with lines of productions `{head} {body}`
 * `input_vertexes`  - list of vertexes, from which will be start all paths in resulting set. In
other words, all pairs in the resulting set will have first element from `input_vertexes` list
 * `output_vertexes` - the same as `input_vertexes` but all paths will be finished in vertexes from
`output_vertexes` list

### Minimal working set

1) `data_base_lists` or `data_base_file` in configuration file or data base file as argument
2) `regular_query_regex`, `regular_query_file`, `context_free_query_text` or `context_free_query_text`
   in configuration file or query file as argument `--rq` or `--cfq`

## Task2

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FSergeyKuz1001%2Fformal_languages_autumn_2020%2Fbadge%3Fref%3Dtask2&style=flat)](https://actions-badge.atrox.dev/SergeyKuz1001/formal_languages_autumn_2020/goto?ref=task2)

Second hometask of the cource "Formal Languages"

### How to run the task

For building a docker container run:
```
docker build -t task2 .
```

You can run the container in interactive mode:
```
docker run --rm -it task2
```

Now you can run:

 * tests through `pytest`:

   ```
   # pytest main_test.py
   ```

 * `main.py` with file of data base and file of query in regular expression and/or
configuration file:

   ```
   # ./main.py -q <file_of_query> -d <file_of_data_base>
   ```
   
   or
   
   ```
   # ./main.py -c <configuration_file>
   ```
   
   or even
   
   ```
   # ./main.py -c <configuration_file> -q <file_of_query> -d <file_of_data_base>
   ```

### What is `main.py`?

It is program which takes information about data base and request in regular expression and
print on the screen a set of pair of data base vertexes, between which a path, which is allowed
by regular expression, exist.

### File of data base

It is text file which contains a set of triple `{V_from} {S} {V_to}` which define an edge in
data base from `V_from` vertex to `V_to` vertex by symbol `S`. For example
  
   ```
   0 a 1
   0 b 2
   1 c 2
   2 a 0
   ```

### File of query

It is text file with single line of regular expression, format of which is the same as
regular expressions in `pyformlang` library.

### Configuration file

It is json file with such possible fields:

 * `data_base_lists` - list of `V_from`s, `S`s and `V_to`s lists
 * `data_base_file`  - name of file with data base in the same directory as this configuration file
 * `query_regex`     - string of regular expression
 * `query_file`      - name of file with regular expression in the same directory as this
configuration file
 * `input_vertexes`  - list of vertexes, from which will be start all paths in resulting set. In
other words, all pairs in the resulting set will have first element from `input_vertexes` list
 * `output_vertexes` - the same as `input_vertexes` but all paths will be finished in vertexes from
`output_vertexes` list

### Minimal working set

1) `data_base_lists` or `data_base_file` in configuration file or data base file as argument
2) `query_regex` or `query_file` in configuration file or query file as argument

## Task1

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FSergeyKuz1001%2Fformal_languages_autumn_2020%2Fbadge%3Fref%3Dtask1&style=flat)](https://actions-badge.atrox.dev/SergeyKuz1001/formal_languages_autumn_2020/goto?ref=task1)

First hometask of the cource "Formal Languages"

### How to run the task

For building a docker container run:
```
docker build -t task1 .
```

Now you can run the container in interactive mode:
```
docker run --rm -it task1 ipython
```
