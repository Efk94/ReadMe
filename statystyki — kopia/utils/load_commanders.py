import os

def load_commanders():
    avatar_folder = r'C:\Users\profo\OneDrive\Pulpit\Nowy folder\Avatar'
    commanders = {}
    for filename in os.listdir(avatar_folder):
        name, _ = os.path.splitext(filename)
        commanders[name] = os.path.join(avatar_folder, filename)
    return commanders
