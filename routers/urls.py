"""Extract API endpoint module."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from jobs.job1.tasks import add
from jobs.utils import get_task_info
from settings import Settings, get_settings

router = APIRouter()


@router.post("/url")
def create_short_url(
    request: Request,
    url: str,
    settings: Settings = Depends(get_settings),
):

    # add.apply_async(args=[1, 2])
    # app.send_task("jobs.job1.tasks.add", args=[1, 2])
    # app.send_task("jobs.job2.tasks.multiply", args=[1, 2])

    from random import choice
    from string import ascii_letters, digits

    ln = 6
    uid = [choice(ascii_letters + digits) for _ in range(ln)]
    uid = "".join(uid)

    task = add.apply_async([3, 5])

    return {
        "url": url,
        "uid": uid,
        "short_url": f"{request.base_url}api/v1/{uid}",
        "task": task.id,
    }


@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """
    Return the status of the submitted Task
    """
    return get_task_info(task_id)


@router.get("/{url_id}")
def redirect_url(
    url_id: str,
    settings: Settings = Depends(get_settings),
):
    return RedirectResponse("https://google.com", status_code=301)
