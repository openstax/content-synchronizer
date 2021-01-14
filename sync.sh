#!/usr/bin/env bash
set -xeo pipefail
cd $OUTPUT
rm -f module-ids canonical-modules
while read slug collid
do
  rm -rf ./"$slug"
  neb get -r -d $slug cnx.org $collid latest
  echo "--- $slug" >> module-ids
  find "./$slug/" -maxdepth 1 -mindepth 1 -type d | xargs -I{} basename {}  >> module-ids
done < archive-syncfile
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
python $CODE_DIR/update_metadata.py modules collections metadata
find modules/. -name metadata.json | xargs rm
rm -rf metadata
echo 'Done.'