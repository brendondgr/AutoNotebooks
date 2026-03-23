from rich.table import Table
from rich.panel import Panel
from rich import box
import threading

# Neutral symbol for artifacts not applicable to this topic
NOT_APPLICABLE = "[dim]─[/dim]"

class StatusDashboard:
    def __init__(self, topic_keys: list, artifact_types: list, topic_artifact_map: dict = None):
        """
        topic_artifact_map: dict of {topic_key: [list of artifact type strings]}
            If None, all artifact types apply to all topics.
            If provided, topics missing an artifact type show NOT_APPLICABLE.
        """
        self.topic_keys = topic_keys
        self.artifact_types = artifact_types
        self.topic_artifact_map = topic_artifact_map or {k: artifact_types for k in topic_keys}
        self.lock = threading.Lock()

        # Initialize status grid: status[topic_key][step] = (icon, message)
        self.status = {
            key: {
                "notebook": ("✘", "Waiting..."),
                "research": ("✘", "Pending..."),
                "msg": "Waiting..."
            } for key in topic_keys
        }
        for key in topic_keys:
            applicable = self.topic_artifact_map.get(key, [])
            for art in artifact_types:
                if art in applicable:
                    self.status[key][art] = ("✘", "Pending...")
                else:
                    self.status[key][art] = (NOT_APPLICABLE, "N/A")

    def update_status(self, key, step, icon, msg=None):
        with self.lock:
            if step == "msg":
                self.status[key]["msg"] = icon
            else:
                # Don't overwrite N/A slots
                if self.status[key].get(step, (None,))[0] == NOT_APPLICABLE:
                    return
                self.status[key][step] = (icon, msg or self.status[key][step][1])

    def generate_table(self):
        table = Table(
            title="[bold blue]NotebookLM Automation — Topic Status[/bold blue]",
            box=box.ROUNDED,
            expand=True
        )
        table.add_column("Topic Key", style="cyan", no_wrap=True)
        table.add_column("Notebook", justify="center")
        table.add_column("Research", justify="center")

        for art in self.artifact_types:
            table.add_column(art.title().replace("_", " "), justify="center")

        table.add_column("Last Action", style="white", ratio=1)

        with self.lock:
            for key in self.topic_keys:
                row = [key]
                row.append(self.status[key]["notebook"][0])
                row.append(self.status[key]["research"][0])

                for art in self.artifact_types:
                    row.append(self.status[key][art][0])

                row.append(self.status[key]["msg"])
                table.add_row(*row)

        return Panel(table, border_style="bright_blue", padding=(1, 1))
