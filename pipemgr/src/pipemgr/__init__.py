from pathlib import Path

from .concourse.models import concourse_session, LDAPTokenProvider, DiskTokenCache

MODULE_ROOT = Path(__file__).resolve().parent
WORKING_ROOT = Path.home()/".pipemgr"
OUTPUT_ROOT = WORKING_ROOT
TEMPLATE_ROOT = MODULE_ROOT/"templates"

if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir(parents=True)


def concourse_session_factory():
    return concourse_session(
        "https://concourse-v7.openstax.org",
        LDAPTokenProvider(DiskTokenCache(OUTPUT_ROOT/"token.txt"))
    )
