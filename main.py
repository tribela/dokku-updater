import functools
import os
import requests
import subprocess
import time

import docker
import yaml

from apscheduler.schedulers.background import BackgroundScheduler

api = docker.from_env()

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
MASTODON_ACCESS_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
MASTODON_HOST = os.getenv('MASTODON_HOST')


def apscheduler_wait(scheduler):
    while scheduler.get_jobs():
        time.sleep(10)


def update_all(apps):
    for app in apps:
        update_app(app)

    api.images.prune()


def update_app(app):
    image_name = app['image']
    app_name = app['name']
    try:
        image = api.images.get(image_name)
    except docker.errors.ImageNotFound:
        image = None

    new_image = api.images.get_registry_data(image_name).pull()

    if image is None or new_image.id != image.id:
        new_image.tag(image_name)
        print(f'Updating {app_name}')
        result = subprocess.run(['dokku', 'ps:rebuild', app_name], stdout=subprocess.DEVNULL)
        if result.returncode != 0:
            if DISCORD_WEBHOOK_URL:
                requests.post(
                    DISCORD_WEBHOOK_URL,
                    data={
                        'username': 'Updater',
                        'content': f'Deploying {app_name} is failed!',
                    }
                )
        else:
            if DISCORD_WEBHOOK_URL:
                requests.post(
                    DISCORD_WEBHOOK_URL,
                    data={
                        'username': 'Updater',
                        'content': f'{app_name} is deployed!',
                    }
                )
            if MASTODON_ACCESS_TOKEN and MASTODON_HOST:
                requests.post(
                    f'https://{MASTODON_HOST}/api/v1/statuses',
                    headers={
                        'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}',
                    },
                    json={
                        'status': f'{app_name} 신제품 게시!',
                        'language': 'ko',
                    }
                )


def main():
    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if DISCORD_WEBHOOK_URL:
        print("Discord webhook is enabled")
    else:
        print("Discord webhook is not enabled")

    scheduler = BackgroundScheduler()
    scheduler.start()

    job = functools.partial(update_all, config['apps'])

    scheduler.add_job(job, 'interval', minutes=5)

    job()
    apscheduler_wait(scheduler)
    scheduler.shutdown()


if __name__ == '__main__':
    main()
