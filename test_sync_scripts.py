"""Tests for Python scripts used for syncing content"""

import hashlib
import consolidate_media
import update_metadata
import remove_pi
import json
import io
from lxml import etree


def _compare_xml_strings(data, expected):
    """Helper to compare two XML strings using etree"""
    parser = etree.XMLParser(remove_blank_text=True)
    data_etree, expected_tree = map(
        lambda str: etree.parse(io.StringIO(str), parser),
        [data, expected]
    )

    assert etree.tostring(data_etree) == etree.tostring(expected_tree)


def test_consolidate_media(tmp_path, mocker):
    """Test consolidate-media script"""

    # Scenarios to test using three modules:
    # - same filename used across modules with no sha differences
    # - same filename used across modules with all three different shas
    # - same filename with 2 modules using sha A and 1 module using sha B
    # - module unique file media file
    # - module with an unused media file

    def _create_module(module_name):
        module_dir = modules_dir / module_name
        module_dir.mkdir()
        module_cnxml = module_dir / "index.cnxml"
        module_cnxml_content = f"""
        <document xmlns="http://cnx.rice.edu/cnxml">
            <content>
                <image src="image1.jpg"/>
                <image src="image2.jpg"/>
                <image src="image3.jpg"/>
                <image src="{module_name}.jpg"/>
            </content>
        </document>
        """
        module_cnxml.write_text(module_cnxml_content)

    def _generate_sha_suffix(image_content):
        sha1 = hashlib.sha1()
        sha1.update(image_content)
        return sha1.hexdigest()[0:consolidate_media.SHA_SUFFIX_LENGTH]

    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    media_dir = tmp_path / "media"
    media_dir.mkdir()

    module1_name = "m00001"
    module2_name = "m00002"
    module3_name = "m00003"

    _create_module(module1_name)
    _create_module(module2_name)
    _create_module(module3_name)

    (modules_dir / module1_name / f"{module1_name}.jpg").write_text(
        f"{module1_name} image"
    )
    (modules_dir / module2_name / f"{module2_name}.jpg").write_text(
        f"{module2_name} image"
    )
    (modules_dir / module3_name / f"{module3_name}.jpg").write_text(
        f"{module3_name} image"
    )

    image2_1_content = b"image2 image1"
    image2_2_content = b"image2 image2"
    image2_3_content = b"image2 image3"
    image3_1_content = b"image3 image1"
    image3_2_content = b"image3 image2"

    (modules_dir / module1_name / "image1.jpg").write_bytes(b"image1 image")
    (modules_dir / module2_name / "image1.jpg").write_bytes(b"image1 image")
    (modules_dir / module3_name / "image1.jpg").write_bytes(b"image1 image")
    (modules_dir / module1_name / "image2.jpg").write_bytes(image2_1_content)
    (modules_dir / module2_name / "image2.jpg").write_bytes(image2_2_content)
    (modules_dir / module3_name / "image2.jpg").write_bytes(image2_3_content)
    (modules_dir / module1_name / "image3.jpg").write_bytes(image3_1_content)
    (modules_dir / module2_name / "image3.jpg").write_bytes(image3_1_content)
    (modules_dir / module3_name / "image3.jpg").write_bytes(image3_2_content)
    (modules_dir / module3_name / "unused.jpg").write_bytes(b"unused")

    mocker.patch(
        "sys.argv",
        ["", modules_dir, media_dir]
    )
    consolidate_media.main()

    # All image files should be gone from modules_dir
    for mf in modules_dir.glob("**/*"):
        if mf.is_file():
            assert mf.name == "index.cnxml"

    # Confirm expected files in media dir
    assert len(list(media_dir.glob("*"))) == 10
    assert (media_dir / f"{module1_name}.jpg").exists()
    assert (media_dir / f"{module2_name}.jpg").exists()
    assert (media_dir / f"{module3_name}.jpg").exists()
    assert (media_dir / "image1.jpg").exists()
    assert not (media_dir / "image2.jpg").exists()
    assert not (media_dir / "image3.jpg").exists()
    image2_1_suffix = _generate_sha_suffix(image2_1_content)
    image2_1_name = f"image2-{image2_1_suffix}.jpg"
    image2_2_suffix = _generate_sha_suffix(image2_2_content)
    image2_2_name = f"image2-{image2_2_suffix}.jpg"
    image2_3_suffix = _generate_sha_suffix(image2_3_content)
    image2_3_name = f"image2-{image2_3_suffix}.jpg"
    image3_1_suffix = _generate_sha_suffix(image3_1_content)
    image3_1_name = f"image3-{image3_1_suffix}.jpg"
    image3_2_suffix = _generate_sha_suffix(image3_2_content)
    image3_2_name = f"image3-{image3_2_suffix}.jpg"
    assert (media_dir / image2_1_name).exists()
    assert (media_dir / image2_2_name).exists()
    assert (media_dir / image2_3_name).exists()
    assert (media_dir / image3_1_name).exists()
    assert (media_dir / image3_2_name).exists()
    assert (media_dir / "unused.jpg").exists()

    # Confirm expected CNXML content after updates
    expected = f"""
        <document xmlns="http://cnx.rice.edu/cnxml">
            <content>
                <image src="../../media/image1.jpg"/>
                <image src="../../media/{image2_1_name}"/>
                <image src="../../media/{image3_1_name}"/>
                <image src="../../media/{module1_name}.jpg"/>
            </content>
        </document>
    """
    _compare_xml_strings(
        (modules_dir / module1_name / "index.cnxml").read_text(),
        expected
    )

    expected = f"""
        <document xmlns="http://cnx.rice.edu/cnxml">
            <content>
                <image src="../../media/image1.jpg"/>
                <image src="../../media/{image2_2_name}"/>
                <image src="../../media/{image3_1_name}"/>
                <image src="../../media/{module2_name}.jpg"/>
            </content>
        </document>
    """
    _compare_xml_strings(
        (modules_dir / module2_name / "index.cnxml").read_text(),
        expected
    )

    expected = f"""
        <document xmlns="http://cnx.rice.edu/cnxml">
            <content>
                <image src="../../media/image1.jpg"/>
                <image src="../../media/{image2_3_name}"/>
                <image src="../../media/{image3_2_name}"/>
                <image src="../../media/{module3_name}.jpg"/>
            </content>
        </document>
    """
    _compare_xml_strings(
        (modules_dir / module3_name / "index.cnxml").read_text(),
        expected
    )


def test_update_metadata(tmp_path, mocker):
    """Test update-metadata script"""

    modules_dir = tmp_path / "modules"
    module_name = "m00001"
    module_dir = modules_dir / module_name
    module_dir.mkdir(parents=True)

    module_json = module_dir / "metadata.json"
    module_json_content = {
        "id": "00000000-0000-0000-0000-000000000001",
        "canonical": "00000000-0000-0000-0000-000000000000",
        "title": "Test module"
    }
    module_json.write_text(json.dumps(module_json_content))

    module_cnxml = module_dir / "index.cnxml"
    module_cnxml_content = """
        <document xmlns="http://cnx.rice.edu/cnxml">
            <title>Test module</title>
            <metadata xmlns:md="http://cnx.rice.edu/mdml" mdml-version="0.5">
                <!-- Some comment -->
                <md:repository>http://legacy.cnx.org/content</md:repository>
                <md:content-url>http://legacy.cnx.org/content/m00001</md:content-url>
                <md:content-id>m00001</md:content-id>
                <md:title>Test module</md:title>
                <md:version>4.2</md:version>
                <md:created>2014/02/20 16:26:27 -0600</md:created>
                <md:revised>2018/03/29 14:26:13 -0500</md:revised>
                <md:actors>
                    <md:organization userid="OpenStaxCollege">
                    <md:shortname>OpenStax</md:shortname>
                    <md:fullname>OpenStax</md:fullname>
                    <md:email>info@openstax.org</md:email>
                    </md:organization>
                    <md:person userid="OSCRiceUniversity">
                    <md:firstname>Rice</md:firstname>
                    <md:surname>University</md:surname>
                    <md:fullname>Rice University</md:fullname>
                    <md:email>info@openstaxcollege.org</md:email>
                    </md:person>
                    <md:person userid="testmod">
                    <md:firstname>OpenStax College</md:firstname>
                    <md:surname>Test</md:surname>
                    <md:fullname>OpenStax Test</md:fullname>
                    <md:email>info@openstax.org</md:email>
                    </md:person>
                </md:actors>
                <md:roles>
                    <md:role type="author">OpenStaxCollege</md:role>
                    <md:role type="maintainer">OpenStaxCollege</md:role>
                    <md:role type="licensor">OSCRiceUniversity</md:role>
                </md:roles>
                <md:license url="http://creativecommons.org/licenses/by/4.0/">
                    Creative Commons Attribution License 4.0
                </md:license>
                <md:keywordlist>
                    <md:keyword>keyword1</md:keyword>
                    <md:keyword>keword2</md:keyword>
                </md:keywordlist>
                <md:subjectlist>
                    <md:subject>Subject1</md:subject>
                </md:subjectlist>
                <md:language>en</md:language>
                <md:abstract/>
            </metadata>
        </document>
    """
    module_cnxml.write_text(module_cnxml_content)

    collections_dir = tmp_path / "collections"
    collections_dir.mkdir()
    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()
    collection_name = "alchemy"

    collection_json = metadata_dir / f"{collection_name}.metadata.json"
    collection_json_content = {
        "id": "6e9c4e99-1fe4-42e2-8268-8cb892f9602e",
        "slug": "alchemy-slug"
    }

    collection_json.write_text(json.dumps(collection_json_content))

    collection_xml = collections_dir / f"{collection_name}.xml"
    collection_xml_content = """
        <col:collection xmlns="http://cnx.rice.edu/collxml"
            xmlns:col="http://cnx.rice.edu/collxml">
            <metadata xmlns:md="http://cnx.rice.edu/mdml" mdml-version="0.5">
                <!-- Some comment -->
                <md:repository>https://legacy.cnx.org/content</md:repository>
                <md:content-url>https://legacy.cnx.org/content/col00001/1.11</md:content-url>
                <md:content-id>col00001</md:content-id>
                <md:title>Alchemy</md:title>
                <md:version>1.11</md:version>
                <md:created>2014/02/20 16:43:38.427 GMT-6</md:created>
                <md:revised>2020/12/09 15:30:14.937 US/Central</md:revised>
                <md:actors>
                    <md:organization userid="OpenStaxCollege">
                    <md:shortname>OpenStax</md:shortname>
                    <md:fullname>OpenStax</md:fullname>
                    <md:email>info@openstax.org</md:email>
                    </md:organization>
                    <md:person userid="OSCRiceUniversity">
                    <md:firstname>Rice</md:firstname>
                    <md:surname>University</md:surname>
                    <md:fullname>Rice University</md:fullname>
                    <md:email>info@openstax.org</md:email>
                    </md:person>
                    <md:person userid="cnxprecal">
                    <md:firstname>OpenStax College</md:firstname>
                    <md:surname>Precalculus</md:surname>
                    <md:fullname>OpenStax Precalculus</md:fullname>
                    <md:email>sanura@mac.com</md:email>
                    </md:person>
                </md:actors>
                <md:roles>
                    <md:role type="author">OpenStaxCollege</md:role>
                    <md:role type="maintainer">
                    OpenStaxCollege cnxprecal
                    </md:role>
                    <md:role type="licensor">OSCRiceUniversity</md:role>
                </md:roles>
                <md:license url="http://creativecommons.org/licenses/by/4.0/">
                    Creative Commons Attribution License 4.0
                </md:license>
                <md:subjectlist>
                    <md:subject>Magic</md:subject>
                </md:subjectlist>
                <md:abstract/>
                <md:language>en</md:language>
            </metadata>
        </col:collection>
    """
    collection_xml.write_text(collection_xml_content)

    mocker.patch(
        "sys.argv",
        ["", modules_dir, collections_dir, metadata_dir]
    )
    update_metadata.main()

    expected = """
        <document xmlns="http://cnx.rice.edu/cnxml">
            <title>Test module</title>
            <metadata xmlns:md="http://cnx.rice.edu/mdml" mdml-version="0.5">
                <md:content-id>m00001</md:content-id>
                <md:title>Test module</md:title>
                <md:abstract/>
            <md:uuid>00000000-0000-0000-0000-000000000001</md:uuid>
            </metadata>
        </document>
    """
    _compare_xml_strings(module_cnxml.read_text(), expected)

    expected = """
        <col:collection xmlns="http://cnx.rice.edu/collxml"
            xmlns:col="http://cnx.rice.edu/collxml">
            <metadata xmlns:md="http://cnx.rice.edu/mdml" mdml-version="0.5">
                <md:content-id>col00001</md:content-id>
                <md:title>Alchemy</md:title>
                <md:license url="http://creativecommons.org/licenses/by/4.0/">
                    Creative Commons Attribution License 4.0
                </md:license>
                <md:uuid>6e9c4e99-1fe4-42e2-8268-8cb892f9602e</md:uuid>
                <md:slug>alchemy-slug</md:slug>
            </metadata>
        </col:collection>
    """
    _compare_xml_strings(collection_xml.read_text(), expected)


def test_remove_pi(tmp_path, mocker):
    """Test remove_pi script"""
    modules_dir = tmp_path / "modules"
    module_name = "m00001"
    module_dir = modules_dir / module_name
    module_dir.mkdir(parents=True)

    module_cnxml = module_dir / "index.cnxml"
    module_cnxml_content = """
        <document xmlns="http://cnx.rice.edu/cnxml">
            <title>Test module</title>
            <content>
            <?cnx.eoc class="key-equations" title="Key Equations"?>
            <?cnx.answers class="section-exercises"?>
            Some Content
            </content>
        </document>
    """
    module_cnxml.write_text(module_cnxml_content)

    collections_dir = tmp_path / "collections"
    collections_dir.mkdir()
    collection_name = "alchemy"

    collection_xml = collections_dir / f"{collection_name}.collection.xml"
    collection_xml_content = """
        <col:collection xmlns="http://cnx.rice.edu/collxml"
            xmlns:col="http://cnx.rice.edu/collxml">
            <?cnx.idk class="not-sure-if-this-happens" title="Please remove"?>
        </col:collection>
    """
    collection_xml.write_text(collection_xml_content)

    mocker.patch(
        "sys.argv",
        ["", modules_dir, collections_dir]
    )
    remove_pi.main()

    expected = """
        <document xmlns="http://cnx.rice.edu/cnxml">
            <title>Test module</title>
            <content>
            
            Some Content
            </content>
        </document>
    """
    _compare_xml_strings(module_cnxml.read_text(), expected)

    expected = """
        <col:collection xmlns="http://cnx.rice.edu/collxml"
            xmlns:col="http://cnx.rice.edu/collxml">
            </col:collection>
    """
    _compare_xml_strings(collection_xml.read_text(), expected)
