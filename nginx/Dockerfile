FROM nginx:latest

ENV TZ="America/Sao_Paulo"

RUN mkdir -p /var/www/certbot
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
