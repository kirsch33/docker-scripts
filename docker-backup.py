import docker
import subprocess
import os
import time
from datetime import date
import tarfile
from rclone_python import rclone

prefix = "docker-backup"
timestamp = date.strftime(date.today(), "%m-%d-%y")
filename = prefix + "_" + str(timestamp) + ".tar.gz"
docker_dir = "/var/docks"

exclude_dirs = [os.path.normpath(r"/var/docks/plex/Library/'Application Support'/'Plex Media Server'/Media"),
                os.path.normpath(r"/var/docks/plex/Library/'Application Support'/'Plex Media Server'/Cache"),
                os.path.normpath(r"/var/docks/influx/data/engine")]
exclude_exts = [".db"]

client = docker.from_env()
containers = client.containers.list()
dep_containers = []

for container in containers:
    dep_container = str(container.labels['com.docker.compose.depends_on'])

    if dep_container !=  "":
        dep_container = dep_container[:dep_container.index(":")]
        containers.remove(client.containers.get(dep_container))

for dep_container in dep_containers:
    containers.append(dep_container)

def filter_func(tarinfo):
    if any(dir in os.path.normpath(os.path.abspath(tarinfo.name)) for dir in exclude_dirs):
        return None
    elif any(ext in tarinfo.name for ext in exclude_exts):
        return None
    return tarinfo

try:
    print("************************************")
    print("**********docker-backup.py**********")
    print("************************************")
    print("...")
    print("...")
    print("...")
    print("Stopping all containers...")

    for container in containers:
        container.stop(timeout=15)
        container.wait()

    print("...")
    print("...")
    print("...")
    print("Creating tar.gz file...")

    tar = tarfile.open(filename, "w:gz")
    tar.add(docker_dir, filter=filter_func)
    tar.close()

    print("...")
    print("...")
    print("...")
    print("Starting all containers...")

    for container in containers:
        container.start()
        time.sleep(15)

    print("...")
    print("...")
    print("...")

    rclone.copy(filename, "gdrive:/lab", args=["--retries=5"])

    print("...")
    print("...")
    print("...")
    print("Deleting tar.gz file...")

    if os.path.exists(filename):
        os.remove(filename)

    backups = rclone.ls(
        "gdrive:/lab",
        files_only=True,
        args=["--include=" + prefix + "*"])

    sorted_backups = sorted(backups, key=lambda x : x['ModTime'], reverse=True)

    if len(sorted_backups) > 2:

        backups_to_delete = sorted_backups[2:]

        print("...")
        print("...")
        print("...")
        print("Deleting " + str(len(backups_to_delete)) + " backups...")

        for backup in backups_to_delete:
            rclone.delete("gdrive:/lab" + "/" + backup['Path'],
                          args=["--drive-use-trash=false"])
    else:
        print("...")
        print("...")
        print("...")
        print("No backups to delete...")

    print("...")
    print("...")
    print("...")
    print("success")
except:
    if os.path.exists(filename):
        os.remove(filename)

    for container in containers:
        container.start()
