"""Create a clean portable folder/ZIP and its byte manifest; no network."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

IGNORED = {'__pycache__', '.git', '.taskflow', '.pytest_cache'}
DIRS = {'taskflow', 'skills', 'upstream', 'config', 'docs', 'tests', 'scripts'}
FILES = {'kit.py', 'README.ko.md', 'LICENSE', '.gitattributes', 'bundle-lock.json'}


def files(root):
    return sorted(p for p in root.rglob('*') if p.is_file()
                  and not IGNORED.intersection(p.relative_to(root).parts)
                  and (p.relative_to(root).parts[0] in DIRS
                       or p.relative_to(root).as_posix() in FILES))


def manifest(root):
    content = {'version': '1.0.0', 'algorithm': 'sha256',
               'files': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in files(root) if p.name != 'bundle-lock.json'}}
    (root / 'bundle-lock.json').write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return content


def package(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError('Delivery directory must be outside the source package')
    destination.mkdir(parents=True, exist_ok=True)
    folder = destination / 'taskflow-kit'
    if folder.exists():
        raise ValueError('Delivery folder already exists; inspect rather than overwrite it')
    content = manifest(source)
    folder.mkdir()
    for p in files(source):
        target = folder / p.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    archive = destination / 'taskflow-kit-1.0.0.zip'
    if archive.exists():
        raise ValueError('Delivery archive already exists')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in files(folder):
            z.write(p, 'taskflow-kit/' + p.relative_to(folder).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'taskflow-kit-1.0.0.sha256.txt').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    print(json.dumps({'folder': str(folder), 'archive': str(archive),
                      'sha256': digest, 'verified_file_count': len(content['files'])}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    package(args.source, args.output)
