FROM python:3-alpine

RUN pip install pyyaml websockets
RUN mkdir /code
COPY . /code

ENV PYTHONASYNCIODEBUG=1

ENTRYPOINT ["python", "-X", "dev", "/code/entrypoint.py"]