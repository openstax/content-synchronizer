#!/usr/bin/env bash

############################################################
# Help                                                     #
############################################################
help() {
  # Display Help
  echo "This script syncs book content from an cnx archive server to a Github book repository"
  echo
  echo "Syntax: scriptTemplate [-h|v|d|c|u|p|e|r]"
  echo "Options:"
  echo "h     Print this Help."
  echo "v     Print software version and exit."
  echo "d     Sync a derived book"
  echo "c     Create new Github repository and push content"
  echo
  echo "Inputs required when c option specified:"
  echo "u     Github user"
  echo "p     Github password or token"
  echo "e     Github email"
  echo "r     Github Repository name"
  echo "o     Github OpenStax Parent Repository"
  echo "k     OpenStax Github Token"
  echo "l     OpenStax Github username"
  echo
  echo "Required if the destination repository is part of an organization"
  echo "q    Destination Github Orhanization"
  echo
}

############################################################
# Main program                                             #
############################################################
# Get options
while getopts ":hcdve:p:u:r:o:k:l:q:" option; do
  case "${option}" in
  c) #Create Github repo
    GITHUB_CREATE_REPO=True ;;
  d) #Create derived book
    #TODO Implement the derived script
    ;;
  e) #Github email
    GITHUB_EMAIL=${OPTARG} ;;
  h) #display help
    help
    exit
    ;;
  p) #Github password or TOKEN
    GITHUB_PASSWORD=${OPTARG} ;;
  r) #Repository name
    REPO_NAME=${OPTARG} ;;
  o) #Openstax Github Book Parent Repository
    PARENT_REPO_NAME=${OPTARG} ;;
  k) #Openstax Github Username
    OPENSTAX_GITHUB_USERNAME=${OPTARG} ;;
  l) #Openstax Github Book Parent Repository
    OPENSTAX_GITHUB_TOKEN=${OPTARG} ;;
  u) #Github user
    GITHUB_USER=${OPTARG} ;;
  q) #Destination Organization
    GITHUB_ORGANIZATION=${OPTARG} ;;
  v) #display version of script and neb
    neb --version
    exit
    ;;
  \?) # Invalid option
    echo "Error: Invalid option"
    help
    exit
    ;;
  esac
done
shift $((OPTIND - 1))

set -xeo pipefail

# Upgrade from ./archive-syncfile to META-INF/books.xml
if [[ ! -f ./META-INF/books.xml ]]; then
  [[ -d ./META-INF/ ]] || mkdir ./META-INF/

  echo '<container xmlns="https://openstax.org/namespaces/book-container" version="1">' >./META-INF/books.xml

  while read slug collid; do
    echo "    <book slug=\"${slug}\" collection-id=\"${collid}\" href=\"../collections/$slug.collection.xml\" />" >>./META-INF/books.xml
  done <./archive-syncfile

  echo '</container>' >>./META-INF/books.xml
fi

# Create a temporary ./archive-syncfile
xmlstarlet sel -t --match '//*[@slug]' --value-of '@slug' --value-of '" "' --value-of '@collection-id' --nl <./META-INF/books.xml >./archive-syncfile

# Write the ./canonical.json file out
[[ ! -f ./canonical-temp.txt ]] || rm ./canonical-temp.txt
echo '[' >./canonical.json
while read slug collid; do
  echo "    \"${slug}\"" >>./canonical-temp.txt
done <./archive-syncfile
# Add a comma to every line except the last line https://stackoverflow.com/a/35021663
sed '$!s/$/,/' ./canonical-temp.txt >>./canonical.json
rm ./canonical-temp.txt
echo ']' >>./canonical.json

# Fetch the books and keep a list of module-ids
while read slug collid; do
  rm -rf ./"$slug"
  neb get -r -d $slug $SERVER $collid latest
  echo "--- $slug" >>module-ids
  find "./$slug/" -maxdepth 1 -mindepth 1 -type d | xargs -I{} basename {} >>module-ids
done <./archive-syncfile

# Exit if content in collection.xml is empty
while read slug collid; do
  sed -i -e  "s/\\\\012//g" "$slug/collection.xml"
  content=$(xmlstarlet sel -t -v "/col:collection/col:content" $slug/collection.xml | sed 's/ *$//g')
  if [[ ! "$content" ]];then
    echo "No content found for $slug"
    exit 1
  fi
done <./archive-syncfile


python $CODE_DIR/find-module-canonical.py >canonical-modules
rm -rf modules collections metadata media
mkdir modules collections metadata media
cat canonical-modules | awk '{ print "cp -r "$1"/"$2" modules/"; }' | xargs -I {} bash -c '{}'
find modules/. -name .sha1sum | xargs rm
python $CODE_DIR/consolidate_media.py modules media
while read slug collid; do
  mv "$slug/collection.xml" "collections/$slug.collection.xml"
  # Inject slug into book metadata so it can be used when updating
  # the book collection XML
  jq --arg slug "$slug" '. + {slug: $slug}' "$slug/metadata.json" >"metadata/$slug.metadata.json"
  rm -rf ./"$slug"

done <archive-syncfile
python $CODE_DIR/remove_pi.py modules collections
python $CODE_DIR/override_module_titles.py modules collections
python $CODE_DIR/update_metadata.py modules collections metadata
python $CODE_DIR/poet_ready.py $CODE_DIR
find modules/. -name metadata.json | xargs rm
rm -rf ./metadata module-ids ./canonical-modules ./archive-syncfile

if [[ $GITHUB_CREATE_REPO = True && -n "$GITHUB_USER" && ! -z "$GITHUB_PASSWORD" && ! -z "$GITHUB_EMAIL" && ! -z "$REPO_NAME" ]]; then

  echo "Creating Github Repository"
  eval $(ssh-agent -s)
  if [ ! -e "$HOME/.ssh/known_hosts" ]; then
    touch "$HOME/.ssh/known_hosts"
  fi


  if [[ ! -z "$GITHUB_ORGANIZATION" ]]; then
    #Check if repository exists.
    repo_container_url="https://api.github.com/orgs/$GITHUB_ORGANIZATION/repos"
  else
    repo_container_url="https://api.github.com/orgs/user/repos"
  fi
  repo_exists=$(curl -u $GITHUB_USER:$GITHUB_PASSWORD "https://api.github.com/repos/$GITHUB_ORGANIZATION/$REPO_NAME" | jq -r '.message')
  if [[ "$repo_exists" == 'Not Found' ]]; then
    repo_creation_output=$(curl -u $GITHUB_USER:$GITHUB_PASSWORD $repo_container_url -d '{"name":"'$REPO_NAME'"}')
  else
    echo "Repository already exists!"
    exit 1
  fi

  git_url=$(echo $repo_creation_output | jq -r '.ssh_url')
  if [[ "$git_url" == null || "$git_url" == "null" ]]; then exit 1; fi

  echo "Repository URL: $git_url"
  #Clone the Parent Github repository if necessary
  if [[ ! -z "$PARENT_REPO_NAME" && ! -z "$OPENSTAX_GITHUB_USERNAME" && ! -z "$OPENSTAX_GITHUB_TOKEN" ]]; then
    curr_dir=${PWD##*/}
    git clone "https://$OPENSTAX_GITHUB_USERNAME:$OPENSTAX_GITHUB_TOKEN@github.com/openstax/$PARENT_REPO_NAME.git" ../$PARENT_REPO_NAME
    cd ../$PARENT_REPO_NAME
    main_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
    for i in $(git branch -a | grep 'remotes' | awk -F/ '{print $3}' | grep -v 'HEAD ->'); do git checkout $i; done
    git checkout $main_branch
    git config --local user.email $GITHUB_EMAIL
    git config --local user.name "Migration Sync Script"
    git remote set-url origin $git_url
    git checkout -b "derived-branch"
    rm -rf *
    cp -R ../$curr_dir/* .
    git add .
    git commit -m "Initial Commit $REPO_NAME"
  else
    git init
    git config --local user.email $GITHUB_EMAIL
    git config --local user.name "Migration Sync Script"
    git add .
    git commit -m "Initial Commit: $REPO_NAME from $SERVER"
    git branch -M main
    git remote add origin "$git_url"
  fi

  git push --all origin
  echo "Github Repository Created!"

fi
echo 'Done.'
