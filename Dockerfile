# Dockerfile для Поиск-Море: QGIS 3.40.9 + ActiveMQ 5.19.0 (локальные сборки)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Системные зависимости
RUN apt-get update && apt-get install -y \
    openjdk-11-jre \
    python3 \
    python3-pip \
    python3-dev \
    locales \
    nano \
    net-tools \
    libgdal-dev \
    libqt5widgets5 libqt5gui5 libqt5core5 \
    qttools5-dev-tools \
    unzip && \
    apt-get clean

# 2. Локальный QGIS
COPY docker/qgis/ /opt/qgis/
ENV PATH="/opt/qgis/bin:$PATH"

# 3. Локальный ActiveMQ
COPY docker/activemq/ /opt/activemq/
ENV ACTIVEMQ_HOME=/opt/activemq
ENV PATH="$ACTIVEMQ_HOME/bin:$PATH"

# 4. Python зависимости
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# 5. Исходный код
COPY . /app/
WORKDIR /app/

# 6. Порт ActiveMQ и запуск bash
EXPOSE 8161 61613 61616
CMD ["/bin/bash"]
