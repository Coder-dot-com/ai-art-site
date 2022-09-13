FROM jwilder/nginx-proxy:latest

COPY custom.conf /etc/nginx/conf.d/custom.conf

WORKDIR certs/

RUN openssl req -x509 \
            -sha256 -days 356 \
            -nodes \
            -newkey rsa:2048 \
            -subj "/CN=allmediterranean.com/C=US/L=San Fransisco" \
            -keyout ssl_certificate.key -out ssl_certificate.crt 

WORKDIR ..

COPY /certs/ /certs/



