import json
import sys
import re

# Map of legacy id to uuid
# Legacy ids provided by HOLY GRAIL spreadsheet from CMs
BOOK_UUIDS = {
    "col11963": "9a1df55a-b167-4736-b5ad-15d996704270",
    "col11965": "1d39a348-071f-4537-85b6-c98912458c3c",
    "col11966": "a31cd793-2162-4e9e-acb5-6e6bbd76a5fa",
    "col31502": "06aba565-9432-40f6-97ee-b8a361f118a8",
    "col30149": "464a3fba-68c1-426a-99f9-597e739dc911",
    "col26739": "9d8df601-4f12-4ac1-8224-b450bf739e5f",
    "col26488": "d9b85ee6-c57f-4861-8208-5ddf261e9c5f",
    "col26069": "7fccc9cf-9b71-44f6-800b-f9457fd64335",
    "col12122": "bc498e1f-efe9-43a0-8dea-d3569ad09a82",
    "col12170": "5c09762c-b540-47d3-9541-dda1f44f16e5",
    "col12190": "27f59064-990e-48f1-b604-5188b9086c29",
    "col23750": "636cbfd9-4e37-4575-83ab-9dec9029ca4e",
    "col23729": "9117cf8c-a8a3-4875-8361-9cb0f1fc9362",
    "col11562": "30189442-6998-4686-ac05-ed152b91b9de",
    "col11776": "b56bb9e9-5eb8-48ef-9939-88b1b12ce22f",
    "col30309": "394a1101-fd8f-4875-84fa-55f15b06ba66",
    "col11964": "8b89d172-2927-466f-8661-01abc7ccdba4",
    "col11994": "74fd2873-157d-4392-bf01-2fccab830f2c",
    "col12067": "af275420-6050-4707-995c-57b9cc13c358",
    "col12074": "7a0f9770-1c44-4acd-9920-1cd9a99f2a1e",
    "col12031": "d50f6e32-0fda-46ef-a362-9bd36ca7c97d",
    "col11667": "fd53eae1-fa23-47c7-bb1b-972349835c3c",
    "col12081": "cce64fde-f448-43b8-ae88-27705cceb0da",
    "col11758": "13ac107a-f15f-49d2-97e8-60ab2e3b519c",
    "col12078": "6c322e32-9fb0-4c4d-a1d7-20c95c5c7af2",
    "col11487": "b3c1e1d2-839c-42b0-a314-e119a8aafbdd",
    "col24361": "8d50a0af-948b-4204-a71d-4826cba765b8",
    "col11629": "4abf04bf-93a0-45c3-9cbc-2cefd46e68cc",
    "col11756": "caa57dab-41c7-455e-bd6f-f443cda5519c",
    "col12116": "0889907c-f0ef-496a-bcb8-2a5bb121717f",
    "col12119": "02776133-d49d-49cb-bfaa-67c7f61b25a1",
    "col11844": "8d04a686-d5e8-4798-a27d-c608e4d0e187",
    "col28330": "c3acb2ab-7d5c-45ad-b3cd-e59673fedd4e",
    "col29124": "2d941ab9-ac5b-4eb8-b21c-965d36a4f296",
    "col25479": "920d1c8a-606c-4888-bfd4-d1ee27ce1795",
    "col12087": "e42bd376-624b-4c0f-972f-e0c57998e765",
    "col25722": "914ac66e-e1ec-486d-8a9c-97b0f7a99774",
    "col11740": "a7ba2fb8-8925-4987-b182-5f4429d48daa",
    "col11762": "02040312-72c8-441e-a685-20e9333f3e1d",
    "col11406": "031da8d3-b525-429c-80cf-6c8ed997733a",
    "col25734": "4e09771f-a8aa-40ce-9063-aa58cc24e77f",
    "col11759": "9b08c294-057f-4201-9f48-5d6ad992740d",
    "col11496": "14fb4ad7-39a1-4eee-ab6e-3ef2482e3e22",
    "col31596": "36004586-651c-4ded-af87-203aca22d946",
    "col31130": "55931856-c627-418b-a56f-1dd0007683a8",
    "col30990": "e8668a14-9a7d-4d74-b58c-3681f8351224",
    "col29104": "d380510e-6145-4625-b19a-4fa68204b6b1",
    "col30939": "f0fa90be-fca8-43c9-9aad-715c0a2cee2b",
    "col31234": "4664c267-cd62-4a99-8b28-1cb9b3aee347",
    "col25448": "9ab4ba6d-1e48-486d-a2de-38ae1617ca84",
    "col11992": "2e737be8-ea65-48c3-aa0a-9f35b4c6a966"
}

# UUIDS from DB, HOLY GRAIL only contained legacy id
Additional_UUIDS = {
    "col11407": "afe4332a-c97f-4fc4-be27-4e4d384a32d8",
    "col11448": "185cbf87-c72e-48f5-b51e-f14f21b5eabd",
    "col11613": "69619d2b-68f0-44b0-b074-a9b2bf90b2c6",
    "col11626": "4061c832-098e-4b3c-a1d9-7eb593a2cb31",
    "col11627": "ea2f225e-6063-41ca-bcd8-36482e15ef65",
    "col11760": "85abf193-2bd2-4908-8563-90b8a7ac8df6",
    "col11858": "ca344e2d-6731-43cd-b851-a7b3aa0b37aa",
    "col11864": "33076054-ec1d-4417-8824-ce354efe42d0",
    "col11995": "5bcc0e59-7345-421d-8507-a1e4608685e8",
    "col12006": "405335a3-7cff-4df2-a9ad-29062a4af261",
    "col12012": "4539ae23-1ccc-421e-9b25-843acbb6c4b0",
    "col32026": "507feb1e-cfff-4b54-bc07-d52636cecfe3"
}

BOOK_UUIDS.update(Additional_UUIDS)


def msg(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    print(msg, file=sys.stderr)
    try:
        with open('/var/log/check', 'a') as f:
            f.write("msg:" + msg + "\n")
    except PermissionError:
        pass


def parse_legacy_ids(sync_file):
    pattern = "col\\d{5}"
    legacy_ids = re.findall(pattern, sync_file)

    return legacy_ids


def determine_archive_server(server):
    if not server:
        msg("Error: No archive server was given.")
        sys.exit(1)

    domain = 'cnx.org'
    archive_subdomain = 'archive'

    if server == 'prod' or server == domain:
        return f"{archive_subdomain}.{domain}"

    delimiter = '-'
    if domain not in server:
        archive_subdomain = archive_subdomain + delimiter + server
        return f"{archive_subdomain}.{domain}"
    else:
        return archive_subdomain + delimiter + server
