"""Create a bounded hash lock from an already downloaded, trusted wheelhouse.

No downloads/installations; hashes establish reproducibility, not publisher trust.
"""
from email.parser import BytesParser
import hashlib
from pathlib import Path
import re
import stat
import sys
import sysconfig
import zipfile


def wheel_lock(root):
    root=Path(root)
    if root.is_symlink() or not root.is_dir(): raise ValueError('wheel directory required')
    files=list(root.iterdir())
    if not 1<=len(files)<=100: raise ValueError('bounded wheel count required')
    rows=[];names=set();total=0
    for path in sorted(files):
        info=path.lstat();total+=info.st_size
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or path.suffix!='.whl' or info.st_size>64*1024**2 or total>256*1024**2:
            raise ValueError('bounded single-link wheels only')
        with zipfile.ZipFile(path) as wheel:
            entries=[e for e in wheel.infolist() if e.filename.endswith('.dist-info/METADATA')]
            if len(entries)!=1 or entries[0].file_size>1024**2: raise ValueError('invalid wheel metadata')
            meta=BytesParser().parsebytes(wheel.read(entries[0]))
        name=meta['Name'];version=meta['Version']
        if not name or not version or not re.fullmatch(r'[A-Za-z0-9_.-]+',name) or not re.fullmatch(r'[A-Za-z0-9_.+!-]+',version):
            raise ValueError('invalid wheel identity')
        canonical=re.sub(r'[-_.]+','-',name).lower()
        if canonical in names: raise ValueError('one wheel per distribution required')
        names.add(canonical)
        rows.append({'name':canonical,'version':version,'filename':path.name,'bytes':info.st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    rows.sort(key=lambda r:r['name'])
    lock=''.join(f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}\n" for r in rows)
    return lock,{'format':'KGM_WHEELHOUSE_V1','python':sys.version.split()[0],
                 'platform':sysconfig.get_platform(),'total_bytes':total,'wheels':rows}
