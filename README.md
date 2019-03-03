# Oreado-Dataset

### Installation & Setup

```sh
$ git clone https://github.com/jaselnik/Oreado-Dataset.git
$ cd Oreado-Dataset
```
```sh
$ sudo -u postgres psql postgres
=# CREATE DATABASE oreado_dataset_db;
```
```sh
$ virtualenv venv
$ source venv/bin/activate 
```
```sh
(venv) $ pip install -r requirements.txt
(venv) $ python manage.py migrate
(venv) $ python manage.py runserver 0.0.0.0:8000
```

### FrontEnd!

- [Local Home](http://127.0.0.1:8000) or [Server Home](http://68.183.75.150:8090)

### REST API!

- [Local Authorize](http://127.0.0.1:8000/authorize/) or [Server Authorize](http://68.183.75.150:8000/authorize/)
