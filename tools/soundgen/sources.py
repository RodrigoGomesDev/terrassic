"""
Recorded sound sources: public domain or CC0 only, downloadable without login.

fetch.py downloads them into art/sounds/src/<id>/ (zips are unpacked there) and writes docs/LICENSES-SOUNDS.md.
recipes.py refers to them as ("src", "<id>/<glob>", {...}); a source that is missing falls back to the
procedural voice, so the mod always builds.

Accepted licences:
  - "PD-USGov": work of the US federal government (National Park Service, US Fish and Wildlife Service).
    Public domain; NPS asks for a courtesy credit ("National Park Service"), which LICENSES-SOUNDS.md gives.
  - "CC0": Creative Commons Zero.
NPS recordings co-credited to the MSU Acoustic Atlas are left out (public domain not confirmed).
Wikimedia files are re-checked by fetch.py against the Commons API and skipped if the licence is not PD/CC0.
"""

NPS = "https://www.nps.gov/nps-audiovideo/legacy/mp3/imr/avElement/"
YELL = "https://home.nps.gov/yell/learn/photosmultimedia/"
OGA = "https://opengameart.org/sites/default/files/"

# id -> source. kind: "file" (single audio file), "zip" (all audio files inside), "commons" (Wikimedia Commons file name)
SOURCES = {
    # ---- big theropods (boom_large)
    "nps_bison_bellow_a": dict(kind="file", url=NPS + "yell-YELLMM8K2005914Bison.mp3", licence="PD-USGov",
                               author="NPS / Shan Burson", page=YELL + "sounds-bison.htm", what="bison bellow"),
    "nps_bison_bellow_b": dict(kind="file", url=NPS + "yell-YELLMM8K2005918Bison.mp3", licence="PD-USGov",
                               author="NPS / Shan Burson", page=YELL + "sounds-bison.htm", what="bison bellow, longer"),
    "nps_grizzly_roar": dict(kind="file", url=NPS + "yell-YELLgrizzlyC20160626SM303143.mp3", licence="PD-USGov",
                             author="NPS", page=YELL + "grizzlysounds.htm", what="two grizzlies roaring"),
    "nps_grizzly_warn": dict(kind="file", url=NPS + "yell-YELLGrizzlyBearVocalizations20160520Android1.mp3",
                             licence="PD-USGov", author="NPS", page=YELL + "grizzlysounds.htm",
                             what="grizzly huffing, jaw popping, growls"),
    "wm_alligator_bellow": dict(kind="commons", url="Alligatorbellow1.ogg", licence="PD-USGov",
                                author="US Fish and Wildlife Service", what="American alligator bellow"),
    "wm_alligator_bellow_2": dict(kind="commons", url="27alligator2bellow.ogg", licence="PD-USGov",
                                  author="US Fish and Wildlife Service", what="American alligator bellow"),
    "wm_alligator_hiss": dict(kind="commons", url="Alligatorhiss.ogg", licence="PD-USGov",
                              author="US Fish and Wildlife Service", what="American alligator hiss"),
    # ---- hadrosaurs (horn_hadrosaur)
    "nps_elk_bugle": dict(kind="file", url="https://www.nps.gov/nps-audiovideo/legacy/mp3/nri/avElement/nri-ElkBuglingGRSA.mp3",
                          licence="PD-USGov", author="NPS", page="https://www.nps.gov/subjects/sound/sounds-elk.htm",
                          what="bull elk bugling, Great Sand Dunes"),
    "wm_swans": dict(kind="commons", url="Tundra swans.ogg", licence="PD-USGov",
                     author="US Fish and Wildlife Service", what="tundra swans calling"),
    "wm_geese": dict(kind="commons", url="Geese Honking (loud).ogg", licence="PD-USGov",
                     author="US Fish and Wildlife Service", what="geese honking"),
    # ---- pterosaurs (squawk_pterosaur)
    "nps_crane": dict(kind="file", url=NPS + "yell-YELLFLBCSACR20075171.mp3", licence="PD-USGov",
                      author="NPS / Shan Burson", page=YELL + "sounds-sandhillcrane.htm", what="sandhill cranes calling"),
    "nps_raven": dict(kind="file", url=NPS + "yell-RavenBlackSandBasin.mp3", licence="PD-USGov",
                      author="NPS / David Restivo", page=YELL + "sounds-raven.htm", what="common raven calling"),
    "wm_heron": dict(kind="commons", url="Littleblueheronfishes.ogg", licence="PD-USGov",
                     author="US Fish and Wildlife Service", what="little blue heron"),
    "wm_pelican": dict(kind="commons", url="Baby pelican.ogg", licence="PD-USGov",
                       author="US Fish and Wildlife Service", what="baby pelican begging"),
    "oga_wings": dict(kind="zip", url=OGA + "wings_flap_large.zip", licence="CC0", author="AntumDeluge",
                      page="https://opengameart.org/content/large-wings-flap", what="large wings flapping"),
    # ---- general creature library (later sets: raptors, small herbivores, mammals of the Ice Age)
    "oga_creature_1": dict(kind="zip", url=OGA + "80-CC0-creature-SFX_0.zip", licence="CC0", author="rubberduck",
                           page="https://opengameart.org/content/80-cc0-creature-sfx", what="80 creature sounds"),
    "oga_creature_2": dict(kind="zip", url=OGA + "80-CC0-creature-sfx-2.zip", licence="CC0", author="rubberduck",
                           page="https://opengameart.org/content/80-cc0-creture-sfx-2", what="80 creature sounds"),
    "oga_bear": dict(kind="zip", url=OGA + "bear.zip", licence="CC0", author="AntumDeluge",
                     page="https://opengameart.org/content/bear-growls", what="bear growls"),
}

AUDIO_EXT = (".wav", ".ogg", ".mp3", ".flac")


def commons_page(name):
    return "https://commons.wikimedia.org/wiki/File:" + name.replace(" ", "_")


def commons_download(name):
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + name.replace(" ", "_")
