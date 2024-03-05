import argparse
import json
import logging
import logging.config
import os
import requests
import sys
from tabulate import tabulate

HELP_DESC="""
ChromeDriver downloader
This program use the following url to query/download chromedriver:
    https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json

(use --url to change it)

See the full list of endpoints and reference in https://github.com/GoogleChromeLabs/chrome-for-testing?tab=readme-ov-file#json-api-endpoints
    
"""
HELP_EXAMPLE="""
- List versions
chromedriver_downloader -l 
- List versions for platform win64 and version 124.*
chromedriver_downloader -l -fp win64 -fv 124
- Download drivers for platform win64 and version 124.0.*
chromedriver_downloader -d -fp win64 -fv 124.0
"""
logger = logging.getLogger("ktxo.app")

DEFAULT_URL="https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

# ---------------------------------------------------------------------------
def do_get(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            logger.error(f"Error accessing to url {url}. res={res.status_code}")
            return None
        return res.json()
    except Exception as e:
        logger.error(f"Error accessing to url {url}. ({str(e)})")
        return None


def get_list(url:str=DEFAULT_URL, platform:str=None, version:str=None, save=False):
    if (res := do_get(url)):
        if save:
            with open("chromedriver_downloader.json", "w") as fd:
                json.dump(res, fd, indent=True)
    records = []
    if not res:
        return records
    try:
        for record in res.get("versions", []):
            for r in record.get("downloads", {"chromedriver":[]}).get("chromedriver", []):
                if platform and platform != r.get("platform"):
                    continue
                if version and not record.get("version").startswith(version):
                    continue

                records.append(dict(
                    version=record.get("version"),
                    revision=record.get("revision"),
                    platform=r.get("platform"),
                    url=r.get("url"))
                )
    except Exception as e:
        logger.error(f"Got some error downloading. ({str(e)})")
    return records

def download_version(version:str, platform:str = None, url=DEFAULT_URL):
    records = get_list(url, platform, version)
    if len(records) == 0:
        logger.error(f"No data for combination platform={platform} and version={version}")
        return
    for record in records:
        try:
            toks_ = os.path.splitext(record.get('url').split("/")[-1])
            filename = f"{toks_[0]}_{record.get('version')}{toks_[1]}"
            logger.info(f"Downloading {record.get('url')} > {filename}")
            r = requests.get(record.get('url'), allow_redirects=True)
            open(filename, 'wb').write(r.content)
        except Exception as e:
            logger.error(f"Got some error downloading. ({str(e)})")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__),
                                     description=HELP_DESC,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-l", "--list", help="List available versions", action='store_true')
    parser.add_argument("-s", "--save", help="Save lsiting output", action='store_true')
    parser.add_argument("-fp", "--filter_platform", help="Filter platforms.\n"
                                                         "e.g.: win64")
    parser.add_argument("-fv", "--filter_version", help="Filter versions\n"
                                                        "e.g.: 124.0.6334")
    parser.add_argument("-u", "--url", help="Url to query/download.\n"
                                            f"Default {DEFAULT_URL}",
                        default=DEFAULT_URL)
    parser.add_argument("-d", "--download", help="Download version. Specify version using -fv", action='store_true')
    parser.add_argument("-L", "--log_level", help="Log level. Valid options: I(info), D(debug), W(warning), E(error)",
                        choices=['I', 'D', 'W', 'E'],
                        default='I')
    args = parser.parse_args()
    if args.download and not args.filter_version:
        parser.error(f"Option --download|-d require a version: --filter_version|-fv")

    LOG_LEVELS = {'I': logging.INFO, 'D': logging.DEBUG, 'W': logging.WARNING, 'E': logging.ERROR}
    logging.basicConfig(level=LOG_LEVELS.get(args.log_level, logging.INFO),
                        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger.info(args)
    #
    if args.list:
        print(tabulate(get_list(args.url, args.filter_platform, args.filter_version, args.save)))
    elif args.download:
        download_version(args.filter_version, args.filter_platform, url=args.url)
    else:
        logger.info(f"Missing options :-(")




