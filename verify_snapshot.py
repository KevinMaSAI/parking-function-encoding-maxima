# SPDX-License-Identifier: MIT
"""Check the exact byte sizes and SHA-256 values of a released snapshot."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent

if __name__=='__main__':
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    for row in manifest['files']:
        relative=Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        p=ROOT/relative
        assert p.is_file(),row['path']
        data=p.read_bytes()
        assert len(data)==row['bytes'],row['path']
        assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
    print(json.dumps({'passed':True,'files_checked':len(manifest['files'])}))
