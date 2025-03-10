FROM python:3.10

RUN apt-get update && apt-get install tini && apt-get clean && rm -rf /var/cache/apt
RUN pip install /work/dist/*.whl

ENTRYPOINT [ "/usr/bin/tini", "--", "kopf", "run", "--module", "calculated_config_map" ]
