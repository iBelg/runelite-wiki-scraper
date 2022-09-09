import traceback
import re
import mwparserfromhell as mw
import api
import util
from typing import *
import copy


def run():
    npcs = {}

    npc_pages = api.query_category("Monsters")
    for name, page in npc_pages.items():
        if name.startswith("Category:"):
            continue

        try:
            code = mw.parse(page, skip_style_tags=True)

            for (vid, version) in util.each_version("Infobox Monster", code):
                if "removal" in version and not str(version["removal"]).strip().lower() in ["", "no"]:
                    continue

                doc = util.get_doc_for_id_string(
                    name + str(vid), version, npcs)
                if doc == None:
                    continue
                util.copy("name", doc, version)
                if not "name" in doc:
                    doc["name"] = name

                doc["scaledhp"] = "scaledhp" in version and not str(
                    version["scaledhp"]).strip().lower() in ["", "no"]

                immunities = {}

                immunities["poison"] = "immunepoison" in version and "yes" in str(
                    version["immunepoison"]).strip().lower()

                immunities["venom"] = "immunevenom" in version and "yes" in str(
                    version["immunevenom"]).strip().lower()

                immunities["cannon"] = "immunecannon" in version and "yes" in str(
                    version["immunecannon"]).strip().lower()

                immunities["thrall"] = "immunethrall" in version and "yes" in str(
                    version["immunethrall"]).strip().lower()

                doc["immunities"] = immunities

                for key in ["hitpoints", "combat", "size", "att", "str", "def", "mage", "range", "attbns", "strbns", "amagic", "mbns", "arange", "rngbns", "dstab", "dslash", "dcrush", "dmagic", "drange"]:
                    try:
                        util.copy(key, doc, version, lambda x: int(x))
                    except ValueError:
                        print("NPC {} has an non integer {}".format(name, key))

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            print("NPC {} failed:".format(name))
            traceback.print_exc()

    util.write_json("npcs.json", "npcs.min.json", npcs)
