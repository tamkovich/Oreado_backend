# Oreado_backend

### Installation & Setup

```sh
$ git clone https://github.com/jaselnik/Oreado_backend.git
$ cd Oreado-Dataset
```
```sh
$ sudo -u postgres psql postgres
=# CREATE DATABASE oreado_backend_db;
```
```sh
$ virtualenv venv
$ source venv/bin/activate 
```
```sh
(venv) $ pip install -r requirements.txt
(venv) $ python manage.py migrate
(venv) $ python manage.py loaddata fixtures/oreado_mail_category.json
(venv) $ python manage.py runserver 0.0.0.0:8000
(venv) $ celery -A oreado_backend worker -l info -B
```

### REST API!

- [Local GET list mails](http://127.0.0.1:8000/api/mails/) or [Server GET list mails](http://oreadobackend.ml/api/mails/)
- [Local GET 1st Mail](http://127.0.0.1:8000/api/mails/1/) or [Server GET 1st Mail](http://oreadobackend.ml/api/mails/1/)
