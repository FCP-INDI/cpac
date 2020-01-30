import os

def recursive_remove_dir(path):
    for fp in os.listdir(path):
        inner_path = os.path.join(path, fp)
        if os.path.isdir(inner_path):
            recursive_remove_dir(inner_path)
        else:
            os.remove(inner_path)
    os.rmdir(path)
