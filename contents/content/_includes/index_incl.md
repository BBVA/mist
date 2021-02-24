![MIST LOGO](https://raw.githubusercontent.com/cr0hn/mist/master/docs/source/_static/images/logo-250x250.png)


`MIST`, a high level programming language focussed in security testing.

# Installing

```bash
> pip install mist-lang
```

# Screenshots

![Image of editor](https://raw.githubusercontent.com/cr0hn/mist/master/docs/source/_static/images/MIST_Editor.png)

# Local usage

You can use MIST for running local mist files (A.K.A. playbooks), or starting a
web editor to write your own playbooks.

## Running a mist file

```bash
> mist run examples/ping.mist
```

## Launch server with editor

### Starting Redis Server

MIST Server need Redis to work. So, we must launch it:

```bash
> docker run --rm -d -p 6379:6379 redis
```

### Starting MIST Server with Editor

```bash
> mist server -E -R redis://127.0.0.1:6379
```

# Developers

After cloning the repository, you can run `MIST` without install it:

```bash
> git clone https://github.com/cr0hn/mist
> cd mist
> python3 -m pip install -r requirements.txt
> python3 -m mist -h
```

# Docker usage

## Image build

```bash
> docker build -t mist-lang .
```

## Run a mist file with Docker

```bash
> docker run -v $(pwd)/examples:/examples -v mist:/root/.mist mist-lang run examples/ping.mist
```

## Launch server with editor with Docker

```bash
> docker run -p 9000:9000 -t mist-lang server -E -l 0.0.0.0
```

## Authors

MIST is being developed by BBVA-Labs Security team members.

## Contributions

Contributions are of course welcome. See [CONTRIBUTING](https://github.com/BBVA/mist/blob/master/CONSTRIBUTING.rst) or skim existing tickets to see where you could help out.

## License

MIST is Open Source Software and available under the [Apache 2 license](https://github.com/BBVA/mist/blob/master/LICENSE)
