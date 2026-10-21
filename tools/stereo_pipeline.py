"""Stereograph overlay pipeline.

Given a scanned stereo pair, produce a rectified, comfort-checked pair image:
  1. find the two printed photographs (stored rects, or auto-detect)
  2. match features between them and fit a full affine (rotation, scale, shear)
  3. warp one eye into the other's frame, set the stereo window, crop to the
     content both eyes share, match brightness
  4. measure the RESULT: leftover rotation, vertical error (global and per
     3x3 cell), and true displayed depth; size the card down if its depth
     exceeds the comfort budget
  5. PASS only if every measurement is inside tolerance

Nothing ships on a promise: the gates run on the output pixels.
"""
import cv2, numpy as np

_sift = cv2.SIFT_create()
_bf = cv2.BFMatcher()
BUDGET_DEG = 1.15          # total comfortable disparity, degrees
GATE_VERT, GATE_ROT, GATE_CELL = 0.35, 0.35, 0.50   # % of height / degrees / % of height
GATE_POST_RANGE = 1.35     # degrees of depth allowed after sizing
MIN_AREA_FRAC = 0.55

def _matches(g_ref, g_mov):
    kpR, dR = _sift.detectAndCompute(g_ref, None)
    kpM, dM = _sift.detectAndCompute(g_mov, None)
    if dR is None or dM is None:
        return None
    good = []
    for m, n in _bf.knnMatch(dM, dR, k=2):
        if m.distance < 0.75 * n.distance:
            good.append(m)
    if len(good) < 12:
        return None
    src = np.float32([kpM[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kpR[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    return src, dst

def _fit(g_ref, g_mov):
    mm = _matches(g_ref, g_mov)
    if mm is None:
        return None
    src, dst = mm
    A, inl = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    if A is None:
        return None
    det = float(np.linalg.det(A[:, :2]))
    if not (0.7 < det < 1.4) or abs(A[0, 1]) > 0.28 or abs(A[1, 0]) > 0.28:
        return None
    return A, inl.ravel().astype(bool), src, dst

def _snap(gray, x0, y0, x1, y1):
    """Snap a box's edges to the strongest nearby gradient lines."""
    H, W = gray.shape
    gx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    gy = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
    ya, yb = max(0, int(y0)), min(H, int(y1)); xa, xb = max(0, int(x0)), min(W, int(x1))
    colsum = gx[ya:yb, :].mean(axis=0); rowsum = gy[:, xa:xb].mean(axis=1)
    def pick(arr, v, tol):
        v = min(max(v, 0), len(arr) - 1)
        lo, hi = max(0, int(v - tol)), min(len(arr) - 1, int(v + tol))
        return lo + int(np.argmax(arr[lo:hi + 1]))
    tw, th = 0.05 * W, 0.05 * H
    return (pick(colsum, x0, tw), pick(rowsum, y0, th), pick(colsum, x1, tw), pick(rowsum, y1, th))

def auto_rects(img):
    """Find the two printed-photo rectangles in a fresh scan, as scan fractions."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = g.shape; hw = W // 2
    hl, hr = g[:, :hw], g[:, hw:]
    fit = _fit(hl, hr)
    if fit is None:
        return None
    A, inl, src, dst = fit
    pts = dst[inl][:, 0, :]
    x0, y0 = pts.min(axis=0); x1, y1 = pts.max(axis=0)
    bw, bh = x1 - x0, y1 - y0
    x0 = max(0, x0 - 0.10 * bw); x1 = min(hw, x1 + 0.10 * bw)
    y0 = max(0, y0 - 0.10 * bh); y1 = min(H, y1 + 0.10 * bh)
    lx0, ly0, lx1, ly1 = _snap(hl, x0, y0, x1, y1)
    Ai = cv2.invertAffineTransform(A)
    corners = np.float32([[lx0, ly0], [lx1, ly0], [lx0, ly1], [lx1, ly1]]).reshape(-1, 1, 2)
    rc = cv2.transform(corners, Ai)[:, 0, :]
    rx0, ry0 = rc.min(axis=0); rx1, ry1 = rc.max(axis=0)
    rx0, ry0, rx1, ry1 = _snap(hr, rx0, ry0, rx1, ry1)
    return [lx0 / W, ly0 / H, (lx1 - lx0) / W, (ly1 - ly0) / H,
            (hw + rx0) / W, ry0 / H, (rx1 - rx0) / W, (ry1 - ry0) / H]

def rectify(img, rects, capture=None):
    """Rectify one pair. Returns (pair_image, metrics dict).
    If capture is a dict, it is filled with the live-warp parameters:
    scan size, crop size, windowed affine A2, common crop rect, gains."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    def box(rr): return int(rr[0] * W), int(rr[1] * H), int(rr[2] * W), int(rr[3] * H)
    lx, ly, lw, lh = box(rects[:4]); rx, ry, rw, rh = box(rects[4:])
    Lg = gray[ly:ly + lh, lx:lx + lw]
    Rg = cv2.resize(gray[ry:ry + rh, rx:rx + rw], (lw, lh))
    rec = {}
    fit = _fit(Lg, Rg)
    if fit is None:
        rec['fail'] = 'no consistent affine between the halves'
        return None, rec
    A, inl, src, dst = fit
    pred = cv2.transform(src, A); res = (dst - pred)[:, 0, :]
    rin = res[inl]
    rec['fit_vert_p90_pct'] = round(float(np.percentile(np.abs(rin[:, 1]), 90)) / lh * 100, 2)
    rec['inl_ratio'] = round(float(inl.mean()), 2)
    # stereo window: far content (p2 of rendered disparity) lands on the plane
    tx = float(np.percentile(rin[:, 0], 2))
    A2 = A.copy(); A2[0, 2] += tx
    # true displayed depth from vertically consistent matches
    pred2 = cv2.transform(src, A2)
    keep = np.abs(dst[:, 0, 1] - pred2[:, 0, 1]) <= 0.006 * lh
    if keep.sum() >= 20:
        rd = (dst[keep, 0, 0] - pred2[keep, 0, 0]) / lw * 100
        disp_range = float(np.percentile(rd, 98) - np.percentile(rd, 2))
    else:
        disp_range = 99.0
    rec['disp_range_pct'] = round(disp_range, 2)
    # warp the right eye into the left eye's frame (warpAffine takes the point transform)
    Rc = cv2.resize(img[ry:ry + rh, rx:rx + rw], (lw, lh))
    Rw = cv2.warpAffine(Rc, A2, (lw, lh), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    mask = cv2.warpAffine(np.full((lh, lw), 255, np.uint8), A2, (lw, lh),
                          flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # largest axis-aligned rectangle inside the valid parallelogram
    m = mask > 0
    if m.sum() < 1000:
        rec['fail'] = 'no common area'; return None, rec
    xl = np.where(m.any(axis=1), m.argmax(axis=1), lw + 1).astype(np.float64)
    xr = np.where(m.any(axis=1), lw - 1 - m[:, ::-1].argmax(axis=1), -1).astype(np.float64)
    best = (0, 0, 0, 0, 0)
    for yy0 in range(0, lh, 3):
        X0 = np.maximum.accumulate(xl[yy0:]); X1 = np.minimum.accumulate(xr[yy0:])
        wid = X1 - X0; hei = np.arange(1, lh - yy0 + 1)
        areas = np.where(wid > 40, wid * hei, 0)
        k = int(np.argmax(areas))
        if areas[k] > best[0]:
            best = (float(areas[k]), int(X0[k]), int(X1[k]), yy0, yy0 + k)
    _, x0, x1, y0, y1 = best
    ix, iy = int(0.012 * (x1 - x0)), int(0.012 * (y1 - y0))
    x0 += ix; x1 -= ix; y0 += iy; y1 -= iy
    rec['area_frac'] = round(float((x1 - x0) * (y1 - y0)) / (lw * lh), 2)
    # brightness: darken the brighter eye to match (means over the common area)
    Lc = img[ly:ly + lh, lx:lx + lw]
    mL = float(Lc[y0:y1, x0:x1].mean()); mR = float(Rw[y0:y1, x0:x1].mean())
    gL = min(1.0, mR / max(mL, 1e-6)); gR = min(1.0, mL / max(mR, 1e-6))
    gL = max(gL, 0.8); gR = max(gR, 0.8)
    Lc2 = (Lc.astype(np.float32) * gL).clip(0, 255).astype(np.uint8)
    Rw2 = (Rw.astype(np.float32) * gR).clip(0, 255).astype(np.uint8)
    pair = np.hstack([Lc2[y0:y1, x0:x1], Rw2[y0:y1, x0:x1]])
    rec['out_w'], rec['out_h'] = int(x1 - x0), int(y1 - y0)
    # depth budget -> display size factor
    aspect = (x1 - x0) / (y1 - y0)
    K = (2.3 + 10) / 2.3 * 1.5
    width_ang = float(np.degrees(2 * np.arctan((K * aspect / 2) / 12.3)))
    range_deg = disp_range / 100 * width_ang
    f = max(0.3, min(1.0, BUDGET_DEG / max(range_deg, 0.01)))
    rec.update(width_ang=round(width_ang, 1), range_deg=round(range_deg, 2), size_f=round(float(f), 2))
    # ---- output self-check on the shipped pixels ----
    ph, pw2 = pair.shape[:2]; pw = pw2 // 2
    gLft = cv2.cvtColor(pair[:, :pw], cv2.COLOR_BGR2GRAY)
    gRgt = cv2.cvtColor(pair[:, pw:], cv2.COLOR_BGR2GRAY)
    orot, overt, cellbad = 9.0, 9.0, 9.0
    fit2 = _fit(gLft, gRgt)
    if fit2 is not None:
        A3, inl3, s2, d2 = fit2
        orot = abs(float(np.degrees(np.arctan2(A3[1, 0], A3[0, 0]))))
        p3 = cv2.transform(s2, A3); r3 = (d2 - p3)[:, 0, :]
        overt = float(np.percentile(np.abs(r3[inl3, 1]), 90)) / ph * 100
        cmax = 0.0
        for cyi in range(3):
            for cxi in range(3):
                sel = inl3 & (d2[:, 0, 0] >= cxi * pw / 3) & (d2[:, 0, 0] < (cxi + 1) * pw / 3) & \
                      (d2[:, 0, 1] >= cyi * ph / 3) & (d2[:, 0, 1] < (cyi + 1) * ph / 3)
                if sel.sum() >= 6:
                    cmax = max(cmax, abs(float(np.median(r3[sel, 1]))) / ph * 100)
        cellbad = cmax
    rec.update(out_rot=round(orot, 2), out_vert=round(overt, 2), out_cellbad=round(cellbad, 2))
    rec['pass'] = bool(overt <= GATE_VERT and orot <= GATE_ROT and cellbad <= GATE_CELL
                       and range_deg * f <= GATE_POST_RANGE and rec['area_frac'] >= MIN_AREA_FRAC)
    if capture is not None:
        capture.update(scan_wh=(W, H), crop_wh=(lw, lh), A2=[[float(v) for v in row] for row in A2],
                       crop_rect=(int(x0), int(y0), int(x1), int(y1)), gains=(round(float(gL), 4), round(float(gR), 4)),
                       rects=[float(v) for v in rects])
    return pair, rec
