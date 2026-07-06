import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from database import Database
from agents.orchestrator import run_orchestrator

app = FastAPI(title="AI Office")
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Database()


@app.get("/")
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/history")
async def get_history():
    return {"tasks": db.get_tasks()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send_update(agent_name: str, status: str, message: str = ""):
        await websocket.send_text(json.dumps({
            "type": "agent_update",
            "agent": agent_name,
            "status": status,
            "message": message
        }))

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            if data.get("type") == "task":
                brief = data.get("content", "").strip()
                if not brief:
                    continue

                task_id = db.create_task(brief)

                await websocket.send_text(json.dumps({
                    "type": "task_started",
                    "task_id": task_id
                }))

                await send_update("xenon", "working", "Получил задачу, формирую команду...")

                try:
                    result = await run_orchestrator(
                        task=brief,
                        send_update=send_update
                    )
                    db.update_task(task_id, result)

                    await websocket.send_text(json.dumps({
                        "type": "result",
                        "task_id": task_id,
                        "content": result
                    }))

                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))

            elif data.get("type") == "get_history":
                await websocket.send_text(json.dumps({
                    "type": "history",
                    "tasks": db.get_tasks()
                }))

    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
