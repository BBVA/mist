#FROM python:3.8-alpine as base
#RUN apk update && \
#    apk upgrade
#
#FROM base as builder
#
#RUN apk add --no-cache build-base gcc musl-dev python3-dev libffi-dev openssl-dev
#
#RUN pip install --no-cache-dir -U pip && \
#    pip wheel --no-cache-dir --wheel-dir=/root/wheels uvloop
#
#COPY . /app
#RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels -r /app/requirements.txt \
#    &&  pip wheel --no-cache-dir --wheel-dir=/root/wheels /app/
#
#FROM gcr.io/distroless/python3
#COPY --from=builder /root/wheels /root/wheels
#
#RUN python -m pip install --no-cache-dir --no-cache /root/wheels/* \
#    && rm -rf /root/wheels
#
#ENTRYPOINT ["franki"]
