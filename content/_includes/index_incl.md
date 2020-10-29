![MIST LOGO](content/assets/images/logo-250x250.png)


`MIST` a high level programming language focussed in security testing.

# Installing

```bash
$ pip install mist
```

# Screenshots

![Image of editor](content/assets/images/MIST_Editor.png)

# Local usage

You can use MIST for running local mist files (A.K.A. playbooks), or starting a
web editor to write your own playbooks.

## Running a mist file

```bash
$ mist run examples/ping.mist
```

## Launch server with editor

```bash
$ mist server -E
```

# Developers

After clone the repository, you can run `MIST` without install them:

```bash
$ git clone https://github.com/cr0hn/mist
$ cd mist
$ python3 -m pip install -r requirements.txt
$ python3 -m mist -h
```

# Docker usage

## Image build

```bash
$ docker build -t mist-lang .
```

## Run a mist file with Docker

```bash
$ docker run -v $(pwd)/examples:/examples -v mist:/root/.mist mist-lang run examples/ping.mist
```

## Launch server with editor with Docker

```bash
$ docker run -p 9000:9000 -t mist-lang server -E -l 0.0.0.0
```

# License

This project is distributed under `BSD license <https://github.com/cr0hn/mist/blob/master/LICENSE>`_
