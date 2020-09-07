FROM graphblas/pygraphblas-minimal:3.4.0
RUN pip3 install pyformlang
WORKDIR /
ADD tests/ /
