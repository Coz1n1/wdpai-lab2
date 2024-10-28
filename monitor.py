from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command, path_to_server):
        self.command = command
        self.path_to_server = path_to_server
        self.process = None
        self.start_server()

    def start_server(self):
        """Uruchamia serwer"""
        print(f"Starting server with command: {self.command}")
        # Uruchamiamy serwer w kontekście odpowiedniego katalogu (path_to_server)
        self.process = subprocess.Popen(self.command, cwd=self.path_to_server, shell=True)

    def restart_server(self):
        """Restartuje serwer"""
        if self.process:
            print("Terminating current server process...")
            self.process.terminate()  # Zatrzymujemy bieżący proces
            self.process.wait()  # Czekamy, aż proces się zakończy
        print("Restarting server...")
        self.start_server()  # Uruchamiamy serwer ponownie

    def on_modified(self, event):
        print(f"Detected change in {event.src_path}. Restarting server...")
        self.restart_server()  # Poprawne zrestartowanie serwera

if __name__ == "__main__":
    # Ścieżka do katalogu, który chcesz monitorować (python_server w bieżącym katalogu)
    path_to_monitor = "./python_server"  # Monitorujemy katalog ./python_server

    # Ścieżka do katalogu, w którym znajduje się serwer
    path_to_server = "./python_server"  # Zakładam, że plik server.py jest w katalogu ./python_server

    # Komenda uruchamiająca serwer
    command = "python server.py"  # Komenda uruchamiająca serwer

    # Tworzymy handler, który będzie monitorował zmiany i zarządzał serwerem
    event_handler = ChangeHandler(command, path_to_server)

    # Inicjalizujemy observer i monitorujemy katalog
    observer = Observer()
    observer.schedule(event_handler, path_to_monitor, recursive=True)

    print(f"Starting server with hot reload at {path_to_monitor}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
