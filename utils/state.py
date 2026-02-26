import json
import os
import threading

class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.lock = threading.Lock()
        self.state = self.load()

    def load(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "notebooks": {},        # key -> notebook_id
            "research_done": [],    # list of keys
            "artifacts_done": {},   # key -> list of types
            "downloads_done": {},   # key -> list of types
        }

    def save(self):
        with self.lock:
            dir_path = os.path.dirname(self.state_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)

    def get_notebook_id(self, key: str) -> str:
        with self.lock:
            return self.state["notebooks"].get(key)

    def set_notebook_id(self, key: str, nb_id: str):
        with self.lock:
            self.state["notebooks"][key] = nb_id
        self.save()

    def is_research_done(self, key: str) -> bool:
        with self.lock:
            return key in self.state["research_done"]

    def set_research_done(self, key: str):
        with self.lock:
            if key not in self.state["research_done"]:
                self.state["research_done"].append(key)
        self.save()

    def is_artifact_done(self, key: str, type: str) -> bool:
        with self.lock:
            done_list = self.state["artifacts_done"].get(key, [])
            return type in done_list

    def set_artifact_done(self, key: str, type: str):
        with self.lock:
            if key not in self.state["artifacts_done"]:
                self.state["artifacts_done"][key] = []
            if type not in self.state["artifacts_done"][key]:
                self.state["artifacts_done"][key].append(type)
        self.save()

    def is_download_done(self, key: str, type: str) -> bool:
        with self.lock:
            done_list = self.state["downloads_done"].get(key, [])
            return type in done_list

    def set_download_done(self, key: str, type: str):
        with self.lock:
            if key not in self.state["downloads_done"]:
                self.state["downloads_done"][key] = []
            if type not in self.state["downloads_done"][key]:
                self.state["downloads_done"][key].append(type)
        self.save()

    def clear_topic(self, key: str):
        with self.lock:
            if key in self.state["notebooks"]:
                del self.state["notebooks"][key]
            if key in self.state["research_done"]:
                self.state["research_done"].remove(key)
            if key in self.state["artifacts_done"]:
                del self.state["artifacts_done"][key]
            if key in self.state["downloads_done"]:
                del self.state["downloads_done"][key]
        self.save()

    def reset_topic_progress(self, key: str):
        with self.lock:
            if key in self.state["research_done"]:
                self.state["research_done"].remove(key)
            if key in self.state["artifacts_done"]:
                del self.state["artifacts_done"][key]
            if key in self.state["downloads_done"]:
                del self.state["downloads_done"][key]
        self.save()
