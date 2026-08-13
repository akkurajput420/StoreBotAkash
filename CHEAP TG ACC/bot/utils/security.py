import os
def session_path(phone, sessions_dir):
    from pathlib import Path
    return str(Path(sessions_dir)/phone.replace("+",""))
