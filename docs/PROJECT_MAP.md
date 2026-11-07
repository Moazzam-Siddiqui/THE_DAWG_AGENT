# What is inside this project?

A map of the folders and files.

```text
THE_DAWG_AGENT/
|
|-- dawg_agent/          The robot's Python code
|   |-- api.py           The control panel (API)
|   |-- cli.py           Commands you type in the terminal
|   |-- config.py        Settings the robot reads
|   |-- db.py            Opens the database
|   |-- models.py        Describes what a post looks like in the database
|   |-- schemas.py       Checks information sent to the API
|   |-- worker.py        Checks the clock and handles due posts
|   |
|   |-- services/        Small helpers that do one job each
|       |-- queue.py       Creates and moves posts through the queue
|       |-- render.py      Makes and checks MP4 videos
|       |-- cloudinary.py  Uploads videos to Cloudinary
|       |-- instagram.py   Talks to Instagram
|       |-- events.py      Writes down what happened
|
|-- assets/
|   |-- inbox/           Pictures waiting to become videos
|   |-- rendered/        Videos made by the robot
|   |-- thumbnails/      Small preview pictures
|
|-- config/              Content rules and creative instructions
|-- docs/                Friendly guides
|-- examples/            Example post files
|-- tests/               Small checks for the code
|-- .env.example         Example settings (copy this to .env)
|-- pyproject.toml       Python package and dependency list
|-- README.md            The front page of the project
```

## One simple rule

Each Python file should have one main job. If a file starts doing too many different jobs, split it into smaller files.
