FROM python:3.10.2-alpine3.14

ENV MOCK_SMTP_ADDRESS=0.0.0.0
ENV MOCK_SMTP_PORT=25
ENV MOCK_SMTP_PATH=/var/lib/mock-smtp-3
ENV MOCK_WEB_ADDRESS=0.0.0.0
ENV MOCK_WEB_PORT=8088

COPY mock-smtp-3.py /usr/sbin/mock-smtp-3
COPY requirements.txt /app/requirements.txt

RUN apk add tzdata --no-cache
RUN pip install -r /app/requirements.txt

EXPOSE $MOCK_SMTP_PORT
EXPOSE $MOCK_WEB_PORT

VOLUME $MOCK_SMTP_PATH

CMD ["python /usr/sbin/mock-smtp-3"]
