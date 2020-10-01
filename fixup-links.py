#!/usr/bin/env python3

import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import re

TOC_DIVIDER_MAP = {
    'Global Objects': 'Object',
    'Prototypes': 'Class',
}

FILES_TO_FIXUP = [
    Path("architecture.html"),
    Path("auth-tokens.html"),
    Path("changelog.html"),
    Path("commit.html"),
    Path("community-servers.html"),
    Path("control.html"),
    Path("cpu-limit.html"),
    Path("creeps.html"),
    Path("debugging.html"),
    Path("defense.html"),
    Path("game-loop.html"),
    Path("global-objects.html"),
    Path("index.html"),
    Path("introduction.html"),
    Path("invaders.html"),
    Path("market.html"),
    Path("modules.html"),
    Path("power.html"),
    Path("privacy-policy.html"),
    Path("ptr.html"),
    Path("resources.html"),
    Path("respawn.html"),
    Path("scripting-basics.html"),
    Path("simultaneous-actions.html"),
    Path("start-areas.html"),
    Path("subscription.html"),
    Path("third-party.html"),
    Path("tos.html"),
    Path("api/constants.html"),
    Path("api/ConstructionSite.html"),
    Path("api/Creep.html"),
    Path("api/Deposit.html"),
    Path("api/Flag.html"),
    Path("api/Game.html"),
    Path("api/index.html"),
    Path("api/InterShardMemory.html"),
    Path("api/Map.html"),
    Path("api/MapVisual.html"),
    Path("api/Market.html"),
    Path("api/Memory.html"),
    Path("api/Mineral.html"),
    Path("api/Nuke.html"),
    Path("api/OwnedStructure.html"),
    Path("api/PathFinder.CostMatrix.html"),
    Path("api/PathFinder.html"),
    Path("api/PowerCreep.html"),
    Path("api/RawMemory.html"),
    Path("api/Resource.html"),
    Path("api/Room.html"),
    Path("api/Room.Terrain.html"),
    Path("api/RoomObject.html"),
    Path("api/RoomPosition.html"),
    Path("api/RoomVisual.html"),
    Path("api/Ruin.html"),
    Path("api/Source.html"),
    Path("api/Store.html"),
    Path("api/Structure.html"),
    Path("api/StructureContainer.html"),
    Path("api/StructureController.html"),
    Path("api/StructureExtension.html"),
    Path("api/StructureExtractor.html"),
    Path("api/StructureFactory.html"),
    Path("api/StructureInvaderCore.html"),
    Path("api/StructureKeeperLair.html"),
    Path("api/StructureLab.html"),
    Path("api/StructureLink.html"),
    Path("api/StructureNuker.html"),
    Path("api/StructureObserver.html"),
    Path("api/StructurePortal.html"),
    Path("api/StructurePowerBank.html"),
    Path("api/StructurePowerSpawn.html"),
    Path("api/StructureRampart.html"),
    Path("api/StructureRoad.html"),
    Path("api/StructureSpawn.html"),
    Path("api/StructureSpawnSpawning.html"),
    Path("api/StructureStorage.html"),
    Path("api/StructureTerminal.html"),
    Path("api/StructureTower.html"),
    Path("api/StructureWall.html"),
    Path("api/Tombstone.html"),
]

def cleanFile(filename):
    # get file contents
    print('\n')
    print(filename)
    f = open(filename, "rb")
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc, 'html.parser')

    # search and modify  all links (anchor tags) that start with "/" and end with "/" AND "/api" (damn edge case...)
    directory_links = []
    directory_links.extend(list(soup.find_all("a", href=re.compile("^/[^#]*/(#.*)?$"))))
    directory_links.extend(list(soup.find_all("a", href=re.compile("^/api(#.*)?$"))))
    for anchor in directory_links:
        before = anchor['href']
        hrefParts = anchor['href'].split('#')
        if hrefParts[0][-1] != '/':
            hrefParts[0] += '/'
        anchor['href'] = hrefParts[0] + 'index.html'+ ('#'+hrefParts[1] if len(hrefParts) > 1 else '')
        print(f'{before} => {anchor["href"]}')
    
    # write changes back to the file
    f = open(filename, "wb")
    f.write(soup.prettify(soup.original_encoding))
    f.close()

def apiTocGetAnchors(soup):
    dividers = soup.select("#toc > ul > li.tocify-item.divider")
    for divider in dividers:
        if divider.text.strip() == 'Global Objects':
            global_objects_li = divider
        elif divider.text.strip() == 'Prototypes':
            prototypes_li = divider
        else:
            print("Unknown divider in ToC!")
    
    toc_headings = soup.select("#toc > ul")

    current_topic = None

    toc = {}

    for heading in toc_headings:
        divider = heading.select_one("#toc > ul > li.tocify-item.divider")
        first_level_entry = heading.select_one("#toc > ul > li > a")
        second_level_header = heading.select_one("#toc > ul > ul")
        if divider is not None:
            # new topic
            current_topic = divider.text.strip()
            print("\n"+current_topic)
            toc[current_topic] = []
            continue
        if second_level_header == None:
            toc[current_topic].append(
                {
                    'first_level': first_level_entry['href'],
                    'second_level': []
                }
            )
        else:
            toc[current_topic].append(
                {
                    'first_level': first_level_entry['href'],
                    'second_level': [ item['href'] for item in second_level_header.select("#toc > ul > ul > li > a") ]
                }
            )
    
    return toc

def apiAddTocLinks(toc, soup):
    for entry_type_name in toc:
        entries_for_type = toc[entry_type_name]
        for entry in entries_for_type:
            # first add an href to the first level entry
            heading_tag = soup.select_one(entry['first_level'])
            tag = soup.new_tag("a")
            tag['name'] = f"//apple_ref/cpp/{TOC_DIVIDER_MAP[entry_type_name]}/{heading_tag.text.strip()}"
            tag['class'] = "dashAnchor"
            heading_tag.insert_after(tag)

def removeToc(soup):
    wrapper = soup.find("div", class_="page-wrapper")
    wrapper['style'] = '''margin-left: 0 !important;'''
    try:
        soup.find("div", class_="tocify-wrapper").decompose()
    except AttributeError:
        print('ToC was already removed. Maybe you ran the cleanup script twice?')
    
def fixToc(filename):
    f = open(filename, "rb")
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc, 'html.parser')
    toc = apiTocGetAnchors(soup)
    apiAddTocLinks(toc, soup)
    removeToc(soup)
    # write changes back to the file
    f = open(filename, "wb")
    f.write(soup.prettify(soup.original_encoding))
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fixup links inside screeps documentation to work in a file archive (e.g. Dash App).')
    parser.add_argument('--path')
    args = parser.parse_args()
    if args.path is None:
        base_path = Path(".")
    else:
        base_path = Path(args.path)
    for filename in FILES_TO_FIXUP:
        cleanFile(base_path / filename)
    fixToc(base_path / Path('api/index.html'))