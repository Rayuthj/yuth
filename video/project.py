"""Multi-video support.

A *project* is one video. The original "What If You Had 500 IQ?" lives at the
legacy locations (video/script.py, video/chapters/, build/, output/). Every
other video lives in video/projects/<slug>/ with its own script.py and
chapters/ package, and builds into build/<slug>/ and output/<slug>/.

The active project comes from $VIDEO_PROJECT (default "iq500"), so worker
processes started by the renderer inherit it automatically. CLIs accept
--project, which sets that variable.
"""
import importlib
import os
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = "iq500"


@dataclass
class Project:
    slug: str
    script_mod: str
    chapters_pkg: str
    build: str
    out: str
    name: str            # base file name of the final video

    @property
    def script(self):
        return importlib.import_module(self.script_mod)

    def chapter(self, ch):
        return importlib.import_module(f"{self.chapters_pkg}.ch{ch:02d}")

    @property
    def timeline(self):
        return os.path.join(self.build, "timeline.json")

    @property
    def video(self):
        return os.path.join(self.out, f"{self.name}.mp4")

    @property
    def title(self):
        return getattr(self.script, "TITLE", "What If You Had 500 IQ?")


def get(slug=None):
    slug = slug or os.environ.get("VIDEO_PROJECT", LEGACY)
    if slug == LEGACY:
        p = Project(slug, "video.script", "video.chapters", os.path.join(ROOT, "build"), os.path.join(ROOT, "output"),
                    "what_if_you_had_500_iq")
    else:
        p = Project(slug, f"video.projects.{slug}.script", f"video.projects.{slug}.chapters",
                    os.path.join(ROOT, "build", slug), os.path.join(ROOT, "output", slug), slug)
        p.name = getattr(p.script, "FILE_NAME", slug)
    os.makedirs(p.build, exist_ok=True)
    os.makedirs(p.out, exist_ok=True)
    return p


def use(slug):
    """Select the active project for this process and its children."""
    if slug:
        os.environ["VIDEO_PROJECT"] = slug
    return get()


def pop_project_arg(argv):
    """Strip '--project X' from an argv list and activate it."""
    if "--project" in argv:
        i = argv.index("--project")
        use(argv[i + 1])
        del argv[i:i + 2]
    return argv
