import requests


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str, timeout: int = 30):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=timeout)
            return response.ok, response.json()
        except Exception as exc:
            return False, {"detail": str(exc)}

    def post_json(self, endpoint: str, payload: dict, timeout: int = 120):
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=timeout)
            return response.ok, response.json()
        except Exception as exc:
            return False, {"detail": str(exc)}

    def post_file(self, endpoint: str, file_obj, target_dir: str = "documentos", timeout: int = 120):
        try:
            files = {"file": (file_obj.name, file_obj.getvalue(), file_obj.type)}
            data = {"target_dir": target_dir}
            response = requests.post(f"{self.base_url}{endpoint}", files=files, data=data, timeout=timeout)
            return response.ok, response.json()
        except Exception as exc:
            return False, {"detail": str(exc)}
