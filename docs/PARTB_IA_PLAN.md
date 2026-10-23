# Phase 2 Part B — Internet Archive Image Move: Plan and Status

Written 2026-10-22. Clay approved the move to the Internet Archive
(the Google Cloud Storage route was declined: it requires a billing
card. The Archive needs no card, and its upload API makes the move
fully scripted — nothing is uploaded by hand.)

**Status: PREP COMPLETE, TEST UPLOAD PASSED. The full upload has
NOT been started — it waits for a separate go.**

## Item plan

Two public items under Clay's archive.org account
(screen name "Clayton Hull537", member since 2024), plus one
scratch test item:

| Item | Mediatype | Contents | Files | Size |
|---|---|---|---|---|
| `stereogram-archive-images` | image | `rect/<n>.jpg` rectified pairs; `thumbs/<STA>/w{250,500,1000}.jpg`; `thumbs-rect/<STA>/w{250,500,1000}.jpg` | 7,182 | 532.5 MB |
| `stereogram-archive-masters` | data | `masters/<STA>/<original filename>` — the preservation masters, paths exactly as in the local preservation store | 1,026 | 4,873.6 MB |
| `stereogram-archive-test` | image | STA-0001 only: its rect pair, 6 thumbnails, and its master | 8 | 1.1 MB |

Metadata on each real item: creator "Claytations Props", subject
tags (stereographs; stereoscopic photography; vintage photography;
3D photography), and a description that mirrors the archive site's
own About/footer wording — factual text about the collection, no
new claims. The masters item's description states that SHA-256 is
recorded per file in the archive fixity manifest.

After the images item is verified, the site's `ASSET_BASE`
(tools/build_catalog.py) becomes
`https://archive.org/download/stereogram-archive-images/`, which
produces exactly the URL shapes the catalog already expects:
`{base}rect/<n>.jpg`, `{base}thumbs/<STA>/w<width>.jpg`,
`{base}thumbs-rect/<STA>/w<width>.jpg`.

## The upload script

`tools/upload_ia.py` (internetarchive 5.12.1, in
`~/workspace/.venvs/cv`):

- Credentials come only from the ia tool's own config,
  `~/.config/internetarchive/ia.ini` (`[s3]` access/secret;
  directory 0700, file 0600), read by the package itself. Nothing
  secret is accepted on the command line or printed/logged.
- Uploads run in batches of 50 files per item with
  `checksum=True` (IAS3 skips any file whose remote MD5 already
  matches — reruns resume where they stopped) and `verify=True`
  (each file's MD5 is checked against what IAS3 received).
- `--verify` compares the full remote file list (name, size, MD5)
  against local hashes; masters and rect pairs are additionally
  checked locally against the fixity manifest's SHA-256 before
  their MD5 is trusted. Progress logs to stdout and
  `~/workspace/stereogram-archive-assets/upload-ia.log`.
- `--dry-run` prints the file plan with no network writes.
  `--test` uploads STA-0001's 8 files to the scratch item and
  verifies them.
- Commands for the full run, in order:
  1. `python tools/upload_ia.py --item images`
  2. `python tools/upload_ia.py --item masters`
  3. `python tools/upload_ia.py --item images --verify-only` and
     `--item masters --verify-only` — both must report 0 missing /
     0 mismatched before the switchover.

## Thumbnail ladder (completed 2026-10-22)

`tools/build_thumbs.py` now covers all 1,026 items in
`~/workspace/stereogram-archive-assets/`:

- thumbs: 3,078 files, 137.6 MB — thumbs-rect: 3,078 files,
  136.8 MB. Every item has all 3 rungs in both ladders;
  0 incomplete items, 0 undecodable sources, 0 failures.
- 232 rungs are honest native-width exceptions (a derivative is
  never upscaled): thumbs 79 (all at w1000); thumbs-rect 153
  (134 at w1000, 16 at w500, 3 at w250). Verified by direct
  inspection of every file; the method reproduces the first run's
  logged count for the original 515 items exactly (203).

## Environment quirks found while testing

- **Egress proxy TLS.** This VM reaches the internet through a
  proxy that re-signs TLS with its own CA (`SSL_CERT_FILE` /
  `REQUESTS_CA_BUNDLE` point at its bundle). Plain `requests`
  honors those variables; the ia S3 upload path verifies against
  certifi instead and failed with `CERTIFICATE_VERIFY_FAILED`
  (self-signed certificate in chain). `upload_ia.py` passes the
  environment bundle to the upload calls via `request_kwargs`
  when one is set; on a normal machine nothing changes.
- **Metadata lag.** IA's metadata service indexes new files
  asynchronously; the test item's file list took several minutes
  to reflect S3. The S3 bucket listing is ground truth
  immediately. The script's verify pass polls the metadata for
  up to ~6 minutes before judging a file missing.
- **Package shape.** In internetarchive 5.12.1, `item.files` is a
  list of dicts (`name`/`size`/`md5`), not File objects.

## CORS / URL verification — checklist and TEST RESULTS

The Parlor loads rectified pairs as WebGL textures, so the IA
download endpoint must serve them cross-origin. The checklist was
executed against `stereogram-archive-test` on 2026-10-22:

1. ✅ **Exact bytes.** `https://archive.org/download/
   stereogram-archive-test/rect/00.jpg`, one thumbnail, and the
   STA-0001 master were downloaded and SHA-256-compared against
   the local files / fixity manifest — identical.
2. ✅ **CORS.** With an `Origin` header, the 302 redirect response
   carries `Access-Control-Allow-Origin: *`, and the final storage
   node (ia600903.us.archive.org) returns 200 with
   `Access-Control-Allow-Origin: *` and
   `Access-Control-Allow-Credentials: true`. Suitable for
   cross-origin texture use (the Parlor's loads are
   non-credentialed).
3. ✅ **HEAD / Range.** HEAD returns the redirect with
   `Access-Control-Allow-Origin: *` and the right content type;
   a `Range: bytes=0-99` request returns 206 with exactly the
   first 100 local bytes. `Accept-Ranges: bytes` is advertised.
4. ✅ **Upload + verify loop.** The script's `--test` uploaded
   all 8 files (auth via the account's S3 keys), a rerun skipped
   them by checksum, and `--verify-only` reported 8 OK /
   0 missing / 0 mismatched.

The same four checks must be re-run against
`stereogram-archive-images` (one rect pair + one thumbnail)
after the full upload, before `ASSET_BASE` is switched.

## Switchover steps (after the full upload verifies)

1. Re-run the CORS checks against the real images item.
2. Set `ASSET_BASE` in tools/build_catalog.py to
   `https://archive.org/download/stereogram-archive-images/`
   (or pass `--asset-base`), regenerate outputs, and wire the
   gallery/Parlor thumbnail URLs to the ladders.
3. Push, then verify live: gallery browse, a record open, and
   the Parlor in the headset (Clay's verdict governs).
4. Remove the `rect/` binaries from the repo working tree in a
   follow-up commit (no history rewrite). The masters copy on
   IA plus the local preservation store gives two geographically
   separate copies of every master, each SHA-256-verified.
5. Rollback at any point: reset `ASSET_BASE` to `''`, regenerate,
   push — the site returns to repo-served images.
