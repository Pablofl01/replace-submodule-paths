FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y git
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install gitpython PyGithub

COPY replace_submodule_paths.py /replace_submodule_paths.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
