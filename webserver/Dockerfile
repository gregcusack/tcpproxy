FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN echo 'exec zsh' > /root/.bashrc
RUN apt-get update && apt-get install -y --no-install-recommends curl dnsutils ipcalc iproute2 iputils-ping jq mtr-tiny nano netcat tcpdump termshark vim-nox zsh
RUN curl -L https://grml.org/zsh/zshrc > /root/.zshrc
RUN apt-get update && apt-get install -y build-essential python3 python3-pip python3-dev

RUN apt-get install -y libnfnetlink-dev libnetfilter-queue-dev
RUN pip3 install --upgrade pip
RUN pip3 install netfilterqueue
RUN pip3 install netifaces
RUN apt-get install iptables sudo -y

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip3 install -r requirements.txt

# copy every content from the local file to the image
COPY . /app
RUN chmod a+x run.sh

RUN mkdir -p /app/logs/

RUN echo "adsd"

# CMD ["python3", "-u", "/app/proxy.py", ">", "/app/logs/log.log", "&"] 

# CMD ["python3", "-u", "/app/app.py", "&"]

CMD ["/app/run.sh"]