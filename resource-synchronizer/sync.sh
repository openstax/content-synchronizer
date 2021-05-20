#!/usr/bin/env bash
set -xeo pipefail

# Upgrade from ./archive-syncfile to META-INF/books.xml
if [[ ! -f ./META-INF/books.xml ]]
then
  [[ -d ./META-INF/ ]] || mkdir ./META-INF/

  echo '<container xmlns="https://openstax.org/namespaces/book-container" version="1">' > ./META-INF/books.xml

  while read slug collid
  do
    echo "    <book slug=\"${slug}\" collection-id=\"${collid}\" href=\"../collections/$slug.collection.xml\" />" >> ./META-INF/books.xml
  done < ./archive-syncfile

  echo '</container>' >> ./META-INF/books.xml
fi

# Create a temporary ./archive-syncfile
xmlstarlet sel -t --match '//*[@slug]' --value-of '@slug' --value-of '" "' --value-of '@collection-id' --nl < ./META-INF/books.xml > ./archive-syncfile

# Write the ./canonical.json file out
[[ ! -f ./canonical-temp.txt ]] || rm ./canonical-temp.txt
echo '[' > ./canonical.json
while read slug collid
do
  echo "    \"${slug}\"" >> ./canonical-temp.txt
done < ./archive-syncfile
# Add a comma to every line except the last line https://stackoverflow.com/a/35021663
sed '$!s/$/,/' ./canonical-temp.txt >> ./canonical.json
rm ./canonical-temp.txt
echo ']' >> ./canonical.json

# Fetch the books and keep a list of module-ids
while read slug collid
do
  rm -rf ./"$slug"
  neb get -r -d $slug $SERVER $collid latest
  echo "--- $slug" >> module-ids
  find "./$slug/" -maxdepth 1 -mindepth 1 -type d | xargs -I{} basename {}  >> module-ids
done < ./archive-syncfile

python $CODE_DIR/find-module-canonical.py > canonical-modules
rm -rf modules collections metadata media
mkdir modules collections metadata media
cat canonical-modules | awk '{ print "cp -r "$1"/"$2" modules/"; }' | xargs -I {} bash -c '{}'
find modules/. -name .sha1sum | xargs rm
python $CODE_DIR/consolidate_media.py modules media
while read slug collid
do
  mv "$slug/collection.xml" "collections/$slug.collection.xml"
  # Inject slug into book metadata so it can be used when updating
  # the book collection XML
  jq --arg slug "$slug" '. + {slug: $slug}' "$slug/metadata.json" > "metadata/$slug.metadata.json"
  rm -rf ./"$slug"
done < archive-syncfile
python $CODE_DIR/remove_pi.py modules collections
python $CODE_DIR/override_module_titles.py modules collections
python $CODE_DIR/update_metadata.py modules collections metadata
find modules/. -name metadata.json | xargs rm
rm -rf ./metadata module-ids ./canonical-modules ./archive-syncfile
echo 'Done.'