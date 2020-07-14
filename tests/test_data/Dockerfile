FROM python:3-alpine

RUN pip install pyyaml
RUN mkdir /code
COPY . /code

ENTRYPOINT ["python", "/code/entrypoint.py"]