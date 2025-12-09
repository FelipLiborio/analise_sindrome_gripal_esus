FROM postgres:16-alpine

ENV POSTGRES_USER=esus_user
ENV POSTGRES_PASSWORD=esus_password
ENV POSTGRES_DB=esus_gripal

# Copiar script SQL de modelagem para inicialização automática
COPY sql/modelagem_final.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
