#!/usr/bin/env python3
"""Collect one already-completed provider result. No generation, charge or approval.

Default is metadata inspection only. --fetch permits one fixed, read-only HTTPS
request to cdn.openart.ai; all redirects are rejected. Result remains a preview.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import ssl
import urllib.request
from urllib.parse import urlsplit
from PIL import Image

URL = 'https://cdn.openart.ai/watermarked_images/UnUC2OldJIjagbwDQQVT/thumbnail_dbe05ed8_1791384899255.webp'
HISTORY_ID = 'XOYmjAm3VZzPsZPb6ZZS'
LIMIT = 20 * 1024 * 1024

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Provider download redirect rejected')

def inspect_bytes(data: bytes) -> dict:
    if not data or len(data) > LIMIT:
        raise ValueError('Unexpected payload size')
    with Image.open(io.BytesIO(data)) as im:
        im.verify()
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.format not in {'PNG', 'WEBP', 'JPEG'} or getattr(im, 'n_frames', 1) != 1:
            raise ValueError('Expected a single image, not animation')
        width, height = im.size
        return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                'actual_format': im.format, 'width': width, 'height': height,
                'single_file_single_frame': True,
                'portrait_geometry': height > width,
                'layout_semantically_reviewed': False}

def collect(out: Path, fetch: bool = False) -> dict:
    result = {'request_id': 'OA001_WARD_W_DAILY', 'history_id': HISTORY_ID,
              'provider': 'OpenArt', 'model': 'nano-banana-2',
              'provider_status': 'COMPLETED', 'result_class': 'PROVIDER_PREVIEW_UNVERIFIED',
              'provider_reported_dimensions': [768, 1376], 'source_url': URL,
              'bytes_received': False, 'new_generation_submitted': False,
              'new_credits_spent_by_this_script': 0, 'user_approved': False,
              'production_ready': False,
              'note': 'COMPLETED is provider job status only; returned URL is a watermarked/thumbnail path, not proof of a clean master.'}
    if not fetch:
        return result
    if out.exists():
        raise ValueError('Output directory exists; do not overwrite a prior receipt')
    u = urlsplit(URL)
    if u.scheme != 'https' or u.hostname != 'cdn.openart.ai' or u.username or u.query:
        raise ValueError('Unexpected provider endpoint')
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    req = urllib.request.Request(URL, headers={'User-Agent': 'AI-short-vidio-claw/OA001-read-only-receipt', 'Accept': 'image/*'})
    with opener.open(req, timeout=45) as response:
        if response.status != 200:
            raise ValueError('Unexpected HTTP status')
        data = response.read(LIMIT + 1)
    meta = inspect_bytes(data)
    suffix = {'PNG': '.png', 'JPEG': '.jpg', 'WEBP': '.webp'}[meta['actual_format']]
    out.mkdir(parents=True, exist_ok=False)
    name = 'OA001_provider_returned' + suffix
    (out / name).write_bytes(data)
    result.update(bytes_received=True, file=name, actual_media=meta)
    (out / 'receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', default='local/provider_review/OA001')
    p.add_argument('--fetch', action='store_true')
    a=p.parse_args()
    try:
        print(json.dumps(collect(Path(a.out),a.fetch),ensure_ascii=False,indent=2)); return 0
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e),'production_ready':False},ensure_ascii=False)); return 2
if __name__=='__main__': raise SystemExit(main())
