"""QC sweep: draw every chapter at a fine time step to catch exceptions and long near-blank stretches.

    python3 video/qc_sweep.py --project king            # all chapters
    python3 video/qc_sweep.py --project king 4 5         # some chapters
"""
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video import project as PROJECT  # noqa: E402

STEP = 0.25


def sweep(ch, slug):
    PROJECT.use(slug)
    from video.render import load_chapter
    from video.engine.core import W, H, new_surface, new_ctx
    from video.engine.scene import draw_frame
    try:
        tl, shots, sfx, overlay = load_chapter(ch)
    except Exception:
        return ch, [f"load failed:\n{traceback.format_exc()}"], []
    surf = new_surface()
    cr = new_ctx(surf)
    errors, blanks = [], []
    times = sorted(set([round(i * STEP, 3) for i in range(int(tl.dur / STEP))] +
                       [round(s.start + 0.05, 3) for s in shots if s.start + 0.05 < tl.dur]))
    run = 0.0
    for T in times:
        try:
            cr.save()
            draw_frame(cr, shots, T, overlay)
            cr.restore()
        except Exception as ex:  # noqa: BLE001
            errors.append(f"T={T:.2f}: {type(ex).__name__}: {ex}")
            cr = new_ctx(surf)
            continue
        surf.flush()
        a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[::24, ::24, :3].astype(np.float32)
        if a.std() < 6.0:
            run += STEP
            if run >= 1.5:
                blanks.append(T)
        else:
            run = 0.0
    return ch, errors, blanks


def main():
    PROJECT.pop_project_arg(sys.argv)
    slug = os.environ.get("VIDEO_PROJECT", "iq500")
    chs = [int(a) for a in sys.argv[1:]] or list(range(1, 11))
    bad = False
    with ProcessPoolExecutor(4) as ex:
        for ch, errors, blanks in ex.map(sweep, chs, [slug] * len(chs)):
            status = "OK" if not errors else f"{len(errors)} ERRORS"
            print(f"ch{ch:02d}: {status}" + (f", near-blank around {blanks[0]:.1f}s..{blanks[-1]:.1f}s ({len(blanks)} samples)"
                                             if blanks else ""))
            for e in errors[:5]:
                print("   ", e)
            bad = bad or bool(errors)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
