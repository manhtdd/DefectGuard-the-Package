#!/bib/bash

docker build -t defectguard:1.0 .
# docker run -it \
#     -v $(pwd):/app \
#     -v $(pwd)/input:/input \
#     --name defectguard \
#     defectguard:1.0