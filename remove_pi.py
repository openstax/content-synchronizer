import sys
from pathlib import Path
from lxml import etree

# We don't want to remove tail text for the processing instruction so a special method is needed
# Credit: SO user Messa @ https://stackoverflow.com/questions/7981840/how-to-remove-an-element-in-lxml


def remove_element(el):
    parent = el.getparent()
    if el.tail and el.tail.strip():
        prev = el.getprevious()
        if prev:
            prev.tail = (prev.tail or '') + el.tail
        else:
            parent.text = (parent.text or '') + el.tail
    parent.remove(el)


def remove_processing_instructions(xml_file):
    xml_doc = etree.parse(str(xml_file))

    pis = xml_doc.xpath("//processing-instruction()")
    for pi in pis:
        remove_element(pi)

    with xml_file.open("wb") as outfile:
        xml_doc.write(outfile, encoding="utf-8", xml_declaration=False)


def main():
    modules_dir = Path(sys.argv[1]).resolve(strict=True)
    collections_dir = Path(sys.argv[2]).resolve(strict=True)

    module_files = [
        cf.resolve(strict=True)
        for cf in modules_dir.glob("**/*")
        if cf.is_file() and cf.name == "index.cnxml"
    ]

    collection_files = [
        cf.resolve(strict=True)
        for cf in collections_dir.glob("*.xml")
    ]

    for module_file in module_files:
        remove_processing_instructions(module_file)

    for collection_file in collection_files:
        remove_processing_instructions(collection_file)


if __name__ == "__main__":
    main()
