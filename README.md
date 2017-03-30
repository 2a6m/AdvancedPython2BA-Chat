# AdvancedPython2BA-Chat

    Projet d'application chat en python pour le cours de 2eme génie électrique ECAM.
L'application utilise un protocole TCP pour avoir la liste des clients connectés au serveur, et un protocole
UDP pour communiquer avec les autres clients sans passer par le serveur.
Le projet utilise les modules socket, threading, re, json, sys

## Description

    Le client créé 2 sockets, une pour la communication client/serveur et l'autres pour la communication peer-to-peer
il se connecte au serveur et lui envoie un pseudo valide (exigence reçu du serveur) et l'adresse IP de son socket
pour la communication peer-to-peer.
Le serveur sauve tout ça dans un dictionnaire, dictionnaire des clients connectés.
le serveur lance un thread pour écouter ce client,tandis que le client lance 2 threads
pour écouter son socket serveur et son socket destiné au peer-to-peer.

    Les données échangées entre le serveur et le client sont du style '#ordre msg'. Selon l'ordre le serveur,
client va traiter les informations du message différemment.
La liste des clients connectés se met à jour chez le client quand celui-ci la demande au serveur.

### Handlers

    Le client peut faire différente actions:
"""
handlers = {
            '/exit': self._exit,
            '/send': self.sendToAll,
            '/clients': self.requestConnected,
            '/mp': self.privatemsg
        }
"""
'/send msg' envoie le msg au serveur qui va le renvoyer à tout les clients connectés
'/clients' demande la liste des clients connectés au serveur
'/mp client msg' envoie un message via le socket peer-to-peer au client spécifié (1 seul client)
'/exit' ferme les connections et quit le programme

## Authors

BOURGUIGNON Maxime
PEETERS Arnaud