FROM python:3.11.2-slim-bullseye
ENV VIRTUAL_ENV=/home/appuser/venv

RUN groupadd --gid 1000 appuser \
 && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

USER appuser
WORKDIR /home/appuser

COPY requirements.txt .
RUN python -m venv ${VIRTUAL_ENV} \
 && . ${VIRTUAL_ENV}/bin/activate \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

COPY . .
ENTRYPOINT ["./run.sh"]
