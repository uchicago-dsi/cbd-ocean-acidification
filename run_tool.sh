# run_docker_bash.sh
#
# Builds and runs a Docker container and then enables
# an interactive bash terminal from which users can view
# container contents and execute Python scripts. Mounts
# the entire pipeline directory to permit testing without
# container restarts.
# 

IMAGE_NAME=cbd
CONTAINER_NAME=cbd

if [[ $4 == "build" ]];
then
    docker build -t $IMAGE_NAME .
fi
docker run --name $CONTAINER_NAME \
    --volume "/${PWD}/output:/src/output" \
    --volume "/${PWD}/pipeline/metadata:/src/pipeline/metadata" \
    --rm \
    $IMAGE_NAME \
    $1 --start $2 --end $3
sudo chown -R $USER: output/