from fastapi import FastAPI, HTTPException
import uvicorn
import os
import time
import re
from typing import Optional

app = FastAPI()

class BrowserSession:
    def __init__(self):
        self.current_session: Optional[dict] = None
        self.ws_endpoint: Optional[str] = None
        self.SESSION_TIMEOUT = 300  # 5 minutes timeout

    def set_session(self, ws_endpoint: str) -> dict:
        self.ws_endpoint = ws_endpoint
        self.current_session = {
            "ws_endpoint": ws_endpoint,
            "created_at": time.time(),
            "last_active": time.time()
        }
        return self.current_session

    def get_session(self) -> Optional[dict]:
        if self.current_session and self._is_session_expired():
            self.clear_session()
            return None
        return self.current_session

    def _is_session_expired(self) -> bool:
        if not self.current_session:
            return True
        return (time.time() - self.current_session["last_active"]) > self.SESSION_TIMEOUT

    def update_session(self) -> bool:
        if self.current_session and not self._is_session_expired():
            self.current_session["last_active"] = time.time()
            return True
        if self.current_session:
            self.clear_session()
        return False

    def clear_session(self):
        self.current_session = None
        self.ws_endpoint = None

browser_session = BrowserSession()

def extract_ws_url(log_line: str) -> Optional[str]:
    match = re.search(r'(ws://localhost:\d+/[a-f0-9]+)', log_line)
    return match.group(1) if match else None

def find_available_ws_url() -> Optional[str]:
    log_file = "/app/server.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                if "ws://localhost:" in line:
                    ws_url = extract_ws_url(line)
                    if ws_url:
                        return ws_url
    return None

@app.get("/get_session")
async def get_session():
    try:
        # If there's no active session, create one
        if not browser_session.get_session():
            ws_url = find_available_ws_url()
            if not ws_url:
                raise HTTPException(
                    status_code=404,
                    detail="No available browser instances found"
                )
            session = browser_session.set_session(ws_url)
        else:
            session = browser_session.get_session()
            browser_session.update_session()

        return {
            "status": True,
            "ws_endpoint": session["ws_endpoint"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/end_session")
async def end_session():
    browser_session.clear_session()
    return {"status": False}

@app.post("/keep_alive")
async def keep_alive():
    if browser_session.update_session():
        return {"status": True}
    raise HTTPException(
        status_code=404,
        detail="No active session found"
    )

@app.get("/status")
async def check_status():
    session = browser_session.get_session()
    if session:
        return {
            "status": True,
            "ws_endpoint": session["ws_endpoint"],
            "created_at": session["created_at"],
            "last_active": session["last_active"]
        }
    return {"status": False}

def start_api_server():
    uvicorn.run(app, host="0.0.0.0", port=9090)

if __name__ == "__main__":
    start_api_server()