# Minecraft Control Panel Backend
A back end server operate with official Minecraft server that makes the gameplay experience better.

**Because of missoperate, I deleted the source code of its frontend. You could check it out on this [site](http://mcp.hplove.com.cn)(Login in with test account ID:sb123,PWD:sb123456).**

## Features

### Basic

- Basic authentication(not operate with mc server yet).
- Grab online player list.

### Teleport

This app majorly provide balanced teleport functions to ordinary players.

- Set/Tp to a specific "Home" position.
- Set/Tp to 2 specific save positions.
- Tp to the spawn point(you need to set it first).
- Tp to a online player.
- Tp to the setted World Translation Points.

## Installation

Install the dependencies

```
pip install Flask, Flask-RESTful, Flask-SQLAlchemy
```

Optional dependencies

```
pip install Flask-Cors, Flask-Docs, Flask-Migrate, Flask-Script
```

## Usage

run the server with development server

```
python app.py
```
