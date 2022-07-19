if [[ "$1" == "--help" ]]; then
  echo "Usage:"
  echo "./run_scraper.sh [--windows] [--debug]"
  echo "--windows [optional] For Windows users and outputs python stdout()/stderr() to file "
  echo "--debug [optional] To launch the Docker container in interactive shell mode, instead of executing the script"
  exit 0
fi

for arg in "$@"; do
  if [ "$arg" == "--debug" ]; then
    EXTRA_PARAMS='-it --entrypoint /bin/bash'
  elif [ "$arg" == '--windows' ]; then
    WINDZ=1
  fi
done

echo "-----------------"
echo "Removing data.csv and /apify_docker_storage (using sudo powers) if they exist"
test -f data.csv && rm data.csv
test -d apify_docker_storage && (if [ -z "${WINDZ+x}" ]; then
                                  rm -rf apify_docker_storage || sudo rm -rf apify_docker_storage
                                else
                                  rm -rf apify_docker_storage # no sudo on windows
                                fi)

if [ -z "${WINDZ+x}" ]; then
    base_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
else
    base_path="`pwd -W`"
fi

domain=${PWD##*/}
scraper_name=$(echo ${domain}-scraper | sed 's/_/-/g')

PWD_SET=$(if [[ -z $PROXY_PASSWORD ]]; then echo ""; else echo "< NON-EMPTY >"; fi)
GAK_SET=$(if [[ -z $GOOGLE_API_KEY ]]; then echo ""; else echo "< NON-EMPTY >"; fi)

echo "-----------------"
echo "BUILDING AND RUNNING DOCKER IMG [$scraper_name:latest] WITH:"
echo
echo "PROXY_URL=$PROXY_URL"
echo "PROXY_PASSWORD=$PWD_SET"
echo "GOOGLE_API_KEY=$GAK_SET"
echo "-----------------"

docker build -t $scraper_name --no-cache .
rm -rf apify_docker_storage

docker run -e GOOGLE_API_KEY -e PROXY_URL -e PROXY_PASSWORD -e APIFY_LOCAL_STORAGE_DIR=apify_storage -e APIFY_TOKEN='' -v "${base_path}/apify_docker_storage:/apify_storage" $EXTRA_PARAMS ${scraper_name}:latest


if [ -n "${WINDZ+x}" ]; then
	error_filename="$(date +"%Y-%m-%d_%H-%M")"
	docker logs "$(docker container ls --format '{{.Names}}' --latest)" 2>&1 |tee "${base_path}/${scraper_name}_${error_filename}.log"
fi
