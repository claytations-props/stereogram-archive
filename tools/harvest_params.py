"""Recover live-warp parameters for every catalogued card.

The published rectified pair IS the ground truth of what the archive shows.
Each baked eye is an affine view of the original scan (crop = affine,
resize = affine, warp = affine; their composition is one affine). So for
each card: fit baked-eye -> scan with SIFT, express the fit as a UV affine
per eye, re-render the pair from those numbers alone, and keep the params
only if the re-render measures inside the comfort gates.

px format (stored per item in data.json):
  {s: scan url the runtime should fetch,
   L: [a,b,c, d,e,f]  scan_uv = (a*u + b*v + c, d*u + e*v + f), (u,v) in eye space
   R: same for the right eye,
   g: [left gain, right gain], ar: eye aspect (out_w/out_h)}
"""
import sys, json, re, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import cv2, numpy as np
from stereo_pipeline import _matches, _fit

def _fit_wide(g_ref, g_mov):
    """_fit with scale bounds widened: baked->scan fits legitimately carry the
    thumbnail/original scale ratio (e.g. det 0.51), which the pipeline's
    same-scale guard rejects. Shear guard and RANSAC unchanged."""
    mm = _matches(g_ref, g_mov)
    if mm is None: return None
    src, dst = mm
    A, inl = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if A is None: return None
    det = float(np.linalg.det(A[:, :2]))
    if not (0.2 < det < 3.0) or abs(A[0, 1]) > 0.28 or abs(A[1, 0]) > 0.28:
        return None
    return A, inl.ravel().astype(bool), src, dst

BASE = pathlib.Path(__file__).parent.parent
UA = {'User-Agent': 'StereographArchive/1.0 (claytations@gmail.com)'}
GATE = 0.35

def fetch(u):
    req = urllib.request.Request(u.split('?')[0], headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        buf = np.frombuffer(r.read(), np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)

def measure(pair):
    h, w2 = pair.shape[:2]; w = w2 // 2
    gL = cv2.cvtColor(pair[:, :w], cv2.COLOR_BGR2GRAY)
    gR = cv2.cvtColor(pair[:, w:], cv2.COLOR_BGR2GRAY)
    fit = _fit(gL, gR)
    if fit is None: return None
    A, inl, src, dst = fit
    pred = cv2.transform(src, A); res = (dst - pred)[:, 0, :][inl]
    rot = abs(float(np.degrees(np.arctan2(A[1, 0], A[0, 0]))))
    vert = float(np.percentile(np.abs(res[:, 1]), 90)) / h * 100
    return round(rot, 2), round(vert, 2)

def uv_affine(A, ow, oh, W, H, xoff=0.0):
    """Pixel affine (baked eye px -> scan px) to UV affine (eye uv -> scan uv)."""
    return [A[0, 0] * ow / W, A[0, 1] * oh / W, (A[0, 2] + xoff) / W,
            A[1, 0] * ow / H, A[1, 1] * oh / H, A[1, 2] / H]

def render(scan, px, ow, oh):
    H, W = scan.shape[:2]
    us = (np.arange(ow) + 0.5) / ow; vs = (np.arange(oh) + 0.5) / oh
    U, V = np.meshgrid(us, vs)
    out = []
    for key in ('L', 'R'):
        a = px[key]
        mx = (a[0] * U + a[1] * V + a[2]) * W
        my = (a[3] * U + a[4] * V + a[5]) * H
        eye = cv2.remap(scan, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        out.append(eye)
    left = (out[0].astype(np.float32) * px['g'][0]).clip(0, 255).astype(np.uint8)
    right = (out[1].astype(np.float32) * px['g'][1]).clip(0, 255).astype(np.uint8)
    return np.hstack([left, right])

def main():
    data = json.loads((BASE / 'data.json').read_text())
    cond = json.loads((BASE / 'condition.json').read_text())
    vr = (BASE / 'vr.html').read_text()
    vrd = json.loads(re.search(r'const DATA=(\[.*?\]);', vr, re.S).group(1))
    report = {}
    for i, it in enumerate(data):
        it['va'] = vrd[i]['a']
        try:
            scan = fetch(it['img'])
            if scan is None: raise ValueError('scan decode failed')
            H, W = scan.shape[:2]; hw = W // 2
            baked = cv2.imread(str(BASE / 'rect' / f'{i:02d}.jpg'))
            bh, bw2 = baked.shape[:2]; bw = bw2 // 2
            gS = cv2.cvtColor(scan, cv2.COLOR_BGR2GRAY)
            px = {'s': it['img'].split('?')[0], 'ar': it['va']}
            sims = []
            for side, (eye, xoff) in enumerate(((baked[:, :bw], 0), (baked[:, bw:], hw))):
                gE = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
                half = gS[:, xoff:xoff + hw]
                fit = _fit_wide(half, gE)   # src = baked eye pts, dst = scan half pts
                if fit is None: raise ValueError(f'eye {side} fit failed')
                A, inl, src, dst = fit
                if inl.mean() < 0.35: raise ValueError(f'eye {side} weak fit (inliers {inl.mean():.2f})')
                px['L' if side == 0 else 'R'] = [round(float(v), 6) for v in uv_affine(A, bw, bh, W, H, xoff)]
                sims.append(eye)
            px['g'] = [1.0, 1.0]
            sim0 = render(scan, px, bw, bh)
            gains = []
            for side in range(2):
                m_sim = float(sim0[:, side * bw:(side + 1) * bw].mean())
                m_ref = float(sims[side].mean())
                gains.append(round(min(1.0, max(0.75, m_ref / max(m_sim, 1e-6))), 4))
            px['g'] = gains
            sim = render(scan, px, bw, bh)
            mm = measure(sim)
            ref = cond[str(i)]
            ok = mm is not None and mm[0] <= GATE and mm[1] <= GATE
            report[str(i)] = {'sim_rot': mm[0] if mm else None, 'sim_vert': mm[1] if mm else None,
                              'ref_rot': ref['rot'], 'ref_vert': ref['vert'], 'gains': gains, 'verified': bool(ok)}
            if ok: it['px'] = px
            print(i, it['id'], 'OK' if ok else 'OUT-OF-GATES', report[str(i)], flush=True)
        except Exception as e:
            report[str(i)] = {'error': str(e)[:200]}
            print(i, it.get('id'), 'FAILED', str(e)[:160], flush=True)
    (BASE / 'data.json').write_text(json.dumps(data, indent=1))
    (BASE / 'tools' / 'params_report.json').write_text(json.dumps(report, indent=1))
    got = sum(1 for v in report.values() if v.get('verified'))
    print(f'VERIFIED PARAMS: {got}/{len(data)}')

if __name__ == '__main__':
    main()
