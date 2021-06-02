FROM python:3.8 as base
RUN pip install --upgrade pip

FROM base as builder

ADD . /mist
WORKDIR /mist
RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels .

WORKDIR /

FROM base
COPY --from=builder /root/wheels /root/wheels

RUN python -m pip install --no-cache-dir --no-cache /root/wheels/* \
    && rm -rf /root/wheels

RUN apt update
RUN apt install -y nmap awscli default-jre
RUN pip install bandit festin git+https://github.com/cr0hn/dnsrecon
RUN curl -L https://github.com/zricethezav/gitleaks/releases/download/v6.1.2/gitleaks-linux-amd64 --output /usr/bin/gitleaks && chmod a+x /usr/bin/gitleaks
RUN curl --show-error --location "https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz" | tar -xzf - -C /usr/local
RUN cd /usr/local/kafka_2.13-2.8.0/bin && ln -s kafka-console-consumer.sh kafka-console-consumer && ln -s kafka-console-producer.sh kafka-console-producer
ENV PATH="/usr/local/kafka_2.13-2.8.0/bin:${PATH}"

RUN mist version

EXPOSE 9000
ENTRYPOINT ["mist"]
