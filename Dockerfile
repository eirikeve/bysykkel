FROM python:3.10-bullseye

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY setup.py setup.py
COPY bysykkel bysykkel
COPY tests tests


RUN python -m pip install ".[dev]"