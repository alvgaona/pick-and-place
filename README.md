# RoboDK Pick and Place

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager.
- [RoboDK](https://robodk.com) simulator.

## Usage

Once you have installed `uv` and `RoboDK` you can just run the following steps.


1. Check uv is installed.
```sh
uv --version
```
2. Sync the project dependencies.
```sh
uv sync
```
3. Open up RoboDK and import the [RDK file](rdk/estacion_practica_tablero.rdk).
4. Run pick and place task
```sh
uv run python main.py
```
