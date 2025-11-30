import os
os.chdir(r"C:\Users\Varsha Kaushik\OneDrive\Desktop\varsh")
print("cwd after chdir:", os.getcwd())
from dotenv import load_dotenv
result = load_dotenv()
print("load_dotenv returned:", result)
v = os.getenv("OPENAI_API_KEY")
if v:
    print("OPENAI_API_KEY found, preview:", v[:15] + "...")
else:
    print("OPENAI_API_KEY not found")
    # manually read .env
    with open(".env") as f:
        lines = f.readlines()
    print("first 3 lines of .env:")
    for line in lines[:3]:
        print(repr(line))
