import os
import threading
import requests
import time
import hashlib
from queue import PriorityQueue

class FileDownloader:
    def __init__(self, urls, dest_folder, progress_callback, error_callback):
        self.urls = PriorityQueue()
        for priority, url in enumerate(urls):
            self.urls.put((priority, url))
        self.dest_folder = dest_folder
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()

    def download_file(self, url, index):
        file_name = os.path.basename(url)
        dest_path = os.path.join(self.dest_folder, file_name)
        retry_limit = 3
        attempt = 0

        while attempt < retry_limit:
            try:
                headers = {}
                current_size = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
                headers['Range'] = f"bytes={current_size}-"
                response = requests.get(url, headers=headers, stream=True, timeout=10)
                total_size = int(response.headers.get('content-length', 0)) + current_size
                progress = current_size

                with open(dest_path, "ab" if current_size > 0 else "wb") as file:
                    for data in response.iter_content(chunk_size=1024):
                        self.pause_event.wait()
                        if self.stop_event.is_set():
                            return
                        file.write(data)
                        progress += len(data)
                        with self.lock:
                            self.progress_callback(index, progress / total_size * 100)

                with self.lock:
                    self.progress_callback(index, 100)
                return
            except Exception as e:
                attempt += 1
                time.sleep(2 ** attempt)
                if attempt == retry_limit:
                    with self.lock:
                        self.error_callback(index, f"Failed: {str(e)}")
                    return

    def start_download(self):
        threads = []
        while not self.urls.empty():
            priority, url = self.urls.get()
            index = len(threads)
            thread = threading.Thread(target=self.download_file, args=(url, index))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()

    def stop(self):
        self.stop_event.set()

    @staticmethod
    def calculate_hash(file_path):
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


