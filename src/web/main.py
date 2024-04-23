import json
import os

import uvicorn
import logging
from aio_pika import connect, Message, DeliveryMode
from fastapi import FastAPI, Request, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, FileResponse, StreamingResponse
from starlette.templating import Jinja2Templates

from src.core.redis_client import RedisClient
from src.web.schemes.submit import SubmitIn, CheckIn

app = FastAPI(
    title="video_downloader", openapi_url=f"/api/v1/openapi.json"
)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
    await self.app(scope, receive, send)
  File "/home/admin/video_downloader_service/.venv/lib/python3.10/site-packages/starlette/routing.py", line 66, in app
    response = await func(request)
  File "/home/admin/video_downloader_service/.venv/lib/python3.10/site-packages/fastapi/routing.py", line 273, in app
    raw_response = await run_endpoint_function(
  File "/home/admin/video_downloader_service/.venv/lib/python3.10/site-packages/fastapi/routing.py", line 190, in run_endpoint_function
    return await dependant.call(**values)
  File "/home/admin/video_downloader_service/src/web/main.py", line 81, in get_url_for_download_video
    task_done = await is_task_already_done_or_exist(red, data.link)
  File "/home/admin/video_downloader_service/src/web/main.py", line 34, in is_task_already_done_or_exist
    tasks = [
  File "/home/admin/video_downloader_service/src/web/main.py", line 36, in <listcomp>
    if literal_eval(message.decode('utf-8'))["link"] == link
TypeError: string indices must be integers
'''

'''
queue_name -> [
    "{link...}",
    "{link2...}",
    "{link3..}"
]

queue_name -> {
    "link1" -> {vars},
    "link2" -> {vars},
    "link3" -> {vars},
}
'''


async def is_task_already_done_or_exist(redis: RedisClient, link: str):
    messages = await redis.get_all_tasks_from_queue(redis.TASKS_DONE_NAME)
    tasks = {k.decode("utf-8"): json.loads(v.decode("utf-8")) for k, v in messages.items()} if messages else None

    if tasks and link in tasks and tasks[link]["status"] in ["done", "exist"]:
        return tasks[link]


async def is_task_in_process(redis: RedisClient, link: str):
    messages = await redis.get_all_tasks_from_queue(redis.TASKS_NAME)
    tasks = {k.decode("utf-8"): json.loads(v.decode("utf-8")) for k, v in messages.items()} if messages else None

    if tasks and link in tasks:
        return tasks[link]


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/submit')
async def get_url_for_download_video(request: Request, data: SubmitIn = Depends()):
    red = RedisClient()
    task_done = await is_task_already_done_or_exist(red, data.link)
    # TODO: где-то не обновился статус после выполнения\провала задачи
    task_in_process = await is_task_in_process(red, data.link)
    if task_in_process:
        return JSONResponse(status_code=202, content={"result": "Задача в работе. Ожидайте"})
    if task_done:
        if isinstance(task_done["result"], str):
            links_to_download_video = [str(request.base_url) + "get/?file_path=" + task_done["result"]]
        else:
            links_to_download_video = [str(request.base_url) + "get/?file_path=" + path for path in task_done["result"]]
        return JSONResponse({"result": links_to_download_video})

    # TODO: учесть, что если делать запрос CURL\urllib3\etc, в теле может быть несколько ссылок -> должно быть создано несколько задач
    async with await connect("amqp://guest:guest@localhost/") as connection:
        # Creating a channel
        channel = await connection.channel()
        body = [
            {
                "link": data.link,
                "format": f"bv[width={data.resolution.value}][ext={data.video_format.value}]+ba[ext={data.audio_format.value}]/"
                          f"bv[width={data.resolution.value}][ext=mp4]+ba[ext=m4a]/"
                          f"bv[width={data.resolution.value}][ext=webm]+ba[ext=webm]/"
                          f"best[ext={data.video_format.value}]/"
                          f"best[ext!=unknown_video]",
                "merge_output_format": data.merge_output_format.value,
                "outtmpl": f"downloads/%(extractor_key)s/%(id)s_%(resolution)s.%(ext)s",
            }, ]
        # Sending the message
        for link in body:
            if "mail" in link["link"]:
                link["parser"] = "MyMailRu"
            elif "yappy" in link["link"]:
                link["parser"] = "Yappy"
            message = Message(
                json.dumps(link, indent=4).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(
                message,
                routing_key='hello',
            )

        logging.info(f" [x] Sent '{link}'")
        # TODO: возможно возвращать идентификаторы задач aka куски ссылок
        return JSONResponse(status_code=201, content={"result": f"Задача поставлена в работу, ссылка: {link['link']}"})
        # TODO: если уже была попытка сделать задачу и в редисе она с ошибкой, то переташить её в очередь на
        #  выполнение с очисткой состояние об ошибке


@app.get('/get/', response_class=FileResponse, status_code=200)
async def download_video(file_path):
    base = os.path.dirname(os.path.dirname(os.path.abspath(file_path)))
    base_download_dir = os.path.join(base, os.pardir, os.pardir, "downloads")

    def iterfile():
        with open(base_download_dir + f'/{file_path}', mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), headers={'Content-Disposition': f'inline; filename="{file_path}"'},
                             media_type="video")


@app.post('/check/', response_class=FileResponse, status_code=200)
async def download_video(data: CheckIn, request: Request):
    try:
        red = RedisClient()
        messages_task_done = await red.get_all_tasks_from_queue(red.TASKS_DONE_NAME)
        messages_tasks = await red.get_all_tasks_from_queue(red.TASKS_NAME)

        tasks_done = {k.decode("utf-8"): json.loads(v.decode("utf-8")) for k, v in
                      messages_task_done.items()} if messages_task_done else None

        tasks = {k.decode("utf-8"): json.loads(v.decode("utf-8")) for k, v in
                 messages_tasks.items()} if messages_tasks else None

        if tasks and data.link in tasks:
            return JSONResponse(
                status_code=202,
                content={"result": f"Задача {data.link} в данный момент в работе, выполняется"}
            )
        # TODO: если уже была попытка сделать задачу и в редисе она с ошибкой, то переташить её в очередь на выполнение с очисткой состояние об ошибке
        if data.link in tasks_done and tasks_done[data.link]["status"] == "error":
            await red.del_task_from_task_done_queue(tasks_done[data.link])
            return JSONResponse(status_code=510,
                                content={"result": f"Задача выполнена с ошибкой, попробуйте загрузить еще раз"})
        if tasks_done and data.link in tasks_done:
            if isinstance(tasks_done[data.link]["result"], str):
                links_to_download_video = [str(request.base_url) + "get/?file_path=" + tasks_done[data.link]["result"]]
            else:
                links_to_download_video = [str(request.base_url) + "get/?file_path=" + path for path in
                                           tasks_done[data.link]["result"]]
            return JSONResponse({"result": links_to_download_video})
        return JSONResponse(status_code=404, content={"result": "Задача не найдена"})

    except (AttributeError, IndexError):
        return JSONResponse(status_code=404, content={"result": "Задача не найдена"})
    except Exception as ex:
        print(ex)

uvicorn.run("src.web.main:app", host="0.0.0.0", log_level="info")
