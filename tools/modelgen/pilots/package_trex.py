"""Validate and package the finished isolated pilot without rebuilding its art."""
import hashlib
import json
from pathlib import Path
import zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'art/pilotos/trex/v1'
ASSETS=ROOT/'common/src/main/resources/assets/terrassic'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    report=json.loads((OUT/'validacao.json').read_text())
    production={str(p.relative_to(ROOT)):sha(p) for p in sorted(ASSETS.rglob('*')) if p.is_file()}
    assert hashlib.sha256(json.dumps(production,sort_keys=True).encode()).hexdigest()==report['production_assets_sha256']
    geo=json.loads((OUT/'tyrannosaurus.geo.json').read_text())['minecraft:geometry'][0]
    bb=json.loads((OUT/'tyrannosaurus.bbmodel').read_text())
    assert sum(len(b.get('cubes',[])) for b in geo['bones'])==report['cubes']==len(bb['elements'])
    dims=geo['description']['texture_width'],geo['description']['texture_height']
    for sex in ('male','female'):
        with Image.open(OUT/f'tyrannosaurus_{sex}.png') as im:
            assert im.size==dims;im.verify()
    for name in ('trex_death.gif','trex_wake.gif','trex_antes_depois.gif','trex_lie_down.gif'):
        with Image.open(OUT/name) as im:assert im.n_frames>20
    with Image.open(OUT/'trex_diorama.png') as im:assert im.size==(1536,1536);im.verify()
    # Final hashes after Cycles has finished, excluding its recoverable backup.
    files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name not in ('validacao.json','manifesto.json','trex_piloto_v1.zip') and p.suffix!='.blend1')
    report['output_hashes']={p.name:sha(p) for p in files}
    (OUT/'validacao.json').write_text(json.dumps(report,indent=2)+'\n')
    files.append(OUT/'validacao.json')
    manifest={p.name:sha(p) for p in files}
    (OUT/'manifesto.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files.append(OUT/'manifesto.json')
    package=OUT/'trex_piloto_v1.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,'trex_piloto_v1/'+p.name)
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        for name,h in manifest.items():assert hashlib.sha256(z.read('trex_piloto_v1/'+name)).hexdigest()==h
    print('PASS: production intact, 147 cubes, textures, animated GIFs, 1536x1536 hero, ZIP hashes')


if __name__=='__main__':main()
