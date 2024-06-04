FROM python:3.10

WORKDIR /home/app/auth_api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN  pip install --no-cache-dir --upgrade pip && \
     pip install --no-cache-dir -r requirements.txt

COPY .. .

RUN chmod +x  /home/app/auth_api/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/home/app/auth_api/entrypoint.sh"]
