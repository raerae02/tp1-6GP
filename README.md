## Docker

```bash
docker pull mysql
docker run --name tp1-6gb-container -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker exec -it tp1-6gb-container mysql -uroot -p
```

## Creation de tables

```bash
#mettez le mot de passe pour la creation des table à l'execution de cette commande
Get-Content database/creation.sql | docker exec -i tp1-6gb-container mysql -uroot -ppassword
```