#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import sys
import subprocess
from urllib.parse import parse_qs, urlparse
import logging
import os

def locate(file):
    # Trouver le chemin pour fping
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
            return os.path.join(path, file)
    return "{}".format(file)

def ping(host, prot, interval, count, size, source):
    # Utiliser une adresse source ?
    if source == '':
        ping_command = '{} -{} -b {} -i 1 -p {} -q -c {} {}'.format(filepath, prot, size, interval, count, host)
    else:
        ping_command = '{} -{} -b {} -i 1 -p {} -q -c {} -S {} {}'.format(filepath, prot, size, interval, count, source, host)

    output = []
    # Enregistrer la commande ping réelle pour des fins de débogage
    logger.info(ping_command)
    # Exécuter le ping
    cmd_output = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    stdout = cmd_output[0].decode('utf-8')
    stderr = cmd_output[1].decode('utf-8')
    # Analyser la sortie de fping
    try:
        loss = stderr.split("%")[1].split("/")[2]
        min = stderr.split("=")[2].split("/")[0]
        avg = stderr.split("=")[2].split("/")[1]
        max = stderr.split("=")[2].split("/")[2].split("\n")[0]
    except IndexError:
        loss = 100
        min = 0
        avg = 0
        max = 0
    # Préparer les métriques
    output.append("ping_avg {}".format(avg))
    output.append("ping_max {}".format(max))
    output.append("ping_min {}".format(min))
    output.append("ping_loss {}".format(loss))
    output.append('')
    return output

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Gérer les requêtes dans un thread séparé."""

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Analyser l'URL
        parsed_path = urlparse(self.path).query
        value = parse_qs(parsed_path)
        # Récupérer la cible du ping
        address = value['target'][0]
        # Récupérer l'adresse source
        if "source" in value:
            source = value['source'][0]
        else:
            source = ''
        # Récupérer le protocole
        if "prot" in value:
            prot = value['prot'][0]
        else:
            prot = 4
        # Récupérer le nombre de pings
        if "count" in value:
            count = value['count'][0]
        else:
            count = 10
        # Récupérer la taille des paquets de ping
        if "size" in value and int(value['size'][0]) < 10240:
            size = value['size'][0]
        else:
            size = 56
        # Récupérer l'intervalle des pings
        if "interval" in value and int(value['interval'][0]) > 1:
            interval = value['interval'][0]
        else:
            interval = 500

        message = '\n'.join(ping(address, prot, interval, count, size, source))
        # Préparer le code de statut HTTP
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
        return

if __name__ == '__main__':
    # Localiser le chemin de fping
    global filepath
    filepath = locate("fping")
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levellevel)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    # Vérifier s'il y a un port spécial configuré
    port = int(os.getenv('PORT', '8085'))  # Utiliser la variable d'environnement PORT si définie
    logger.info('Démarrage du serveur sur le port {}, utilisez <Ctrl-C> pour arrêter'.format(port))
    server = ThreadedHTTPServer(('0.0.0.0', port), GetHandler)
    server.serve_forever()
