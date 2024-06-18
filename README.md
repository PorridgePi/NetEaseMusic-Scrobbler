# NetEase Music Scrobbler

An API built with FastAPI to translate encrypted song information from NetEase Music and scrobble it to various services.

## Requirements
- Bare-metal: Python 3
- Containerised: Docker

## Usage
### Using Docker Compose (Recommended)
1. Clone the repository
```sh
git clone https://github.com/PorridgePi/NetEaseMusic-Scrobbler
```
2. Copy `.env.example` to `.env` and fill in the required information
3. Build the image and run the container
```sh
docker-compose up --build
```
4. API up at `http://localhost:8888`

### Using Docker
1. Clone the repository
```sh
git clone https://github.com/PorridgePi/NetEaseMusic-Scrobbler
```
2. Copy `.env.example` to `.env` and fill in the required information
3. Build the image
```sh
docker build -t netease-music-scrobbler .
```
4. Run the container
```sh
docker run -p 8888:80 --env-file .env netease-music-scrobbler
```
5. API up at `http://localhost:8888`

### Bare-metal Python
1. Clone the repository
```sh
git clone https://github.com/PorridgePi/NetEaseMusic-Scrobbler
```
2. Copy `.env.example` to `.env` and fill in the required information
3. Set up a virtual environment
```sh
python -m venv venv
```
4. Activate virtual environment
```sh
source venv/bin/activate
```
5. Install dependencies
```sh
pip install -r requirements.txt
```
6. Run the server
```sh
fastapi run app/main.py --port 8888
```
7. API up at `http://localhost:8888`

## API Endpoints
A general overview of the endpoints is available below.

Alternatively, uncomment this line in `compose.yml`:
```
    # - IS_FASTAPI_DEBUG=true`
```
Then, restart the container and visit `http://localhost:8888/docs` for a more interactive documentation page (thanks to FastAPI).

### Scrobble
- Method: `POST`
- Path: `/scrobble`
- JSON Body Structure:

| Key | Type | Description |
| --- | ---- | ----------- |
| `id` | Integer | Song ID from NetEase Music |

### Encrypted Scrobble
- Method: `POST`
- Path: `/encrypted_scrobble`
- JSON Body Structure:

| Key | Type | Description |
| --- | ---- | ----------- |
| `encrypted` | String | Encrypted `params` parameter from NetEase Music API requests |
