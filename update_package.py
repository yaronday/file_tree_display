import subprocess


def run():
    commands = [
        "uv add --dev build twine",
        "uv build",
        "twine upload dist/*"
    ]
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            break


if __name__ == "__main__":
    pass  # run()
