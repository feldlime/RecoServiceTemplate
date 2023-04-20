#!/bin/bash

download() {
    folder=$1
    file_path=$2
    gdrive_file_id=$3

    mkdir -p "$folder"
    if [ ! -f "$file_path" ]
    then
        gdown "$gdrive_file_id" -O "$file_path"
    fi
    echo "Downloaded" "$file_path"
}

download "models/" "models/light_fm.dill" "1NjTwM9hMveiV8twsfmcElswkj6iAZnsx"

download "models/lightfm" "models/lightfm/user_embeddings.dill" "107WdHB8Ka6Hqupw4g3iALLEG2w3N52y9"

download "models/popular_in_category" "models/popular_in_category/popular_in_category_model.dill" "1-0jA4-8wYMlzD1G4CxFQvjDVuwhRPtfm"
