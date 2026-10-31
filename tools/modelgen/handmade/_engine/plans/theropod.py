"""Body-plan template: the big biped theropod (T. rex, Spinosaurus, Carcharodontosaurus, Giganotosaurus, Albertosaurus,
Daspletosaurus, Tarbosaurus, Carnotaurus, Majungasaurus...). The 28 poses of the approved T. rex v2 (rexanims.py),
written once against a bone CONTRACT instead of one rig, so a new species brings its cubes and only the few
animations that make it itself.

Contract (bone names): root, body, neck (+ optional neck2...), head, skull, jaw, arm_l/r, forearm_l/r,
thigh_l/r, shin_l/r, foot_l/r, toes_l/r, tail1..tailN. Extra bones (hand, sail, crest...) are free: the template
leaves them at rest and the species animates them in its own poses.

    import theropod
    T = theropod.Plan(spec, K=1.0, necks=("neck", "neck2"), tails=("tail1", ..., "tail5"), lie_drop=24)
    ANIMS = T.anims()                 # the 28 (name -> (fn, length, loop, category, when))
    ANIMS["fish"] = (my_fish, 3.6, False, "Comer", "...")   # the species' own
"""
import math
from anim2 import add, world, chain_angle, solve_leg, solve_leg2, Track, smooth, ease_out, ease_in, back_out, ground_fit
import geo

W = lambda t, T: 2 * math.pi * t / T
SIDES = (("l", 0.0), ("r", 0.5))


def tr(*keys): return Track(keys)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


class Plan:
    def __init__(self, S, K=1.0, necks=("neck",), tails=("tail1", "tail2", "tail3", "tail4"), lie_drop=28.0,
                 lie_ankle_y=4.4, walk=(1.9, 72, 0.62, 9, 1.6), run=(0.8, 128, 0.42, 16, 3.0), arms=1.0, jaw=1.0, reach=1.0):
        self.S, self.K, self.necks, self.tails = S, K, tuple(necks), tuple(tails)
        self.lie_drop, self.lie_ankle_y, self.walk_p, self.run_p, self.arm_amp = lie_drop, lie_ankle_y, walk, run, arms
        self.jaw, self.reach = jaw, reach      # jaw: how wide it opens (a long thin jaw opens less); reach: head down
        self.BALL = {s: world(S, {}, f"toes_{s}") for s in ("l", "r")}
        self.ANKLE = {s: world(S, {}, f"foot_{s}") for s in ("l", "r")}
        self.REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in ("l", "r")}
        self.LEG = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in ("l", "r")}

    # ------------------------------------------------------------ helpers
    def neck(self, p, rot):
        """a neck rotation spread over the neck bones (the T. rex has one, long necks two or three)"""
        n = len(self.necks)
        for b in self.necks: add(p, b, rot=tuple(r / n for r in rot))

    def tailk(self, k):
        """tail bone k (1-based, on the T. rex's 4-bone scale) -> list of (bone, weight) on this rig"""
        n = len(self.tails)
        if n == 4: return [(self.tails[k - 1], 1.0)]
        x = (k - 1) / 3 * (n - 1)            # spread the 4 keys over n bones
        i = int(math.floor(x)); f = x - i
        out = [(self.tails[i], 4 / n * (1 - f))]
        if f > 1e-6 and i + 1 < n: out.append((self.tails[i + 1], 4 / n * f))
        return out

    def tail_add(self, p, k, rot):
        for b, w in self.tailk(k): add(p, b, rot=tuple(r * w for r in rot))

    def leg_low(self, pose, s):
        return min(q[:, 1].min() for c, q in geo.cube_points(self.S, pose) if c["bone"] in self.LEG[s])

    def plant(self, pose, s, dy=0.0, dz=0.0, meta=0.0, toe=0.0, clear=-0.05):
        K = self.K; b = self.BALL[s]; target = (b[1] + K * dy, b[2] + K * dz)
        clear = None if clear is None else (K * clear if clear > 0 else clear)
        for _ in range(4):
            solve_leg(self.S, pose, s, target, self.REST_META[s] + meta, toe)
            if clear is None: break
            lo = self.leg_low(pose, s)
            if lo > clear - 0.02: break
            target = (target[0] + clear - lo, target[1])

    def stand(self, pose):
        for s, _ in SIDES: self.plant(pose, s)
        return pose

    def tail(self, pose, t, yaw=0.0, pitch=0.0, T=4.0, lag=0.5, amp=1.0, base_pitch=0.0):
        for k in range(1, 5):
            a = amp * (0.6 + 0.35 * k)
            self.tail_add(pose, k, (base_pitch * (0.5 + 0.25 * k) + pitch * a * math.sin(W(t, T) - lag * k),
                                    yaw * a * math.sin(W(t, T) - 0.6 - lag * k), 0))

    def arms(self, p, rot_arm=0.0, rot_fore=0.0):
        a = self.arm_amp
        for s, _ in SIDES:
            if rot_arm: add(p, f"arm_{s}", rot=(rot_arm * a, 0, 0))
            if rot_fore: add(p, f"forearm_{s}", rot=(rot_fore * a, 0, 0))

    def breathe(self, pose, t, T=2.0, amp=1.0):
        br = math.sin(W(t, T))
        add(pose, "body", rot=(0.8 * amp * br, 0, 0), pos=(0, 0.35 * amp * br * self.K, 0))
        self.neck(pose, (-0.6 * amp * br, 0, 0)); add(pose, "skull", rot=(-0.4 * amp * br, 0, 0))
        self.arms(pose, 1.5 * amp * br)
        return br

    # ------------------------------------------------------------ gaits
    def gait(self, t, T, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, sway=1.0, arms=5.0, roll=2.4, stance_clear=-0.05):
        K = self.K
        ph = (t / T) % 1.0; w = 2 * math.pi * ph; pose = {}
        add(pose, "body", rot=(lean + 1.2 * math.sin(2 * w - 0.4), 2.2 * sway * math.sin(w), roll * sway * math.sin(w + 0.35)),
            pos=(0, K * (-bob * math.cos(2 * w - 0.9) - 0.6 - drop), 0))
        self.neck(pose, (head - lean * 0.6 - 1.0 * math.sin(2 * w - 0.4) + 1.4 * math.sin(2 * w - 1.6), -1.6 * sway * math.sin(w - 0.6), -1.2 * sway * math.sin(w + 0.35)))
        add(pose, "skull", rot=(head * 0.4 - lean * 0.4 + 0.9 * math.sin(2 * w - 2.1), -0.8 * sway * math.sin(w - 1.3), -1.0 * sway * math.sin(w)))
        add(pose, "jaw", rot=(-1.0 - 1.0 * math.sin(2 * w - 2.6), 0, 0))
        for k in range(1, 5):
            self.tail_add(pose, k, (tail_up * (0.4 + 0.2 * k) + 0.8 * math.sin(2 * w - 0.9 - 0.55 * k),
                                    -(1.6 + 1.1 * k) * sway * math.sin(w - 0.5 - 0.6 * k), 0.6 * math.sin(w - 0.6 * k)))
        a = arms * self.arm_amp
        for s, o in SIDES:
            add(pose, f"arm_{s}", rot=(a * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
            add(pose, f"forearm_{s}", rot=(a * 1.2 * math.sin(w + o * 2 * math.pi - 2.6), 0, 0))
        for s, o in SIDES:
            u = (ph + o) % 1.0
            if u < duty:
                st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
                meta = 34 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0; clear = stance_clear
            else:
                sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
                dz = stride * duty / 2 - stride * duty * e
                ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
                meta = 34 * (1 - smooth(sw / 0.5)) - 18 * math.sin(math.pi * sw)
                toe = -28 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
                clear = 1.2 * math.sin(math.pi * sw) ** 0.5
            self.plant(pose, s, ly, dz - 6, meta, toe, clear)
        return pose

    def walk(self, t):
        T, st, du, li, bo = self.walk_p; return self.gait(t, T, st, du, li, bo)

    def run(self, t):
        T, st, du, li, bo = self.run_p
        # fast: between two baked frames the foot can sweep below the ground, so the stance foot is kept 0.2 px up
        return self.gait(t, T, st, du, li, bo, lean=6, drop=3, head=-4, tail_up=3, sway=0.6, arms=3, roll=1.2, stance_clear=0.2)

    def stalk(self, t):
        T, st, du, li, bo = self.walk_p
        p = self.gait(t, T * 1.47, st * 0.78, 0.74, li * 0.78, bo * 0.44, lean=3, drop=7, head=-9, tail_up=1, sway=0.5, arms=2, roll=1.0)
        add(p, "skull", rot=(0, 6 * math.sin(W(t, 5.6)), 0)); add(p, "jaw", rot=(1, 0, 0))
        return p

    def swim(self, t):
        T = 1.6; w = W(t, T); p = {}; K = self.K
        add(p, "body", rot=(-4 + 1.5 * math.sin(2 * w), 3 * math.sin(w), 4 * math.sin(w + 0.4)), pos=(0, K * 1.5 * math.sin(2 * w), 0))
        self.neck(p, (10 - 1.5 * math.sin(2 * w + 0.5), -2 * math.sin(w - 0.5), 0)); add(p, "skull", rot=(6, -1.5 * math.sin(w - 1), 0))
        self.tail(p, t, yaw=6, T=T, lag=0.7)
        for s, o in SIDES:
            f = w + o * 2 * math.pi
            add(p, f"thigh_{s}", rot=(-10 + 28 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-22 - 22 * math.cos(f), 0, 0))
            add(p, f"foot_{s}", rot=(30 + 20 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-25 * math.sin(f + 1.0), 0, 0))
            add(p, f"arm_{s}", rot=(-15, 0, 0))
        return p

    # ------------------------------------------------------------ idle family
    def idle(self, t):
        LOOK = tr((0, (0, 0)), (0.9, (0, 0)), (1.25, (4, 16), ease_out), (3.0, (4, 16)), (3.3, (-2, -10), ease_out), (3.5, (-2, -10)),
                  (5.2, (-2, -10)), (5.5, (6, 4), ease_out), (7.2, (6, 4)), (7.7, (0, 0)))
        pose = {}; IT = 8.0
        br = math.sin(2 * math.pi * t / 2.0); sh = math.sin(2 * math.pi * t / IT)
        add(pose, "body", rot=(0.8 * br, 0.8 * sh, 1.4 * sh), pos=(0, 0.35 * br * self.K, 0))
        self.neck(pose, (-0.6 * br, 0, -0.8 * sh))
        lp, ly = LOOK(t)
        self.neck(pose, (lp * 0.4, ly * 0.45, 0))
        add(pose, "skull", rot=(lp * 0.6 - 0.4 * br, ly * 0.55, -ly * 0.12))
        add(pose, "jaw", rot=(-0.8 - 0.8 * max(0, br), 0, 0))
        for k in range(1, 5):
            self.tail_add(pose, k, (0.5 * math.sin(2 * math.pi * t / 2.0 - 0.5 * k), -(0.8 + 0.7 * k) * math.sin(2 * math.pi * t / IT - 0.45 * k), 0))
        self.arms(pose, 1.5 * br, -2 * math.sin(2 * math.pi * t / 2.0 - 0.8))
        return self.stand(pose)

    def sniff(self, t):
        F = tr((0, (0, 0)), (0.5, (12, 6)), (1.6, (12, 6)), (2.0, (6, -10), ease_out), (2.4, (6, -10)), (3.0, (0, 0)))
        pose = {}; np_, ny = F(t)
        add(pose, "body", rot=(-1.5 * smooth(t / 0.5) * (t < 2.4) - 1.5 * (1 - smooth((t - 2.4) / 0.6)) * (t >= 2.4), 0, 0))
        self.neck(pose, (np_ * 0.6, ny * 0.5, 0))
        sn = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.75, 1.0, 1.25))
        add(pose, "skull", rot=(np_ * 0.6 + 2.5 * sn, ny * 0.5, -ny * 0.15))
        add(pose, "jaw", rot=(-1 - 1.5 * sn, 0, 0))
        for k in range(1, 5):
            self.tail_add(pose, k, (0.4 * k * smooth(t / 0.6) * (t < 2.4), -0.6 * k * math.sin(2 * math.pi * t / 3.0 - 0.4 * k), 0))
        return self.stand(pose)

    def look_back(self, t):
        p = {}; self.breathe(p, t)
        k = float(tr((0, 0), (0.5, 0), (0.85, 1, ease_out), (2.2, 1), (2.6, 0.3), (3.2, 0))(t))
        add(p, "body", rot=(0, 9 * k, -2 * k)); self.neck(p, (4 * k, 34 * k, 0)); add(p, "skull", rot=(2 * k, 26 * k, -8 * k))
        self.tail(p, t, yaw=1.0, T=4, amp=0.8)
        for i in range(1, 5): self.tail_add(p, i, (0, 5 * k * (0.5 + 0.3 * i), 0))
        return self.stand(p)

    def shake(self, t):
        p = {}
        env = math.exp(-((t - 0.9) / 0.45) ** 2)
        for bone, a, d in (("skull", 14, 0.0), ("neck", 10, 0.05), ("body", 4, 0.12)):
            r = (0, a * 0.4 * env * math.sin(2 * math.pi * 5.5 * (t - d)), a * env * math.sin(2 * math.pi * 5.5 * (t - d)))
            self.neck(p, r) if bone == "neck" else add(p, bone, rot=r)
        for k in range(1, 5):
            d = 0.12 + 0.06 * k
            self.tail_add(p, k, (0, (2 + 2 * k) * math.exp(-((t - 0.9 - d) / 0.45) ** 2) * math.sin(2 * math.pi * 5.5 * (t - d)), 0))
        add(p, "jaw", rot=(-6 * env, 0, 0)); self.neck(p, (6 * window(t, 0.3, 1.5), 0, 0))
        return self.stand(p)

    def yawn(self, t):
        p = {}; self.breathe(p, t, amp=0.6)
        up = float(tr((0, 0), (0.6, 1), (1.9, 1), (2.3, 0.2), (3.0, 0))(t))
        self.neck(p, (14 * up, 0, 0)); add(p, "skull", rot=(10 * up, 0, -4 * up))
        jaw = float(tr((0, 0), (0.4, -6), (1.3, -52, ease_out), (1.8, -50), (2.0, -2, ease_in), (3.0, 0))(t))
        add(p, "jaw", rot=(jaw + 1.0 * math.sin(2 * math.pi * 7 * t) * window(t, 1.2, 1.8, 0.1), 0, 0))
        add(p, "skull", rot=(0, 0, 5 * math.sin(2 * math.pi * 4 * t) * window(t, 2.1, 2.6, 0.12)))
        self.arms(p, -10 * up, 14 * up)
        self.tail(p, t, yaw=0.6, T=4)
        return self.stand(p)

    def stretch(self, t):
        p = {}; K = self.K
        k = float(tr((0, 0), (0.8, 1), (1.8, 1), (2.4, -0.4), (3.0, -0.4), (3.6, 0))(t))
        a = max(0, k); b = max(0, -k) / 0.4
        add(p, "body", rot=(-7 * a + 4 * b, 0, 0), pos=(0, -2 * a * K, 3 * a * K))
        self.neck(p, (-10 * a + 10 * b, 0, 0)); add(p, "skull", rot=(-8 * a + 6 * b, 0, 0))
        for i in range(1, 5): self.tail_add(p, i, (6 * a * (0.5 + 0.2 * i) - 3 * b, 0, 0))
        add(p, "jaw", rot=(-10 * b, 0, 0))
        self.arms(p, -25 * a, 30 * a)
        return self.stand(p)

    # ------------------------------------------------------------ voice
    def roar(self, t):
        RB = tr((0, (0, 0)), (0.3, (6, 0)), (0.75, (-9, 0), ease_out), (1.0, (-4, 0)), (2.6, (-4, 0)), (3.4, (0, 0), back_out))
        RD = tr((0, 0), (0.3, -3.0), (0.75, 1.0, ease_out), (1.0, -1.0), (2.6, -1.0), (3.4, 0))
        RN = tr((0, (0, 0, 0)), (0.3, (-8, 0, 0)), (0.75, (18, 0, 0), ease_out), (1.0, (12, 0, 0), ease_out), (1.6, (10, 14, 0)),
                (2.2, (10, -14, 0)), (2.6, (2, 0, 0)), (3.4, (0, 0, 0), back_out))
        RS = tr((0, (0, 0, 0)), (0.3, (-10, 0, 0)), (0.75, (14, 0, 0), ease_out), (1.0, (2, 0, 0), ease_out), (1.6, (2, 10, -8)),
                (2.2, (2, -10, 8)), (2.6, (-2, 0, 0)), (3.4, (0, 0, 0), back_out))
        RJ = tr((0, 0), (0.3, -2), (0.75, -10), (1.0, -42, ease_out), (2.5, -38), (2.75, -2, ease_in), (3.4, 0))
        RT = tr((0, 0), (0.3, -2), (0.75, 7, ease_out), (2.6, 5), (3.4, 0, back_out))
        pose = {}
        bp, by = RB(t)
        add(pose, "body", rot=(bp, by, 0), pos=(0, float(RD(t)) * self.K, 0))
        self.neck(pose, tuple(RN(t)))
        sk = RS(t); vib = 1.2 * math.sin(2 * math.pi * t * 9) * (1.0 <= t <= 2.5)
        add(pose, "skull", rot=(sk[0] + vib, sk[1], sk[2])); add(pose, "jaw", rot=(float(RJ(t)) - vib, 0, 0))
        for k in range(1, 5):
            self.tail_add(pose, k, (float(RT(max(0, t - 0.08 * k))) * (0.6 + 0.2 * k) * 0.5, 0, 0))
        self.arms(pose, -8 * smooth(t / 0.75) * (t < 2.6) - 8 * (1 - smooth((t - 2.6) / 0.8)) * (t >= 2.6))
        return self.stand(pose)

    def call(self, t):
        p = {}; k = float(tr((0, 0), (0.5, 1), (2.0, 1), (2.6, 0))(t))
        hum = 0.9 * math.sin(2 * math.pi * 11 * t) * window(t, 0.5, 2.0, 0.15)
        add(p, "body", rot=(3 * k + hum * 0.5, 0, 0), pos=(0, 1.0 * k * self.K, 0))
        self.neck(p, (-10 * k + hum, 0, 0)); add(p, "skull", rot=(-14 * k - hum, 0, 0)); add(p, "jaw", rot=(1, 0, 0))
        self.tail(p, t, yaw=0.5, T=3, base_pitch=-2 * k)
        return self.stand(p)

    def threat(self, t):
        p = {}; K = self.K
        k = float(tr((0, 0), (0.4, 1), (2.0, 1), (2.4, 0))(t))
        stomp = float(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (1.05, 0, ease_in), (2.4, 0))(t))
        jolt = math.exp(-((t - 1.08) / 0.07) ** 2)
        add(p, "body", rot=(5 * k + 2 * jolt, 0, -2 * stomp), pos=(0, K * (-3 * k - 1.2 * jolt), 0))
        self.neck(p, (-8 * k, 0, 0)); add(p, "skull", rot=(-4 * k + 3 * jolt, 0, 0))
        add(p, "jaw", rot=(-12 * k - 6 * jolt, 0, 0))
        self.tail(p, t, yaw=2.5 * k, T=0.9, base_pitch=3 * k)
        self.plant(p, "r"); self.plant(p, "l", 13 * stomp, -6 * stomp, 0, -10 * stomp, clear=-0.05)
        return p

    # ------------------------------------------------------------ combat
    def attack(self, t):
        BN = tr((0, (0, 0, 0)), (0.3, (10, 0, 0), ease_out), (0.45, (-16, 0, 0), ease_in), (0.6, (-12, 0, 0)), (0.8, (-12, 16, 0)), (0.98, (-12, -16, 0)),
                (1.16, (-12, 14, 0)), (1.32, (-12, -10, 0)), (1.5, (-8, 0, 0)), (2.0, (0, 0, 0), back_out))
        BS = tr((0, (0, 0, 0)), (0.3, (8, 0, 0), ease_out), (0.45, (-10, 0, 0), ease_in), (0.6, (-6, 0, 0)), (0.8, (-6, 8, -10)), (0.98, (-6, -8, 10)),
                (1.16, (-6, 7, -9)), (1.32, (-6, -5, 6)), (1.5, (-4, 0, 0)), (2.0, (0, 0, 0), back_out))
        BJ = tr((0, 0), (0.3, -36, ease_out), (0.45, -40), (0.52, -4, ease_in), (1.5, -4), (1.7, -14), (2.0, 0))
        BB = tr((0, (0, 0)), (0.3, (-3, 0)), (0.45, (6, 0), ease_in), (0.8, (5, 3)), (0.98, (5, -3)), (1.16, (5, 3)), (1.5, (3, 0)), (2.0, (0, 0), back_out))
        BP = tr((0, 0), (0.3, 2), (0.45, -6, ease_in), (1.5, -5), (2.0, 0))
        pose = {}; K = self.K
        bp, by = BB(t)
        add(pose, "body", rot=(bp, by, -by * 0.5), pos=(0, K * (-1.5 * smooth(t / 0.45) * (t < 1.5) - 1.5 * (1 - smooth((t - 1.5) / 0.5)) * (t >= 1.5)), K * float(BP(t))))
        self.neck(pose, tuple(BN(t))); add(pose, "skull", rot=tuple(BS(t))); add(pose, "jaw", rot=(float(BJ(t)), 0, 0))
        for k in range(1, 5):
            lag = max(0, t - 0.07 * k)
            self.tail_add(pose, k, (-0.4 * BB(lag)[0], -0.9 * k * BB(lag)[1], 0))
        return self.stand(pose)

    def attack_quick(self, t):
        p = {}; K = self.K
        n = tr((0, (0, 0)), (0.15, (8, 4), ease_out), (0.27, (-14, 0), ease_in), (0.5, (-10, 0)), (0.9, (0, 0)))(t)
        j = float(tr((0, 0), (0.15, -32, ease_out), (0.27, -3, ease_in), (0.9, 0))(t))
        e = smooth((t - 0.15) / 0.12) * (1 - smooth((t - 0.5) / 0.4))
        add(p, "body", rot=(3 * e, 0, 0), pos=(0, 0, -4 * e * K))
        self.neck(p, (n[0], n[1], 0)); add(p, "skull", rot=(n[0] * 0.6, n[1] * 0.5, 0)); add(p, "jaw", rot=(j, 0, 0))
        self.tail(p, t, yaw=1.5, T=0.9, lag=0.4)
        return self.stand(p)

    def hurt(self, t):
        p = {}; K = self.K; e = math.exp(-(t / 0.16)) * smooth(t / 0.04)
        add(p, "body", rot=(-6 * e, 6 * e, -4 * e), pos=(0, -1.5 * e * K, 3 * e * K))
        self.neck(p, (12 * e, -8 * e, 0)); add(p, "skull", rot=(8 * e, -6 * e, 6 * e)); add(p, "jaw", rot=(-22 * e, 0, 0))
        for k in range(1, 5):
            d = 0.04 * k; ek = math.exp(-max(0, t - d) / 0.2) * smooth((t - d) / 0.05)
            self.tail_add(p, k, (4 * ek, -6 * ek * k * 0.6, 0))
        return self.stand(p)

    # ------------------------------------------------------------ eating
    def eat(self, t):
        p = {}; K = self.K
        down = float(tr((0, 0), (0.6, 1), (1.4, 1), (1.7, 0.45, ease_out), (2.6, 0.45), (3.2, 0))(t))
        twist = float(tr((0, 0), (1.35, 0), (1.55, 1, ease_out), (1.9, -0.4), (2.2, 0))(t))
        add(p, "body", rot=(-8 * down, 0, 0), pos=(0, -3 * down * K, 0))
        r = self.reach
        self.neck(p, (-34 * down * r, 16 * twist, 0)); add(p, "skull", rot=(-20 * down * r, 8 * twist, -12 * twist))
        j = float(tr((0, 0), (0.6, -30), (0.9, -32), (1.05, -3, ease_in), (1.9, -3), (2.1, -12), (2.3, -2), (2.5, -12), (2.7, -2), (3.2, 0))(t))
        add(p, "jaw", rot=(j, 0, 0))
        add(p, "skull", rot=(8 * math.exp(-((t - 2.75) / 0.1) ** 2), 0, 0))
        self.tail(p, t, yaw=0.8, T=3.2, base_pitch=6 * down)
        return self.stand(p)

    def drink(self, t):
        p = {}; K = self.K
        down = float(tr((0, 0), (0.9, 1), (3.0, 1), (3.7, 0), (4.0, 0))(t))
        add(p, "body", rot=(-12 * down, 0, 0), pos=(0, -5 * down * K, 2 * down * K))
        self.neck(p, (-31 * down * self.reach, 0, 0)); add(p, "skull", rot=(-10 * down * self.reach, 0, 0))
        lap = window(t, 1.1, 2.8, 0.15)
        add(p, "jaw", rot=(-6 * lap * (0.5 + 0.5 * math.sin(2 * math.pi * 2.5 * t)), 0, 0))
        add(p, "skull", rot=(3 * lap * math.sin(2 * math.pi * 2.5 * t - 0.6), 0, 0))
        add(p, "skull", rot=(10 * math.exp(-((t - 3.75) / 0.1) ** 2), 0, 0))
        self.tail(p, t, yaw=0.6, T=4, base_pitch=8 * down)
        self.arms(p, 10 * down)
        return self.stand(p)

    # ------------------------------------------------------------ resting
    def lie(self, p, k, head_down=0.0):
        """k = 0 standing .. 1 lying on the belly, metatarsi flat with the ankle behind the toes"""
        K = self.K
        add(p, "body", rot=(2 * k, 0, 0), pos=(0, -self.lie_drop * k, 0))
        self.neck(p, (-6 * k - 30 * head_down * self.reach, 0, 0)); add(p, "skull", rot=(4 * k - 4 * head_down, 0, 0))
        for i in range(1, 5): self.tail_add(p, i, (-7 * k * (0.3 + 0.25 * i) + 4 * k * (i == 1), 0, 0))
        self.arms(p, -15 * k, 20 * k)
        for s, _ in SIDES:
            b = self.BALL[s]; a = self.ANKLE[s]
            ay = a[1] + (self.lie_ankle_y - a[1]) * k; az = a[2] + 9 * K * k
            solve_leg2(self.S, p, s, (b[1] + 0.5 * k, b[2] - 6 * K * k), (ay, az), w_ankle=0.8 * k + 0.05)
        return p

    def sit(self, t):
        p = {}; br = math.sin(W(t, 3.0))
        self.lie(p, 1.0); add(p, "body", rot=(0.8 * br, 0, 0))
        self.neck(p, (-0.6 * br + 2 * math.sin(W(t, 6.0)), 3 * math.sin(W(t, 6.0) - 1), 0))
        self.tail(p, t, yaw=0.5, T=6)
        return ground_fit(self.S, p)

    def sleep(self, t):
        p = {}; br = math.sin(W(t, 4.0))
        self.lie(p, 1.0, head_down=1.0)
        add(p, "body", rot=(1.0 * br, 0, 0), pos=(0, 0.4 * br * self.K, 0)); self.neck(p, (-0.8 * br, 0, 0))
        add(p, "jaw", rot=(-1.5 * max(0, br), 0, 0))
        return ground_fit(self.S, p)

    def wake_sleep(self, t):
        p = {}
        hd = float(tr((0, 1), (0.6, 0, ease_out), (2.4, 0))(t))
        up = float(tr((0, 1), (0.8, 1), (1.7, 0, back_out), (2.4, 0))(t))
        self.lie(p, up, head_down=hd)
        env = math.exp(-((t - 2.0) / 0.18) ** 2)
        add(p, "skull", rot=(0, 4 * env * math.sin(2 * math.pi * 6 * t), 10 * env * math.sin(2 * math.pi * 6 * t)))
        return ground_fit(self.S, p)

    def _side(self, p, side):
        self.neck(p, (-4 * side, 0, -14 * side)); add(p, "skull", rot=(-6 * side, 0, -10 * side)); add(p, "jaw", rot=(-9 * side, 0, 0))

    def wake(self, t):
        p = {}
        roll = float(tr((0, 80), (0.3, 80), (0.9, 0, ease_out), (3.0, 0))(t))
        k = float(tr((0, 0.8), (0.9, 1.0), (1.5, 1.0), (2.4, 0, back_out), (3.0, 0))(t))
        hd = float(tr((0, 0.6), (0.9, 0.4), (1.3, 0, ease_out), (3.0, 0))(t))
        self.lie(p, k, head_down=hd)
        add(p, "root", rot=(0, 0, roll)); self._side(p, roll / 80.0)
        env = math.exp(-((t - 1.2) / 0.2) ** 2)
        add(p, "skull", rot=(0, 5 * env * math.sin(2 * math.pi * 6 * t), 12 * env * math.sin(2 * math.pi * 6 * t)))
        return ground_fit(self.S, p)

    def knocked_out(self, t):
        p = {}; br = math.sin(W(t, 4.0))
        self.lie(p, 0.8); add(p, "root", rot=(0, 0, 80))
        add(p, "body", rot=(0.8 * br, 0, 0)); self._side(p, 1.0); add(p, "jaw", rot=(-1.5 * br, 0, 0))
        for i in range(1, 5): self.tail_add(p, i, (0, 0, -3))
        self.arms(p, 20)
        add(p, "thigh_r", rot=(18, 0, 0)); add(p, "shin_r", rot=(10, 0, 0))
        return ground_fit(self.S, p)

    def death(self, t):
        p = {}
        g = float(tr((0, 0), (0.5, 0.15), (1.1, 0.8, ease_in), (3.0, 0.8))(t))
        rl = float(tr((0, 0), (0.7, -6), (1.15, 84, ease_in), (1.3, 77), (1.45, 81), (3.0, 80))(t))
        self.lie(p, g); add(p, "root", rot=(0, 0, rl))
        sway = math.sin(2 * math.pi * 1.2 * t) * (1 - smooth((t - 0.8) / 0.3))
        s2 = smooth((t - 1.1) / 0.3)
        add(p, "body", rot=(0, 4 * sway, 0)); self.neck(p, (6 * window(t, 0, 0.9) - 6 * s2, -6 * sway, -14 * s2))
        add(p, "skull", rot=(-6 * s2, 0, -10 * s2))
        add(p, "jaw", rot=(-18 * window(t, 0.2, 1.0) - 9 * smooth((t - 1.2) / 0.4), 0, 0))
        self.arms(p, 20 * smooth((t - 1.0) / 0.3))
        return ground_fit(self.S, p)

    # ------------------------------------------------------------ tamed
    def beg(self, t):
        T = 2.0; w = W(t, T); p = {}
        add(p, "body", rot=(-3, 3 * math.sin(w), 2 * math.sin(w)), pos=(0, 0.6 * abs(math.sin(w)) * self.K, 0))
        self.neck(p, (12 + 3 * math.sin(2 * w), 4 * math.sin(w - 0.5), 0)); add(p, "skull", rot=(10 + 3 * math.sin(2 * w - 0.6), 0, 8 * math.sin(w - 1)))
        add(p, "jaw", rot=(-6 * max(0, math.sin(2 * w)), 0, 0))
        self.tail(p, t, yaw=4, T=T / 2, lag=0.5)
        for s, o in SIDES:
            f = w + o * 2 * math.pi
            self.plant(p, s, 5 * max(0, math.sin(f)) ** 2, 0, 0, -6 * max(0, math.sin(f)), clear=-0.05)
        return p

    def tame(self, t):
        p = {}
        k = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.4, 0))(t))
        toss = math.exp(-((t - 0.5) / 0.15) ** 2)
        add(p, "body", rot=(-4 * k, 0, 0), pos=(0, 1.0 * toss * self.K, 0))
        self.neck(p, (16 * k + 8 * toss, 0, 0)); add(p, "skull", rot=(12 * k, 0, 10 * math.sin(2 * math.pi * 1.5 * t) * k))
        hum = 0.8 * math.sin(2 * math.pi * 11 * t) * window(t, 0.8, 1.6, 0.12)
        add(p, "jaw", rot=(-16 * toss - 4 * k + hum, 0, 0))
        self.tail(p, t, yaw=6 * k, T=0.8, lag=0.5)
        return self.stand(p)

    # ------------------------------------------------------------ the set
    def scaled(self, fn):
        """the jaw opening scaled for this species (the poses are written for the T. rex's jaw)"""
        if self.jaw == 1.0: return fn
        def g(t):
            p = fn(t)
            if "jaw" in p:
                e = p["jaw"]; p["jaw"] = ([e[0][0] * self.jaw, e[0][1], e[0][2]], e[1]) + tuple(e[2:])
            return p
        return g

    def anims(self):
        """name: (fn, length, loop, category, when it plays) -- the T. rex's set minus its own (roar_loud, stomp)"""
        return {n: (self.scaled(v[0]),) + v[1:] for n, v in self._anims().items()}

    def _anims(self):
        return {
            "idle": (self.idle, 8.0, True, "Parado", "base, sempre que está parado"),
            "sniff": (self.sniff, 3.0, False, "Parado", "gesto sorteado parado"),
            "look_back": (self.look_back, 3.2, False, "Parado", "gesto sorteado parado"),
            "shake": (self.shake, 2.0, False, "Parado", "gesto sorteado parado; ao sair da água"),
            "yawn": (self.yawn, 3.0, False, "Parado", "gesto sorteado parado, mais à noite"),
            "stretch": (self.stretch, 3.6, False, "Parado", "gesto sorteado parado; depois de acordar"),
            "walk": (self.walk, self.walk_p[0], True, "Movimento", "andando"),
            "run": (self.run, self.run_p[0], True, "Movimento", "correndo, caçando ou fugindo"),
            "stalk": (self.stalk, self.walk_p[0] * 1.47, True, "Movimento", "chegando perto da presa antes do ataque"),
            "swim": (self.swim, 1.6, True, "Movimento", "dentro da água"),
            "roar": (self.roar, 3.4, False, "Voz", "ao ver o alvo; domado, sob comando"),
            "call": (self.call, 2.6, False, "Voz", "ronco grave de vez em quando, chamando outros"),
            "threat": (self.threat, 2.4, False, "Voz", "aviso antes de atacar quem chega perto"),
            "attack": (self.attack, 2.0, False, "Combate", "mordida forte e sacudida"),
            "attack_quick": (self.attack_quick, 0.9, False, "Combate", "mordida rápida, alternando com a forte"),
            "hurt": (self.hurt, 0.6, False, "Combate", "ao levar dano"),
            "death": (self.death, 3.0, False, "Combate", "ao morrer"),
            "eat": (self.eat, 3.2, False, "Comer", "comendo carne ou carcaça"),
            "drink": (self.drink, 4.0, False, "Comer", "bebendo na beira da água"),
            "sit": (self.sit, 6.0, True, "Descanso", "sentado (domado) ou descansando"),
            "sleep": (self.sleep, 8.0, True, "Descanso", "dormindo"),
            "wake": (self.wake, 3.0, False, "Descanso", "ao acordar do nocaute (o jogo já chama)"),
            "wake_sleep": (self.wake_sleep, 2.4, False, "Descanso", "ao acordar de um sono normal"),
            "knocked_out": (self.knocked_out, 4.0, True, "Descanso", "nocauteado (domesticação)"),
            "beg": (self.beg, 2.0, True, "Domado", "pedindo comida ao dono"),
            "tame": (self.tame, 2.4, False, "Domado", "no momento em que é domesticado"),
        }


STANDING = ("idle", "sniff", "look_back", "shake", "yawn", "stretch", "roar", "call", "attack", "attack_quick", "hurt", "eat", "drink", "tame")
