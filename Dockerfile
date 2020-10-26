FROM python:3.8 as base
RUN pip install --upgrade pip

FROM base as builder

#RUN git clone https://github.com/darkoperator/dnsrecon
#RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels ./dnsrecon

# RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels mist-lang
ADD . /mist
WORKDIR /mist
RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels .

WORKDIR /

#FROM gcr.io/distroless/python3
FROM base
COPY --from=builder /root/wheels /root/wheels

RUN python -m pip install --no-cache-dir --no-cache /root/wheels/* \
    && rm -rf /root/wheels

RUN apt update
RUN apt install -y nmap
RUN curl -L https://github.com/zricethezav/gitleaks/releases/download/v6.1.2/gitleaks-linux-amd64 --output /usr/bin/gitleaks && chmod a+x /usr/bin/gitleaks
RUN pip install bandit festin

RUN git clone https://github.com/darkoperator/dnsrecon
RUN cd dnsrecon && pip install -r requirements.txt
RUN ln -s /dnsrecon/dnsrecon.py /usr/bin/dnsrecon.py

RUN mist
ADD ./mist/action_editor/assets/ /usr/local/lib/python3.8/site-packages/mist/action_editor/assets

EXPOSE 9000
ENTRYPOINT ["mist"]
