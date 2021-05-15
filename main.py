import functools
import subprocess
import time

import yaml
import docker

from apscheduler.schedulers.background import BackgroundScheduler

api = docker.from_env()


def apscheduler_wait(scheduler):
    while scheduler.get_jobs():
        time.sleep(10)


def update_all(apps):
    for app in apps:
        update_app(app)


def update_app(app):
    image_name = app['image']
    print(f'Updating {image_name}')
    try:
        image = api.images.get(image_name)
    except docker.errors.ImageNotFound:
        image = None

    new_image = api.images.get_registry_data(image_name).pull()

    if image is None or new_image.id != image.id:
        subprocess.run(['dokku', 'ps:rebuild', app['name']])


def main():
    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    scheduler = BackgroundScheduler()
    scheduler.start()

    job = functools.partial(update_all, config['apps'])

    scheduler.add_job(job, 'interval', minutes=5)

    job()
    apscheduler_wait(scheduler)
    scheduler.shutdown()


if __name__ == '__main__':
    main()
