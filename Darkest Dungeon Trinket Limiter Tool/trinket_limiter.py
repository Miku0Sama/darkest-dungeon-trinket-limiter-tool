import sys
import json
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET

if getattr(sys, "frozen", False):
    # Running as exe
    mod_dir = Path(sys.executable).resolve().parent
else:
    # Running as normal script
    mod_dir = Path(__file__).resolve().parent

workshop_dir = mod_dir.parent
backups_dir = mod_dir / 'backups'
CONFIG = mod_dir / 'config.json'
with CONFIG.open('r', encoding='UTF-8') as f:
	configs = json.load(f)
LIMIT = configs['limit']
EXCLUDE = configs['exclude']


def findTrinkets(mod):
	for dir in mod.iterdir():
		if dir.name == "trinkets":
			return dir
	return None

def getModName(projectXML, default):
	mod_name = ""
	if projectXML.exists():
		tree = ET.parse(projectXML)
		root = tree.getroot()
		title = root.find('.//Title')
		if title is not None:
			mod_name = title.text
			if mod_name == "" or None:
				mod_name = default
		else:
			mod_name = default
	return mod_name

def cloneTrinkets():
	modNum = 0
	totalTrinkets = 0
	totalSkipped = 0
	for mod in workshop_dir.iterdir():
		if mod == mod_dir:
			continue
		projectXML = mod / "project.xml"
		modID = mod.name
		modfiles = mod / "modfiles.txt"
		modName = getModName(projectXML, modID)
		trinketsDir = findTrinkets(mod)
		if trinketsDir == None:
			continue
		print(f'Trinkets folder found in {modID}')
		print(f'Mod Name: {modName}')
		print(f'Creating backup...')
		destDir = backups_dir / modID / "trinkets"
		destDir.mkdir(exist_ok=True, parents=True)
		shutil.copytree(trinketsDir, destDir, dirs_exist_ok=True)
		print('Backup successful')
		print(f'Adjusting Trinket Limits to {LIMIT}')
		adjustedTrinkets, skippedTrinkets = modifyLimits(trinketsDir, LIMIT)
		totalTrinkets += adjustedTrinkets
		totalSkipped += skippedTrinkets
		print('Deleting modfiles.txt\n')
		modfiles.unlink(missing_ok=True)
		modNum += 1
	return modNum, totalTrinkets, totalSkipped

def modifyLimits(trinketDir: Path, lim: int, exclude:list[str]=EXCLUDE):
	trinketCount = 0
	skipped = 0
	for file in trinketDir.iterdir():
		if file.name.endswith("entries.trinkets.json"):
			with file.open('r', encoding='UTF-8') as f:
				trinkets = json.load(f)

			for trinket in trinkets['entries']:
				if trinket['id'] in exclude:
					print(f'{trinket['id']} is in the Exclude list, skipping...')
					skipped += 1
					continue
				if trinket['limit'] == lim:
					print(f'{trinket['id']} limit already set to {lim}, skipping...')
					skipped += 1
					continue
				trinket['limit'] = lim
				trinketCount += 1

			with file.open('w', encoding='UTF-8') as f:
				json.dump(trinkets, f, indent=4)
	print(f'Modified the limits of {trinketCount} trinkets')
	return trinketCount, skipped

def main():
	mods, amt, skip = cloneTrinkets()
	return mods, amt, skip

if __name__ == "__main__":
	modCount, modifiedTrinketCount, skippedTrinketCount = main()
	print("Done!")
	print(f'Adjusted the limits of {modifiedTrinketCount} trinkets across {modCount} mods!')
	print(f'{skippedTrinketCount} trinkets were skipped due to being excluded or already at the desired limit')
	input("Press enter to continue...")