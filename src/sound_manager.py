import pygame
import os

_MUSIC_DIR = "assets/music"
_FALLBACK  = "amongus.mp3"

_CHAR_SOUND: dict[str, str] = {
    "Windah":              "Windah.mp3",
    "SunFlower":           "wielino.mp3",
    "Ambatron":            "ambatron.mp3",
    "IshowSpeed":          "amongus.mp3",
    "Tung Sahur":          "tungtungsahur.mp3",
    "Balmond":             "balmond.mp3",
    "Bagasdribble":        "bagasdribble.mp3",
    "Keju joget":          "wielino.mp3",
    "Masamba":             "masamba.mp3",
    "Faiz immo":           "amongus.mp3",
    "Windi":               "Windi.mp3",
    "Pakvincent":          "pakvincent.mp3",
    "Kumar":               "kumar.mp3",
    "Juki":                "wielino.mp3",
    "Mambo":               "mambo.mp3",
    "HengkerwibuproTzy":        "squadhengker.mp3",
    "Masmasnunjuk":        "masmasnunjuk.mp3",
    "Patrick":          "patrickplenger.mp3",
    "Mengerikan":          "mengerikan.mp3",
    "Doraemon":            "doraemon.mp3",
    "Kucinguiaeo":         "kucinguiaeo.mp3",
    "Serigalasumatra":     "serigalasumatra.mp3",
    "Rajakucing":          "rajakucing.mp3",
    "Thomasalphaedisound": "thomasalphaedisound.mp3",
}

_HIT_ATTACK = "attacker_hit.mp3"    
_HIT_HEAL   = "healing-sound.mp3"   
_BGM        = "background_music1.mp3"
_BGM_MENU  = "gow 2.mp3"    
_BGM_STAGE = "gow 2.mp3"   
_BGM_DECK  = "gow 2.mp3"    


class SoundManager:
    def __init__(self):
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._enabled = False
        self._current_music: str | None = None   

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[SoundManager] mixer init failed: {e}")
                return

        self._enabled = True
        self._preload()

    def _preload(self):
        # Karakter SFX
        loaded = set()
        for fname in list(_CHAR_SOUND.values()) + [_HIT_ATTACK, _HIT_HEAL, _FALLBACK]:
            if fname in loaded:
                continue
            path = os.path.join(_MUSIC_DIR, fname)
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(0.75)
                self._sounds[fname] = snd
            except Exception as e:
                print(f"[SoundManager] gagal load {path}: {e}")
                self._sounds[fname] = None
            loaded.add(fname)

    def _play_sound(self, fname: str, volume: float = 0.75):
        if not self._enabled:
            return
        snd = self._sounds.get(fname) or self._sounds.get(_FALLBACK)
        if snd:
            try:
                ch = pygame.mixer.find_channel(True)
                if ch:
                    ch.set_volume(volume)
                    ch.play(snd)
            except Exception as e:
                print(f"[SoundManager] play error: {e}")

    def play(self, character_name: str):
        """Putar SFX karakter saat pakai skill/attack."""
        fname = _CHAR_SOUND.get(character_name, _FALLBACK)
        self._play_sound(fname, volume=0.75)

    def play_hit(self, is_heal: bool = False):
        """Putar SFX kena serangan atau kena heal."""
        fname = _HIT_HEAL if is_heal else _HIT_ATTACK
        self._play_sound(fname, volume=0.8)

    def play_menu_bgm(self):
        """Musik menu utama — diputar ulang dari awal."""
        self._play_music(_BGM_MENU)

    def play_stage_bgm(self):
        """Musik pemilihan stage."""
        self._play_music(_BGM_STAGE)

    def play_deck_bgm(self):
        """Musik pemilihan karakter."""
        self._play_music(_BGM_DECK)

    def _play_music(self, filename: str, volume: float = 0.40):
        """Internal: load dan play file musik sebagai BGM (loop).
        Jika file yang sama sudah diputar, tidak direstart (musik lanjut)."""
        if not self._enabled:
            return
        if self._current_music == filename and pygame.mixer.music.get_busy():
            return   
        path = os.path.join(_MUSIC_DIR, filename)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)   
            self._current_music = filename
        except Exception as e:
            print(f"[SoundManager] musik {filename} gagal: {e}")

    def play_bgm(self):
        """Mulai background music."""
        if not self._enabled:
            return
        path = os.path.join(_MUSIC_DIR, _BGM)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)  
        except Exception as e:
            print(f"[SoundManager] BGM error: {e}")

    def stop_bgm(self):
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
            self._current_music = None
        except Exception:
            pass

    def set_volume(self, vol: float):
        for snd in self._sounds.values():
            if snd:
                snd.set_volume(max(0.0, min(1.0, vol)))
