# 3 VS 3 — Turn-Based RPG Battle Game
> Game RPG berbasis giliran (turn-based) dengan sistem elemen yang saling counter mengcounter dan pemilihan karakter, dibuat menggunakan Python & Pygame.


## Anggota Kelompok 
1.Faiz Ahmad Arrafi (25051204006)
2.Firly Radiansyah  (25051204071)
3.M Rafif Raihan Afzaal (25051204073)
4.M Ilham Erlangga (25051204240)

##  Deskripsi Project

**Who Let Them Fight??** adalah game turn-based yang dikembangkan untuk memenuhi tugas akhir mata kuliah Pemrograman Berorientasi Objek (PBO). Pemain memilih 3 karakter dari 18 karakter yang tersedia dimana karakter masing-masing memiliki **elemen**, **role**, dan **skill**  untuk bertarung melawan tim musuh yang dikendalikan AI.

Game ini menampilkan:
- **18 karakter playable** dengan sprite dan suara unik
- **6 elemen**:  Fire,  Water,  Wind,  Earth,  Light, Dark
- **3 role**: Attacker, Healer, Tanker
- **5 stage** dengan tingkat kesulitan berbeda
- Sistem kelebihan/kelemahan elemen (element effectiveness)
- Sistem cooldown skill
- sound effect per karakter
- Sistem save progress berbasis JSON

##  Fitur Utama

###  Gameplay
- **3 vs 3** — Pilih 3 karakter, hadapi 3 musuh per stage
- **Turn-based combat** — Setiap giliran, pemain memilih aksi untuk karakter yang aktif
- **2 jenis serangan**:
  -  **Basic Attack** — Serangan dasar, selalu tersedia (cooldown 0)
  -  **Special Skill** — Skill unik per karakter (cooldown 3 giliran)
- **Element effectiveness** — Serangan 2× lebih kuat atau 0.5× kurang efektif bergantung elemen
- **AI musuh** — Musuh memilih aksi secara otomatis berdasarkan kondisi battle

###  Alur Permainan
Menu Utama → Pilih Stage → Pilih 3 Karakter → Battle → Hasil (Menang/Kalah)

###  Sistem Elemen
| Elemen | Kuat Lawan | Lemah Lawan |
|--------|-----------|-------------|
|  Fire  | Earth     | Water |
|  Water | Fire      | Wind  |
|  Wind  | Water     | Earth |
|  Earth | Wind      | Fire, Water |
|  Light | Dark      | — |
|  Dark  | Light     | — |

###  Fitur Pendukung
- **Save System** — Progress stage tersimpan otomatis di `savegame.json`
- **Sound Manager** — BGM menu, BGM battle, SFX per karakter, SFX hit/heal
- **Stage Lock** — Stage berikutnya terbuka setelah menyelesaikan stage sebelumnya

##  Cara Menjalankan Project

### Prasyarat
- Python **3.10** atau lebih baru
- pip (package manager Python)

### Langkah Instalasi

**1. Clone repository ini**
```bash
git clone https://github.com/Ilufiaa/ProjectPBO_Kelompok6.git
cd ProjectPBO_Kelompok6
```

**2. Install dependensi**
```bash
pip install pygame
```

**3. Jalankan game**
```bash
python main.py
```

>  Pastikan menjalankan dari **root folder project** (`ProjectPBO_Kelompok6/`), bukan dari dalam folder `src/`, agar path asset terbaca dengan benar.

### Kontrol
| Tombol / Aksi | Fungsi |
|---------------|--------|
| Klik kiri mouse | Pilih tombol / karakter / target |
| `ESC` | Kembali ke scene sebelumnya |

---

##  Penjelasan Implementasi OOP

### 1. Kelas & Objek
Seluruh objek game direpresentasikan sebagai kelas. Contoh:

```python
class Character:
    def __init__(self, data: dict, x: int, y: int):
        self.name    = data["name"]
        self.element = data["element"]
        self.role    = data["role"]
        self.max_hp  = data["hp"]
        self.hp      = data["hp"]
        self.attack  = data["attack"]
        self.defense = data["defense"]
        self.basic_attack  = Skill(...)   
        self.special_skill = Skill(...)
```

---
### 2. Encapsulation
Setiap kelas mengelola state-nya sendiri dan hanya mengekspos method yang diperlukan. Data internal dilindungi dari modifikasi langsung luar kelas.

```python
def take_damage(self, dmg):
    self.hp = max(0, self.hp - dmg)   # HP tidak bisa negatif
    self.shake_timer = 10

def _do_heal(self, amount) -> int:    
    before  = self.hp
    self.hp = min(self.max_hp, self.hp + amount)  # HP tidak melebihi max
    return self.hp - before
```

### 3.  Abstraksi (Abstraction)
Kompleksitas implementasi disembunyikan di balik ui yang sederhana.
Pengguna kelas tidak perlu tahu *bagaimana* cara kerjanya cukup hanya ttahu *apa* yang bisa dilakukan.

**Contoh 1 — `SoundManager`** menyembunyikan seluruh logika `pygame.mixer`:
```python

class SoundManager:
    def play(self, char_name: str):      
        ...                              

    def play_menu_bgm(self): ...
    def stop_bgm(self):      ...
    def play_hit(self, is_heal: bool): ...

ctx.sfx.play("Windah")
ctx.sfx.stop_bgm()
```

**Contoh 2 — `run_scene()`** mengabstraksi game loop dari detail tiap scene:
```python
def run_scene(scene):          
    while not scene.done:      
        scene.handle(event)     
        scene.draw()
```
---

### 4. Polimorfisme (Polymorphism)
Semua scene mengimplementasikan ui yang sama: `handle(event)` dan `draw()`. Main loop dapat memanggil method yang sama tanpa peduli scene mana yang sedang berjalan.

```python
# main.py — satu fungsi untuk semua scene
def run_scene(scene):
    while not scene.done:
        for event in pygame.event.get():
            scene.handle(event)   
        scene.draw()              
        pygame.display.update()

# Dipanggil untuk scene yang berbeda
run_scene(PetunjukScene())
run_scene(StageScene())
run_scene(DeckScene())
run_scene(ResultScene(player_won=True))
```
##  Screenshot Tampilan Program

###  Menu Utama
![Menu Utama](screenshots/menu.png)

###  Pilih Stage
![Stage Select](screenshots/stageselect.png)

###  Pilih Karakter
![Deck Scene](screenshots/deckscene.png)

###  Battle Scene
![Battle Scene](screenshots/battlescene.png)

###  Hasil Pertandingan
![Result](screenshots/win.png)
![Result](screenshots/win2.png)
