"""Generates the boilerplate species classes (one file per dinosaur).
Behaviour that is shared lives in DinosaurEntity / HerbivoreDinosaur / PredatorDinosaur; here each species only
sets numbers, food, sounds and a few overrides. Re-run after editing SPECIES:  python3 gen_species.py
"""
import os
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "common", "src", "main", "java", "com", "primalera", "entity")

SPECIES = [
 # id, Class, base, doc, attrs, food, sounds(ambient,hurt,death,pitch,volume,interval), extras(dict)
 dict(id="tyrannosaurus", cls="Tyrannosaurus", base="PredatorDinosaur",
      doc="Tyrannosaurus rex - apex predator. Hunts players and big animals, roars when it locks onto a target. Rideable when tamed (raised from an egg or a baby).",
      attrs=dict(MAX_HEALTH=160, MOVEMENT_SPEED=0.24, ATTACK_DAMAGE=16, ATTACK_KNOCKBACK=1.5, ARMOR=6, KNOCKBACK_RESISTANCE=0.9, FOLLOW_RANGE=32),
      food="Items.BEEF, Items.PORKCHOP, Items.MUTTON",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.6, 2.0, 240), step=("RAVAGER_STEP", 0.9, 0.6),
      xp=40, step_height=1.5, cull=3.5, head=(35, 25), rideable=True, ride_offset=2.1, ride_speed=1.1,
      prey="!(e instanceof Tyrannosaurus) && !(e instanceof Compsognathus) && !(e instanceof Brachiosaurus) && !e.isBaby()",
      roar=True, prey_interval=200),
 dict(id="spinosaurus", cls="Spinosaurus", base="PredatorDinosaur",
      doc="Spinosaurus aegyptiacus - huge river predator with a sail. Lives by rivers and swamps, hunts fish, swims well and does not drown.",
      attrs=dict(MAX_HEALTH=140, MOVEMENT_SPEED=0.23, ATTACK_DAMAGE=14, ATTACK_KNOCKBACK=1.0, ARMOR=4, KNOCKBACK_RESISTANCE=0.85, FOLLOW_RANGE=32),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.75, 2.0, 260), step=("RAVAGER_STEP", 0.8, 0.7),
      xp=35, step_height=1.5, cull=3.5, head=(35, 25),
      prey="!(e instanceof DinosaurEntity) && e.isInWaterOrBubble()", roar=True, prey_interval=160, fish=True),
 dict(id="dilophosaurus", cls="Dilophosaurus", base="PredatorDinosaur",
      doc="Dilophosaurus wetherilli - mid-sized Jurassic predator with a pair of thin head crests. Flashes its crests before attacking.",
      attrs=dict(MAX_HEALTH=40, MOVEMENT_SPEED=0.30, ATTACK_DAMAGE=7, FOLLOW_RANGE=24, ARMOR=2),
      food="Items.CHICKEN, Items.RABBIT, Items.MUTTON, Items.PORKCHOP",
      sounds=("HOGLIN_AMBIENT", "HOGLIN_HURT", "HOGLIN_DEATH", 1.25, 1.2, 220),
      xp=12, step_height=1.0, cull=1.5, head=(45, 30),
      prey="e.getBbWidth() < 1.0F && !(e instanceof DinosaurEntity)", display=True, prey_interval=100),
 dict(id="velociraptor", cls="Velociraptor", base="PredatorDinosaur",
      doc="Velociraptor mongoliensis - fast feathered pack hunter. When one raptor picks a target, the rest of the pack nearby joins in. Leaps at its prey and avoids T. rex.",
      attrs=dict(MAX_HEALTH=24, MOVEMENT_SPEED=0.34, ATTACK_DAMAGE=5, FOLLOW_RANGE=24),
      food="Items.CHICKEN, Items.RABBIT, Items.MUTTON, Items.BEEF, Items.PORKCHOP",
      sounds=("FOX_SCREECH", "FOX_HURT", "FOX_DEATH", 0.8, 1.0, 200),
      xp=8, cull=1.0, run=0.03, prey="e.getBbWidth() < 1.0F && !(e instanceof Velociraptor)", prey_interval=80, pack=True, leap=True),
 dict(id="compsognathus", cls="Compsognathus", base="PredatorDinosaur",
      doc="Compsognathus longipes - tiny skittish scavenger living in groups. Avoids players but the group swarms whoever hurts one of them. Can be tamed with fish, like a cat.",
      attrs=dict(MAX_HEALTH=6, MOVEMENT_SPEED=0.32, ATTACK_DAMAGE=1.5),
      food="Items.CHICKEN, Items.COD, Items.SALMON",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 1.2, 1.0, 120),
      xp=2, cull=0.6, run=0.03, prey="false", hunts_players=False, feeding_tame=True, skittish=True),
 dict(id="triceratops", cls="Triceratops", base="HerbivoreDinosaur",
      doc="Triceratops horridus - armoured herd herbivore that charges with its horns. Rideable when tamed.",
      attrs=dict(MAX_HEALTH=110, MOVEMENT_SPEED=0.22, ATTACK_DAMAGE=11, ATTACK_KNOCKBACK=2.5, ARMOR=10, KNOCKBACK_RESISTANCE=0.85, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.LARGE_FERN",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 1.25, 1.0, 300), step=("RAVAGER_STEP", 0.6, 0.8),
      xp=20, rideable=True, ride_offset=1.55, ride_speed=1.05),
 dict(id="stegosaurus", cls="Stegosaurus", base="HerbivoreDinosaur",
      doc="Stegosaurus stenops - slow herbivore that defends itself with the spiked tail (thagomizer).",
      attrs=dict(MAX_HEALTH=90, MOVEMENT_SPEED=0.20, ATTACK_DAMAGE=10, ATTACK_KNOCKBACK=1.2, ARMOR=8, KNOCKBACK_RESISTANCE=0.8, FOLLOW_RANGE=20),
      food="Items.FERN, Items.LARGE_FERN, Items.MELON_SLICE, Items.WHEAT",
      sounds=("COW_AMBIENT", "COW_HURT", "COW_DEATH", 0.55, 1.5, 320), step=("RAVAGER_STEP", 0.5, 1.0), xp=18),
 dict(id="ankylosaurus", cls="Ankylosaurus", base="HerbivoreDinosaur",
      doc="Ankylosaurus magniventris - living tank covered in bony armour, swings a heavy tail club when attacked. Drops its tail club.",
      attrs=dict(MAX_HEALTH=100, MOVEMENT_SPEED=0.17, ATTACK_DAMAGE=12, ATTACK_KNOCKBACK=2.0, ARMOR=16, ARMOR_TOUGHNESS=4, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food="Items.FERN, Items.LARGE_FERN, Items.SWEET_BERRIES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.7, 1.2, 300), step=("RAVAGER_STEP", 0.5, 1.1), xp=20),
 dict(id="brachiosaurus", cls="Brachiosaurus", base="HerbivoreDinosaur",
      doc="Brachiosaurus altithorax - gigantic long-necked browser, eats leaves. Peaceful unless hurt. Rideable when tamed - the tallest mount in the game.",
      attrs=dict(MAX_HEALTH=300, MOVEMENT_SPEED=0.18, ATTACK_DAMAGE=18, ATTACK_KNOCKBACK=2.0, ARMOR=8, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.45, 3.0, 360), step=("RAVAGER_STEP", 1.2, 0.5),
      xp=50, step_height=1.6, cull=5.0, head=(25, 30), rideable=True, ride_offset=2.7, ride_forward=0.8, ride_speed=1.0),
 dict(id="parasaurolophus", cls="Parasaurolophus", base="HerbivoreDinosaur",
      doc="Parasaurolophus walkeri - duck-billed herbivore with a long hollow crest it uses to call. Flees from danger with the herd. Rideable when tamed.",
      attrs=dict(MAX_HEALTH=60, MOVEMENT_SPEED=0.27, ATTACK_DAMAGE=4, ARMOR=2, KNOCKBACK_RESISTANCE=0.3, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.SWEET_BERRIES",
      sounds=("CAMEL_AMBIENT", "CAMEL_HURT", "CAMEL_DEATH", 0.7, 1.6, 260), xp=12,
      fights=False, rideable=True, ride_offset=1.6, ride_speed=1.15, call=True),
 dict(id="pachycephalosaurus", cls="Pachycephalosaurus", base="HerbivoreDinosaur",
      doc="Pachycephalosaurus wyomingensis - bipedal herbivore with a thick bony dome. Headbutts hard (huge knockback) when provoked.",
      attrs=dict(MAX_HEALTH=40, MOVEMENT_SPEED=0.28, ATTACK_DAMAGE=8, ATTACK_KNOCKBACK=3.0, ARMOR=4, KNOCKBACK_RESISTANCE=0.4, FOLLOW_RANGE=16),
      food="Items.SWEET_BERRIES, Items.GLOW_BERRIES, Items.APPLE",
      sounds=("GOAT_AMBIENT", "GOAT_HURT", "GOAT_DEATH", 0.7, 1.0, 240), xp=10, cull=1.2, run=0.02),
 dict(id="gallimimus", cls="Gallimimus", base="HerbivoreDinosaur",
      doc="Gallimimus bullatus - ostrich-like ornithomimid, the fastest dinosaur. Flocks flee from players and predators. A very fast mount when tamed.",
      attrs=dict(MAX_HEALTH=30, MOVEMENT_SPEED=0.36, ATTACK_DAMAGE=3, FOLLOW_RANGE=20),
      food="Items.WHEAT_SEEDS, Items.SWEET_BERRIES, Items.APPLE",
      sounds=("CHICKEN_AMBIENT", "CHICKEN_HURT", "CHICKEN_DEATH", 0.55, 1.2, 200), xp=8, cull=1.2, run=0.03,
      fights=False, rideable=True, ride_offset=1.1, ride_forward=0.12, ride_speed=1.35),
]


def gen(s):
    cls, base = s["cls"], s["base"]
    imports = {
        "com.primalera.registry.ModEntities", "net.minecraft.server.level.ServerLevel", "net.minecraft.sounds.SoundEvent",
        "net.minecraft.sounds.SoundEvents", "net.minecraft.world.damagesource.DamageSource", "net.minecraft.world.entity.AgeableMob",
        "net.minecraft.world.entity.EntityType", "net.minecraft.world.entity.ai.attributes.AttributeSupplier",
        "net.minecraft.world.entity.ai.attributes.Attributes", "net.minecraft.world.entity.animal.Animal",
        "net.minecraft.world.item.crafting.Ingredient", "net.minecraft.world.level.Level",
    }
    body = []
    if "food_tag" in s:
        imports.add("net.minecraft.tags.ItemTags")
        body.append(f"    private static final Ingredient FOOD = Ingredient.of({s['food_tag']});")
    else:
        imports.add("net.minecraft.world.item.Items")
        body.append(f"    private static final Ingredient FOOD = Ingredient.of({s['food']});")
    if s.get("roar") or s.get("display"):
        body.append("    private int displayCooldown;")
    if s.get("pack"):
        body.append("    private static boolean alertingPack;")
    body.append("")
    body.append(f"    public {cls}(EntityType<? extends {cls}> type, Level level) {{")
    body.append("        super(type, level);")
    if "step_height" in s:
        body.append(f"        this.setMaxUpStep({s['step_height']}F);")
    body.append(f"        this.xpReward = {s.get('xp', 5)};")
    body.append("    }")
    body.append("")
    body.append("    public static AttributeSupplier.Builder createAttributes() {")
    body.append("        return Animal.createMobAttributes()")
    for k, v in s["attrs"].items():
        body.append(f"                .add(Attributes.{k}, {float(v)}D)")
    body[-1] += ";"
    body.append("    }")
    body.append("")
    body.append("    @Override\n    public String speciesId() {\n        return \"%s\";\n    }\n" % s["id"])
    body.append("    @Override\n    protected Ingredient food() {\n        return FOOD;\n    }\n")
    extras = []
    if base == "HerbivoreDinosaur":
        extras.append("graze")
    if s.get("roar"):
        extras.append("roar")
    if s.get("display"):
        extras.append("display")
    if s.get("call"):
        extras.append("call")
    if base == "PredatorDinosaur" and extras:
        body.append("    @Override\n    protected String[] extraActions() {\n        return new String[]{%s};\n    }\n" % ", ".join(f'"{e}"' for e in extras))
    elif base == "HerbivoreDinosaur" and len(extras) > 1:
        body.append("    @Override\n    protected String[] extraActions() {\n        return new String[]{%s};\n    }\n" % ", ".join(f'"{e}"' for e in extras))
    if "cull" in s:
        body.append(f"    @Override\n    protected double cullingInflate() {{\n        return {s['cull']}D;\n    }}\n")
    if "run" in s:
        body.append(f"    @Override\n    protected double runThresholdSqr() {{\n        return {s['run']}D;\n    }}\n")
    if "head" in s:
        body.append(f"    @Override\n    public int getMaxHeadYRot() {{\n        return {s['head'][0]};\n    }}\n")
        body.append(f"    @Override\n    public int getMaxHeadXRot() {{\n        return {s['head'][1]};\n    }}\n")
    if s.get("rideable"):
        body.append("    @Override\n    public boolean isRideable() {\n        return true;\n    }\n")
        body.append(f"    @Override\n    protected float riddenSpeedFactor() {{\n        return {s['ride_speed']}F;\n    }}\n")
        body.append(f"    @Override\n    public double getPassengersRidingOffset() {{\n        return {s['ride_offset']}D * (this.isBaby() ? 0.5D : 1.0D);\n    }}\n")
        if s.get("ride_forward"):
            body.append(f"    @Override\n    protected double riderForwardOffset() {{\n        return {s['ride_forward']}D;\n    }}\n")
    if s.get("fights") is False:
        body.append("    @Override\n    protected boolean fightsBack() {\n        return false;\n    }\n")
    if base == "PredatorDinosaur":
        imports.add("net.minecraft.world.entity.LivingEntity")
        body.append(f"    @Override\n    protected boolean isPrey(LivingEntity e) {{\n        return {s['prey']};\n    }}\n")
        if "prey_interval" in s:
            body.append(f"    @Override\n    protected int preyInterval() {{\n        return {s['prey_interval']};\n    }}\n")
        if s.get("hunts_players") is False:
            body.append("    @Override\n    protected boolean huntsPlayers() {\n        return false;\n    }\n")
        if s.get("feeding_tame"):
            body.append("    @Override\n    public TameMethod tameMethod() {\n        return TameMethod.FEEDING;\n    }\n")
    # extra goals
    goals = []
    if s.get("leap"):
        imports.add("net.minecraft.world.entity.ai.goal.LeapAtTargetGoal")
        goals.append("        this.goalSelector.addGoal(2, new LeapAtTargetGoal(this, 0.4F));")
    if s["id"] == "velociraptor":
        imports.add("net.minecraft.world.entity.ai.goal.AvoidEntityGoal")
        goals.append("        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Tyrannosaurus.class, 14.0F, 1.2D, 1.5D, e -> !this.isTame()));")
    if s.get("skittish"):
        imports.add("net.minecraft.world.entity.ai.goal.AvoidEntityGoal")
        imports.add("net.minecraft.world.entity.EntitySelector")
        imports.add("net.minecraft.world.entity.player.Player")
        goals.append("        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 8.0F, 1.1D, 1.4D,\n                e -> EntitySelector.NO_CREATIVE_OR_SPECTATOR.test(e) && !this.isTame() && this.getTarget() == null));")
    if s.get("fish"):
        imports.add("net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal")
        imports.add("net.minecraft.world.entity.animal.AbstractFish")
        goals.append("        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, AbstractFish.class, 40, true, false, e -> this.canHunt()));")
    if goals:
        body.append("    @Override\n    protected void addExtraGoals() {\n" + "\n".join(goals) + "\n    }\n")
    if s.get("fish"):
        body.append("    @Override\n    public boolean canBreatheUnderwater() {\n        return true;\n    }\n")
        body.append("    @Override\n    public boolean isPushedByFluid() {\n        return false;\n    }\n")
    if s.get("roar") or s.get("display"):
        imports.add("net.minecraft.world.entity.LivingEntity")
        anim = "roar" if s.get("roar") else "display"
        snd = "SoundEvents.RAVAGER_ROAR, 3.0F, %sF" % (0.55 if s["id"] == "tyrannosaurus" else 0.7) if s.get("roar") else "SoundEvents.HOGLIN_ANGRY, 1.2F, 1.3F"
        body.append(f"""    @Override
    public void setTarget(LivingEntity target) {{
        LivingEntity previous = this.getTarget();
        super.setTarget(target);
        if (!this.level().isClientSide() && target != null && previous == null && this.displayCooldown <= 0 && !this.isVehicle()) {{
            this.displayCooldown = 400;
            triggerAnim(ACTION_CONTROLLER, "{anim}");
            this.playSound({snd});
        }}
    }}

    @Override
    protected void customServerAiStep() {{
        super.customServerAiStep();
        if (this.displayCooldown > 0) {{
            this.displayCooldown--;
        }}
    }}
""")
    if s.get("pack"):
        imports.add("net.minecraft.world.entity.LivingEntity")
        body.append("""    @Override
    public void setTarget(LivingEntity target) {
        super.setTarget(target);
        if (target != null && !this.level().isClientSide() && !alertingPack && !this.isTame()) {
            alertingPack = true;
            try {
                for (Velociraptor other : this.level().getEntitiesOfClass(Velociraptor.class, this.getBoundingBox().inflate(16.0D),
                        r -> r != this && r != target && r.getTarget() == null && !r.isBaby() && !r.isTame())) {
                    other.setTarget(target);
                }
            } finally {
                alertingPack = false;
            }
        }
    }
""")
    if s.get("call"):
        imports.add("net.minecraft.world.damagesource.DamageSource")
        body.append("""    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "call");
        }
        return hurt;
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && this.random.nextInt(3) == 0) {
            triggerAnim(ACTION_CONTROLLER, "call");
        }
    }
""")
    # breeding offspring + sounds
    body.append(f"""    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {{
        return ModEntities.{s['id'].upper()}.get().create(level);
    }}
""")
    amb, hurt, death, pitch, vol, interval = s["sounds"]
    body.append(f"""    @Override
    protected SoundEvent getAmbientSound() {{
        return SoundEvents.{amb};
    }}

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {{
        return SoundEvents.{hurt};
    }}

    @Override
    protected SoundEvent getDeathSound() {{
        return SoundEvents.{death};
    }}

    @Override
    public float getVoicePitch() {{
        return super.getVoicePitch() * {pitch}F;
    }}

    @Override
    protected float getSoundVolume() {{
        return {vol}F;
    }}

    @Override
    public int getAmbientSoundInterval() {{
        return {interval};
    }}""")
    if "step" in s:
        imports.add("net.minecraft.core.BlockPos")
        imports.add("net.minecraft.world.level.block.state.BlockState")
        st, v, p = s["step"]
        body.append(f"""
    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {{
        this.playSound(SoundEvents.{st}, {v}F, {p}F);
    }}""")
    src = "package com.primalera.entity;\n\n" + "\n".join(f"import {i};" for i in sorted(imports)) + "\n\n"
    src += f"/**\n * {s['doc']}\n *\n * Generated by tools/javagen/gen_species.py - edit the table there.\n */\n"
    src += f"public class {cls} extends {base} {{\n" + "\n".join(body) + "\n}\n"
    with open(os.path.join(OUT, cls + ".java"), "w") as f:
        f.write(src)


if __name__ == "__main__":
    for s in SPECIES:
        gen(s)
    print("generated", len(SPECIES))
