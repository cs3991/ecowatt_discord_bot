# Bot Discord alerte Ecowatt

Ce bot envoie un message à 18h en cas de prévision de tension sur le réseau électrique français. 
Ce message vous donnera toutes les informations nécessaires pour économiser l'électricité aux bons moments pour éviter d'avoir des coupures. 

## Conseils

Lorsque la consommation électrique est trop élevée par rapport à la production, il est nécessaire de réduire la consommation électrique à l'échelle du pays. Pour cela, RTE (Réseau de Transport de l'Électricité) a mis en place le site [Ecowatt](https://www.monecowatt.fr), qui donne les prévisions de consommation 4 jours à l'avance heure par heure. Les consommateurs peuvent alors baisser leurs consommations non essentielles afin d'éviter des coupures d'électricité globales.

La couleur Orange indique une situation tendue, c'est à dire qu'il faut économiser l'électricité pour éviter les coupures. La couleur Rouge indique que des coupures électriques sont à prévoir. Les informations sur la consommation actuelle sont disponibles sur https://www.monecowatt.fr/.

Les appareils à couper en priorité lors des alertes sont :
- les chauffages électriques
- les chauffes-eau électriques
- les recharges de véhicules électriques
- les plaques de cuisson électriques (vitrocéramiques, induction, ...)

En général, les moments tendus pour le réseau électrique sont entre 8h et 13h et entre 18h et 20h. Mais le bot vous précisera les heures pendant lesquelles il faudra économiser l'électricité pour chaque alerte. 

Ce bot n'est pas affilié à Ecowatt.

## Commandes disponibles

- `/ecowatt today` permet d'obtenir les prévisions de consommations pour la journée actuelle
- `/ecowatt tomorrow` la même chose pour le lendemain
- `/invite` permet d'obtenir le lien d'invitation du bot, n'hésitez pas à l'inviter dans vos propres serveurs !



