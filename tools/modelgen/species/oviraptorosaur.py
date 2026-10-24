"""
Oviraptorosaur rig (Oviraptor, Citipati; later Anzu, Gigantoraptor...): the small theropod rig with a toothless,
short and deep parrot beak, a casque on the skull, long arms carrying big wing feathers, a long neck and a short
tail ending in a wide feather fan. Two extra animations shared by the family:

  display : rears up, spreads both wings and fans the tail, bobbing the head (threat / courtship)
  brood   : the sitting pose with the wings spread low to the sides, covering a clutch (Citipati on its nest)

Spec keys on top of smalltheropod's P:
  casque : (x0, y0, z0, x1, y1, z1[, bone]) relative to the head pivot, tagged "casque" (flat palette colour)
  brood  : dict(drop=, arms=) overrides for the brooding pose
"""
from smalltheropod import build_small
from rig import track, keys, sit_tracks, ground_drop


def build_ovi(ident, P):
    P = dict(P)
    P.setdefault("teeth", False)
    P.setdefault("beak", True)
    P.setdefault("herbivore", True)      # the graze animation: it pecks at the ground like the ornithomimids
    P.setdefault("sickle", False)
    casque = P.pop("casque", None)
    brood = P.pop("brood", {})
    head_extra = list(P.get("head_extra", []))
    if casque:
        head_extra.append(dict(box=tuple(casque[:6]), tag="casque", bone=casque[6] if len(casque) > 6 else "skull", name="casque"))
    P["head_extra"] = head_extra
    m = build_small(ident, P)

    # display: rear up, wings out, tail fan up, head bobbing
    m.anim("display", 1.8, False, {
        "body": track(rot=keys([(0, 0, 0, 0), (0.4, -10, 0, 0), (1.4, -10, 0, 0), (1.8, 0, 0, 0)])),
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.4, 12, 0, 0), (1.4, 12, 0, 0), (1.8, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.4, 10, 0, 0), (0.7, -8, 0, 0), (1.0, 10, 0, 0), (1.3, -8, 0, 0), (1.8, 0, 0, 0)])),
        "arm_l": track(rot=keys([(0, 0, 0, 0), (0.4, -70, 0, -55), (1.4, -70, 0, -55), (1.8, 0, 0, 0)])),
        "arm_r": track(rot=keys([(0, 0, 0, 0), (0.4, -70, 0, 55), (1.4, -70, 0, 55), (1.8, 0, 0, 0)])),
        "tail1": track(rot=keys([(0, 0, 0, 0), (0.4, 25, 0, 0), (1.4, 25, 0, 0), (1.8, 0, 0, 0)])),
        "tail2": track(rot=keys([(0, 0, 0, 0), (0.4, 15, 0, 0), (1.4, 15, 0, 0), (1.8, 0, 0, 0)])),
    })

    # brood: the sitting pose with the wings spread low over the clutch
    st = P.get("sit", {})
    drop = brood.get("drop", st.get("drop", P["hip"][0] * 0.45))
    arms = brood.get("arms", (-20, 0, -70))
    joints = {}
    for side, sx in (("l", 1), ("r", -1)):
        joints["@thigh_" + side] = (st.get("thigh", 55), 0, 0)
        joints["shin_" + side] = (st.get("shin", -100), 0, 0)
        joints["foot_" + side] = (st.get("foot", 55), 0, 0)
        joints["toes_" + side] = (st.get("toes", -10), 0, 0)
        joints["arm_" + side] = (arms[0], arms[1] * sx, arms[2] * sx)
    joints["tail1"] = (st.get("tail", 8), 0, 0)
    joints["tail2"] = (4, 0, 0)
    joints["neck1"] = (st.get("neck", -10), 0, 0)
    joints["skull"] = (6, 0, 0)
    drop = ground_drop(m, sit_tracks(4.0, drop, joints), drop)
    m.anim("brood", 4.0, True, sit_tracks(4.0, drop, joints, breathe=0.35))
    return m
