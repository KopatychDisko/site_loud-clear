from fastapi import FastAPI, Query, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from model import async_main, shutdown_db, get_session, ExecutorOut, ExecutorsListOut

from request import get_executor, get_executors

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount('/image', StaticFiles(directory='image'), name='image')


@app.on_event('startup')
async def start():
    await async_main()
    
@app.on_event('shutdown')
async def end():
    await shutdown_db()
    

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/api/artist', response_class=JSONResponse)
async def artist(uuid: str = Query(), session=Depends(get_session)):
    result = await get_executor(session, uuid)
    return ExecutorOut.model_validate(result)

@app.get('/api/ten_artist', response_class=JSONResponse)
async def ten_artist(session=Depends(get_session)):
    executors = await get_executors(session)
    return ExecutorsListOut(executors=[ExecutorOut.model_validate(e) for e in executors])

@app.get('/mini_aps_artist', response_class=HTMLResponse)
async def mini_aps_artist(uuid: str = Query()):
    return templates.TemplateResponse("mini_aps_artist.html")

@app.get('/artist', response_class=HTMLResponse)
async def html_artist(request: Request, uuid: str = Query()):
    return templates.TemplateResponse("artist.html", {"request": request})