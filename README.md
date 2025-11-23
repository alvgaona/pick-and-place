# Pick and Place with RoboDK

![Python Version](https://img.shields.io/badge/python-3.13-blue)

https://github.com/user-attachments/assets/10c2939d-7070-4d08-993d-b2e0a17689a2

A project for the subject Applied Robotics within the Automation & Robotics Master at
Universidad Politécnica de Madrid.

## 📋 Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager.
- [RoboDK](https://robodk.com) simulator.

## 🚀 Usage

Once you have installed `uv` and `RoboDK` you can just run the following steps.

1.  Check `uv` is installed.
  ```sh
  uv --version
  ```
2.  Sync the project dependencies.
  ```sh
  uv sync
  ```
3.  Open up RoboDK and import the [RDK file](rdk/estacion_practica_tablero.rdk).
4.  Run pick and place task.
  ```sh
  uv run python main.py
  ```

## ✍️ Authors

- **Alvaro J. Gaona** - [@alvgaona](https://github.com/alvgaona)
- **Lucas Gomez-Velayos** - [@Pigamer37](https://github.com/Pigamer37)
- **Silvia Ochando-Valero** - [@sochval](https://github.comcom/sochval)
- **Peter Pasuy-Quevedo** - [@peter2395](https://github.com/peter2395)

## 📜 License

This project is licensed under the [MIT License](LICENSE.md).
