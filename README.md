# Mediaserver

Mediaserver -  это сервис для загрузки файлов по HTTP. Сначала мы должны отправить POST запрос о том, что мы хотим начать загружать файл и передать имя файла и его итоговый размер. Это нужно для того, чтобы заранее знать, насколько большой будет файл, и предотвратить возможные ошибки. Далее уже с помощью PUT запросов мы должны отправить байты файлов, сопровождая их параметром ```last_byte```. С помощью этого параметра контролируется то, что посылается корректный range байтов. 

# Example

```python
import requests
import os


def post_file(file: str):
    file_size = os.stat(file).st_size
    res = requests.post(
        "http://localhost:7000/load_file",
        json={"file_name": file, "file_size": file_size},
    )
    print(f"Code - {res.status_code}, json - {res.json()}")

    if res.status_code == 201:
        file_id = res.json()["file_id"]

        last_byte = 0
        with open(file, "rb") as f:
            chunk = f.read(50 * 1024 * 1024)  # 50 MB

            while len(chunk) > 0:
                last_byte += len(chunk)
                resp = requests.put(
                    f"http://localhost:7000/load_file/{file_id}",
                    files={"file_data": chunk},
                    params={"last_byte": last_byte},
                )
                print(resp.json())
                chunk = f.read(50 * 1024 * 1024)
```
