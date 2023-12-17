FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    mysql-server

RUN service mysql start && \
    mysql -e "CREATE DATABASE MedAssistant;" && \
    mysql -e "CREATE USER 'medassistant'@'localhost' IDENTIFIED BY 'medassistant';" && \
    mysql -e "GRANT ALL PRIVILEGES ON MedAssistant.* TO 'medassistant'@'localhost';" && \
    mysql -e "FLUSH PRIVILEGES;"

COPY requirements.txt /MedAssistant/requirements.txt
RUN pip3 install --no-cache-dir -r /MedAssistant/requirements.txt

COPY app/ /MedAssistant/app/
COPY datasets/ /MedAssistant/datasets/ 
COPY configs/ /MedAssistant/configs/
COPY db_init/ /MedAssistant/db_init/
COPY ml_model/ /MedAssistant/ml_model/
COPY start.sh /MedAssistant/.
RUN chmod +x /MedAssistant/start.sh
RUN mkdir /MedAssistant/logs

WORKDIR /MedAssistant

CMD ["./start.sh"]
