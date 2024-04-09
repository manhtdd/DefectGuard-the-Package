#!/bin/bash

# docker import img.tar manhtdd/srcml:latest
docker run -it \
    -v $(pwd):/app \
    -v $(pwd)/input:/input \
    --name tan-srcml \
    2d4fe30839f3