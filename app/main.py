from functools import lru_cache
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.security import api_key
from pydantic import BaseModel
from time import time
import sys, os, requests, logging

# Local imports
from app import config
from app.netease_decrypt import decrypt


### FastAPI and Logging Setup
IS_DEBUG = False if os.environ.get("IS_FASTAPI_DEBUG") == None else os.environ.get("IS_FASTAPI_DEBUG").lower() == "true"
app = FastAPI(docs_url="/docs" if IS_DEBUG else None, redoc_url="/redoc" if IS_DEBUG else None, openapi_url="/openapi.json" if IS_DEBUG else None)

# log = logging.getLogger("uvicorn.error")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(levelname)s:\t\t%(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
log.addHandler(stream_handler)

log.info('API is starting up')


### Pydantic Models
class ScrobbleItem(BaseModel):
    id: int

class EncryptedScrobbleItem(BaseModel):
    encrypted: str

### Data
app.lastSong = None
app.lastListenTime = 0


### Get and Validate Settings
@lru_cache
def get_settings():
    return config.Settings()

try:
    for var in vars(get_settings()):
        print(f'INFO\t {var} = {getattr(get_settings(), var)}')
except Exception as e:
   print(f"ERROR\t Missing environmental variables. Check .env file.\n     ->  {e}\nTerminating...")
   sys.exit(4)


### Auth - [python - Enabling API Key Auth in FastAPI for all endpoints except / and a healthcheck endpoint? - Stack Overflow](https://stackoverflow.com/questions/76284496/enabling-api-key-auth-in-fastapi-for-all-endpoints-except-and-a-healthcheck-en)
api_key_header = api_key.APIKeyHeader(name="X-API-Key")

async def validate_api_key(key: str = Depends(api_key_header)):
    if key != get_settings().api_key:
        print(type(key), type(get_settings().api_key))
        raise HTTPException(
            status_code=401, detail="Unauthorized"
        )

### Scrobble Function
def scrobble(id: int):
    log.info(f"Scrobbling song with id {id}")
    try:
        song_info = requests.get(f"https://music.163.com/api/song/detail/?id={id}&ids=%5B{id}%5D").json()["songs"][0]
    except IndexError:
        log.erorr(f"Song with id {id} not found")
        return

    body = {
      "title": song_info["name"],
      "album": song_info["album"]["name"],
      "artists": [artist["name"] for artist in song_info["artists"]],
      "length": song_info["duration"],
        # duration Integer How long the song was listened to in seconds (Optional)
        # time Integer Timestamp of the listen if it was not at the time of submitting (Optional)
    }

    lastSong = app.lastSong
    lastListenTime = app.lastListenTime

    if lastSong == None:
        log.info(f"No last song, assigning current song ({body["title"]}) as last song.")
    else:
        timeDiff = time() - lastListenTime
        if (timeDiff > lastSong["length"] / 2000 and timeDiff < lastSong["length"]/1000 + 60): # if played more than half song and less than 1 min from song ended
            response = requests.post(f"{get_settings().maloja_api_url}?key={get_settings().maloja_api_token}", json=lastSong)

            if response.json()["status"] != "success":
                log.error(f"Failed to scrobble song (id: {id}, title: {lastSong['title']}, album: {lastSong['album']}, artists: {lastSong['artists']})")
                log.error(response.text)
            else:
                log.info(response.json()["desc"])
        else:
            log.info(f"Skipped scrobbling song (id: {id}, title: {lastSong['title']}, album: {lastSong['album']}, artists: {lastSong['artists']})") 
            log.info(f"Time difference: {timeDiff}")
            log.info(f"Greater than half: {timeDiff > lastSong["length"] / 2000}: {lastSong["length"] / 2000}, Less than +1 min: {timeDiff < lastSong["length"]/1000 + 60}: {lastSong["length"]/1000}")

    app.lastSong = body
    app.lastListenTime = time()



### Endpoints
@app.post("/api/encrypted_scrobble", dependencies=[Depends(validate_api_key)])
async def encrypted_scrobble(encryptedScrobbleItem: EncryptedScrobbleItem, background_tasks: BackgroundTasks):
    try:
        path, data = decrypt(encryptedScrobbleItem.encrypted)
        background_tasks.add_task(scrobble, data["songId"])
        return {"message": f"Scrobbling song (id: {data['songId']})"}
    except:
        return {"message": "Failed to decrypt"}

@app.post("/api/scrobble", dependencies=[Depends(validate_api_key)])
async def root_scrobble(scrobbleItem: ScrobbleItem, background_tasks: BackgroundTasks):
    background_tasks.add_task(scrobble, scrobbleItem.id)
    return {"message": "Scrobbling song (id: {scrobbleItem.id})"}
