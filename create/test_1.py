import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zero.settings")  # manage.py랑 똑같이

import django
django.setup()

from rest_framework.test import APIRequestFactory
from create.api import SunoGenerateView


def run_test(song_id: int):
    factory = APIRequestFactory()
    request = factory.post(f"/api/create/{song_id}/", data={}, format="json")

    view = SunoGenerateView.as_view()
    response = view(request, song_id=song_id)

    print("\n=== SunoGenerateView 응답 ===")
    print("Status:", response.status_code)
    print("Response:", response.data)
    print("================================\n")


if __name__ == "__main__":
    run_test(song_id=1)
