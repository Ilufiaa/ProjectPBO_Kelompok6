class Skill:
    def __init__(self, name, power, skill_type, max_cd=0, desc=""):
        self.name       = name
        self.power      = power
        self.skill_type = skill_type   
        self.max_cd     = max_cd
        self.desc       = desc
        self.cooldown   = 0

    def is_ready(self):
        return self.cooldown == 0

    def use(self):
        self.cooldown = self.max_cd

    def reduce_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def status_text(self):
        return "READY" if self.is_ready() else f"CD {self.cooldown}"
