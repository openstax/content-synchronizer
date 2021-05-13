"""Move module media files to ./media and handle sha conflicts"""

import sys
from pathlib import Path
import hashlib
from lxml import etree
import os.path

IGNORE_FILENAMES = [
    "index.cnxml",
    "metadata.json"
]

SHA_SUFFIX_LENGTH = 4


def update_cnxml_references(cnxml_file, reference_updates):
    """Given a cnxml file, update all specified image references
    """
    doc = etree.parse(str(cnxml_file))

    for node in doc.xpath(
        "//x:image",
        namespaces={"x": "http://cnx.rice.edu/cnxml"}
    ):
        src_filename = node.attrib["src"]
        if src_filename in reference_updates:
            node.attrib["src"] = reference_updates[src_filename]

    with open(cnxml_file, "wb") as f:
        doc.write(f, encoding="utf-8", xml_declaration=False)


def main():
    modules_dir = Path(sys.argv[1]).resolve(strict=True)
    media_dir = Path(sys.argv[2]).resolve(strict=True)

    media_files = [
        mf for mf in modules_dir.glob("**/*")
        if mf.is_file() and mf.name not in IGNORE_FILENAMES
    ]

    print(f"{len(media_files)} media files found")

    # Pass 1: Find any files that have sha conflicts so we know how to handle
    # them when we move to the media directory

    shas_by_filename = {}  # Map of filename: sha
    shas_by_filepath = {}  # Map of filepath: sha
    sha_conflicts = set()  # Set of file names with sha conflicts

    for media in media_files:
        sha1 = hashlib.sha1()
        sha1.update(media.read_bytes())
        media_sha = sha1.hexdigest()
        shas_by_filepath[media] = media_sha

        prev_sha = shas_by_filename.get(media.name)
        if prev_sha and media_sha != prev_sha:
            # Add this filename to the conflicts set since it has a conflicting
            # sha with at least one other module using the same filename
            sha_conflicts.add(media.name)
        else:
            # Either this is a filename we haven't seen before, or it has the
            # same sha value so this is a nop
            shas_by_filename[media.name] = media_sha

    print(f"Found {len(sha_conflicts)} filenames with conflicting shas")

    # Pass 2: Move files to media directory, adding a subset of the sha string
    # to the name as a suffix if it has a sha conflict and queue updates to
    # CNXML files

    cnxml_reference_updates = {}

    for media in media_files:
        cnxml_file = media.parent / "index.cnxml"

        # Add the relative path to all image filenames
        new_media_relpath = os.path.relpath(
            media_dir,
            media.resolve().parent
        )

        if media.name not in sha_conflicts:
            cnxml_reference_updates.setdefault(cnxml_file, {})[media.name] = \
                f"{new_media_relpath}/{media.name}"

            media.rename(media_dir / media.name)
        else:
            sha_suffix = shas_by_filepath[media][0:SHA_SUFFIX_LENGTH]
            new_filename = \
                f"{media.with_suffix('').name}-{sha_suffix}{media.suffix}"

            cnxml_reference_updates.setdefault(cnxml_file, {})[media.name] = \
                f"{new_media_relpath}/{new_filename}"

            media.rename(media_dir / new_filename)

    # Update image references in CNXML files
    for cnxml_file, reference_updates in cnxml_reference_updates.items():
        update_cnxml_references(cnxml_file, reference_updates)


if __name__ == "__main__":
    main()
