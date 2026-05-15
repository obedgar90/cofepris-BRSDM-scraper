FROM mcr.microsoft.com/playwright/python:v1.59.0-noble

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e .

COPY . .

CMD ["cofepris", "run"]
