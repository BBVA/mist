#!/bin/bash

apt update && \
apt install -y nmap awscli default-jre && \
pip install bandit festin git+https://github.com/cr0hn/dnsrecon && \
curl -L https://github.com/zricethezav/gitleaks/releases/download/v6.1.2/gitleaks-linux-amd64 --output /usr/bin/gitleaks && chmod a+x /usr/bin/gitleaks && \
curl --show-error --location "https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz" | tar -xzf - -C /usr/local && \
cd /usr/local/kafka_2.13-2.8.0/bin && ln -s -f kafka-console-consumer.sh kafka-console-consumer && ln -s -f kafka-console-producer.sh kafka-console-producer && \
echo "Installation done" && \
echo "Add this route to your PATH '/usr/local/kafka_2.13-2.8.0/bin' to use kafka commands" \
