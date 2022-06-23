import sys
from pathlib import Path
from lxml import etree
from namespaces import XPATH_NSMAP_BASIC


def parse_module_titles(collection_file):
    collection = etree.parse(str(collection_file))
    data = {}

    module_titles = collection.xpath(
        "//col:module/md:title",
        namespaces=XPATH_NSMAP_BASIC
    )
    for mtitle_element in module_titles:
        module_id = mtitle_element.getparent().get("document")
        title = mtitle_element.text
        data[module_id] = title

    return data


def override_title(module_file, titles_by_id):
    module = etree.parse(str(module_file))

    module_title_element = module.xpath(
        "//cnxml:title",
        namespaces=XPATH_NSMAP_BASIC
    )[0]

    # The md:title will likely be there, but just in case it is removed
    # prior to this script running in the future we'll assume it's possible
    # for it not to be there
    maybe_module_md_title_element = module.xpath(
        "//md:title",
        namespaces=XPATH_NSMAP_BASIC
    )

    module_content_id = module.xpath(
        "//md:content-id",
        namespaces=XPATH_NSMAP_BASIC
    )

    override_title_value = titles_by_id.get(module_content_id[0].text) if len(module_content_id) > 0 else None
    if not override_title_value:
        # Module title wasn't defined in a collection file
        return

    module_title_element.text = override_title_value

    if len(maybe_module_md_title_element) > 0:
        maybe_module_md_title_element[0].text = override_title_value

    with module_file.open("wb") as outfile:
        module.write(outfile, encoding="utf-8", xml_declaration=False)


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

    module_titles_by_id = {}
    for collection_file in collection_files:
        collection_module_titles = parse_module_titles(collection_file)

        # Instead of blindly updating our existing dict, check for unexpected
        # conflicts and raise an error if found
        for module_id, module_title in collection_module_titles.items():
            existing_title = module_titles_by_id.get(module_id)
            if existing_title and (existing_title != module_title):
                raise Exception(f"Found conflicting titles for {module_id}")
            module_titles_by_id[module_id] = module_title

    for module_file in module_files:
        override_title(module_file, module_titles_by_id)


if __name__ == "__main__":
    main()
