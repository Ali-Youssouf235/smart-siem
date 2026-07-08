import requests

from config import API_URL


def send_log(message):

    headers = {

        "Content-Type": "text/plain"

    }

    response = requests.post(

        API_URL,

        data=message.encode("utf8"),

        headers=headers,

        timeout=5

    )

    return response.status_code