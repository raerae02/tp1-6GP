## Docker


```bash
docker run --name tp1-6gb-container -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
docker exec -it tp1-6gb-container mysql -uroot -p
```
