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

# TODO

[ ] Nueva gramatica simplificada
[X] Funcion para generador de nombres de ficheros temporales
[X] Soporte completo para funciones escritas en Python
[ ] Soporte completo para funciones escritas en Mist (DOING German)
[ ] Que el templating de strings {} funcione en todos los sitios, y no solo en el print
[ ] Hacer que el put itere listas automaticamente si coincide el numero de campos
[ ] Funcion para leer ficheros
[X] Soporte para crear listas y añadir elementos a una lista creada
[ ] Soporte completo de listas incluyendo utilidades de filtro, mapeo, etc.
[ ] Soporte completo de strings incluyendo utilidades de concatenacion, split, busqueda, etc.
[ ] Que los comandos de busqueda de text, XML y JSON sean funciones
[ ] Que no se pinte por defecto la salida de los comandos, o que sea configurable por un parametro en el exec

# Possible new grammar

```mist
watch myhosts => m {
    findOpenPorts m.ip m.ports => result openPorts console {
        put openports => targetHosts
    }
}

call foo => result openPorts console {
    print openPorts
    targetHosts <= ddsad
    taget2 <= cdsfsgfsa
} to targetHosts, target2

call findOpenPort ip="127.0.0.1" ports:=targetHosts => result openPorts console {
    print openPorts
}
```

# License

This project is distributed under `BSD license <https://github.com/cr0hn/mist/blob/master/LICENSE>`_
