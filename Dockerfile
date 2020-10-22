FROM python:3.8 as base
RUN pip install --upgrade pip

FROM base as builder

RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels mist-lang

#FROM gcr.io/distroless/python3
FROM base
COPY --from=builder /root/wheels /root/wheels

RUN python -m pip install --no-cache-dir --no-cache /root/wheels/* \
    && rm -rf /root/wheels

ENTRYPOINT ["mist"]
