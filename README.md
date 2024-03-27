# Test Task Tenderplan

This repository contains the Test Task for Tenderplan


### Dependencies

Dependencies are described in `requirements.txt`. Ensure you have them installed to run the project successfully.

Also, you need a **redis** and **celery**

### Installing

To install the dependencies from `requirements.txt`, run the following command:

```bash
pip install -r requirements.txt
```

Alternatively, you can build the Docker image which includes all necessary dependencies:

```bash
docker-compose build
```

### Executing program

To start the program, set-up redis, celery and execute the main.py:

```bash
python3 main.py
```
Or, you can use docker-compose up to bring up a Docker container:

```bash
docker-compose up
```
