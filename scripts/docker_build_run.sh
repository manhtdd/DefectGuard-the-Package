#!/bib/bash

docker build -t defectguard:1.0 .
docker run -it \
    -v $(pwd):/app \
    --name defectguard \
    defectguard:1.0