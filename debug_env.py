import os
from pathlib import Path
print("cwd:", Path.cwd())
print(".env_exists:", Path(".env").exists())
try:
    from dotenv import load_dotenv
    load_dotenv()
    v = os.getenv("OPENAI_API_KEY")
    preview = (v[:8] + "...") if v else "<empty>"
    print("OPENAI loaded:", bool(v))
    print("OPENAI preview:", preview)
except Exception as e:
    print("dotenv error:", e)
