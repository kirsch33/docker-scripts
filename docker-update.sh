#!/bin/bash

declare -a containers=("caddy" "unifi" "jackett" "ombi" "radarr" "sonarr" "transmission" "plex" "diun" "fail2ban")

arraylength=${#containers[@]}

function update_all {
        for (( i=0; i<arraylength; i++ ));
        do
                update_container "${containers[i]}"
        done

        exit
}

function update_selective {
        for (( i=0; i<arraylength; i++ ));
        do
                echo "Update container " "${containers[i]}" "?"

                select yn in "Yes" "No";
                do
                        case $yn in
                                Yes ) update_container "${containers[i]}"; break;;
                                No ) break;;
                        esac
                done
        done

        exit
}

function update_container {
                (/usr/bin/docker stop "$1")
                (/usr/bin/docker rm "$1")

                (/usr/bin/docker system prune -f -a)

                (/usr/local/bin/docker-compose -f /var/docks/"$1"/docker-compose.yml up -d)

                (/usr/bin/docker system prune -f -a)
}

echo "Update all containers?"

select yn in "Yes" "No";
do
        case $yn in
                Yes ) update_all; break;;
                No ) update_selective;;
        esac
done


