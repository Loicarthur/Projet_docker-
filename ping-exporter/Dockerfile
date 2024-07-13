# Utiliser une image de base légère pour Alpine avec Python
FROM alpine:3.9

# Installer Python, pip et fping
RUN apk add --no-cache python3 py3-pip fping
ca
# Copier le script Python dans le conteneur
COPY ping-exporter.py /opt/ping-exporter.py

# Rendre le script exécutable
RUN chmod +x /opt/ping-exporter.py

# Exposer le port sur lequel l'application écoute
EXPOSE 8085

# Définir la commande à exécuter lorsque le conteneur démarre
CMD ["python3", "/opt/ping-exporter.py"]
