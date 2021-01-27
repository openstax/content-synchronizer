"""Update metadata in repository during content sync"""

import sys
import json
from pathlib import Path
from lxml import etree


NS_MDML = "http://cnx.rice.edu/mdml"
NS_CNXML = "http://cnx.rice.edu/cnxml"
NS_COLLXML = "http://cnx.rice.edu/collxml"
MODULE_METADATA_ACCEPT_TAGS = [
    f"{{{NS_MDML}}}title",
    f"{{{NS_MDML}}}abstract",
    f"{{{NS_MDML}}}content-id"
]
MODULE_METADATA_ADDED_TAGS_FROM_JSON = {
    "id": "uuid"
}
COLLECTION_METADATA_ACCEPT_TAGS = [
    f"{{{NS_MDML}}}title",
    f"{{{NS_MDML}}}content-id",
    f"{{{NS_MDML}}}license"
]
COLLECTION_METADATA_ADDED_TAGS_FROM_JSON = {
    "id": "uuid",
    "slug": "slug"
}


def filter_accepted_tags(xml_doc, accept_tags, md_namespace):
    """Remove metadata fields based upon an accepted tags list"""
    metadata = xml_doc.xpath(
        "//x:metadata",
        namespaces={"x": md_namespace}
    )[0]

    for elem in metadata:
        if elem.tag not in accept_tags:
            metadata.remove(elem)


def add_metadata_from_json(xml_doc, metadata_json, added_tags, md_namespace):
    metadata = xml_doc.xpath(
        "//x:metadata",
        namespaces={"x": md_namespace}
    )[0]

    for from_key, to_tag in added_tags.items():
        value = metadata_json[from_key]
        element = etree.Element(f"{{{NS_MDML}}}{to_tag}")
        element.text = value
        element.tail = "\n"
        metadata.append(element)


def update_xml_metadata(input_files, accept_tags, added_tags, md_namespace):
    """Update a list of module or collection files given a list of input_files
    where each entry is a (xml, metadata) tuple
    """
    for xml_file, metadata_file in input_files:
        xml_doc = etree.parse(str(xml_file))
        metadata_json = json.load(metadata_file.open())

        filter_accepted_tags(xml_doc, accept_tags, md_namespace)
        add_metadata_from_json(
            xml_doc, metadata_json, added_tags, md_namespace
        )

        with xml_file.open("wb") as outfile:
            xml_doc.write(outfile, encoding="utf-8", xml_declaration=False)


def main():
    modules_dir = Path(sys.argv[1]).resolve(strict=True)
    collections_dir = Path(sys.argv[2]).resolve(strict=True)
    collection_metadata_dir = Path(sys.argv[3]).resolve(strict=True)

    module_files = [
        (
            cf.resolve(strict=True),
            (cf / ".." / "metadata.json").resolve(strict=True)
        )
        for cf in modules_dir.glob("**/*")
        if cf.is_file() and cf.name == "index.cnxml"
    ]

    collection_files = [
        (
            cf.resolve(strict=True),
            (collection_metadata_dir /
                f"{cf.name.split('.')[0]}.metadata.json").resolve(strict=True)
        )
        for cf in collections_dir.glob("*.xml")
    ]

    update_xml_metadata(
        module_files,
        MODULE_METADATA_ACCEPT_TAGS,
        MODULE_METADATA_ADDED_TAGS_FROM_JSON,
        NS_CNXML
    )

    update_xml_metadata(
        collection_files,
        COLLECTION_METADATA_ACCEPT_TAGS,
        COLLECTION_METADATA_ADDED_TAGS_FROM_JSON,
        NS_COLLXML
    )


if __name__ == "__main__":
    main()
