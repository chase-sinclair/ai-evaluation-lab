"""Optional bounded acquisition. Only the three exact small validation members are readable."""

import argparse
import gzip
import hashlib
import io
import json
import re
import struct
import tempfile
import urllib.request
import zipfile
from pathlib import Path

CACHE = Path("datasets/cache/wdc-products-validation")
BASE = "https://data.dws.informatik.uni-mannheim.de/largescaleproductcorpus/data/wdc-products/"


def member(tier):
    if tier not in (20, 50, 80):
        raise ValueError("Unknown corner-case mixture")
    return f"wdcproducts{tier}cc{100 - tier}rnd000un_valid_small.json.gz"


def fetch(tier, directory):
    name = member(tier)
    url = BASE + f"{tier}pair.zip"

    def part(span, limit):
        req = urllib.request.Request(url, headers={"Range": "bytes=" + span})
        with urllib.request.urlopen(req, timeout=30) as response:
            match = re.fullmatch(
                r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", "")
            )
            if response.status != 206 or not match:
                raise ValueError("Server did not honor bounded range")
            start, end, size = map(int, match.groups())
            expected = (
                (size - limit, size - 1)
                if span.startswith("-")
                else tuple(map(int, span.split("-")))
            )
            if (start, end) != expected or end - start + 1 > limit:
                raise ValueError("Unexpected response range")
            data = response.read(limit + 1)
            if len(data) != end - start + 1:
                raise ValueError("Unexpected response size")
            return data, size

    tail, size = part("-65536", 65536)
    if size > 32_000_000:
        raise ValueError("Unexpected archive size")
    with tempfile.TemporaryFile() as sparse:
        sparse.seek(size - len(tail))
        sparse.write(tail)
        with zipfile.ZipFile(sparse) as archive:
            info = archive.getinfo(name)
    if info.compress_type != zipfile.ZIP_STORED or info.file_size > 1_500_000:
        raise ValueError("Unexpected member format/size")
    offset = info.header_offset
    header, _ = part(f"{offset}-{offset + 29}", 30)
    if header[:4] != b"PK\x03\x04":
        raise ValueError("Invalid local header")
    ns, extra = struct.unpack("<HH", header[26:])
    data_start = offset + 30 + ns + extra
    data, _ = part(f"{data_start}-{data_start + info.file_size - 1}", info.file_size)
    if zipfile.crc32(data) != info.CRC:
        raise ValueError("Member CRC mismatch")
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        raw = stream.read(16_000_001)
    if len(raw) > 16_000_000:
        raise ValueError("Uncompressed validation member too large")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Existing cache differs")
    else:
        with path.open("xb") as f:
            f.write(data)
    return {
        "url": url,
        "member": name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=CACHE)
    args = parser.parse_args()
    for t in (20, 50, 80):
        print(json.dumps(fetch(t, args.cache)))
