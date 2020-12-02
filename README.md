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

[X] Nueva gramatica simplificada y convertir todo a funciones
[X] Funcion nativa para generar de nombres de ficheros temporales y actualizar ejemplo "command_findOpenPorts.mist"
[X] Soporte completo para funciones escritas en Python
[X] Soporte completo para funciones escritas en Mist
[X] Que no se pinte por defecto la salida de los comandos, o que sea configurable por un parametro en el exec
[X] Hacer que el put itere listas automaticamente si coincide el numero de campos
[X] Soporte para crear listas y añadir elementos a una lista creada
[X] Migrar comandos de busqueda de text, XML y JSON a funciones
[X] Migrar CSV dump y load a funciones
[ ] Refactor comando exec como función (DOING GERMAN)
[ ] Integración del nuevo codigo multihilo y flujos (DANI + GERMAN)
[X] Que el templating de strings {} funcione en todos los sitios, y no solo en el print
[X] Funcion nativa para leer ficheros. Comparar usando el ejemplo "mist_commands_vs_mist_functions.mist" y actualizar ejemplo "command_findOpenPorts.mist"
[ ] Soporte completo de listas incluyendo utilidades de filtro, mapeo, etc. (HECTOR?)
[ ] Soporte completo de strings incluyendo utilidades de concatenacion, split, busqueda, etc.
[ ] Convertir todos los comandos core posibles (print?) en funciones y simplificar más la gramática

# Possible new grammar

```mist
# Current
watch myhosts => m {
    findOpenPorts m.ip m.ports => openPorts {
        put openports => targetHosts
    }
}

# New proposal

call findOpenPort(ip="127.0.0.1" ports=:targetHosts) => result {
    print result
    targetHosts <= ddsad
    taget2 <= cdsfsgfsa
} to targetHosts, target2

print findOpenPort(ip="127.0.0.1" ports=:targetHosts)
```

# License

This project is distributed under `BSD license <https://github.com/cr0hn/mist/blob/master/LICENSE>`_
