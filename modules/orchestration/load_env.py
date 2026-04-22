import os
# chemin ABSOLU vers la racine du projet
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_dir, ".env")

def load_env():
    env = {}
    try:
        f = open(env_path, "r")
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env[key] = value
        f.close()
    except:
        pass
    return env
