"""The ceratopsians' fluid plumbing (06/11/2026): what the T. rex's rexflow/rexduel/rexmore taught
(docs/estudos/08_ANIMACAO_RAXIORES.md), adapted to four legs, for the Triceratops (trikeflow.py), the Styracosaurus
(styracosaurus/styraflow.py) and the Protoceratops (protoceratops/protoflow.py). Only the plumbing is shared; every
species passes its own numbers and writes its own signatures (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md).

Four legs instead of two:
  * the body of these rigs is ONE bone pivoting at the hips, so the hips roll over the standing hind leg with the
    body and the shoulders' counter-roll goes into the neck (the neck rolls back against it, the head stays level);
  * every leg is counter-rolled against the body (thigh/arm z = -roll, y = -yaw) and then PINNED sideways: after the
    planar IK each foot is abducted until it is back on its own track (x), so a rolling or yawing body never slides a
    planted foot sideways. The same pin carries the feet sideways on purpose in the strafe and the turn;
  * the front legs carry the head's weight: when the head goes down or the weight goes forward the forefeet step or
    brace, the body sinks at the shoulders; the steps of the turn and the strafe go in DIAGONAL pairs (left fore with
    right hind), as a quadruped trots;
  * the body drops fast after each hind footfall and rises slowly (the bob is skewed), the heavy head nods LATE, and
    the tail swings with a delay and a gain that grow to the tip.
Signs (all three rigs): body +x = nose up; neck/skull -x = down; jaw -x = open; + yaw swings the head to the animal's
RIGHT in game (a left turn leads with - yaw); + model x is the animal's left; + roll lifts the left side.
"""
import math

import numpy as np
from anim2 import add, world, chain_angle, smooth, ease_in, ease_out, back_out, Track


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def ring(t, t0, freq, tau):
    """a damped shake that starts at t0 from zero (continuous) and dies out"""
    if t <= t0: return 0.0
    return math.exp(-(t - t0) / tau) * math.sin(2 * math.pi * freq * (t - t0))


def kick(t, t0, tau, rise=0.05):
    """a jolt: rises in `rise`, decays with `tau` (never switches)"""
    return math.exp(-max(0.0, t - t0) / tau) * smooth((t - t0 + rise) / rise) if t > t0 - rise else 0.0


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up (-1.9 .. 1.9 at most)"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def loop_tremor(t, L, n=(9, 14, 6), amp=(1.0, 0.55, 0.35), phase=0.0):
    """the same shiver with whole numbers of cycles per loop, so a loop of length L closes"""
    return tremor(t, tuple(k / L for k in n), amp, phase)


def blend(a, b, w):
    out = {}
    for bone in set(a) | set(b):
        ea = a.get(bone, ([0, 0, 0], [0, 0, 0])); eb = b.get(bone, ([0, 0, 0], [0, 0, 0]))
        out[bone] = ([ea[0][i] * (1 - w) + eb[0][i] * w for i in range(3)], [ea[1][i] * (1 - w) + eb[1][i] * w for i in range(3)])
    return out


def skew_drop(x, k=0.6):
    """one bob per unit of x: falls fast (to the bottom at ~30%), rises slow; smooth at the seam"""
    x = x % 1.0
    return 0.5 - 0.5 * math.cos(2 * math.pi * x ** k)


def _yz(v): return np.array([v[1], v[2]], float)


def _ang(v): return math.degrees(math.atan2(v[0], v[1]))


def _norm(v): return float(math.hypot(v[0], v[1]))


def _wrap(a): return (a + 180.0) % 360.0 - 180.0


def _rot(v, deg):
    r = math.radians(deg); c, s_ = math.cos(r), math.sin(r)
    # the inverse of _ang's convention: _ang(_rot(v, d)) = _ang(v) + d
    return np.array([v[0] * c + v[1] * s_, -v[0] * s_ + v[1] * c])


class Quad:
    """the four-legged fluid layer, bound to one species' anims module A (its IK, its head, its tail)"""

    def __init__(self, A, weapon, hind=(18, 12, 16), fore=(16, 28), head_k=0.55, scap=(0.25, 0.05)):
        self.A = A
        self.weapon = weapon                      # weapon(p, k): the head set for the fight (horns, nose horn, frill)
        self.hind = hind                          # (heel lift at push-off, metatarsus swing, toe curl)
        self.fore = fore                          # (heel lift at push-off, hand flip in the swing)
        self.head_k = head_k
        self.scap = scap
        self.tails = A.TAILS
        self.n = len(A.TAILS)
        self.drop = A.STAND_DROP
        self.X0, self.kpd = {}, {}
        for s in A.SIDES:
            for kind, bone, end, rest in (("h", f"thigh_{s}", f"toes_{s}", A.BALL[s]), ("f", f"arm_{s}", f"hand_{s}", A.WRIST[s])):
                q = {}; add(q, bone, rot=(0, 0, 1.0))
                self.kpd[(s, kind)] = world(A.S, q, end)[0] - world(A.S, {}, end)[0]
                self.X0[(s, kind)] = rest[0]
        # the analytic leg IK: which way each joint turns in the side plane, and which way each knee/elbow bends
        self.sx, self.bend = {}, {}
        for s in A.SIDES:
            for up, lo, end in ((f"thigh_{s}", f"shin_{s}", f"foot_{s}"), (f"arm_{s}", f"forearm_{s}", f"hand_{s}")):
                for b, child in ((up, lo), (lo, end)):
                    o = _yz(world(A.S, {}, b)); c0 = _yz(world(A.S, {}, child))
                    q = {}; add(q, b, rot=(1.0, 0, 0)); c1 = _yz(world(A.S, q, child))
                    self.sx[b] = 1.0 if _wrap(_ang(c1 - o) - _ang(c0 - o)) > 0 else -1.0
                j0, j1, j2 = (_yz(world(A.S, {}, b)) for b in (up, lo, end))
                dlt = _wrap(_ang(j1 - j0) - _ang(j2 - j0))
                self.bend[up] = 1.0 if dlt > 0 else -1.0
            o = _yz(world(A.S, {}, f"foot_{s}")); c0 = _yz(world(A.S, {}, f"toes_{s}"))
            q = {}; add(q, f"foot_{s}", rot=(1.0, 0, 0))
            self.sx[f"foot_{s}"] = 1.0 if _wrap(_ang(_yz(world(A.S, q, f"toes_{s}")) - o) - _ang(c0 - o)) > 0 else -1.0
            v0 = _yz(world(A.S, {}, f"toes_{s}")) - _yz(world(A.S, {}, f"foot_{s}"))
            v1 = _yz(world(A.S, q, f"toes_{s}")) - _yz(world(A.S, q, f"foot_{s}"))
            dc = chain_angle(A.S, q, [f"foot_{s}"]) - chain_angle(A.S, {}, [f"foot_{s}"])
            self.sx["meta_" + s] = (_wrap(_ang(v1) - _ang(v0)) / dc, dc)
        self.bend_report = dict(self.bend)

    # ------------------------------------------------------------ feet
    def pin(self, p, s, kind, dx=0.0):
        """abduct the leg until the foot is back on its track (+ dx); returns how far it turned (deg)"""
        bone = f"thigh_{s}" if kind == "h" else f"arm_{s}"
        end = f"toes_{s}" if kind == "h" else f"hand_{s}"
        tot = 0.0
        for _ in range(3):
            err = self.X0[(s, kind)] + dx - world(self.A.S, p, end)[0]
            if abs(err) < 0.03: break
            a = err / self.kpd[(s, kind)]; add(p, bone, rot=(0, 0, a)); tot += abs(a)
        return tot

    # the planar IK of the engine (solve_leg, solve_arm) is numeric and starts from the pose's own angles, so a fast
    # swing can jump from one solution to another between two frames (a 40 deg knee pop in the old walk). Here the
    # side-plane IK is solved in closed form, the knee and the elbow always bending the way they bend at rest, so the
    # same target gives the same leg and a moving target a moving leg.
    REACH = (0.4, 0.6)          # (margin, softness) in px: these pillar legs stand all but straight (hip to ankle
                                # 99.4% of the leg), where the knee angle runs away from any small change of reach

    def _reach(self, D, m):
        M = m - self.REACH[0]; sft = self.REACH[1]
        return M - sft * math.log1p(math.exp((M - D) / sft)) if (M - D) / sft < 30 else D

    def _two(self, p, up, lo, end, T):
        S = self.A.S
        for _ in range(2):
            j0, j1, j2 = (_yz(world(S, p, b)) for b in (up, lo, end))
            L1, L2 = _norm(j1 - j0), _norm(j2 - j1)
            dv = T - j0; D = max(self._reach(_norm(dv), L1 + L2), abs(L1 - L2) + 1e-3)
            a = math.degrees(math.acos(max(-1.0, min(1.0, (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D)))))
            want = _ang(dv) + self.bend[up] * a
            add(p, up, rot=(self.sx[up] * _wrap(want - _ang(j1 - j0)), 0, 0))
            j1, j2 = _yz(world(S, p, lo)), _yz(world(S, p, end))
            add(p, lo, rot=(self.sx[lo] * _wrap(_ang(T - j1) - _ang(j2 - j1)), 0, 0))

    def ik_hind(self, p, s, dy, dz, meta, toe, clear=-0.05):
        """the ball of the foot exactly on its target; the metatarsus at its pitch unless the hip cannot reach that
        far, then the heel rises (the ankle is put where the leg reaches and the ball is still on the target)"""
        A = self.A; S = A.S
        b = A.BALL[s]; T = np.array([b[1] + dy, b[2] + dz])
        k, dc = self.sx["meta_" + s]
        hip = f"thigh_{s}"
        for _ in range(4):
            for _ in range(2):
                m = A.REST_META[s] + meta
                mc = chain_angle(S, p, [f"foot_{s}"])
                ank = _yz(world(S, p, f"foot_{s}")); ball = _yz(world(S, p, f"toes_{s}"))
                v = _rot(ball - ank, k * (m - mc)); lv = _norm(v)
                at = T - v
                j0, j1 = _yz(world(S, p, hip)), _yz(world(S, p, f"shin_{s}"))
                Lm = _norm(j1 - j0) + _norm(ank - j1)
                D = _norm(at - j0); De = self._reach(D, Lm)
                if De < D - 1e-4:
                    # the ankle on both circles: De from the hip, |v| from the ball; the one nearer the wanted ankle
                    c = T - j0; dc_ = _norm(c)
                    if abs(lv - De) < dc_ < lv + De:
                        x = (De * De - lv * lv + dc_ * dc_) / (2 * dc_); h = math.sqrt(max(0.0, De * De - x * x))
                        u = c / dc_; nrm = np.array([-u[1], u[0]])
                        cands = [j0 + x * u + h * nrm, j0 + x * u - h * nrm]
                        at = min(cands, key=lambda q: _norm(q - at))
                self._two(p, hip, f"shin_{s}", f"foot_{s}", at)
                ank = _yz(world(S, p, f"foot_{s}")); ball = _yz(world(S, p, f"toes_{s}"))
                add(p, f"foot_{s}", rot=(self.sx[f"foot_{s}"] * _wrap(_ang(T - ank) - _ang(ball - ank)), 0, 0))
            cur = chain_angle(S, p, [f"toes_{s}"])
            add(p, f"toes_{s}", rot=(toe - cur, 0, 0))
            if clear is None: break
            lo = A.low_of(p, A.HIND[s])
            if lo > clear - 0.02: break
            T = T + np.array([clear - lo, 0.0])

    def ik_fore(self, p, s, dy, dz, pitch, clear=-0.05, scap=True):
        A = self.A; S = A.S
        w = A.WRIST[s]; T = np.array([w[1] + dy, w[2] + dz])
        if scap and self.scap[0]: add(p, f"arm_{s}", pos=(0, -self.scap[1] * abs(dz), self.scap[0] * dz))
        for _ in range(4):
            self._two(p, f"arm_{s}", f"forearm_{s}", f"hand_{s}", T)
            cur = chain_angle(S, p, [f"hand_{s}"])
            add(p, f"hand_{s}", rot=(A.REST_HAND[s] + pitch - cur, 0, 0))
            if clear is None: break
            lo = A.low_of(p, A.FORE[s])
            if lo > clear - 0.02: break
            T = T + np.array([clear - lo, 0.0])

    def foot(self, p, s, kind, dy=0.0, dz=0.0, dx=0.0, meta=0.0, toe=0.0, pitch=0.0, clear=-0.05):
        if kind == "h":
            self.ik_hind(p, s, dy, dz, meta, toe, clear)
            if self.pin(p, s, kind, dx) > 0.5: self.ik_hind(p, s, dy, dz, meta, toe, clear)
        else:
            self.ik_fore(p, s, dy, dz, pitch, clear)
            if self.pin(p, s, kind, dx) > 0.5: self.ik_fore(p, s, dy, dz, pitch, clear, scap=False)

    def counter_legs(self, p, k=1.0):
        """each leg takes back the body's roll and yaw, so it hangs straight under its joint"""
        e = p.get("body", ([0, 0, 0], [0, 0, 0]))
        r, y = e[0][2], e[0][1]
        for s in self.A.SIDES:
            add(p, f"thigh_{s}", rot=(0, -k * y, -k * r)); add(p, f"arm_{s}", rot=(0, -k * y, -k * r))

    def stance(self, p, fore=(0.0, 0.0), hind=(0.0, 0.0), fdx=(0.0, 0.0), hdx=(0.0, 0.0), clear=0.3, lift=True):
        """all four feet on the ground, each on its own track (fore/hind: dz per side, + = back; dx: + = left)"""
        self.counter_legs(p)
        if lift: self.A.lift_head(p, clear)
        for i, s in enumerate(self.A.SIDES):
            self.foot(p, s, "h", 0.0, hind[i], hdx[i])
            self.foot(p, s, "f", 0.0, fore[i], fdx[i])
        return p

    def step(self, p, s, kind, u, dz0=0.0, dz1=0.0, dx0=0.0, dx1=0.0, lift=5.0, base_dz=0.0, base_dx=0.0):
        """one step of a foot: u in [0, 1] = lift-off to touch-down (outside: planted at the start/end)"""
        uu = min(1.0, max(0.0, u)); e = smooth(uu); arc = math.sin(math.pi * e)      # leaves and lands softly
        dz = base_dz + dz0 + (dz1 - dz0) * e; dx = base_dx + dx0 + (dx1 - dx0) * e
        if 0.0 < u < 1.0:
            hm, hs, ht = self.hind; fh, fs = self.fore
            if kind == "h":
                self.foot(p, s, "h", lift * arc ** 1.2, dz, dx, meta=-hs * arc, toe=-ht * arc, clear=-0.05 + 0.85 * arc ** 1.5)
            else:
                self.foot(p, s, "f", lift * arc ** 1.2, dz, dx, pitch=-0.4 * fs * arc, clear=-0.05 + 0.85 * arc ** 1.5)
        else:
            self.foot(p, s, kind, 0.0, dz, dx)

    def plan(self, p, t, s, kind, keys=(), base=(0.0, 0.0), meta=0.0, pitch=0.0):
        """a foot through a list of moves (the fight set, 06/11): keys = (t0, t1, dz, dx, lift), each from where the
        last one left it to (dz, dx) around base (dz, dx); lift > 0 is a step, lift 0 a drag along the ground; while
        planted the hind heel takes `meta` (the push of a leg driving the body) and the hand `pitch`"""
        cz, cx = 0.0, 0.0
        for t0, t1, dz, dx, lift in keys:
            if t < t0: break
            if t < t1:
                u = (t - t0) / (t1 - t0)
                if lift > 0:
                    self.step(p, s, kind, u, dz0=cz, dz1=dz, dx0=cx, dx1=dx, lift=lift, base_dz=base[0], base_dx=base[1])
                else:
                    e = smooth(u)
                    self.foot(p, s, kind, 0.0, base[0] + cz + (dz - cz) * e, base[1] + cx + (dx - cx) * e)
                return
            cz, cx = dz, dx
        if kind == "h": self.foot(p, s, "h", 0.0, base[0] + cz, base[1] + cx, meta=meta)
        else: self.foot(p, s, "f", 0.0, base[0] + cz, base[1] + cx, pitch=pitch)

    # ------------------------------------------------------------ layers
    def alive(self, p, t, k=1.0, period=3.2):
        """the breathing under every standing pose: the barrel swells, the head rides it a beat late (no feet here:
        call it before the legs are planted)"""
        br = wave(t, period)
        add(p, "body", rot=(0.45 * k * br, 0, 0), pos=(0, -0.35 * k * (1 + br), 0))
        add(p, "neck", rot=(-0.4 * k * wave(t, period, -0.5), 0, 0))
        add(p, "skull", rot=(-0.3 * k * wave(t, period, -1.0), 0, 0))
        for i, b in enumerate(self.tails):
            add(p, b, rot=(0.25 * k * (1 + 0.3 * i) * wave(t, period, -0.45 * i), 0, 0))
        return br

    def alive_upper(self, p, t, k=1.0, period=3.2, slow=None):
        """the breathing layer without the body (for poses whose feet are already planted)"""
        add(p, "neck", rot=(-0.6 * k * wave(t, period, -0.4), 0.5 * k * wave(t, slow or period * 2, 0.3), 0))
        add(p, "skull", rot=(-0.45 * k * wave(t, period, -0.9), 0.4 * k * wave(t, slow or period * 2, -0.4), 0))
        add(p, "jaw", rot=(-0.4 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
        for i, b in enumerate(self.tails):
            add(p, b, rot=(0.25 * k * (1 + 0.3 * i) * wave(t, period, -0.45 * i),
                           0.7 * k * (1 + 0.6 * i) * wave(t, slow or period * 2, -0.7 * i), 0))

    def gains(self, base=0.6, step=0.4):
        return tuple(base + step * i for i in range(self.n))

    def trail(self, p, t, fn, gain=None, delay=0.07, axis=1, loop=None):
        """follow-through down the tail: segment k takes fn(t - (k+1)*delay) * gain[k]"""
        gain = gain or self.gains()
        for k, b in enumerate(self.tails):
            u = t - delay * (k + 1)
            v = fn(u % loop if loop else max(0.0, u)) * gain[k]
            r = [0.0, 0.0, 0.0]; r[axis] = v
            add(p, b, rot=tuple(r))

    def head(self, p, pitch=0.0, yaw=0.0, roll=0.0, k=None):
        k = self.head_k if k is None else k
        add(p, "neck", rot=(pitch * k, yaw * k, roll * 0.3))
        add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * 0.7))

    # ------------------------------------------------------------ the gait with weight
    def gait(self, t, Tc, stride, duty, lift, feet, flift=None, bob=0.6, drop=0.0, lean=0.0, hd=0.0, roll=4.0, yaw=2.0,
             rock=0.0, nod=1.0, head_keep=0.75, head_lag=0.1, neck_roll=0.7, tail_yaw=4.0, tail_lag=0.1, tail_pitch=0.8,
             tail_base=0.0, weapon=0.0, jaw=0.0, pant=0.0, clear_pow=1.5, lift_pow=2.0):
        """a four-beat walk or a gallop with the weight in it. The hips drop on the side of the swinging hind leg and
        turn with it; the body falls fast after each hind footfall and rises slow; the neck rolls back against the
        body (the shoulders' counter-roll) and the heavy head nods late; the tail swings out, later and wider to
        the tip; every leg is counter-rolled and pinned on its track"""
        A = self.A
        ph = (t / Tc) % 1.0; w = 2 * math.pi * ph
        c = (1.0 + duty) / 2.0                               # the left hind leg's mid-swing
        a = 2 * math.pi * (ph - c)
        r = -roll * math.cos(a)
        y = yaw * math.sin(a)
        bp = 0.5 * nod * math.sin(2 * w - 0.5) + rock * math.sin(w - 0.4)
        d = skew_drop(2 * ph)
        p = {}
        add(p, "body", rot=(lean + bp, y, r), pos=(0, -self.drop - drop - bob * d, 0))
        dl = skew_drop(2 * ph - head_lag)
        self.head(p, hd - head_keep * (bp + lean) - 2.2 * nod * (dl - 0.5), -head_keep * y, 0)
        add(p, "neck", rot=(0, 0, -neck_roll * r))
        add(p, "skull", rot=(0.8 * nod * (skew_drop(2 * ph - head_lag - 0.08) - 0.5), 0, -0.3 * neck_roll * r))
        for i, b in enumerate(self.tails):
            g = 1.0 + 0.55 * i
            add(p, b, rot=(tail_base - lean * 0.2 + tail_pitch * math.sin(2 * w - 1.0 - 0.5 * i),
                           tail_yaw * g * math.sin(a - math.pi / 2 - 2 * math.pi * tail_lag * (i + 1)), 0))
        if weapon: self.weapon(p, weapon)
        if jaw or pant:
            add(p, "jaw", rot=(jaw - pant * max(0.0, math.sin(4 * w - 0.6)), 0, 0))
        self.counter_legs(p)
        A.lift_head(p, 1.0)
        hm, hs, ht = self.hind; fh, fs = self.fore
        flift = lift * 0.9 if flift is None else flift
        for foot, o in feet.items():
            s, kind = foot[0], foot[1]
            u = (ph + o) % 1.0
            if u < duty:
                st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0; clear = -0.05
                heel = smooth(max(0.0, (st - 0.65) / 0.35)); sw = 0.0
            else:
                sw = (u - duty) / (1 - duty); heel = 0.0
                # the swing leaves and lands at the stance's own speed (a Hermite curve): the foot carries on back a
                # little as it lifts and is drawn back before it lands, so the knee never starts or stops in a frame
                A0, A1, m = stride * duty / 2, -stride * duty / 2, stride * (1 - duty)
                s2, s3 = sw * sw, sw * sw * sw
                dz = (2 * s3 - 3 * s2 + 1) * A0 + (s3 - 2 * s2 + sw) * m + (-2 * s3 + 3 * s2) * A1 + (s3 - s2) * m
                ly = (lift if kind == "h" else flift) * math.sin(math.pi * min(1, sw * 1.1)) ** lift_pow
                # the toe clearance grows gently out of the push-off (a square root here snapped the knee shut in
                # one frame as the clearance jumped under a toe still pointing down)
                clear = -0.05 + 0.85 * math.sin(math.pi * sw) ** clear_pow
            if kind == "h":
                meta = hm * heel + hm * (1 - smooth(sw / 0.4)) * (u >= duty) - hs * math.sin(math.pi * sw)
                toe = -ht * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
                self.foot(p, s, "h", ly, dz, 0.0, meta=meta, toe=toe, clear=clear)
            else:
                # the hand leaves the ground still tipped up on its heel and only then flips (the old cycles dropped
                # the heel lift at lift-off: the hand flicked 20-30 deg in a frame)
                lifted = heel if u < duty else (1 - smooth(sw / 0.4))
                pitch = -fh * lifted - fs * math.sin(math.pi * min(1, sw * 1.15))
                self.foot(p, s, "f", ly, dz, 0.0, pitch=pitch, clear=clear)
        return p

    # ------------------------------------------------------------ stepping in place: the turn and the strafe
    DIAG = {"lf": 0.0, "rh": 0.0, "rf": 0.5, "lh": 0.5}

    def _diag_steps(self, p, ph, fore_dx, hind_dx, swing=0.4, lift=4.0, fore_dz=0.0, hind_dz=0.0):
        """the four feet in diagonal pairs: each lifts in [0, swing) and travels from -dx to +dx, then on the ground
        the body passes over it (+dx back to -dx), so the feet never slide"""
        hm, hs, ht = self.hind; fh, fs = self.fore
        for foot, o in self.DIAG.items():
            s, kind = foot[0], foot[1]
            amp = fore_dx if kind == "f" else hind_dx
            dzb = fore_dz if kind == "f" else hind_dz
            u = (ph + o) % 1.0
            if u < swing:
                sw = u / swing; arc = math.sin(math.pi * sw)
                dx = -amp * math.cos(math.pi * sw)
                if kind == "h":
                    self.foot(p, s, "h", lift * arc ** 1.2, dzb - 1.0 * arc, dx, meta=-hs * arc, toe=-ht * arc, clear=0.8 * arc ** 0.5)
                else:
                    self.foot(p, s, "f", lift * arc ** 1.2, dzb - 1.0 * arc, dx, pitch=-0.7 * fs * arc, clear=0.8 * arc ** 0.5)
            else:
                st = (u - swing) / (1 - swing)
                self.foot(p, s, kind, 0.0, dzb, amp * (1 - 2 * st))

    def turn(self, t, side, T, fore_dx=3.0, hind_dx=2.2, lift=4.0, lead_yaw=8.0, body_yaw=3.0, roll=1.6, bob=0.5,
             head_pitch=0.0, tail_yaw=2.5, weapon=0.0):
        """turning on the spot: the head leads into the turn, the shoulders follow, the tail swings out the other way
        and lags; the forefeet step toward the turn and the hind feet away from it (the body pivots about its
        middle), in diagonal pairs"""
        d = 1.0 if side == "left" else -1.0
        lead = -d
        ph = (t / T) % 1.0; w = 2 * math.pi * ph; p = {}
        add(p, "body", rot=(0.4 * math.sin(2 * w - 0.6), lead * (body_yaw + 0.8 * math.sin(w)), roll * math.sin(2 * w + 0.3)),
            pos=(0, -self.drop - bob * skew_drop(2 * ph), 0))
        self.head(p, head_pitch, lead * (lead_yaw + 1.5 * math.sin(w - 0.6)), 0)
        add(p, "neck", rot=(0, 0, -0.6 * roll * math.sin(2 * w + 0.3)))
        add(p, "skull", rot=(0.6 * math.sin(2 * w - 1.6), lead * 0.3 * lead_yaw, 0))
        for i, b in enumerate(self.tails):
            add(p, b, rot=(0.3 * (1 + 0.3 * i) * math.sin(2 * w - 0.6 * i),
                           -lead * tail_yaw * (1 + 0.5 * i) - (0.8 + 0.5 * i) * math.sin(w - 0.8 * (i + 1)), 0))
        if weapon: self.weapon(p, weapon)
        self.counter_legs(p)
        self.A.lift_head(p, 0.6)
        self._diag_steps(p, ph, d * fore_dx, -d * hind_dx, lift=lift)
        return p

    def strafe(self, t, side, T, step_dx=3.0, lift=4.0, lean=1.8, guard=0.8, look=3.0, tail_yaw=2.5, drop=1.0, extra=None):
        """sidesteps round the rival keeping the weapon on it: the feet cross the ground in diagonal pairs toward the
        travel, the body leans into it, the head turns a little back toward the rival, the tail swings out behind"""
        d = 1.0 if side == "left" else -1.0
        ph = (t / T) % 1.0; w = 2 * math.pi * ph; p = {}
        add(p, "body", rot=(-1.5 * guard + 0.4 * math.sin(2 * w - 0.5), d * 0.8 * math.sin(2 * w),
                            -d * lean + 0.9 * math.sin(2 * w + 0.4)),
            pos=(0, -self.drop - drop * guard - 0.5 * skew_drop(2 * ph), -0.8 * guard))
        if guard: self.weapon(p, guard)
        self.head(p, 0.6 * math.sin(2 * w - 1.4), d * look, 0)
        add(p, "neck", rot=(0, 0, d * 0.6 * lean))
        for i, b in enumerate(self.tails):
            add(p, b, rot=(-1.0 * guard * (0.5 + 0.2 * i), -d * tail_yaw * (1 + 0.5 * i) - (0.6 + 0.4 * i) * math.sin(2 * w - 0.7 * (i + 1)), 0))
        if extra: extra(p, t, w)
        self.counter_legs(p)
        self.A.lift_head(p, 0.6)
        self._diag_steps(p, ph, d * step_dx, d * step_dx, lift=lift, fore_dz=-1.2 * guard, hind_dz=0.6 * guard)
        return p

    def head_low(self, p):
        A = self.A
        return A.low_of(p, set(getattr(A, "LOWHEAD", None) or A.HEADB))

    def lift(self, p, clear=0.3):
        """the head kept off the ground by a CONTINUOUS lift of the neck (the species' lift_head steps 1.5 deg at a
        time, which in the fast low moves of the duel jumped up to 9 deg in a frame); 06/11, the fight set"""
        bones = set(self.A.HEADB)
        if self.A.low_of(p, bones) >= clear: return p
        lo, hi = 0.0, 40.0
        for _ in range(14):
            m = 0.5 * (lo + hi); q = dict(p); add(q, "neck", rot=(m, 0, 0))
            if self.A.low_of(q, bones) >= clear: hi = m
            else: lo = m
        add(p, "neck", rot=(hi, 0, 0))
        return p

    def keep_head(self, p, before):
        """a layer added on top of a finished pose must not take the head lower into the ground than it was"""
        floor = min(before, 0.0)
        for _ in range(20):
            if self.head_low(p) >= floor - 0.02: break
            add(p, "neck", rot=(0.5, 0, 0))
        return p

    # ------------------------------------------------------------ the species' own feet, through this IK
    def adopt(self):
        """rebind the species module's plant_h / plant_f to this IK (and the pin), so every original animation that
        plants its feet (the ones kept and wrapped) stops popping too: the engine's numeric solver, started from the
        pose's own angles, jumped between solutions in fast frames (40-60 deg a frame in the old walk and attack)"""
        A, Q = self.A, self
        # the lying blend (`lie`, which plants with clear=0.0) folds the legs past the elbow's other side, where the
        # engine's solver, seeded at rest, already bends the way the fold goes: it keeps it
        old_h, old_f = A.plant_h, A.plant_f

        def plant_h(p, s, dy=0.0, dz=0.0, meta=0.0, toe=0.0, clear=-0.05):
            if clear == 0.0: return old_h(p, s, dy, dz, meta, toe, clear)
            Q.foot(p, s, "h", dy, dz, 0.0, meta=meta, toe=toe, clear=clear)

        def plant_f(p, s, dy=0.0, dz=0.0, pitch=0.0, clear=-0.05, scap=None):
            if clear == 0.0: return old_f(p, s, dy, dz, pitch, clear) if scap is None else old_f(p, s, dy, dz, pitch, clear, scap)
            Q.ik_fore(p, s, dy, dz, pitch, clear, scap=scap is None or bool(scap))
            if Q.pin(p, s, "f") > 0.5: Q.ik_fore(p, s, dy, dz, pitch, clear, scap=False)
        A.plant_h, A.plant_f = plant_h, plant_f

