import docker
import subprocess
from simple_term_menu import TerminalMenu

client = docker.from_env()
containers = client.containers.list()

for container in containers:
    dep_container = str(container.labels['com.docker.compose.depends_on'])

    if dep_container !=  "":
        dep_container = dep_container[:dep_container.index(":")]
        containers.remove(client.containers.get(dep_container))

def update_all():
    for container in containers:
        update_container(container)

def update_selective():
    for container in containers:
        print("Update container " + str(container.name) + " ?")

        options = ["Yes", "No", "Exit"]
        menu = TerminalMenu(options)
        index = menu.show()

        if options[index] == "Yes":
            update_container(container)
        elif options[index] == "No":
            continue
        elif options[index] == "Exit":
            break

def update_container(container):
    dep_container = str(container.labels['com.docker.compose.depends_on'])

    if dep_container != "":
        dep_container = dep_container[:dep_container.index(":")]
        subprocess.run(["/usr/bin/docker", "stop", dep_container])

    subprocess.run(["/usr/bin/docker", "stop", str(container.name)])

    subprocess.run([
        "/usr/local/bin/docker-compose",
        "-f",
        container.labels['com.docker.compose.project.config_files'],
        "up",
        "-d",
        "--build",
        "--pull=always",
        "--force-recreate"])

print("Update all containers?")
options = ["Yes", "No", "Exit"]
menu = TerminalMenu(options)
index = menu.show()

if options[index] == "Yes":
    update_all()
elif options[index] == "No":
    update_selective()
elif options[index] == "Exit":
    quit()

print("...")
print("...")
print("...")
print("Prune everything?")

options = ["Yes", "Exit"]
menu = TerminalMenu(options)
index = menu.show()

if options[index] == "Yes":
    subprocess.run(["/usr/bin/docker", "system", "prune", "-f", "-a"])
elif options[index] == "Exit":
    quit()
    
