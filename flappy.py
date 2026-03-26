import pygame
import random
import time
import math
import json
import os
import sys
import gc
import getpass
import shutil
import threading
import queue as _queue
import io
import hashlib
import hmac
import struct
import requests as _requests
from pygame.locals import *
#pour conv en exe ne pas oublier pillow et gdown

# ══════════════════════════════════════════════════════════════════════════════
#  ██████╗  ██████╗  ███╗   ██╗███████╗██╗ ██████╗
#  ██╔════╝██╔═══██╗ ████╗  ██║██╔════╝██║██╔════╝
#  ██║     ██║   ██║ ██╔██╗ ██║█████╗  ██║██║  ███╗
#  ██║     ██║   ██║ ██║╚██╗██║██╔══╝  ██║██║   ██║
#  ╚██████╗╚██████╔╝ ██║ ╚████║██║     ██║╚██████╔╝
#   ╚═════╝ ╚═════╝  ╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝
#
#  ⚠️  REMPLIS CES DEUX VALEURS — Dashboard Supabase > Settings > API
# ══════════════════════════════════════════════════════════════════════════════
SUPABASE_URL = "https://sabrdqwpzxlycxohtxrt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNhYnJkcXdwenhseWN4b2h0eHJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwOTYzNzgsImV4cCI6MjA4OTY3MjM3OH0.A1o2iXFobWRwbxIu1QM9VyyWUZbdrXVagOwPtIuRb-k"

# ══════════════════════════════════════════════════════════════════════════════
#  VERSION DU JEU
# ══════════════════════════════════════════════════════════════════════════════
VERSION = "3.0.5"

_GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Pcquifume/Flappy_bird/main/version"
_GITHUB_RELEASES_URL = "https://github.com/Pcquifume/Flappy_bird/tree/main"
_GITHUB_API_CONTENTS = "https://api.github.com/repos/Pcquifume/Flappy_bird/contents/"

# ══════════════════════════════════════════════════════════════════════════════
#  VÉRIFICATION INTERNET
# ══════════════════════════════════════════════════════════════════════════════
def _check_internet(timeout=5) -> bool:
    """Teste la connectivité réseau. Retourne True si internet est disponible."""
    try:
        _requests.get("https://www.google.com", timeout=timeout)
        return True
    except Exception:
        try:
            _requests.get("https://www.cloudflare.com", timeout=timeout)
            return True
        except Exception:
            return False

def _show_no_internet_screen():
    """Affiche un écran d'erreur si pas de connexion et attend que l'utilisateur quitte."""
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    _info = pygame.display.Info()
    W, H  = min(600, _info.current_w - 40), 260
    win   = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Flappy Bird — Pas de connexion")
    fn_title = pygame.font.SysFont('Impact', 34)
    fn_sub   = pygame.font.SysFont('Verdana', 14)
    fn_btn   = pygame.font.SysFont('Verdana', 13, bold=True)
    CLR_BG   = (8, 10, 22)
    CLR_GOLD = (255, 215, 60)
    CLR_RED  = (255, 80, 80)
    CLR_GREY = (160, 170, 200)
    CLR_W    = (255, 255, 255)
    CX = W // 2
    btn_rect = pygame.Rect(CX - 90, H - 64, 180, 40)
    clock_no = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if btn_rect.collidepoint(ev.pos):
                    pygame.quit(); sys.exit()
        win.fill(CLR_BG)
        # Icône wifi barré (simple dessin)
        pygame.draw.circle(win, CLR_RED, (CX, 62), 30, 3)
        pygame.draw.line(win, CLR_RED, (CX - 22, 40), (CX + 22, 84), 3)
        # Textes
        t = fn_title.render("Pas de connexion Internet", True, CLR_GOLD)
        win.blit(t, (CX - t.get_width()//2, 105))
        l1 = fn_sub.render("Flappy Bird nécessite une connexion Internet pour fonctionner.", True, CLR_GREY)
        win.blit(l1, (CX - l1.get_width()//2, 148))
        l2 = fn_sub.render("Connecte-toi au Wi-Fi ou à Internet, puis relance le jeu.", True, CLR_GREY)
        win.blit(l2, (CX - l2.get_width()//2, 170))
        # Bouton Quitter
        mx, my = pygame.mouse.get_pos()
        hov = btn_rect.collidepoint(mx, my)
        col_btn = (200, 60, 60) if hov else (140, 30, 30)
        pygame.draw.rect(win, col_btn, btn_rect, border_radius=10)
        pygame.draw.rect(win, CLR_RED, btn_rect, 2, border_radius=10)
        bt = fn_btn.render("QUITTER", True, CLR_W)
        win.blit(bt, (btn_rect.centerx - bt.get_width()//2, btn_rect.centery - bt.get_height()//2))
        pygame.display.flip()
        clock_no.tick(30)

# ══════════════════════════════════════════════════════════════════════════════
#  VÉRIFICATION DE MISE À JOUR
# ══════════════════════════════════════════════════════════════════════════════
def _parse_version(v):
    """Convertit '3.0.1' en tuple (3, 0, 1) pour comparaison."""
    try:
        # Nettoyer : retirer espaces, retours chariot, BOM, guillemets éventuels
        clean = v.strip().strip("\r\n\t '\"\ufeff")
        parts = clean.split('.')
        return tuple(int(x) for x in parts if x.isdigit())
    except Exception as e:
        print(f"[UPDATE] _parse_version error: {e!r} for value {v!r}")
        return (0, 0, 0)

def _get_remote_version():
    """
    Récupère la version ET le lien de téléchargement depuis GitHub.
    Le fichier 'version' contient :
      ligne 1 : numéro de version  ex: 3.0.2
      ligne 2 : lien Google Drive  ex: https://drive.google.com/file/d/XXXX/view?usp=sharing
    Retourne (version_str, download_url) ou (None, None) si échec.
    """
    try:
        r = _requests.get(_GITHUB_VERSION_URL, timeout=8)
        print(f"[UPDATE] HTTP {r.status_code} — contenu brut: {r.content!r}")
        r.raise_for_status()
        lines = [l.strip().strip("\r\n\t '\"\ufeff") for l in r.text.splitlines() if l.strip()]
        ver      = lines[0] if len(lines) >= 1 else None
        dl_url   = lines[1] if len(lines) >= 2 else None
        print(f"[UPDATE] Version distante : {ver!r}  —  lien : {dl_url!r}")
        return ver, dl_url
    except Exception as e:
        print(f"[UPDATE] Impossible de récupérer la version distante : {e!r}")
        return None, None

def _check_for_update():
    """
    Compare la version locale avec GitHub.
    Si mise à jour disponible : télécharge le .exe via le lien Google Drive
    contenu dans la 2e ligne du fichier 'version', puis relance.
    """
    print(f"[UPDATE] Version locale : {VERSION}")
    remote_ver, dl_url = _get_remote_version()
    if remote_ver is None:
        print("[UPDATE] Version distante introuvable, on continue sans màj.")
        return

    local_t  = _parse_version(VERSION)
    remote_t = _parse_version(remote_ver)
    print(f"[UPDATE] Comparaison : local={local_t}  distante={remote_t}")

    if remote_t <= local_t:
        print("[UPDATE] Déjà à jour.")
        return

    if not dl_url:
        print("[UPDATE] Lien de téléchargement absent dans le fichier version.")
        return

    # ── Chemin de l'exe actuel ────────────────────────────────────────────
    if getattr(sys, 'frozen', False):
        current_exe = sys.executable
    else:
        current_exe = os.path.abspath(__file__)

    current_dir = os.path.dirname(current_exe)
    bat_path    = os.path.join(current_dir, "_update.bat")
    dl_dir      = os.path.join(current_dir, "_update_dl")

    # ── Initialiser pygame pour l'écran de mise à jour ───────────────────
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    W, H  = 640, 300
    win   = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Flappy Bird — Mise à jour disponible")
    fn_big  = pygame.font.SysFont("Impact",  32)
    fn_med  = pygame.font.SysFont("Verdana", 14, bold=True)
    fn_sub  = pygame.font.SysFont("Verdana", 12)
    CLR_BG   = (8,  10, 22)
    CLR_GOLD = (255, 215, 60)
    CLR_CYAN = (70,  210, 255)
    CLR_GREY = (150, 165, 200)
    CLR_RED  = (255,  80,  80)
    CX = W // 2
    BAR_X, BAR_Y, BAR_W, BAR_H = 50, 200, W - 100, 22

    def _upd_draw(status_line, prog=None, done=False, error=False):
        win.fill(CLR_BG)
        ts = fn_big.render(f"Mise à jour  {VERSION}  →  {remote_ver}", True, CLR_GOLD)
        win.blit(ts, (CX - ts.get_width()//2, 28))
        col_st = CLR_RED if error else (CLR_CYAN if not done else CLR_GOLD)
        st = fn_med.render(status_line, True, col_st)
        win.blit(st, (CX - st.get_width()//2, 80))
        if not done and not error:
            sub = fn_sub.render("Le jeu se fermera et se relancera automatiquement après la mise à jour.", True, CLR_GREY)
            win.blit(sub, (CX - sub.get_width()//2, 108))
        pygame.draw.rect(win, (20, 22, 50), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=11)
        pygame.draw.rect(win, (45, 55, 100), (BAR_X, BAR_Y, BAR_W, BAR_H), 1, border_radius=11)
        if prog is not None and prog > 0:
            fill = int((BAR_W - 4) * min(prog, 1.0))
            col_bar = CLR_RED if error else (CLR_GOLD if done else CLR_CYAN)
            pygame.draw.rect(win, col_bar, (BAR_X+2, BAR_Y+2, fill, BAR_H-4), border_radius=9)
            pct_s = fn_sub.render(f"{int(prog*100)} %", True, (255,255,255))
            win.blit(pct_s, (CX - pct_s.get_width()//2, BAR_Y + BAR_H + 10))
        elif prog is None:
            dots = "." * (int(pygame.time.get_ticks() / 400) % 4)
            ani = fn_sub.render(f"Téléchargement en cours{dots}", True, CLR_GREY)
            win.blit(ani, (CX - ani.get_width()//2, BAR_Y + BAR_H + 10))
        if done:
            note = fn_sub.render("Fermeture dans quelques secondes...", True, CLR_GREY)
            win.blit(note, (CX - note.get_width()//2, BAR_Y + BAR_H + 10))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

    _upd_draw("Connexion au serveur de mise à jour...", prog=None)
    pygame.time.wait(300)

    # ── Vérifier / installer gdown ────────────────────────────────────────
    import subprocess as _sp
    try:
        import gdown as _gdown
    except ImportError:
        _upd_draw("Installation de gdown...", prog=None)
        _sp.run([sys.executable, "-m", "pip", "install", "gdown", "--quiet"], check=True)
        import gdown as _gdown

    # ── Télécharger le .exe depuis Google Drive ───────────────────────────
    _upd_draw("Téléchargement de la nouvelle version...", prog=None)
    pygame.time.wait(200)
    new_exe_path = None
    try:
        if os.path.exists(dl_dir):
            shutil.rmtree(dl_dir, ignore_errors=True)
        os.makedirs(dl_dir, exist_ok=True)

        # gdown télécharge le fichier et retourne le chemin local
        downloaded = _gdown.download(dl_url, output=dl_dir + os.sep, quiet=False, fuzzy=True)
        print(f"[UPDATE] Fichier téléchargé : {downloaded}")

        if downloaded is None:
            raise RuntimeError("gdown n'a pas pu télécharger le fichier.")

        # Si ce n'est pas déjà un .exe, chercher dans le dossier
        if downloaded.lower().endswith(".exe"):
            new_exe_path = os.path.join(current_dir, os.path.basename(downloaded))
            shutil.move(downloaded, new_exe_path)
        else:
            for root, dirs, fnames in os.walk(dl_dir):
                for fname in fnames:
                    if fname.lower().endswith(".exe"):
                        new_exe_path = os.path.join(current_dir, fname)
                        shutil.move(os.path.join(root, fname), new_exe_path)
                        break
                if new_exe_path:
                    break

        if new_exe_path is None:
            raise FileNotFoundError("Aucun .exe trouvé après téléchargement.")

        print(f"[UPDATE] EXE prêt : {new_exe_path}")

    except Exception as e:
        print(f"[UPDATE] Erreur téléchargement : {e}")
        _upd_draw(f"Erreur : {e}", prog=0, error=True)
        pygame.time.wait(3000)
        shutil.rmtree(dl_dir, ignore_errors=True)
        pygame.quit()
        return

    # ── Création du .bat ─────────────────────────────────────────────────
    _upd_draw("Préparation du remplacement...", prog=1.0)
    pygame.time.wait(400)

    bat_lines = [
        "@echo off",
        "timeout /t 3 /nobreak >nul",
        ":retry_del",
        f'del /f /q "{current_exe}" 2>nul',
        f'if exist "{current_exe}" (',
        "  timeout /t 1 /nobreak >nul",
        "  goto retry_del",
        ")",
        f'if exist "{dl_dir}" rmdir /s /q "{dl_dir}" 2>nul',
        f'if exist "{_CACHE_DIR}" rmdir /s /q "{_CACHE_DIR}"',
        f'start "" "{new_exe_path}"',
        '(goto) 2>nul & del "%~f0"',
    ]
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("\r\n".join(bat_lines))

    _upd_draw("Mise à jour réussie ! Fermeture et relancement...", prog=1.0, done=True)
    pygame.time.wait(2500)

    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS         = 0x00000008
    _sp.Popen(
        ["cmd.exe", "/c", bat_path],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )
    pygame.quit()
    sys.exit()

# ══════════════════════════════════════════════════════════════════════════════
#  CACHE LOCAL — tout dans %APPDATA%\FlappyBird  (caché, invisible du joueur)
# ══════════════════════════════════════════════════════════════════════════════
def _get_cache_dir():
    """
    Retourne le dossier cache caché.
    - .exe compilé  -> %APPDATA%/FlappyBird/
    - .py dev       -> .asset_cache/ à côté du script
    Le dossier est créé s'il n'existe pas.
    """
    if getattr(sys, 'frozen', False):
        base = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FlappyBird')
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.asset_cache')
    os.makedirs(base, exist_ok=True)
    # Cacher le dossier sous Windows
    try:
        import ctypes
        ctypes.windll.kernel32.SetFileAttributesW(base, 0x02)  # FILE_ATTRIBUTE_HIDDEN
    except Exception:
        pass
    return base

_CACHE_DIR       = _get_cache_dir()
_ASSETS_BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/assets"

# Fichier sentinelle : présent = tous les assets ont été téléchargés au moins une fois
_READY_FLAG = os.path.join(_CACHE_DIR, ".ready")

# ══════════════════════════════════════════════════════════════════════════════
#  LISTE COMPLÈTE DES ASSETS À TÉLÉCHARGER AU PREMIER LANCEMENT
#  (tous les fichiers qui seront nécessaires pendant la partie)
# ══════════════════════════════════════════════════════════════════════════════
_ALL_ASSETS = [
    # ── Sprites ──────────────────────────────────────────────────────────────
    "assets/sprites/background-day.png",
    "assets/sprites/message.png",
    "assets/sprites/gameover.png",
    "assets/sprites/base.png",
    "assets/sprites/pipe-green.png",
    "assets/sprites/bluebird-upflap.png",
    "assets/sprites/bluebird-midflap.png",
    "assets/sprites/bluebird-downflap.png",
    "assets/sprites/redbird-upflap.png",
    "assets/sprites/redbird-midflap.png",
    "assets/sprites/redbird-downflap.png",
    "assets/sprites/mouche.png",
    "assets/sprites/avion.png",
    "assets/sprites/Ninja.png",
    "assets/sprites/avion_de_chasse.png",
    "assets/sprites/Nyancat.png",
    "assets/sprites/coin.gif",
    "assets/sprites/play_btn.png",
    "assets/sprites/boutique_btn.png",
    "assets/sprites/mission_btn.png",
    "assets/sprites/niveau_btn.png",
    "assets/sprites/fleche_gauche_1.png",
    "assets/sprites/fleche_gauche_2.png",
    "assets/sprites/fleche_droit_1.png",
    "assets/sprites/fleche_droit_2.png",
    "assets/sprites/background_custom_1.png",
    "assets/sprites/background_custom_2.png",
    "assets/sprites/background_custom_3.png",
    "assets/sprites/background_custom_4.png",
    "assets/sprites/background_custom_5.png",
    "assets/sprites/background_custom_6.png",
    "assets/sprites/background_custom_7.png",
    "assets/sprites/Flappy_Bird_icon.ico",  # uploadé dans assets/sprites/
    # ── Audio ─────────────────────────────────────────────────────────────────
    "assets/audio/wing.wav",
    "assets/audio/hit.wav",
    "assets/audio/coin.mp3",
    "assets/audio/musique_default_game.mp3",
    "assets/audio/musique_default_menu.mp3",
]

# ── Téléchargement unitaire ────────────────────────────────────────────────────
_dl_lock   = threading.Lock()
_dl_failed = set()

def _cached_path(remote_path: str) -> str:
    """Chemin local dans le cache pour un remote_path donné."""
    return os.path.join(_CACHE_DIR, remote_path.replace('/', os.sep))

def _download_one(remote_path: str) -> bool:
    """
    Télécharge un seul fichier depuis Supabase Storage vers le cache.
    Retourne True si succès (ou déjà présent), False si échec.
    """
    cached = _cached_path(remote_path)
    if os.path.exists(cached):
        return True
    url = f"{_ASSETS_BASE_URL}/{remote_path}"
    try:
        r = _requests.get(url, timeout=8)
        r.raise_for_status()
        os.makedirs(os.path.dirname(cached), exist_ok=True)
        with open(cached, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"[ASSET] ✗ {remote_path}: {e}")
        _dl_failed.add(remote_path)
        return False

def _asset_local(remote_path: str) -> str:
    """
    Retourne le chemin local utilisable par pygame.
    Ordre de priorité :
      1. Fichier local à côté du .py/exe  (mode dev ou fallback)
      2. Cache %APPDATA%/FlappyBird/      (mode normal)
      3. Téléchargement à la demande      (si raté au premier lancement)
    """
    # 1. Fichier local direct
    if os.path.exists(remote_path):
        return remote_path

    # 2. Cache
    cached = _cached_path(remote_path)
    if os.path.exists(cached):
        return cached

    # 3. Déjà marqué en échec → ne pas re-tenter indéfiniment
    if remote_path in _dl_failed:
        return remote_path

    # 4. Téléchargement à la demande (thread-safe)
    with _dl_lock:
        if os.path.exists(cached):  # double-check
            return cached
        _download_one(remote_path)
        return cached if os.path.exists(cached) else remote_path

# ── Wrappers pygame ────────────────────────────────────────────────────────────
def _pygame_load(path: str):
    """pygame.image.load avec résolution cloud automatique."""
    return pygame.image.load(_asset_local(path))

def _pygame_load_sound(path: str):
    """pygame.mixer.Sound avec résolution cloud automatique."""
    return pygame.mixer.Sound(_asset_local(path))

def _pygame_load_music(path: str) -> str:
    """Retourne le chemin local d'un fichier audio (pour pygame.mixer.music.load)."""
    return _asset_local(path)

# ══════════════════════════════════════════════════════════════════════════════
#  DÉTECTION PREMIER LANCEMENT + TÉLÉCHARGEMENT COMPLET
#  Appelé AVANT pygame.init() — affiche une fenêtre console simple
# ══════════════════════════════════════════════════════════════════════════════
def _is_first_launch() -> bool:
    """True si le fichier sentinelle .ready est absent = premier lancement."""
    return not os.path.exists(_READY_FLAG)

def _check_missing_assets() -> list:
    """Retourne la liste des assets absents du cache."""
    return [p for p in _ALL_ASSETS if not os.path.exists(_cached_path(p))]

def _run_first_launch_download():
    """
    Télécharge tous les assets manquants avec une barre de progression console.
    Appelé avant pygame si c'est le premier lancement.
    Lance pygame.init() après pour afficher la progression dans une vraie fenêtre.
    """
    missing = _check_missing_assets()
    if not missing:
        # Tout est déjà là (réinstallation ?), on marque ready et on continue
        open(_READY_FLAG, 'w').close()
        return

    total = len(missing)
    print(f"\n🎮  FLAPPY BIRD — Premier lancement détecté")
    print(f"    Téléchargement de {total} fichiers depuis le serveur...")
    print(f"    Dossier cache : {_CACHE_DIR}\n")

    # ── Fenêtre pygame de téléchargement ─────────────────────────────────────
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    _info = pygame.display.Info()
    W, H  = min(700, _info.current_w - 40), 220
    win   = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Flappy Bird — Téléchargement en cours...")
    try:
        _icon_cached = _cached_path("assets/sprites/Flappy_Bird_icon.ico")
        if not os.path.exists(_icon_cached):
            _download_one("assets/sprites/Flappy_Bird_icon.ico")
        if os.path.exists(_icon_cached):
            pygame.display.set_icon(pygame.image.load(_icon_cached))
    except Exception:
        pass

    fn_title = pygame.font.SysFont('Impact', 32)
    fn_sub   = pygame.font.SysFont('Verdana', 15)
    fn_pct   = pygame.font.SysFont('Impact', 22)
    CLR_BG   = (8, 10, 22)
    CLR_GOLD = (255, 215, 60)
    CLR_CYAN = (70, 210, 255)
    CLR_GREY = (100, 110, 140)
    CLR_W    = (255, 255, 255)

    ok = err = 0
    for idx, remote_path in enumerate(missing):
        # Événements pygame (évite "fenêtre ne répond pas")
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # Téléchargement
        success = _download_one(remote_path)
        if success: ok += 1
        else:       err += 1

        progress  = (idx + 1) / total
        fname     = remote_path.split('/')[-1]

        # ── Rendu ─────────────────────────────────────────────────────────
        win.fill(CLR_BG)
        CX = W // 2

        # Titre
        t = fn_title.render("FLAPPY BIRD", True, CLR_GOLD)
        win.blit(t, (CX - t.get_width()//2, 18))

        # Sous-titre
        sub = fn_sub.render("Téléchargement des ressources du jeu...", True, CLR_CYAN)
        win.blit(sub, (CX - sub.get_width()//2, 60))

        # Barre de progression
        BAR_X, BAR_Y, BAR_W, BAR_H = 40, 96, W - 80, 22
        pygame.draw.rect(win, (20, 22, 50), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=11)
        pygame.draw.rect(win, (40, 44, 80), (BAR_X, BAR_Y, BAR_W, BAR_H), 1, border_radius=11)
        fill_w = int((BAR_W - 4) * progress)
        if fill_w > 0:
            pygame.draw.rect(win, CLR_CYAN,
                             (BAR_X + 2, BAR_Y + 2, fill_w, BAR_H - 4), border_radius=9)

        # Pourcentage
        pct = fn_pct.render(f"{int(progress*100)}%  ({idx+1}/{total})", True, CLR_W)
        win.blit(pct, (CX - pct.get_width()//2, BAR_Y + BAR_H + 8))

        # Fichier en cours
        fname_s = fn_sub.render(fname, True, CLR_GREY)
        win.blit(fname_s, (CX - fname_s.get_width()//2, BAR_Y + BAR_H + 34))

        # Erreurs éventuelles
        if err:
            err_s = fn_sub.render(f"⚠  {err} fichier(s) en erreur (non bloquant)", True, (220, 80, 80))
            win.blit(err_s, (CX - err_s.get_width()//2, BAR_Y + BAR_H + 56))

        pygame.display.flip()

    # ── Fin du téléchargement ─────────────────────────────────────────────
    # Marquer comme prêt (sauf si trop d'erreurs critiques)
    if err == 0 or ok > (total // 2):
        open(_READY_FLAG, 'w').close()

    # Petit message final
    win.fill(CLR_BG)
    done = fn_title.render("Téléchargement terminé !", True, CLR_GOLD)
    win.blit(done, (CX - done.get_width()//2, H//2 - 30))
    msg = fn_sub.render(f"{ok} fichiers OK{'  —  ' + str(err) + ' erreurs' if err else ''}  —  Lancement du jeu...", True, CLR_CYAN)
    win.blit(msg, (CX - msg.get_width()//2, H//2 + 10))
    pygame.display.flip()
    pygame.time.wait(1200)

    # Ne pas fermer la fenêtre : on laisse le jeu prendre la main
    # et agrandir/remplacer la fenêtre normalement via pygame.display.set_mode

# ── POINT D'ENTRÉE DU SYSTÈME DE CACHE ────────────────────────────────────────
# 1. Vérifier la connexion Internet (obligatoire)
if not _check_internet():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    _show_no_internet_screen()   # bloque jusqu'à ce que l'utilisateur quitte
    sys.exit()

# 2. Vérifier si une mise à jour est disponible
_check_for_update()   # si màj → télécharge, crée le bat et quitte

# 3. Premier lancement → téléchargement complet avant tout le reste
if _is_first_launch():
    _run_first_launch_download()
# Sinon : init pygame + vérification rapide des assets critiques
else:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    _critical = [
        "assets/sprites/background-day.png",
        "assets/audio/musique_default_menu.mp3",
    ]
    for _cp in _critical:
        if not os.path.exists(_cached_path(_cp)):
            _download_one(_cp)

# ══════════════════════════════════════════════════════════════════════════════
#  SUPABASE REST API — helpers internes
# ══════════════════════════════════════════════════════════════════════════════
def _sb_headers(extra=None):
    h = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }
    if extra:
        h.update(extra)
    return h

def _sb_url(table):
    return f"{SUPABASE_URL}/rest/v1/{table}"

def _sb_get(table, params=""):
    try:
        r = _requests.get(f"{_sb_url(table)}?{params}", headers=_sb_headers(), timeout=4)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[SB] GET {table}: {e}")
        return []

def _sb_post(table, payload, upsert=False):
    extra = {"Prefer": "resolution=merge-duplicates,return=representation"} if upsert else {"Prefer": "return=representation"}
    try:
        r = _requests.post(_sb_url(table), json=payload, headers=_sb_headers(extra), timeout=4)
        if r.status_code == 409:
            # Conflit — tenter un PATCH selon la table
            if table == "players":
                name = payload.get("name")
                if name:
                    r2 = _requests.patch(f"{_sb_url(table)}?name=eq.{name}", json=payload,
                                         headers=_sb_headers(), timeout=4)
                    if r2.status_code in (200, 201, 204):
                        return r2.json() if r2.content else {}
            elif table == "levels":
                level_id = payload.get("id")
                if level_id:
                    r2 = _requests.patch(f"{_sb_url(table)}?id=eq.{level_id}", json=payload,
                                         headers=_sb_headers(), timeout=4)
                    if r2.status_code in (200, 201, 204):
                        return r2.json() if r2.content else {}
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[SB] POST {table}: {e}")
        return None

def _sb_patch(table, params, payload):
    try:
        r = _requests.patch(f"{_sb_url(table)}?{params}", json=payload,
                            headers=_sb_headers(), timeout=4)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[SB] PATCH {table}: {e}")
        return None

def _sb_delete(table, params):
    try:
        r = _requests.delete(f"{_sb_url(table)}?{params}", headers=_sb_headers(), timeout=4)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[SB] DELETE {table}: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  CACHE JOUEUR (évite les appels réseau à chaque frame)
# ══════════════════════════════════════════════════════════════════════════════
_player_cache       = {}
_PLAYER_CACHE_TTL   = 15.0
_display_name_cache = {}   # {session_name: display_name} — cache permanent, jamais expiré

def _pc_get(name):
    e = _player_cache.get(name)
    return e[0] if e and (time.time() - e[1]) < _PLAYER_CACHE_TTL else None

def _pc_set(name, p):
    _player_cache[name] = (p, time.time())

def _pc_clear(name):
    _player_cache.pop(name, None)

# ══════════════════════════════════════════════════════════════════════════════
#  SAUVEGARDE ASYNCHRONE (ne bloque pas pygame)
# ══════════════════════════════════════════════════════════════════════════════
_save_queue = _queue.Queue()

def _save_worker():
    while True:
        item = _save_queue.get()
        if item is None:
            break
        name, player = item
        try:
            _sb_post("players", _player_to_row(player), upsert=True)
            _pc_set(name, player)
        except Exception as e:
            print(f"[SaveWorker] {e}")
        # [FIX] Ne pas vider la queue — chaque sauvegarde doit être traitée

_save_thread = threading.Thread(target=_save_worker, daemon=True, name="SupaSave")
_save_thread.start()

# ══════════════════════════════════════════════════════════════════════════════
#  CONVERSION JOUEUR ↔ SUPABASE ROW
# ══════════════════════════════════════════════════════════════════════════════
def _row_to_player(row):
    return {
        "name":               row.get("name", ""),
        "display_name":       row.get("display_name") or row.get("name", ""),
        "best_score":         row.get("best_score", 0),
        "games_played":       row.get("games_played", 0),
        "total_score":        row.get("total_score", 0),
        "total_coins":        row.get("total_coins", 0),
        "mission_coins":      row.get("mission_coins", 0),
        "total_mission_coins_earned": row.get("total_mission_coins_earned", 0),
        "owned_skins":        row.get("owned_skins") or ["Flappy"],
        "owned_backgrounds":  row.get("owned_backgrounds") or [],
        "owned_musics":       row.get("owned_musics") or [],
        "selected_skin":      row.get("selected_skin", "Flappy"),
        "selected_bg":        row.get("selected_bg"),
        "selected_music":     row.get("selected_music"),
        "selected_music_menu":row.get("selected_music_menu"),
        "auto_next_music":    row.get("auto_next_music", False),
        "music_vol_menu":     row.get("music_vol_menu", 0.5),
        "music_vol_game":     row.get("music_vol_game", 0.5),
        "sfx_vol_menu":       row.get("sfx_vol_menu", 0.7),
        "sfx_vol_game":       row.get("sfx_vol_game", 0.7),
        "avatar_color":       row.get("avatar_color") or [80, 180, 255],
        "avatar_image_path":  row.get("avatar_image_path"),
        "streak1_days":       row.get("streak1_days", 0),
        "streak1_last_day":   row.get("streak1_last_day", ""),
        "completed_levels":   row.get("completed_levels") or [],
        "liked_levels":       row.get("liked_levels") or [],
        "missions":       row.get("missions") or {},
        "missions_stats": row.get("missions_stats") or {},
        "is_admin":       row.get("is_admin", False),
        "is_banned":           row.get("is_banned", False),
    }

def _player_to_row(p):
    # Pour display_name : le cache est la source de vérité (le watcher peut l'avoir mis à jour
    # sans que l'objet player en mémoire ait encore été synchronisé)
    _name = p.get("name", "")
    _dn = _display_name_cache.get(_name) or p.get("display_name") or _name
    return {
        "name":               _name,
        "display_name":       _dn,
        "best_score":         p.get("best_score", 0),
        "games_played":       p.get("games_played", 0),
        "total_score":        p.get("total_score", 0),
        "total_coins":        p.get("total_coins", 0),
        "mission_coins":      p.get("mission_coins", 0),
        "total_mission_coins_earned": p.get("total_mission_coins_earned", 0),
        "owned_skins":        p.get("owned_skins", ["Flappy"]),
        "owned_backgrounds":  p.get("owned_backgrounds", []),
        "owned_musics":       p.get("owned_musics", []),
        "selected_skin":      p.get("selected_skin", "Flappy"),
        "selected_bg":        p.get("selected_bg"),
        "selected_music":     p.get("selected_music"),
        "selected_music_menu":p.get("selected_music_menu"),
        "auto_next_music":    p.get("auto_next_music", False),
        "music_vol_menu":     p.get("music_vol_menu", 0.5),
        "music_vol_game":     p.get("music_vol_game", 0.5),
        "sfx_vol_menu":       p.get("sfx_vol_menu", 0.7),
        "sfx_vol_game":       p.get("sfx_vol_game", 0.7),
        "avatar_color":       p.get("avatar_color", [80, 180, 255]),
        "avatar_image_path":  p.get("avatar_image_path"),
        "streak1_days":       p.get("streak1_days", 0),
        "streak1_last_day":   p.get("streak1_last_day", ""),
        "completed_levels":   p.get("completed_levels", []),
        "liked_levels":       p.get("liked_levels", []),
        "missions":       p.get("missions", {}),
        "missions_stats": p.get("missions_stats", {}),
    }

# ══════════════════════════════════════════════════════════════════════════════
#  API JOUEURS (interface identique à l'ancien data.py)
# ══════════════════════════════════════════════════════════════════════════════
DATA_FILE = BACKUP_FILE = BUG_FILE = ":supabase:"
BACKUP_INTERVAL = 60
# ── Système STOP global via Supabase (remplace le fichier local) ──────────────
STOP_FILE = ":supabase:"   # plus de fichier local

def _get_stop_file_path(): return ":supabase:"

_stop_state_cache    = False
_stop_state_cache_ts = 0.0

def stop_file_exists() -> bool:
    """Vérifie dans Supabase config si le jeu est en maintenance."""
    global _stop_state_cache, _stop_state_cache_ts
    # Cache 5 secondes pour ne pas spammer Supabase
    if (time.time() - _stop_state_cache_ts) < 5.0:
        return _stop_state_cache
    try:
        rows = _sb_get("config", "key=eq.stop_global")
        if rows:
            val = rows[0].get("value", {})
            _stop_state_cache = bool(val.get("active", False))
        else:
            _stop_state_cache = False
        _stop_state_cache_ts = time.time()
    except:
        pass
    return _stop_state_cache

def create_stop_file() -> bool:
    """Active la maintenance globale dans Supabase."""
    global _stop_state_cache, _stop_state_cache_ts
    try:
        # Upsert la clé stop_global
        r = _requests.post(
            f"{SUPABASE_URL}/rest/v1/config",
            json={"key": "stop_global", "value": {"active": True, "since": time.strftime("%Y-%m-%d %H:%M:%S")}},
            headers={**_sb_headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
            timeout=4
        )
        if r.status_code in (200, 201):
            _stop_state_cache    = True
            _stop_state_cache_ts = time.time()
            return True
        # Fallback PATCH
        r2 = _requests.patch(
            f"{SUPABASE_URL}/rest/v1/config?key=eq.stop_global",
            json={"value": {"active": True, "since": time.strftime("%Y-%m-%d %H:%M:%S")}},
            headers=_sb_headers(), timeout=4
        )
        _stop_state_cache    = True
        _stop_state_cache_ts = time.time()
        return True
    except Exception as e:
        print(f"[STOP] create error: {e}")
        return False

def remove_stop_file() -> bool:
    """Désactive la maintenance globale dans Supabase."""
    global _stop_state_cache, _stop_state_cache_ts
    try:
        _requests.patch(
            f"{SUPABASE_URL}/rest/v1/config?key=eq.stop_global",
            json={"value": {"active": False}},
            headers=_sb_headers(), timeout=4
        )
        _stop_state_cache    = False
        _stop_state_cache_ts = time.time()
        return True
    except Exception as e:
        print(f"[STOP] remove error: {e}")
        return False

def _acquire_file_lock(path, timeout=5.0): return None
def _release_file_lock(fd): pass

def random_avatar_color():
    return random.choice([[255,80,80],[80,180,255],[80,220,120],[220,120,255],[255,180,60],[60,220,220]])

def load_data():
    return {"players": {}, "current_player": None}

def get_player(data, name):
    cached = _pc_get(name)
    if cached:
        data["players"][name] = cached
        return cached
    rows = _sb_get("players", f"name=eq.{name}&limit=1")
    if rows:
        p = _row_to_player(rows[0])
        # Pré-remplir le cache display_name
        if rows[0].get("display_name"):
            _display_name_cache[name] = rows[0]["display_name"]
    else:
        p = {"name": name, "display_name": name, "best_score": 0, "games_played": 0,
             "total_score": 0, "total_coins": 0, "mission_coins": 0,
             "owned_skins": ["Flappy"], "owned_backgrounds": [], "owned_musics": [],
             "selected_skin": "Flappy", "avatar_color": random_avatar_color(),
             "missions": {}, "missions_stats": {}, "streak1_days": 0,
             "streak1_last_day": "", "completed_levels": [], "liked_levels": [],
             "auto_next_music": False, "music_vol_menu": 0.5, "music_vol_game": 0.5,
             "sfx_vol_menu": 0.7, "sfx_vol_game": 0.7, "is_admin": False, "is_banned": False}
        _sb_post("players", _player_to_row(p), upsert=True)
    data["players"][name] = p
    _pc_set(name, p)
    return p

def save_data(data):
    for name, p in data.get("players", {}).items():
        _sb_post("players", _player_to_row(p), upsert=True)
        _pc_set(name, p)

def save_data_async(data):
    for name, p in data.get("players", {}).items():
        _save_queue.put((name, dict(p)))

def save_player_async(player):
    """Sauvegarde un joueur directement (sans passer par data['players'])."""
    if player and player.get("name"):
        _save_queue.put((player["name"], dict(player)))

def start_backup_thread(): return None
def stop_backup_thread(): pass

def get_leaderboard(data):
    rows = _sb_get("players", "order=best_score.desc&limit=15&is_banned=eq.false")
    result = []
    for r in rows:
        p = _row_to_player(r)
        # Pré-remplir le cache display_name
        if r.get("display_name"):
            _display_name_cache[r["name"]] = r["display_name"]
        result.append(p)
    return result

def update_player_score(data, name, score, coins_earned):
    p = get_player(data, name)
    p["games_played"] = p.get("games_played", 0) + 1
    p["total_score"]  = p.get("total_score", 0) + score
    p["total_coins"]  = p.get("total_coins", 0) + coins_earned
    if score > p.get("best_score", 0): p["best_score"] = score
    _sb_post("players", _player_to_row(p), upsert=True)
    _pc_set(name, p)

def update_first_place_streak(data):
    import datetime
    today = time.strftime("%Y-%m-%d")
    lb = get_leaderboard(data)
    if not lb: return
    leader = lb[0]
    p = get_player(data, leader["name"])
    if p.get("streak1_last_day") == today: return
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    p["streak1_days"] = p.get("streak1_days", 0) + 1 if p.get("streak1_last_day") == yesterday else 1
    p["streak1_last_day"] = today
    _sb_post("players", _player_to_row(p), upsert=True)
    _pc_set(leader["name"], p)

def player_owns_skin(player, skin_key):
    return skin_key in player.get("owned_skins", ["Flappy"])

def player_owns_background(player, bg_key):
    return bg_key in player.get("owned_backgrounds", [])

def player_owns_music(player, music_key):
    return music_key in player.get("owned_musics", [])

def _buy_skin_data(data, player, skin_key, skin_prices):
    price = skin_prices.get(skin_key, 9999)
    if player.get("total_coins", 0) >= price and not player_owns_skin(player, skin_key):
        player["total_coins"] -= price
        player.setdefault("owned_skins", ["Flappy"]).append(skin_key)
        _sb_post("players", _player_to_row(player), upsert=True)
        _pc_set(player["name"], player)
        return True
    return False

def _buy_bg_data(data, player, bg_key, bg_items):
    item = next((b for b in bg_items if b["key"] == bg_key), None)
    if not item: return False
    if player.get("mission_coins", 0) >= item["price"] and not player_owns_background(player, bg_key):
        player["mission_coins"] -= item["price"]
        player.setdefault("owned_backgrounds", []).append(bg_key)
        _sb_post("players", _player_to_row(player), upsert=True)
        _pc_set(player["name"], player)
        return True
    return False

def _buy_music_data(data, player, music_key, music_items):
    item = next((m for m in music_items if m["key"] == music_key), None)
    if not item: return False
    if player.get("mission_coins", 0) >= item["price"] and not player_owns_music(player, music_key):
        player["mission_coins"] -= item["price"]
        player.setdefault("owned_musics", []).append(music_key)
        _sb_post("players", _player_to_row(player), upsert=True)
        _pc_set(player["name"], player)
        return True
    return False

def save_bug_report(player_name, bug_text):
    return _sb_post("bug_reports", {"player_name": player_name, "text": bug_text}) is not None

_banner_cache = None
_banner_cache_ts = 0.0

def get_banner_config(data):
    global _banner_cache, _banner_cache_ts
    if _banner_cache is not None and (time.time() - _banner_cache_ts) < 30.0:
        return _banner_cache
    try:
        rows = _sb_get("config", "key=eq.banner")
        if rows:
            val = rows[0].get("value", {})
            _banner_cache = {"enabled": bool(val.get("enabled", False)),
                             "message": str(val.get("message", "Bienvenue !"))}
            _banner_cache_ts = time.time()
            return _banner_cache
    except: pass
    return {"enabled": False, "message": "Bienvenue sur Flappy Bird !"}

def set_banner_config(data, enabled, message):
    global _banner_cache, _banner_cache_ts
    _sb_patch("config", "key=eq.banner", {"value": {"enabled": enabled, "message": message}})
    # Invalider le cache local immédiatement
    _banner_cache    = {"enabled": enabled, "message": message}
    _banner_cache_ts = time.time()

def register_session(session_name):
    rows = _sb_get("players", f"name=eq.{session_name}&limit=1")
    if not rows:
        p = {"name": session_name, "display_name": session_name, "best_score": 0,
             "owned_skins": ["Flappy"], "avatar_color": random_avatar_color(),
             "missions": {}, "missions_stats": {}}
        _sb_post("players", _player_to_row(p), upsert=True)

def get_display_name(session_name):
    """Retourne le pseudo affiché. Cache permanent en mémoire (pas d appel réseau après le 1er)."""
    if session_name in _display_name_cache:
        return _display_name_cache[session_name]
    try:
        rows = _sb_get("players", f"name=eq.{session_name}&select=display_name&limit=1")
        if rows and rows[0].get("display_name"):
            _display_name_cache[session_name] = rows[0]["display_name"]
            return _display_name_cache[session_name]
    except:
        pass
    _display_name_cache[session_name] = session_name
    return session_name

def _invalidate_display_name(session_name):
    """Invalider le cache pour un joueur (après changement de pseudo)."""
    _display_name_cache.pop(session_name, None)

def set_display_name(session_name, display_name):
    _sb_patch("players", f"name=eq.{session_name}", {"display_name": display_name.strip()})
    _pc_clear(session_name)
    _invalidate_display_name(session_name)
    _display_name_cache[session_name] = display_name.strip()

def submit_pseudo_request(session_name, requested_pseudo):
    _sb_post("pseudo_requests", {"session_name": session_name, "requested": requested_pseudo.strip()}, upsert=True)

def get_pending_requests():
    rows = _sb_get("pseudo_requests", "order=created_at.asc")
    return [{"session": r["session_name"], "pseudo": r["requested"],
             "date": r["created_at"][:16].replace("T", " ")} for r in rows]

def accept_pseudo_request(session_name):
    rows = _sb_get("pseudo_requests", f"session_name=eq.{session_name}&limit=1")
    if not rows: return False
    set_display_name(rows[0]["session_name"], rows[0]["requested"])
    _sb_delete("pseudo_requests", f"session_name=eq.{session_name}")
    return True

def reject_pseudo_request(session_name):
    _sb_delete("pseudo_requests", f"session_name=eq.{session_name}")
    return True

def has_pending_request(session_name):
    return bool(_sb_get("pseudo_requests", f"session_name=eq.{session_name}&limit=1"))

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN USERS (depuis Supabase config)
# ══════════════════════════════════════════════════════════════════════════════
_admin_users_cache = None
_admin_users_cache_ts = 0.0

def _get_admin_users():
    global _admin_users_cache, _admin_users_cache_ts
    # Cache 60 secondes — pas besoin de re-fetch à chaque appel is_admin()
    if _admin_users_cache is not None and (time.time() - _admin_users_cache_ts) < 60.0:
        return _admin_users_cache
    try:
        rows = _sb_get("config", "key=eq.admins")
        if rows:
            _admin_users_cache = rows[0].get("value", {}).get("users", [])
            _admin_users_cache_ts = time.time()
            return _admin_users_cache
    except: pass
    _admin_users_cache = ["spertuiselcosse", "sperc"]
    return _admin_users_cache

ADMIN_USERS = ["spertuiselcosse", "sperc"]   # fallback statique

def is_admin(player):
    return player.get("is_admin", False) or player.get("name", "") in ADMIN_USERS

# ══════════════════════════════════════════════════════════════════════════════
#  NIVEAUX (ex-levels_data.py)
# ══════════════════════════════════════════════════════════════════════════════
LEVELS_FILE     = ":supabase:"
OFFICIAL_LEVELS = []

def _row_to_level(row):
    # Désérialiser "layout" qui peut être un dict (nouveau format) ou une liste (ancien)
    raw_layout = row.get("layout", {})
    if isinstance(raw_layout, dict):
        pipes       = raw_layout.get("pipes", [])
        length      = raw_layout.get("length", 3000)
        completable = raw_layout.get("completable", False)
        liked_by    = raw_layout.get("liked_by", [])
        coords      = raw_layout.get("coords", "pixels")  # "normalized" ou "pixels"
    else:
        # Ancien format : layout était une liste brute (ou vide)
        pipes       = raw_layout if isinstance(raw_layout, list) else []
        length      = 3000
        completable = False
        liked_by    = []
        coords      = "pixels"

    # Dénormaliser les coordonnées si elles sont en 0.0-1.0
    if coords == "normalized":
        # GROUND_HEIGHT = 200, défini après cette fonction mais avant tout appel réel
        _gh = globals().get("GROUND_HEIGHT", 200)
        _game_zone = SCREEN_HEIGHT - _gh
        def _denorm(p):
            pd = dict(p)
            pd["gap_y"] = p["gap_y"] * _game_zone
            pd["gap_h"] = p["gap_h"] * _game_zone
            return pd
        pipes = [_denorm(p) for p in pipes]

    return {
        "id": row["id"], "author": row.get("author",""), "name": row.get("name",""),
        "level_type": row.get("level_type","community"), "published": row.get("published",False),
        "likes": row.get("likes",0), "reward_coins": row.get("reward_coins",0),
        "reward_mission_coins": row.get("reward_mission_coins",0),
        "pipes":       pipes,
        "length":      length,
        "completable": completable,
        "liked_by":    liked_by,
        "last_edited": row.get("last_edited",0),
        "speed":       row.get("speed", 7.0),
    }

def _level_to_row(lv):
    # Sérialiser les tuyaux + métadonnées du niveau dans "layout" (JSON stocké en Supabase)
    # Les coordonnées gap_y / gap_h sont normalisées en 0.0-1.0 par rapport à la zone de jeu
    # pour être indépendantes de la résolution d'écran.
    _gh = globals().get("GROUND_HEIGHT", 200)
    _game_zone = SCREEN_HEIGHT - _gh  # hauteur de la zone jouable
    def _norm_pipe(p):
        pn = dict(p)
        pn["gap_y"] = round(p["gap_y"] / _game_zone, 6)
        pn["gap_h"] = round(p["gap_h"] / _game_zone, 6)
        return pn
    layout_data = {
        "pipes":       [_norm_pipe(p) for p in lv.get("pipes", [])],
        "length":      lv.get("length", 3000),
        "completable": lv.get("completable", False),
        "liked_by":    lv.get("liked_by", []),
        "coords":      "normalized",   # marqueur de version du format
    }
    return {
        "id": lv["id"], "author": lv.get("author",""), "name": lv.get("name","Nouveau niveau"),
        "level_type": lv.get("level_type","community"), "published": lv.get("published",False),
        "likes": lv.get("likes",0), "reward_coins": lv.get("reward_coins",0),
        "reward_mission_coins": lv.get("reward_mission_coins",0),
        "layout": layout_data, "last_edited": lv.get("last_edited", int(time.time())),
        "speed": lv.get("speed", 7.0),
    }

def load_levels():
    try:
        rows = _sb_get("levels", "order=last_edited.desc")
        return {
            "community": [_row_to_level(r) for r in rows if r.get("level_type") == "community"],
            "official":  [_row_to_level(r) for r in rows if r.get("level_type") == "official"],
        }
    except: return {"community": [], "official": []}

def save_levels(lvl_data):
    for lv in lvl_data.get("community", []) + lvl_data.get("official", []):
        _sb_post("levels", _level_to_row(lv), upsert=True)

def save_level(lv):
    """Sauvegarde un seul niveau. Tente POST upsert, puis PATCH si echec."""
    row = _level_to_row(lv)
    result = _sb_post("levels", row, upsert=True)
    if result is None:
        # Fallback PATCH direct sur l'ID
        _sb_patch("levels", f"id=eq.{lv['id']}", row)

def delete_level_from_file(level_id):
    _sb_delete("levels", f"id=eq.{level_id}&level_type=eq.community")
    return load_levels()

def delete_official_level_from_file(level_id):
    _sb_delete("levels", f"id=eq.{level_id}&level_type=eq.official")
    return load_levels()

def unpublish_level_in_file(level_id):
    _sb_patch("levels", f"id=eq.{level_id}", {"published": False})
    return load_levels()

def update_official_level_reward_in_file(level_id, reward_coins, reward_mission_coins):
    _sb_patch("levels", f"id=eq.{level_id}", {
        "reward_coins": reward_coins, "reward_mission_coins": reward_mission_coins,
        "last_edited": int(time.time())})
    return load_levels()

def get_player_completed_levels(player): return player.get("completed_levels", [])
def get_player_liked_levels(player): return player.get("liked_levels", [])

def mark_level_completed(player, data, level_id, coins_reward, mc_reward):
    completed = player.get("completed_levels", [])
    if level_id not in completed:
        completed.append(level_id)
        player["completed_levels"] = completed
        player["total_coins"]   = player.get("total_coins",   0) + coins_reward
        player["mission_coins"] = player.get("mission_coins", 0) + mc_reward
        player["total_mission_coins_earned"] = player.get("total_mission_coins_earned", 0) + mc_reward
        save_data(data)
        return True
    return False

def new_level_id(player_name):
    ts   = int(time.time() * 1000) % 9999999
    safe = "".join(c for c in player_name if c.isalnum())[:6]
    return f"usr_{safe}_{ts}"

# ══════════════════════════════════════════════════════════════════════════════
#  AUDIO (ex-audio.py) — charge les fichiers depuis Supabase Storage
# ══════════════════════════════════════════════════════════════════════════════
# Le mixer est initialisé via pygame.init() — pas besoin de re-init séparé

wing_snd         = 'assets/audio/wing.wav'
hit_snd          = 'assets/audio/hit.wav'
coin_snd         = 'assets/audio/coin.mp3'
background_music = 'assets/audio/musique_default_game.mp3'
menu_music       = 'assets/audio/musique_default_menu.mp3'

_MUSIC_KEY_DEFAULT_GAME = "__default_game__"
_MUSIC_KEY_DEFAULT_MENU = "__default_menu__"

def _load_music_items_sb():
    try:
        rows = _sb_get("config", "key=eq.musiques")
        data = rows[0].get("value", {"musiques": []}) if rows else {"musiques": []}
        items = []
        for m in data.get("musiques", []):
            col = m.get("color", [255, 160, 60])
            if isinstance(col, list): col = tuple(col)
            items.append({"key": m["key"], "name": m["name"], "file": m["file"],
                           "price": m.get("price", 100), "color": col,
                           "artiste": m.get("artiste",""), "duree": m.get("duree","")})
        return items
    except Exception as e:
        print(f"[MUSIC] {e}"); return []

def reload_music_items():
    global MUSIC_ITEMS
    MUSIC_ITEMS = _load_music_items_sb()

# Chargement initial synchrone (petit appel Supabase, acceptable au démarrage)
MUSIC_ITEMS = _load_music_items_sb()

_sound_cache = {}
def _get_sound(path):
    if path not in _sound_cache:
        try: _sound_cache[path] = _pygame_load_sound(path)
        except: _sound_cache[path] = None
    return _sound_cache[path]

# Pré-charger les sons de façon différée (après pygame.init complet)
# On ne les charge pas ici pour éviter que le mixer ne soit pas encore prêt

_music_vol_menu = 0.5; _music_vol_game = 0.5
_sfx_vol_menu   = 0.7; _sfx_vol_game   = 0.7
_current_context = "menu"
_MUSIC_END_EVENT = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(_MUSIC_END_EVENT)
_auto_next_enabled  = False
_auto_next_playlist = []
_auto_next_idx      = 0

def _music_volume(): return _music_vol_game if _current_context == "game" else _music_vol_menu
def _sfx_volume():   return _sfx_vol_game   if _current_context == "game" else _sfx_vol_menu

def set_context(ctx):
    global _current_context; _current_context = ctx
    try: pygame.mixer.music.set_volume(_music_volume())
    except: pass

def set_music_volume_menu(v):
    global _music_vol_menu; _music_vol_menu = max(0.0, min(1.0, v))
    if _current_context == "menu":
        try: pygame.mixer.music.set_volume(_music_vol_menu)
        except: pass

def set_music_volume_game(v):
    global _music_vol_game; _music_vol_game = max(0.0, min(1.0, v))
    if _current_context == "game":
        try: pygame.mixer.music.set_volume(_music_vol_game)
        except: pass

def set_sfx_volume_menu(v):  global _sfx_vol_menu;  _sfx_vol_menu  = max(0.0, min(1.0, v))
def set_sfx_volume_game(v):  global _sfx_vol_game;  _sfx_vol_game  = max(0.0, min(1.0, v))
def set_music_volume(v):
    if _current_context == "game": set_music_volume_game(v)
    else: set_music_volume_menu(v)
def set_sfx_volume(v):
    if _current_context == "game": set_sfx_volume_game(v)
    else: set_sfx_volume_menu(v)

def play_sound(path):
    try:
        snd = _get_sound(path)
        if snd: snd.set_volume(_sfx_volume()); snd.play()
    except: pass

def _resolve_music_file(music_key):
    if music_key is None: return None
    if music_key == _MUSIC_KEY_DEFAULT_GAME: return _pygame_load_music(background_music)
    if music_key == _MUSIC_KEY_DEFAULT_MENU: return _pygame_load_music(menu_music)
    item = next((m for m in MUSIC_ITEMS if m["key"] == music_key), None)
    return _pygame_load_music(item["file"]) if item else None

def _switch_music_smart(track):
    global _auto_next_idx
    try:
        current = getattr(_switch_music_smart, '_current_track', None)
        if current == track and pygame.mixer.music.get_busy(): return
        pygame.mixer.music.load(track)
        pygame.mixer.music.set_volume(_music_volume())
        pygame.mixer.music.play(0 if _auto_next_enabled else -1)
        _switch_music_smart._current_track = track
        if _auto_next_enabled and track in _auto_next_playlist:
            _auto_next_idx = _auto_next_playlist.index(track)
    except: pass

def play_game_music(music_file=None):
    set_context("game")
    track = music_file if music_file and os.path.exists(music_file) else _pygame_load_music(background_music)
    _switch_music_smart(track)

def play_menu_music(music_file=None):
    set_context("menu")
    track = music_file if music_file and os.path.exists(music_file) else _pygame_load_music(menu_music)
    _switch_music_smart(track)

def stop_music():
    try: pygame.mixer.music.stop()
    except: pass

def set_auto_next(enabled, player=None):
    global _auto_next_enabled; _auto_next_enabled = bool(enabled)
    if player:
        # S'assurer que MUSIC_ITEMS est chargé avant de rebuild
        if not MUSIC_ITEMS:
            reload_music_items()
        _rebuild_playlist(player)
    if not enabled:
        try:
            current = getattr(_switch_music_smart, '_current_track', None)
            if current and not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)
        except: pass

def _rebuild_playlist(player):
    global _auto_next_playlist, _auto_next_idx
    owned = player.get("owned_musics", [])
    paths = []
    bg = _pygame_load_music(background_music)
    if os.path.exists(bg): paths.append(bg)
    for key in owned:
        item = next((m for m in MUSIC_ITEMS if m["key"] == key), None)
        if item:
            lp = _pygame_load_music(item["file"])
            if os.path.exists(lp) and lp not in paths: paths.append(lp)
    _auto_next_playlist = paths
    current = getattr(_switch_music_smart, '_current_track', None)
    _auto_next_idx = _auto_next_playlist.index(current) if current in _auto_next_playlist else 0

def handle_music_end_event(player=None):
    global _auto_next_idx
    if not _auto_next_enabled or not _auto_next_playlist:
        try:
            current = getattr(_switch_music_smart, '_current_track', None)
            if current: pygame.mixer.music.play(-1)
        except: pass
        return
    _auto_next_idx = (_auto_next_idx + 1) % len(_auto_next_playlist)
    next_track = _auto_next_playlist[_auto_next_idx]
    try:
        pygame.mixer.music.load(next_track)
        pygame.mixer.music.set_volume(_music_volume())
        pygame.mixer.music.play(0)
        _switch_music_smart._current_track = next_track
    except Exception as e: print(f"[AUTO-NEXT] {e}")

def load_volumes_from_player(player):
    set_music_volume_menu(player.get("music_vol_menu", player.get("music_volume", 0.5)))
    set_music_volume_game(player.get("music_vol_game", player.get("music_volume", 0.5)))
    set_sfx_volume_menu(player.get("sfx_vol_menu",    player.get("sfx_volume",   0.7)))
    set_sfx_volume_game(player.get("sfx_vol_game",    player.get("sfx_volume",   0.7)))

# Wrappers locaux pour buy_* (accèdent aux constantes locales SKIN_PRICES etc.)
def update_missions_after_purchase(player, data):
    """Vérifie les missions basées sur l'inventaire après un achat (skins, bgs, musics)."""
    init_missions(player)
    s = player["missions_stats"]
    # Synchroniser les stats d'inventaire
    s["skins_owned"]  = len(player.get("owned_skins", ["Flappy"]))
    s["bgs_owned"]    = len(player.get("owned_backgrounds", []))
    s["musics_owned"] = len(player.get("owned_musics", []))

    stat_map = {
        "skins_owned":   s["skins_owned"],
        "bgs_owned":     s["bgs_owned"],
        "musics_owned":  s["musics_owned"],
        "coins_spent":   s.get("coins_spent", 0),
        "coins_balance": player.get("total_coins", 0),
    }

    newly_completed = []
    for mid, mtype, label, desc, goal, reward in ALL_MISSIONS.values():
        if mtype not in stat_map:
            continue
        entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
        if entry["claimed"]:
            continue
        val = stat_map[mtype]
        old_prog = entry["progress"]
        new_prog = min(goal, val)
        entry["progress"] = new_prog
        player["missions"][mid] = entry
        if new_prog >= goal and old_prog < goal:
            newly_completed.append(mid)

    save_data(data)
    return newly_completed


def _track_purchase(player, amount):
    """Ajoute `amount` aux stats coins_spent (total + aujourd'hui)."""
    if "missions_stats" in player:
        s = player["missions_stats"]
        s["coins_spent"]       = s.get("coins_spent", 0)       + amount
        s["coins_spent_today"] = s.get("coins_spent_today", 0) + amount
        # Mettre à jour skins/bgs/musics possédés
        s["skins_owned"]  = len(player.get("owned_skins", ["Flappy"]))
        s["bgs_owned"]    = len(player.get("owned_backgrounds", []))
        s["musics_owned"] = len(player.get("owned_musics", []))

def buy_skin(data, player, skin_key):
    # La déduction de total_coins est gérée dans data.py (buy_skin)
    # On ne déduit PAS ici pour éviter la double déduction
    result = _buy_skin_data(data, player, skin_key, SKIN_PRICES)
    if result:
        price = SKIN_PRICES.get(skin_key, 0)
        _track_purchase(player, price)
        update_missions_after_purchase(player, data)
    return result

def buy_background(data, player, bg_key):
    # La déduction de mission_coins est gérée dans data.py (buy_background)
    # On ne déduit PAS ici pour éviter la double déduction
    result = _buy_bg_data(data, player, bg_key, BG_ITEMS)
    if result:
        price = next((b["price"] for b in BG_ITEMS if b["key"] == bg_key), 0)
        _track_purchase(player, price)
        update_missions_after_purchase(player, data)
    return result

def buy_music(data, player, music_key):
    # La déduction de mission_coins est gérée dans data.py (buy_music)
    # On ne déduit PAS ici pour éviter la double déduction
    result = _buy_music_data(data, player, music_key, MUSIC_ITEMS)
    if result:
        price = next((m.get("price", 0) for m in MUSIC_ITEMS if m["key"] == music_key), 0)
        _track_purchase(player, price)
        update_missions_after_purchase(player, data)
    return result

# Récupérer la zone de travail Windows (écran sans la barre des tâches)
# sans créer de fenêtre temporaire (évite le flash)
try:
    import ctypes
    _rc = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(_rc), 0)  # SPI_GETWORKAREA = 48
    SCREEN_WIDTH  = _rc.right  - _rc.left
    SCREEN_HEIGHT = _rc.bottom - _rc.top
    _work_left    = _rc.left
    _work_top     = _rc.top
except Exception:
    import ctypes
    _sm_cx = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
    _sm_cy = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
    SCREEN_WIDTH  = _sm_cx
    SCREEN_HEIGHT = _sm_cy - 70
    _work_left    = 0
    _work_top     = 0

# Positionner la fenêtre AVANT sa création via SDL (évite le snap Windows)
# On soustrait la hauteur de la barre de titre pour que la fenêtre soit bien calée
try:
    _title_bar_h = ctypes.windll.user32.GetSystemMetrics(4)  # SM_CYCAPTION
    _border_h    = ctypes.windll.user32.GetSystemMetrics(6)  # SM_CYBORDER
except Exception:
    _title_bar_h = 30
    _border_h    = 1
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{_work_left},{_work_top + _title_bar_h + _border_h}"

SPEED         = 15
GRAVITY       = 0.8
GAME_SPEED    = 8
FPS           = 60
ACCELERATION  = 0.2
GROUND_WIDTH  = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 200
PIPE_WIDTH    = 160
PIPE_HEIGHT   = 1000
PIPE_GAP      = 300
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)


# ── Palette ───────────────────────────────────────────────────────────────────
GOLD       = (255, 215,  60)
GOLD_DARK  = (180, 130,  10)
GOLD_LIGHT = (255, 245, 160)
NIGHT      = (  8,  10,  22)
NIGHT2     = ( 14,  18,  42)
PANEL_BG   = ( 12,  16,  36)
WHITE      = (255, 255, 255)
RED_HOT    = (230,  50,  50)
GREEN_SOFT = ( 60, 210, 110)
CYAN       = ( 70, 210, 255)
GREY       = (130, 135, 160)

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTÈME DE NOTIFICATIONS GLOBALES (haut droite de l'écran)
# ══════════════════════════════════════════════════════════════════════════════
_notifs = []   # liste de {"msg", "col", "timer", "max_timer"}

def push_notif(msg: str, col=None, duration=300):
    """Ajoute une notification flottante en haut à droite."""
    if col is None: col = (60, 210, 110)
    _notifs.append({"msg": msg, "col": col, "timer": duration, "max_timer": duration})
    if len(_notifs) > 5:
        _notifs.pop(0)

def draw_notifs():
    """À appeler à chaque frame — dessine les notifs actives et les fait disparaître."""
    fn = pygame.font.SysFont("Verdana", 16)
    NOTIF_W = 340
    NOTIF_H = 46
    NOTIF_X = SCREEN_WIDTH - NOTIF_W - 18
    NOTIF_Y_START = 18
    GAP = 10
    to_remove = []
    for idx, n in enumerate(_notifs):
        n["timer"] -= 1
        if n["timer"] <= 0:
            to_remove.append(n)
            continue
        alpha = min(255, n["timer"] * 4)
        # Slide-in depuis la droite
        slide = max(0, min(1.0, 1.0 - (n["timer"] - 30) / 30.0)) if n["timer"] < 30 else 1.0
        ox = int((1.0 - slide) * (NOTIF_W + 20))
        ny = NOTIF_Y_START + idx * (NOTIF_H + GAP)
        nx = NOTIF_X + ox
        s = pygame.Surface((NOTIF_W, NOTIF_H), pygame.SRCALPHA)
        bg_col = (10, 22, 40, min(230, alpha))
        pygame.draw.rect(s, bg_col, (0, 0, NOTIF_W, NOTIF_H), border_radius=12)
        border = (*n["col"][:3], min(220, alpha))
        pygame.draw.rect(s, border, (0, 0, NOTIF_W, NOTIF_H), 2, border_radius=12)
        # Barre de progression
        prog_w = int((NOTIF_W - 4) * n["timer"] / n["max_timer"])
        if prog_w > 0:
            pygame.draw.rect(s, (*n["col"][:3], 80), (2, NOTIF_H - 4, prog_w, 3), border_radius=2)
        # Texte
        txt = fn.render(n["msg"], True, n["col"])
        txt.set_alpha(alpha)
        s.blit(txt, (14, NOTIF_H // 2 - txt.get_height() // 2))
        screen.blit(s, (nx, ny))
    for n in to_remove:
        if n in _notifs:
            _notifs.remove(n)

# ── Prix des skins ─────────────────────────────────────────────────────────────
SKIN_PRICES = {
    "Flappy":  0,
    "Redbird": 3,
    "Mouche":  5,
    "Avion":   10,
    "Ninja": 20,
    "Avion de chasse" : 50,
    "Nyancat": 100,
    
}

# ── Fonds d'écran disponibles dans la boutique ────────────────────────────────
# Pour ajouter un fond : copie-colle la ligne ci-dessous et change le chemin de l'image, le nom et le prix.
# {"key": "background_custom_2", "name": "Fond 2", "file": "assets/sprites/background_custom_2.png", "price": 100, "color": (60, 200, 255)},
BG_ITEMS = [
    {"key": "background_custom_2", "name": "Fond Personnalisé 2", "file": "assets/sprites/background_custom_2.png", "price": 100, "color": (60, 200, 255)},
    {"key": "background_custom_3", "name": "Fond Personnalisé 3", "file": "assets/sprites/background_custom_3.png", "price": 150, "color": (60, 200, 255)},
    {"key": "background_custom_4", "name": "Fond Personnalisé 4", "file": "assets/sprites/background_custom_4.png", "price": 200, "color": (60, 200, 255)},
    {"key": "background_custom_5", "name": "Fond Personnalisé 5", "file": "assets/sprites/background_custom_5.png", "price": 250, "color": (60, 200, 255)},
    {"key": "background_custom_6", "name": "Fond Personnalisé 6", "file": "assets/sprites/background_custom_6.png", "price": 300, "color": (60, 200, 255)},
    {"key": "background_custom_7", "name": "Fond Personnalisé 7", "file": "assets/sprites/background_custom_7.png", "price": 350, "color": (60, 200, 255)},
    {"key": "background_custom_1", "name": "Fond Personnalisé 1", "file": "assets/sprites/background_custom_1.png", "price": 500, "color": (60, 200, 255)},
]


# ══════════════════════════════════════════════════════════════════════════════
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.RESIZABLE,
    vsync=1
)
pygame.display.set_caption('Flappy Bird')
try:
    _icon = _pygame_load('assets/sprites/Flappy_Bird_icon.ico')
    pygame.display.set_icon(_icon)
except Exception:
    pass

# ══════════════════════════════════════════════════════════════════════════════
#  ÉCRAN DE CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════════
_ld_clock = pygame.time.Clock()
_ld_t     = 0.0          # temps animé
_ld_step  = ""           # texte étape courante
_ld_prog  = 0.0          # progression 0.0 → 1.0
_ld_anim  = 0            # frame animée (points clignotants)

# Couleurs disponibles dès le départ (avant chargement des constantes)
_LD_NIGHT   = (8, 10, 22)
_LD_GOLD    = (255, 215, 60)
_LD_GOLD_D  = (180, 130, 10)
_LD_WHITE   = (255, 255, 255)
_LD_GREY    = (100, 110, 140)
_LD_CYAN    = (70, 210, 255)
_LD_GREEN   = (60, 210, 110)

# Fonts de chargement (basiques, chargées en premier)
_ld_font_title = pygame.font.SysFont('Impact', 72)
_ld_font_sub   = pygame.font.SysFont('Impact', 32)
_ld_font_step  = pygame.font.SysFont('Verdana', 17)
_ld_font_pct   = pygame.font.SysFont('Impact', 28)

# Tentative de chargement du logo/fond pour l'écran de chargement
_ld_bg = None
try:
    _raw_ld = _pygame_load('assets/sprites/background-day.png').convert()
    _ld_bg  = pygame.transform.scale(_raw_ld, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    pass

def _loading_draw(progress: float, step_label: str):
    """Dessine l'écran de chargement complet et flip."""
    global _ld_t, _ld_anim
    _ld_t    += 0.04
    _ld_anim  = int(_ld_t * 2) % 4   # 0-3 points clignotants

    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2

    # ── Fond ────────────────────────────────────────────────────────────────
    if _ld_bg:
        # Fond de jeu assombri
        screen.blit(_ld_bg, (0, 0))
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        screen.blit(ov, (0, 0))
    else:
        screen.fill(_LD_NIGHT)
        # Dégradé vertical simple
        for _gy in range(0, SCREEN_HEIGHT, 4):
            _ratio = _gy / SCREEN_HEIGHT
            _col   = (
                int(8  + 12 * _ratio),
                int(10 + 14 * _ratio),
                int(22 + 28 * _ratio),
            )
            pygame.draw.rect(screen, _col, (0, _gy, SCREEN_WIDTH, 4))

    # ── Particules flottantes légères ─────────────────────────────────────
    for _pi in range(18):
        _px = (CX - 300 + _pi * 35 + int(math.sin(_ld_t * 0.7 + _pi) * 12)) % SCREEN_WIDTH
        _py = int(SCREEN_HEIGHT * 0.18 + math.sin(_ld_t * 0.5 + _pi * 0.9) * 22)
        _pa = int(40 + 30 * math.sin(_ld_t + _pi * 1.3))
        _ps = pygame.Surface((3, 3), pygame.SRCALPHA)
        _ps.fill((*_LD_GOLD, _pa))
        screen.blit(_ps, (_px, _py))

    # ── Titre "FLAPPY BIRD" ───────────────────────────────────────────────
    _title_y  = int(CY - 190 + math.sin(_ld_t * 1.1) * 5)
    _shad_s   = _ld_font_title.render("FLAPPY BIRD", True, (0, 0, 0))
    _title_s  = _ld_font_title.render("FLAPPY BIRD", True, _LD_GOLD)
    screen.blit(_shad_s, (CX - _shad_s.get_width()//2 + 3, _title_y + 3))
    screen.blit(_title_s, (CX - _title_s.get_width()//2, _title_y))

    # Soulignement doré animé
    _ul_w  = int(_title_s.get_width() * (0.6 + 0.4 * progress))
    _ul_x  = CX - _ul_w // 2
    _ul_y  = _title_y + _title_s.get_height() + 4
    for _xi in range(_ul_w):
        _ratio_x = _xi / max(1, _ul_w - 1)
        _aa      = int(200 * (1 - abs(_ratio_x - 0.5) * 2))
        pygame.draw.line(screen, (*_LD_GOLD, _aa), (_ul_x + _xi, _ul_y), (_ul_x + _xi, _ul_y + 2))

    # ── Sous-titre ────────────────────────────────────────────────────────
    _sub_s = _ld_font_sub.render("Chargement en cours", True, _LD_CYAN)
    screen.blit(_sub_s, (CX - _sub_s.get_width()//2, _title_y + _title_s.get_height() + 18))

    # ── Barre de progression ──────────────────────────────────────────────
    BAR_W = min(700, SCREEN_WIDTH - 120)
    BAR_H = 18
    BAR_X = CX - BAR_W // 2
    BAR_Y = CY + 30

    # Fond barre
    _bar_bg = pygame.Surface((BAR_W, BAR_H), pygame.SRCALPHA)
    pygame.draw.rect(_bar_bg, (20, 22, 50, 220), (0, 0, BAR_W, BAR_H), border_radius=9)
    pygame.draw.rect(_bar_bg, (*_LD_GOLD_D, 120), (0, 0, BAR_W, BAR_H), 2, border_radius=9)
    screen.blit(_bar_bg, (BAR_X, BAR_Y))

    # Remplissage
    _fill_w = max(0, int((BAR_W - 4) * min(1.0, progress)))
    if _fill_w > 0:
        _fill = pygame.Surface((_fill_w, BAR_H - 4), pygame.SRCALPHA)
        for _xi in range(_fill_w):
            _rx  = _xi / max(1, _fill_w - 1)
            # Dégradé vert → cyan
            _fc  = (
                int(60  + (70  - 60)  * _rx),
                int(210 + (210 - 210) * _rx),
                int(110 + (255 - 110) * _rx),
            )
            pygame.draw.line(_fill, _fc, (_xi, 0), (_xi, BAR_H - 5))
        # Brillance haute
        _shine = pygame.Surface((_fill_w, 5), pygame.SRCALPHA)
        pygame.draw.rect(_shine, (255, 255, 255, 60), (0, 0, _fill_w, 5), border_radius=3)
        _fill.blit(_shine, (0, 0))
        screen.blit(_fill, (BAR_X + 2, BAR_Y + 2))

    # Lueur animée au bout de la barre
    if _fill_w > 8:
        _glow_x = BAR_X + 2 + _fill_w
        _glow_r = int(10 + 5 * math.sin(_ld_t * 4))
        _glow_s = pygame.Surface((_glow_r * 2 + 2, _glow_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(_glow_s, (*_LD_CYAN, 80), (_glow_r + 1, _glow_r + 1), _glow_r)
        pygame.draw.circle(_glow_s, (*_LD_WHITE, 160), (_glow_r + 1, _glow_r + 1), 4)
        screen.blit(_glow_s, (_glow_x - _glow_r - 1, BAR_Y + BAR_H//2 - _glow_r - 1))

    # ── Pourcentage ───────────────────────────────────────────────────────
    _pct_s = _ld_font_pct.render(f"{int(progress * 100)} %", True, _LD_WHITE)
    screen.blit(_pct_s, (CX - _pct_s.get_width()//2, BAR_Y + BAR_H + 10))

    # ── Étape courante (avec points animés) ───────────────────────────────
    _dots  = "." * _ld_anim
    _step_txt = f"{step_label}{_dots}"
    _step_s   = _ld_font_step.render(_step_txt, True, _LD_GREY)
    screen.blit(_step_s, (CX - _step_s.get_width()//2, BAR_Y + BAR_H + 44))

    # ── Version / watermark ───────────────────────────────────────────────
    _ver_s = _ld_font_step.render("v1.0  •  Flappy Bird", True, (50, 55, 80))
    screen.blit(_ver_s, (CX - _ver_s.get_width()//2, SCREEN_HEIGHT - 34))

    pygame.display.flip()
    _ld_clock.tick(60)

    # Absorbe les événements pour éviter que la fenêtre soit marquée "gelée"
    for _ev in pygame.event.get():
        if _ev.type == QUIT:
            pygame.quit(); sys.exit()

# ── Affichage initial ────────────────────────────────────────────────────────
_loading_draw(0.0, "Démarrage")

# ══════════════════════════════════════════════════════════════════════════════
#  CHARGEMENT DES ASSETS (avec progression)
# ══════════════════════════════════════════════════════════════════════════════

_loading_draw(0.04, "Chargement du fond d'écran")
BACKGROUND   = pygame.transform.scale(
    _pygame_load('assets/sprites/background-day.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

_loading_draw(0.08, "Chargement des images de jeu")
_bi = _pygame_load('assets/sprites/message.png').convert_alpha()
BEGIN_IMAGE  = pygame.transform.smoothscale(
    _bi, (int(_bi.get_width()*1.4), int(_bi.get_height()*1.4)))

_go = _pygame_load('assets/sprites/gameover.png').convert_alpha()
GAMEOVER_IMG = pygame.transform.smoothscale(
    _go, (int(_go.get_width()*1.6), int(_go.get_height()*1.6)))

_loading_draw(0.13, "Chargement des flèches de navigation")
# Nouvelles flèches : _1 = état normal, _2 = état cliqué (animé)
_ARR_SIZE = (64, 64)

def _load_arrow(path, size):
    """Charge une image flèche en gérant tous les formats via PIL si nécessaire."""
    # Essai direct pygame
    try:
        return pygame.transform.scale(
            _pygame_load(path).convert_alpha(), size)
    except Exception:
        pass
    # Fallback PIL : convertit n'importe quel format en RGBA puis pygame
    try:
        from PIL import Image as _PImg
        img = _PImg.open(path).convert("RGBA")
        raw = img.tobytes()
        surf = pygame.image.fromstring(raw, img.size, "RGBA").convert_alpha()
        return pygame.transform.scale(surf, size)
    except Exception as e:
        print(f"[ARROW] Impossible de charger {path} : {e}")
        # Fallback dessiné : triangle coloré
        s = pygame.Surface(size, pygame.SRCALPHA)
        w, h = size
        is_left = 'gauche' in path
        pts = [(w-4, 4), (4, h//2), (w-4, h-4)] if is_left else [(4, 4), (w-4, h//2), (4, h-4)]
        pygame.draw.polygon(s, (200, 210, 255, 230), pts)
        return s

ARROW_LEFT_1  = _load_arrow('assets/sprites/fleche_gauche_1.png', _ARR_SIZE)
ARROW_LEFT_2  = _load_arrow('assets/sprites/fleche_gauche_2.png', _ARR_SIZE)
ARROW_RIGHT_1 = _load_arrow('assets/sprites/fleche_droit_1.png',  _ARR_SIZE)
ARROW_RIGHT_2 = _load_arrow('assets/sprites/fleche_droit_2.png',  _ARR_SIZE)
# Alias de compatibilité (utilisés ailleurs comme LEFT_ARROW / RIGHT_ARROW)
LEFT_ARROW  = ARROW_LEFT_1
RIGHT_ARROW = ARROW_RIGHT_1

# -- Podium icons (1st / 2nd / 3rd place) — plus utilisé, remplacé par badge streak

# -- Badges streak (first_1 à first_10 seulement — on ne tente pas les absents)
_loading_draw(0.18, "Chargement des badges de série")
STREAK_BADGE_SIZE = 48
STREAK_BADGE_MAX  = 10
STREAK_BADGE_IMGS = {}
for _d in range(1, STREAK_BADGE_MAX + 1):
    _bp = f'assets/sprites/first_{_d}_day.png'
    _bc = os.path.join(_CACHE_DIR, _bp.replace("/", os.sep))
    if os.path.exists(_bp) or os.path.exists(_bc):
        try:
            _raw = _pygame_load(_bp).convert_alpha()
            STREAK_BADGE_IMGS[_d] = pygame.transform.smoothscale(_raw, (STREAK_BADGE_SIZE, STREAK_BADGE_SIZE))
        except:
            pass

def get_streak_badge(days):
    """Retourne l'image du badge pour `days` jours (la plus haute dispo <= days)."""
    best = None
    for d in sorted(STREAK_BADGE_IMGS.keys()):
        if d <= days:
            best = STREAK_BADGE_IMGS[d]
    return best

_loading_draw(0.28, "Chargement des boutons du menu")
# -- Boutons menu principal
_play_raw     = _pygame_load('assets/sprites/play_btn.png').convert_alpha()
PLAY_BTN_IMG  = pygame.transform.smoothscale(_play_raw, (480, 360))

_shop_raw     = _pygame_load('assets/sprites/boutique_btn.png').convert_alpha()
SHOP_BTN_IMG  = pygame.transform.smoothscale(_shop_raw, (350, 250))

_miss_raw     = _pygame_load('assets/sprites/mission_btn.png').convert_alpha()
MISS_BTN_IMG  = pygame.transform.smoothscale(_miss_raw, (350, 250))

_lvl_raw      = _pygame_load('assets/sprites/niveau_btn.png').convert_alpha()
LEVEL_BTN_IMG = pygame.transform.smoothscale(_lvl_raw, (350, 250))

# ── Chargement de la pièce (GIF animé) ───────────────────────────────────────
_loading_draw(0.38, "Chargement de l'animation de pièce")
def _load_gif_frames(path, size):
    """Charge toutes les frames d'un GIF — résout via cache Supabase."""
    frames = []
    try:
        from PIL import Image
        gif = Image.open(_asset_local(path))
        for frame_idx in range(getattr(gif, 'n_frames', 1)):
            gif.seek(frame_idx)
            frame_rgba = gif.convert('RGBA')
            frame_data = frame_rgba.tobytes()
            surf = pygame.image.fromstring(frame_data, frame_rgba.size, 'RGBA').convert_alpha()
            surf = pygame.transform.smoothscale(surf, (size, size))
            frames.append(surf)
    except Exception as e:
        print(f"Erreur chargement GIF frames : {e}")
    return frames

COIN_SIZE = 38
try:
    _gif_frames = _load_gif_frames('assets/sprites/coin.gif', COIN_SIZE)
    if _gif_frames:
        COIN_FRAMES = _gif_frames
        COIN_IMG    = COIN_FRAMES[0]
    else:
        raise ValueError("Aucune frame extraite du GIF")
except Exception as e:
    print(f"Impossible de charger coin.gif : {e}")
    _fallback = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(_fallback, (255, 215, 60), (COIN_SIZE//2, COIN_SIZE//2), COIN_SIZE//2)
    pygame.draw.circle(_fallback, (255, 245, 160), (COIN_SIZE//2, COIN_SIZE//2), COIN_SIZE//2 - 4, 3)
    pygame.draw.circle(_fallback, (200, 160, 20), (COIN_SIZE//2, COIN_SIZE//2), COIN_SIZE//2, 2)
    COIN_IMG    = _fallback
    COIN_FRAMES = [_fallback] * 8

_loading_draw(0.50, "Mise à l'échelle des pièces")
# Pré-calcul des frames redimensionnées (évite smoothscale à chaque frame → zéro lag)
COIN_FRAMES_34 = [pygame.transform.smoothscale(f, (34, 34)) for f in COIN_FRAMES]
COIN_FRAMES_44 = [pygame.transform.smoothscale(f, (44, 44)) for f in COIN_FRAMES]
COIN_FRAMES_54 = [pygame.transform.smoothscale(f, (54, 54)) for f in COIN_FRAMES]
COIN_FRAMES_90 = [pygame.transform.smoothscale(f, (60, 60)) for f in COIN_FRAMES]
COIN_FRAMES_36 = [pygame.transform.smoothscale(f, (36, 36)) for f in COIN_FRAMES]
COIN_IMG_34    = COIN_FRAMES_34[0]
COIN_IMG_36    = COIN_FRAMES_36[0]
COIN_GAME_SIZE = 60   # taille du coin ramassable en jeu

# ── Fonts ─────────────────────────────────────────────────────────────────────
_loading_draw(0.58, "Chargement des polices")
font_title  = pygame.font.SysFont('Impact', 82)
font_big    = pygame.font.SysFont('Impact', 58)
font_med    = pygame.font.SysFont('Impact', 40)
font_small  = pygame.font.SysFont('Verdana', 24)
font_tiny   = pygame.font.SysFont('Verdana', 18)
font_hud    = pygame.font.SysFont('Impact', 44)
font_score  = pygame.font.SysFont('Impact', 72)
font_avatar = pygame.font.SysFont('Impact', 26)

_loading_draw(0.65, "Chargement des skins")
skin_images = {
    "Flappy":  pygame.transform.scale(_pygame_load('assets/sprites/bluebird-midflap.png').convert_alpha(), (60, 60)),
    "Redbird": pygame.transform.scale(_pygame_load('assets/sprites/redbird-midflap.png').convert_alpha(), (60, 60)),
    "Mouche":  pygame.transform.scale(_pygame_load('assets/sprites/mouche.png').convert_alpha(), (55, 55)),
    "Avion":   pygame.transform.scale(_pygame_load('assets/sprites/avion.png').convert_alpha(), (110, 100)),
    "Ninja": pygame.transform.scale(_pygame_load('assets/sprites/Ninja.png').convert_alpha(), (75, 70)),
    "Avion de chasse": pygame.transform.scale(_pygame_load('assets/sprites/avion_de_chasse.png').convert_alpha(), (75, 70)),
    "Nyancat": pygame.transform.scale(_pygame_load('assets/sprites/Nyancat.png').convert_alpha(), (60, 60)),
    
    
}

SKIN_DISPLAY_NAMES = {
    "Flappy":  "Flappy",
    "Redbird": "Redbird",
    "Mouche":  "Mouche",
    "Avion":   "Avion",
    "Ninja": "Ninja",
    "Nyancat": "Nyancat",
    "Avion de chasse": "Avion de chasse",
    
}
SKIN_ASSET_NAMES = {
    "Flappy":  "Flappy",
    "Redbird": "Redbird",
    "Mouche":  "Mouche",
    "Avion":   "Avion",
    "Ninja": "Ninja",
    "Nyancat": "Nyancat",
    "Avion de chasse": "Avion de chasse",
    
}

clock      = pygame.time.Clock()

# ── Pré-chargement des fonds d'écran boutique ─────────────────────────────────
_loading_draw(0.75, "Chargement des fonds d'écran")
BG_PREVIEW_IMAGES = {}   # key -> surface (plein écran)
for _bg_i, _bg in enumerate(BG_ITEMS):
    _loading_draw(0.75 + 0.18 * (_bg_i / max(1, len(BG_ITEMS))), f"Fond : {_bg['name']}")
    try:
        _raw_bg = _pygame_load(_bg["file"]).convert()
        BG_PREVIEW_IMAGES[_bg["key"]] = pygame.transform.scale(_raw_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as _e:
        print(f"Impossible de charger fond {_bg['file']} : {_e}")
        BG_PREVIEW_IMAGES[_bg["key"]] = None

# ── Fin du chargement ────────────────────────────────────────────────────────
_loading_draw(1.0, "Prêt !")

score      = 0
best_score = 0


# ══════════════════════════════════════════════════════════════════════════════
#  PARTICULES
# ══════════════════════════════════════════════════════════════════════════════
class Particle:
    COLORS = [GOLD, GOLD_LIGHT, WHITE, CYAN, (255, 180, 60)]
    def __init__(self):
        self.reset(born=True)
    def reset(self, born=False):
        self.x     = random.uniform(0, SCREEN_WIDTH)
        self.y     = SCREEN_HEIGHT + 5 if not born else random.uniform(0, SCREEN_HEIGHT)
        self.r     = random.uniform(1.0, 3.0)
        self.vx    = random.uniform(-0.3, 0.3)
        self.vy    = random.uniform(-0.8, -0.2)
        self.alpha = random.randint(80, 200)
        self.color = random.choice(self.COLORS)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.alpha -= 1.0
        if self.alpha <= 0 or self.y < -6: self.reset()
    def draw(self, surf):
        ri = max(1, int(self.r))
        alpha = int(max(0, self.alpha))
        color = (*self.color[:3], alpha)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), ri)

PARTICLES = [Particle() for _ in range(90)]
_particle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

def draw_particles():
    _particle_surf.fill((0, 0, 0, 0))
    for p in PARTICLES:
        p.update()
        p.draw(_particle_surf)
    screen.blit(_particle_surf, (0, 0))


# ══════════════════════════════════════════════════════════════════════════════
#  EFFET COLLECTE PIÈCE (pop visuel)
# ══════════════════════════════════════════════════════════════════════════════
class CoinPopEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255
        self.vy = -2.5
        self.life = 45

    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.life -= 1
        self.alpha = int(255 * (self.life / 45))

    def draw(self, surf):
        if self.life <= 0:
            return
        txt = font_small.render("+1", True, GOLD)
        txt.set_alpha(max(0, self.alpha))
        surf.blit(txt, (int(self.x) - txt.get_width()//2, int(self.y)))

    @property
    def dead(self):
        return self.life <= 0

coin_pop_effects = []


# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def draw_overlay(alpha=180):
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((8, 10, 22, alpha)); screen.blit(ov, (0, 0))

def draw_panel(cx, cy, w, h, radius=18, border=GOLD, border_w=2, shine_ratio=3, shine=True):
    x, y = cx - w//2, cy - h//2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*PANEL_BG, 215), (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(s, (*border, 210),   (0, 0, w, h), width=border_w, border_radius=radius)
    if shine:
        shine_h = h // shine_ratio
        shine_surf = pygame.Surface((w-6, shine_h), pygame.SRCALPHA)
        pygame.draw.rect(shine_surf, (255, 255, 255, 12), (0, 0, w-6, shine_h), border_radius=radius)
        s.blit(shine_surf, (3, 3))
    screen.blit(s, (x, y))

def text_glow(text, fnt, color, cx, y, glow_col=GOLD, strength=3):
    base = fnt.render(text, True, color)
    for off in range(strength, 0, -1):
        gs = fnt.render(text, True, glow_col)
        gs.set_alpha(min(255, int(55/off)*2))
        gx = cx - gs.get_width()//2
        for dx, dy in [(-off, 0), (off, 0), (0, -off), (0, off)]:
            screen.blit(gs, (gx+dx, y+dy))
    screen.blit(base, (cx - base.get_width()//2, y)); return base

_sep_cache = {}
def draw_sep(y, w_margin=100, alpha=65):
    w = max(4, SCREEN_WIDTH - w_margin*2)
    key = (w, alpha)
    if key not in _sep_cache:
        s = pygame.Surface((w, 2), pygame.SRCALPHA)
        for i in range(w):
            t_val = abs(i/w - 0.5) * 2
            a = int(alpha * (1 - t_val*t_val))
            s.set_at((i, 0), (*GOLD, a))
            s.set_at((i, 1), (*GOLD_DARK, max(0, a//2)))
        _sep_cache[key] = s
    screen.blit(_sep_cache[key], (w_margin, y))

def btn_rect(cx, cy, w, h):
    return pygame.Rect(cx - w//2, cy - h//2, w, h)

def is_hov(cx, cy, w, h):
    return btn_rect(cx, cy, w, h).collidepoint(pygame.mouse.get_pos())

def draw_tooltip(text, anchor_cx, anchor_y):
    """Affiche une bulle d'info centrée sur anchor_cx, au-dessus de anchor_y."""
    lines = text.split("\n")
    surfs = [font_tiny.render(l, True, WHITE) for l in lines]
    tw = max(s.get_width() for s in surfs) + 22
    th = sum(s.get_height() for s in surfs) + 12 + (len(surfs)-1)*4
    tx = max(6, min(SCREEN_WIDTH - tw - 6, anchor_cx - tw//2))
    ty = anchor_y - th - 8
    bg = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.rect(bg, (8, 10, 22, 230), (0, 0, tw, th), border_radius=8)
    pygame.draw.rect(bg, (*GOLD, 180), (0, 0, tw, th), width=1, border_radius=8)
    screen.blit(bg, (tx, ty))
    cy_off = 6
    for s in surfs:
        screen.blit(s, (tx + tw//2 - s.get_width()//2, ty + cy_off))
        cy_off += s.get_height() + 4

def draw_btn(label, cx, cy, w=260, h=60, danger=False, accent=False, small=False, color_override=None):
    hov  = is_hov(cx, cy, w, h)
    x, y = cx - w//2, cy - h//2
    sh = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 75), (0, 0, w+8, h+8), border_radius=14)
    screen.blit(sh, (x-4, y+5))
    if color_override:
        bg = color_override[0] if not hov else color_override[1]
        border = color_override[2]
    elif danger:
        bg = (150, 28, 28) if not hov else (195, 38, 38); border = RED_HOT
    elif accent:
        bg = (28, 120, 55) if not hov else (38, 160, 75); border = GREEN_SOFT
    else:
        bg = (18, 24, 58) if not hov else (26, 34, 76)
        border = GOLD_LIGHT if hov else GOLD
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*bg, 238), (0, 0, w, h), border_radius=13)
    shine = pygame.Surface((w-6, h//2), pygame.SRCALPHA)
    pygame.draw.rect(shine, (255, 255, 255, 20 if hov else 8), (0, 0, w-6, h//2), border_radius=13)
    s.blit(shine, (3, 3))
    pygame.draw.rect(s, (*border, 255), (0, 0, w, h), width=3 if hov else 2, border_radius=13)
    screen.blit(s, (x, y))
    fnt   = font_tiny if small else (font_small if w <= 180 else font_med)
    color = WHITE if danger or accent else (GOLD_LIGHT if hov else GOLD)
    lbl   = fnt.render(label, True, color)
    screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))
    return btn_rect(cx, cy, w, h)

def btn_clicked(event, cx, cy, w=260, h=60):
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        return btn_rect(cx, cy, w, h).collidepoint(event.pos)
    return False

def draw_avatar(player, cx, cy, radius=28, font=None):
    img_path = player.get("avatar_image_path")
    if img_path and os.path.exists(img_path):
        try:
            raw = _pygame_load(img_path).convert_alpha()
            size = radius * 2
            scaled = pygame.transform.smoothscale(raw, (size, size))
            # Masque circulaire
            mask_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(mask_surf, (255,255,255,255), (radius, radius), radius)
            result = pygame.Surface((size, size), pygame.SRCALPHA)
            result.blit(scaled, (0, 0))
            result.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(result, (cx - radius, cy - radius))
            pygame.draw.circle(screen, GOLD, (cx, cy), radius, 2)
            return
        except Exception:
            pass
    # Fallback : cercle coloré avec initiales
    color = tuple(player.get("avatar_color", [255, 215, 60]))
    pygame.draw.circle(screen, color, (cx, cy), radius)
    pygame.draw.circle(screen, WHITE, (cx, cy), radius, 2)
    name = player.get("name", "?")
    initials = (name[:2]).upper()
    fnt = font or font_avatar
    txt = fnt.render(initials, True, NIGHT)
    screen.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

def draw_coin_badge(coins, cx, cy):
    coin_mini = COIN_IMG_34
    total_w = 34 + 8 + font_small.size(str(coins))[0]
    x0 = cx - total_w // 2
    screen.blit(coin_mini, (x0, cy - 17))
    txt = font_small.render(str(coins), True, GOLD)
    screen.blit(txt, (x0 + 42, cy - txt.get_height()//2))


# ══════════════════════════════════════════════════════════════════════════════
#  SPRITES
# ══════════════════════════════════════════════════════════════════════════════
class Bird(pygame.sprite.Sprite):
    # J'ai renommé la clé en "Ninja" pour corriger ton erreur
    SK_MAP = {
        "Flappy": [
            ('assets/sprites/bluebird-upflap.png',   None),
            ('assets/sprites/bluebird-midflap.png',  None),
            ('assets/sprites/bluebird-downflap.png', None),
        ],
        "Avion": [('assets/sprites/avion.png',   (100, 90))],
        "Mouche":             [('assets/sprites/mouche.png',  (45,  45))],
        "Ninja":              [('assets/sprites/Ninja.png',   (65,  60))],
        "Avion de chasse":    [('assets/sprites/avion_de_chasse.png',   (65,  60))],
        "Nyancat":            [('assets/sprites/Nyancat.png', (45,  45))],
        "Redbird": [
            ('assets/sprites/redbird-upflap.png',   None),
            ('assets/sprites/redbird-midflap.png',  None),
            ('assets/sprites/redbird-downflap.png', None),
        ],

    }

    def __init__(self, skin_asset_name):
        super().__init__()
        self.skin_name = skin_asset_name
        # On récupère les images, sinon Flappy par défaut
        raw = self.SK_MAP.get(skin_asset_name, self.SK_MAP["Flappy"])
        
        self.base_images = []
        for path, size in raw:
            img = _pygame_load(path).convert_alpha()
            if size: 
                img = pygame.transform.scale(img, size)
            self.base_images.append(img)
            
        self.speed = SPEED
        self.current_frame = 0
        self._anim_tick = 0
        self.angle = 0 
        
        self.image = self.base_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 6
        self.rect.y = int(SCREEN_HEIGHT / 2.5)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt=1/60, held=False):
        scale = dt * FPS
        
        # 1. Animation des ailes
        if len(self.base_images) > 1:
            self._anim_tick += 1
            if self._anim_tick >= 5:
                self._anim_tick = 0
                self.current_frame = (self.current_frame + 1) % len(self.base_images)
        
        # 2. Physique de chute/montée
        if held:
            self.speed = -SPEED * 0.45
        else:
            self.speed += GRAVITY * scale
        self.rect.y += int(self.speed * scale)

        # 3. PHYSIQUES DE ROTATION PERSONNALISÉES
        if "Avion" in self.skin_name:
            # Avion : Rotation fluide et limitée (pas de piqué vertical)
            target_angle = self.speed * -1.2
            if target_angle > 15: target_angle = 15
            if target_angle < -40: target_angle = -40
            self.angle = target_angle

        elif self.skin_name == "Ninja":
            # Ninja : Très stable, penche à peine pour garder l'équilibre
            target_angle = self.speed * -0.4
            if target_angle > 8: target_angle = 8
            if target_angle < -8: target_angle = -8
            self.angle = target_angle

        elif self.skin_name == "Nyancat":
            # Nyancat : Toujours parfaitement horizontal (0 degré)
            self.angle = 0

        else:
            # Classique (Flappy / Mouche) : Rotation organique complète
            target_angle = self.speed * -3
            if target_angle > 30: target_angle = 30
            if target_angle < -90: target_angle = -90
            self.angle = target_angle

        # 4. Application visuelle (Rotation et recentrage)
        current_base_img = self.base_images[self.current_frame]
        
        if self.angle != 0:
            self.image = pygame.transform.rotate(current_base_img, self.angle)
        else:
            self.image = current_base_img
            
        # On utilise le centre du rectangle pour éviter que l'image ne saute
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

        # Empêcher de sortir par le haut
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed = 0

    def bump(self):
        self.speed = -SPEED
        play_sound(wing_snd)
class Pipe(pygame.sprite.Sprite):
    _IMG      = None
    _IMG_FLIP = None

    @classmethod
    def _load(cls):
        if cls._IMG is None:
            raw = pygame.transform.scale(
                _pygame_load('assets/sprites/pipe-green.png').convert_alpha(),
                (PIPE_WIDTH, PIPE_HEIGHT))
            cls._IMG      = raw
            cls._IMG_FLIP = pygame.transform.flip(raw, False, True)

    def __init__(self, inverted, xpos, ysize, bob_phase=0.0):
        super().__init__()
        Pipe._load()
        self.bob_phase  = bob_phase   # phase partagée avec le tuyau partenaire
        self.bob_offset = 0           # décalage vertical actuel (pixels)
        self.score_passed = False     # True une fois que l'oiseau est passé
        if inverted:
            self.image = Pipe._IMG_FLIP
            self.rect  = self.image.get_rect()
            self.rect.x = xpos
            self._base_y = -(self.rect.height - ysize)
            self.rect.y = self._base_y
        else:
            self.image = Pipe._IMG
            self.rect  = self.image.get_rect()
            self.rect.x = xpos
            self._base_y = SCREEN_HEIGHT - ysize
            self.rect.y = self._base_y
        self.mask = pygame.mask.from_surface(self.image)
        self.ysize = ysize
        self.inverted = inverted
        self.float_x = float(xpos)

    def update(self, game_speed, bob_active=False, dt=1/60):
        self.float_x -= game_speed
        self.rect.x = round(self.float_x)
        if bob_active:
            self.bob_phase += dt * 1.8   # ~0.29 Hz, oscillation lente
            _amp = getattr(self, '_tryhard_amp', 28)
            self.bob_offset = int(math.sin(self.bob_phase) * _amp)
        else:
            self.bob_offset = 0
        self.rect.y = self._base_y + self.bob_offset

class Ground(pygame.sprite.Sprite):
    _IMG = None

    @classmethod
    def _load(cls):
        if cls._IMG is None:
            cls._IMG = pygame.transform.scale(
                _pygame_load('assets/sprites/base.png').convert_alpha(),
                (GROUND_WIDTH, GROUND_HEIGHT))

    def __init__(self, xpos):
        super().__init__()
        Ground._load()
        self.image  = Ground._IMG
        self.mask   = pygame.mask.from_surface(self.image)
        self.rect   = self.image.get_rect()
        self.rect.x = xpos; self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.float_x = float(xpos)
    def update(self, game_speed):
        self.float_x -= game_speed
        self.rect.x = round(self.float_x)


# ══════════════════════════════════════════════════════════════════════════════
#  PIÈCES
# ══════════════════════════════════════════════════════════════════════════════
class Coin(pygame.sprite.Sprite):
    COLLECT_SOUND = 'assets/audio/wing.wav'
    
    def __init__(self, xpos, ypos):
        super().__init__()
        self.frame_idx = 0
        self.frame_timer = 0
        self.image = COIN_FRAMES_90[0]
        self.rect  = self.image.get_rect(center=(xpos, ypos))
        self.mask  = pygame.mask.from_surface(self.image)
        self.base_y   = ypos
        self.bob_t    = random.uniform(0, math.pi * 2)
        self.bob_amp  = 6
        self.bob_speed = 0.07
        self.float_x  = float(xpos)

    def update(self, game_speed):
        self.float_x -= game_speed
        self.rect.x = round(self.float_x)
        self.bob_t += self.bob_speed
        self.rect.centery = int(self.base_y + math.sin(self.bob_t) * self.bob_amp)
        self.frame_timer += 1
        if self.frame_timer >= 4:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(COIN_FRAMES_90)
            self.image = COIN_FRAMES_90[self.frame_idx]
            self.mask  = pygame.mask.from_surface(self.image)


def try_spawn_random_coin(pipe_grp):
    MARGIN_TOP    = 60
    MARGIN_GROUND = GROUND_HEIGHT + 55
    MARGIN_PIPE   = 30

    y_min = MARGIN_TOP
    y_max = SCREEN_HEIGHT - MARGIN_GROUND

    if y_max - y_min < COIN_GAME_SIZE + 20:
        return None

    x = SCREEN_WIDTH + COIN_GAME_SIZE + random.randint(0, 200)

    for _ in range(8):
        y = random.randint(y_min, y_max)
        coin_rect = pygame.Rect(x - COIN_GAME_SIZE//2, y - COIN_GAME_SIZE//2, COIN_GAME_SIZE, COIN_GAME_SIZE)

        blocked = False
        for pipe in pipe_grp.sprites():
            inflated = pipe.rect.inflate(MARGIN_PIPE * 2, MARGIN_PIPE * 2)
            if inflated.colliderect(coin_rect):
                blocked = True
                break

        if not blocked:
            return Coin(x, y)

    return None


def off_screen(sprite): return sprite.rect.right < 0

def random_pipes(xpos):
    size = random.randint(200, 600)
    phase = random.uniform(0, math.pi * 2)   # phase commune aux 2 tuyaux
    return Pipe(False, xpos, size, phase), Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP, phase)


def get_system_username():
    try:
        name = getpass.getuser()
    except Exception:
        name = os.environ.get("USERNAME") or os.environ.get("USER") or "Joueur"
    clean = "".join(c for c in name if c.isalnum() or c in ("-", "_"))[:16]
    return clean if clean else "Joueur"


# ══════════════════════════════════════════════════════════════════════════════
#  RAPPORT DE BUG
# ══════════════════════════════════════════════════════════════════════════════
def bug_report_screen(player):
    """Écran de signalement de bug avec zone de texte multi-ligne."""
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2

    MAX_CHARS   = 10000
    TEXT_BOX_W  = min(900, SCREEN_WIDTH - 120)
    TEXT_BOX_H  = 320
    TEXT_BOX_X  = CX - TEXT_BOX_W // 2
    TEXT_BOX_Y  = CY - TEXT_BOX_H // 2 + 20

    text_lines  = [""]        # liste de lignes
    cursor_line = 0
    cursor_col  = 0
    active      = True        # zone de texte toujours active ici
    submitted   = False
    error_msg   = ""
    t           = 0.0

    # Scroll
    scroll_offset = 0
    line_height   = font_tiny.get_height() + 4
    visible_lines = (TEXT_BOX_H - 20) // line_height

    BTN_SEND_Y   = TEXT_BOX_Y + TEXT_BOX_H + 55
    BTN_CANCEL_Y = BTN_SEND_Y + 70

    def get_full_text():
        return "\n".join(text_lines)

    def count_chars():
        return len(get_full_text())

    # Police monospace pour la zone de texte (déclarée ici pour le wrap auto)
    _font_wrap = pygame.font.SysFont('Courier New', 17) or font_tiny
    MAX_LINE_W = TEXT_BOX_W - 30  # largeur max en pixels avant wrap automatique

    def insert_char(ch):
        nonlocal cursor_line, cursor_col
        if count_chars() >= MAX_CHARS:
            return
        line = text_lines[cursor_line]
        new_line = line[:cursor_col] + ch + line[cursor_col:]
        # Retour à la ligne automatique si la ligne dépasse la largeur max
        if _font_wrap.size(new_line)[0] > MAX_LINE_W:
            # Chercher le dernier espace avant le curseur pour couper proprement
            break_pos = new_line.rfind(' ', 0, cursor_col + 1)
            if break_pos > 0:
                text_lines[cursor_line] = new_line[:break_pos]
                rest = new_line[break_pos + 1:]
                cursor_line += 1
                text_lines.insert(cursor_line, rest)
                cursor_col = len(rest) - len(line[cursor_col:])
                cursor_col = max(0, cursor_col)
            else:
                # Pas d'espace → couper juste après le nouveau caractère
                text_lines[cursor_line] = new_line[:cursor_col + 1]
                rest = new_line[cursor_col + 1:]
                cursor_line += 1
                text_lines.insert(cursor_line, rest)
                cursor_col = 0
        else:
            text_lines[cursor_line] = new_line
            cursor_col += 1

    def handle_backspace():
        nonlocal cursor_line, cursor_col
        if cursor_col > 0:
            line = text_lines[cursor_line]
            text_lines[cursor_line] = line[:cursor_col-1] + line[cursor_col:]
            cursor_col -= 1
        elif cursor_line > 0:
            prev_len = len(text_lines[cursor_line - 1])
            text_lines[cursor_line - 1] += text_lines[cursor_line]
            text_lines.pop(cursor_line)
            cursor_line -= 1
            cursor_col = prev_len

    def handle_return():
        nonlocal cursor_line, cursor_col
        if count_chars() >= MAX_CHARS:
            return
        line = text_lines[cursor_line]
        rest = line[cursor_col:]
        text_lines[cursor_line] = line[:cursor_col]
        text_lines.insert(cursor_line + 1, rest)
        cursor_line += 1
        cursor_col = 0

    def clamp_scroll():
        nonlocal scroll_offset
        max_scroll = max(0, len(text_lines) - visible_lines)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        # S'assurer que le curseur est visible
        if cursor_line < scroll_offset:
            scroll_offset = cursor_line
        elif cursor_line >= scroll_offset + visible_lines:
            scroll_offset = cursor_line - visible_lines + 1

    # Police monospace pour la zone de texte (réutilise _font_wrap définie plus haut)
    font_code = _font_wrap

    while True:
        clock.tick(FPS)
        t += 0.04
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_RETURN or event.key == K_KP_ENTER:
                    handle_return()
                elif event.key == K_BACKSPACE:
                    handle_backspace()
                elif event.key == K_DELETE:
                    line = text_lines[cursor_line]
                    if cursor_col < len(line):
                        text_lines[cursor_line] = line[:cursor_col] + line[cursor_col+1:]
                    elif cursor_line < len(text_lines) - 1:
                        text_lines[cursor_line] += text_lines[cursor_line + 1]
                        text_lines.pop(cursor_line + 1)
                elif event.key == K_LEFT:
                    if cursor_col > 0:
                        cursor_col -= 1
                    elif cursor_line > 0:
                        cursor_line -= 1
                        cursor_col = len(text_lines[cursor_line])
                elif event.key == K_RIGHT:
                    if cursor_col < len(text_lines[cursor_line]):
                        cursor_col += 1
                    elif cursor_line < len(text_lines) - 1:
                        cursor_line += 1
                        cursor_col = 0
                elif event.key == K_UP:
                    if cursor_line > 0:
                        cursor_line -= 1
                        cursor_col = min(cursor_col, len(text_lines[cursor_line]))
                elif event.key == K_DOWN:
                    if cursor_line < len(text_lines) - 1:
                        cursor_line += 1
                        cursor_col = min(cursor_col, len(text_lines[cursor_line]))
                elif event.key == K_HOME:
                    cursor_col = 0
                elif event.key == K_END:
                    cursor_col = len(text_lines[cursor_line])
                elif event.unicode and event.unicode.isprintable():
                    insert_char(event.unicode)
                error_msg = ""
                clamp_scroll()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Bouton Envoyer
                if btn_rect(CX, BTN_SEND_Y, 280, 58).collidepoint(event.pos):
                    full_text = get_full_text().strip()
                    if not full_text:
                        error_msg = "Veuillez décrire le bug avant d'envoyer."
                    else:
                        ok = save_bug_report(player["name"], full_text)
                        if ok:
                            submitted = True
                        else:
                            error_msg = "Erreur lors de la sauvegarde."
                # Bouton Annuler
                elif btn_rect(CX, BTN_CANCEL_Y, 280, 52).collidepoint(event.pos):
                    return
                # Clic dans la zone de texte → positionner le curseur
                elif pygame.Rect(TEXT_BOX_X, TEXT_BOX_Y, TEXT_BOX_W, TEXT_BOX_H).collidepoint(event.pos):
                    rel_y = my - TEXT_BOX_Y - 10
                    clicked_line = scroll_offset + rel_y // line_height
                    clicked_line = max(0, min(clicked_line, len(text_lines) - 1))
                    cursor_line = clicked_line
                    # Approximation colonne par largeur de caractère
                    rel_x = mx - TEXT_BOX_X - 10
                    line_text = text_lines[cursor_line]
                    best_col = 0
                    for ci in range(len(line_text) + 1):
                        w = font_code.size(line_text[:ci])[0]
                        if w <= rel_x:
                            best_col = ci
                        else:
                            break
                    cursor_col = best_col
                    clamp_scroll()

            if event.type == MOUSEBUTTONDOWN and event.button in (4, 5):
                scroll_offset += -3 if event.button == 4 else 3
                clamp_scroll()

        # ── Écran de confirmation ──────────────────────────────────────────
        if submitted:
            screen.blit(BACKGROUND, (0, 0))
            draw_overlay(210)
            draw_panel(CX, CY, 520, 280, radius=18, border=GREEN_SOFT)

            ok_title = font_med.render("BUG SIGNALÉ !", True, GREEN_SOFT)
            screen.blit(ok_title, (CX - ok_title.get_width()//2, CY - 90))

            ok_sub1 = font_tiny.render("Merci pour ton rapport !", True, WHITE)
            ok_sub2 = font_tiny.render(f"Enregistré dans : {BUG_FILE}", True, GREY)
            screen.blit(ok_sub1, (CX - ok_sub1.get_width()//2, CY - 30))
            screen.blit(ok_sub2, (CX - ok_sub2.get_width()//2, CY + 10))

            draw_btn("RETOUR AU MENU", CX, CY + 90, 300, 58, accent=True)

            if _GLOBAL_CHAT:
                _GLOBAL_CHAT.draw()
            pygame.display.flip()

            # Attendre un clic sur "RETOUR AU MENU" ou Échap
            waiting = True
            while waiting:
                clock.tick(FPS)
                for ev in pygame.event.get():
                    if ev.type == QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                        waiting = False
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                        if btn_rect(CX, CY + 90, 300, 58).collidepoint(ev.pos):
                            waiting = False
            return

        # ── DESSIN PRINCIPAL ───────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(200)

        # Titre
        title_col = (255, 100, 100)
        t_surf = font_med.render("SIGNALER UN BUG", True, title_col)
        t_shad = font_med.render("SIGNALER UN BUG", True, (10, 5, 5))
        tx = CX - t_surf.get_width()//2
        screen.blit(t_shad, (tx + 3, 30))
        screen.blit(t_surf,  (tx,     28))
        # Ligne déco
        line_w = t_surf.get_width() + 60
        lx = CX - line_w // 2
        for i in range(line_w):
            alpha = int(160 * (1 - abs(i / line_w - 0.5) * 2))
            s = pygame.Surface((1, 2), pygame.SRCALPHA)
            s.fill((255, 80, 80, alpha))
            screen.blit(s, (lx + i, 28 + t_surf.get_height() + 4))

        # Sous-titre
        sub = font_tiny.render("Décris le bug en détail. Utilise Entrée pour sauter des lignes.", True, GREY)
        screen.blit(sub, (CX - sub.get_width()//2, 82))

        # Panneau de la zone de texte
        panel_surf = pygame.Surface((TEXT_BOX_W + 16, TEXT_BOX_H + 16), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (8, 10, 22, 230), (0, 0, TEXT_BOX_W + 16, TEXT_BOX_H + 16), border_radius=14)
        pygame.draw.rect(panel_surf, (*RED_HOT, 200), (0, 0, TEXT_BOX_W + 16, TEXT_BOX_H + 16), width=2, border_radius=14)
        screen.blit(panel_surf, (TEXT_BOX_X - 8, TEXT_BOX_Y - 8))

        # Zone de texte (fond légèrement distinct)
        tb_surf = pygame.Surface((TEXT_BOX_W, TEXT_BOX_H), pygame.SRCALPHA)
        pygame.draw.rect(tb_surf, (14, 16, 38, 220), (0, 0, TEXT_BOX_W, TEXT_BOX_H), border_radius=10)
        screen.blit(tb_surf, (TEXT_BOX_X, TEXT_BOX_Y))

        # Rendu des lignes visibles avec clip
        clip_rect = pygame.Rect(TEXT_BOX_X + 10, TEXT_BOX_Y + 10, TEXT_BOX_W - 20, TEXT_BOX_H - 20)
        screen.set_clip(clip_rect)

        for li in range(visible_lines):
            real_li = li + scroll_offset
            if real_li >= len(text_lines):
                break
            ly = TEXT_BOX_Y + 10 + li * line_height
            line_text = text_lines[real_li]

            # Surlignage de la ligne courante
            if real_li == cursor_line:
                hl = pygame.Surface((TEXT_BOX_W - 20, line_height), pygame.SRCALPHA)
                hl.fill((255, 80, 80, 28))
                screen.blit(hl, (TEXT_BOX_X + 10, ly))

            txt_surf = font_code.render(line_text, True, WHITE)
            screen.blit(txt_surf, (TEXT_BOX_X + 10, ly))

            # Curseur clignotant sur la ligne active
            if real_li == cursor_line and int(t * 3) % 2 == 0:
                cx_pos = TEXT_BOX_X + 10 + font_code.size(line_text[:cursor_col])[0]
                pygame.draw.line(screen, (255, 120, 120),
                                 (cx_pos, ly + 1),
                                 (cx_pos, ly + line_height - 2), 2)

        screen.set_clip(None)

        # Barre de défilement si nécessaire
        if len(text_lines) > visible_lines:
            sb_x = TEXT_BOX_X + TEXT_BOX_W - 10
            sb_h = TEXT_BOX_H - 20
            sb_y = TEXT_BOX_Y + 10
            pygame.draw.rect(screen, (30, 35, 60), (sb_x, sb_y, 6, sb_h), border_radius=3)
            ratio       = visible_lines / len(text_lines)
            thumb_h     = max(20, int(sb_h * ratio))
            scroll_max  = max(1, len(text_lines) - visible_lines)
            thumb_y     = sb_y + int((scroll_offset / scroll_max) * (sb_h - thumb_h))
            pygame.draw.rect(screen, RED_HOT, (sb_x, thumb_y, 6, thumb_h), border_radius=3)

        # Compteur de caractères
        char_count = count_chars()
        ratio_used  = char_count / MAX_CHARS
        count_col   = (255, 80, 80) if ratio_used > 0.9 else (GOLD if ratio_used > 0.7 else GREY)
        count_txt   = font_tiny.render(f"{char_count} / {MAX_CHARS} caractères", True, count_col)
        screen.blit(count_txt, (TEXT_BOX_X + TEXT_BOX_W - count_txt.get_width(),
                                TEXT_BOX_Y + TEXT_BOX_H + 8))

        # Message d'erreur
        if error_msg:
            err_surf = font_tiny.render(error_msg, True, RED_HOT)
            screen.blit(err_surf, (CX - err_surf.get_width()//2, TEXT_BOX_Y + TEXT_BOX_H + 8))

        # Boutons
        # Envoyer (rouge)
        hov_send = is_hov(CX, BTN_SEND_Y, 280, 58)
        send_bg  = (180, 35, 35) if hov_send else (140, 22, 22)
        send_brd = (255, 120, 120) if hov_send else RED_HOT
        sb_s = pygame.Surface((280, 58), pygame.SRCALPHA)
        pygame.draw.rect(sb_s, (*send_bg, 245), (0, 0, 280, 58), border_radius=13)
        pygame.draw.rect(sb_s, (*send_brd, 255), (0, 0, 280, 58), width=3 if hov_send else 2, border_radius=13)
        screen.blit(sb_s, (CX - 140, BTN_SEND_Y - 29))
        sl = font_med.render("ENVOYER", True, WHITE)
        screen.blit(sl, (CX - sl.get_width()//2, BTN_SEND_Y - sl.get_height()//2))

        draw_btn("ANNULER", CX, BTN_CANCEL_Y, 280, 52)

        # Indication joueur
        player_info = font_tiny.render(f"Signalé par : {get_display_name(player['name'])}", True, (100, 100, 130))
        screen.blit(player_info, (TEXT_BOX_X, TEXT_BOX_Y - 30))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE ADMINISTRATION
# ══════════════════════════════════════════════════════════════════════════════
def admin_screen(data, current_player):
    """Page d'administration : arrêt global, gestion des joueurs, bugs, admins."""
    CX     = SCREEN_WIDTH  // 2
    CY     = SCREEN_HEIGHT // 2
    t      = 0.0

    ADMIN_COLOR  = (230,  80,  80)
    ADMIN_BORDER = (255, 130, 100)
    GREEN2       = ( 60, 210, 110)
    ORANGE       = (255, 160,  40)

    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0

    TAB_STOP    = 0
    TAB_PLAYERS = 1
    TAB_BANNER  = 2
    TAB_PSEUDOS = 3
    TAB_BUGS    = 4
    TAB_ADMINS  = 5
    current_tab = TAB_STOP

    pseudo_requests  = get_pending_requests()
    bug_reports_list = []
    bug_popup        = None   # dict du bug affiché en popup, ou None
    bug_copied_timer = 0      # timer feedback "Copié !"
    bug_sel_start    = -1     # index char début sélection dans le texte
    bug_sel_end      = -1     # index char fin sélection
    bug_sel_dragging = False  # en train de glisser
    admin_input_text    = ""
    admin_input_active  = False
    admin_feedback_msg  = ""
    admin_feedback_col  = WHITE
    admin_feedback_timer = 0

    _bcfg          = get_banner_config(data)
    banner_enabled = _bcfg["enabled"]
    banner_message = _bcfg["message"]
    banner_editing = False
    banner_cursor  = len(banner_message)   # position du curseur dans le texte
    banner_scroll  = 0                     # décalage horizontal de l'affichage (en px)

    scroll_y        = 0
    selected_player = None
    edit_field      = None
    edit_values     = {}
    pending_save    = False
    confirm_reset   = False

    PANEL_W  = min(1200, SCREEN_WIDTH  - 40)
    PANEL_H  = min(720,  SCREEN_HEIGHT - 60)
    PANEL_CY = CY + 10

    TAB_W, TAB_H = 140, 38
    TAB_GAP      = 5
    _tabs_total  = 6 * TAB_W + 5 * TAB_GAP
    TAB1_X = CX - _tabs_total // 2
    TAB2_X = TAB1_X + TAB_W + TAB_GAP
    TAB3_X = TAB2_X + TAB_W + TAB_GAP
    TAB4_X = TAB3_X + TAB_W + TAB_GAP
    TAB5_X = TAB4_X + TAB_W + TAB_GAP
    TAB6_X = TAB5_X + TAB_W + TAB_GAP

    TITLE_OFFSET  = 12
    TAB_Y_OFFSET  = 50
    CONTENT_OFFSET = TAB_Y_OFFSET + TAB_H + 16

    BTN_BACK_Y = PANEL_CY + PANEL_H // 2 - 36

    ROW_H   = 50
    LIST_X0 = CX - PANEL_W // 2 + 20
    LIST_W  = PANEL_W - 40
    LIST_Y0 = PANEL_CY - PANEL_H // 2 + CONTENT_OFFSET + 24

    def set_feedback(msg, col=WHITE, duration=160):
        nonlocal feedback_msg, feedback_col, feedback_timer
        feedback_msg = msg; feedback_col = col; feedback_timer = duration

    def _draw_player_row(p, ry, hov, selected):
        row_bg     = (40, 60, 110, 220) if selected else ((30, 40, 80, 180) if hov else (18, 24, 55, 160))
        row_border = ADMIN_COLOR if selected else (GOLD if hov else (40, 50, 90))
        rs = pygame.Surface((LIST_W, ROW_H - 4), pygame.SRCALPHA)
        pygame.draw.rect(rs, row_bg,            (0, 0, LIST_W, ROW_H - 4), border_radius=10)
        pygame.draw.rect(rs, (*row_border, 200), (0, 0, LIST_W, ROW_H - 4), 2, border_radius=10)
        screen.blit(rs, (LIST_X0, ry))
        name_surf = font_small.render(get_display_name(p.get("name","?"))[:18], True, (GOLD if selected else WHITE))
        screen.blit(name_surf, (LIST_X0 + 14, ry + (ROW_H-4)//2 - name_surf.get_height()//2))
        info_txt = font_tiny.render(
            f"Coins:{p.get('total_coins',0)}  MC:{p.get('mission_coins',0)}  Best:{p.get('best_score',0)}"
            + ("  [BANNI]" if p.get("is_banned") else "") + ("  [ADMIN]" if p.get("is_admin") else ""),
            True, (200, 210, 240))
        screen.blit(info_txt, (LIST_X0 + LIST_W//3, ry + (ROW_H-4)//2 - info_txt.get_height()//2))

    EDIT_PANEL_W  = min(PANEL_W - 40, 900)
    EDIT_PANEL_H  = 500
    EDIT_PANEL_CY = PANEL_CY
    FIELD_LABEL_W = 200; FIELD_W = 140; FIELD_H = 34
    EDITBTN_W = 100; EDITBTN_H = 32

    def _field_x(EX_L):     return EX_L + FIELD_LABEL_W
    def _editbtn_cx(EX_L):  return EX_L + FIELD_LABEL_W + FIELD_W + EDITBTN_W//2 + 10
    def _edit_coords():
        return EDIT_PANEL_CY - EDIT_PANEL_H//2 + 76, CX - EDIT_PANEL_W//2 + 28

    def _draw_field(label, field_key, val_in_data, row_y, label_col):
        EY0, EX_L = _edit_coords()
        lbl_s = font_small.render(label, True, label_col)
        screen.blit(lbl_s, (EX_L, row_y + FIELD_H//2 - lbl_s.get_height()//2))
        if edit_field == field_key:
            display_txt = edit_values.get(field_key, str(val_in_data))
            cursor = "|" if int(t*3)%2==0 else ""
            val_col = (80, 220, 255); fc = (22,38,78,225); fb = (90,155,255)
        else:
            display_txt = str(val_in_data); cursor = ""
            val_col = WHITE; fc = (14,22,50,180); fb = (50,70,120)
        # Champ décalé vers la droite, plus large, sans bouton EDITER
        fx = EX_L + FIELD_LABEL_W + 20
        fw = FIELD_W + EDITBTN_W + 20
        fs = pygame.Surface((fw, FIELD_H), pygame.SRCALPHA)
        pygame.draw.rect(fs, fc, (0,0,fw,FIELD_H), border_radius=8)
        pygame.draw.rect(fs, (*fb,200), (0,0,fw,FIELD_H), 2, border_radius=8)
        screen.blit(fs, (fx, row_y))
        val_s = font_small.render(display_txt+cursor, True, val_col)
        screen.blit(val_s, (fx+8, row_y+FIELD_H//2-val_s.get_height()//2))
        return fx, fw  # retourne la zone cliquable (x, largeur)

    def _draw_edit_panel(p):
        draw_panel(CX, EDIT_PANEL_CY, EDIT_PANEL_W, EDIT_PANEL_H, radius=14, border=ADMIN_COLOR)
        EY0, EX_L = _edit_coords()
        nm = get_display_name(p.get("name","?"))
        nm_s = font_med.render(nm, True, WHITE)
        screen.blit(nm_s, (CX - nm_s.get_width()//2, EDIT_PANEL_CY - EDIT_PANEL_H//2 + 18))
        # Champs éditables (sans bouton EDITER — cliquer directement dedans)
        _draw_field("Pièces (total_coins)",   "total_coins",   p.get("total_coins",0),   EY0,      GOLD)
        _draw_field("Pièces mission",          "mission_coins", p.get("mission_coins",0), EY0+56,   (100,220,255))
        _draw_field("Meilleur score",          "best_score",    p.get("best_score",0),    EY0+112,  (255,100,100))
        # Missions
        mis_y = EY0 + 168
        mis_lbl = font_small.render("Missions", True, ORANGE)
        screen.blit(mis_lbl, (EX_L, mis_y + FIELD_H//2 - mis_lbl.get_height()//2))
        draw_btn("RESET MISSIONS", CX + 120, mis_y+FIELD_H//2, EDITBTN_W+80, EDITBTN_H, small=True)
        # Séparateur
        sep_y = EY0 + 218
        pygame.draw.line(screen, (*GOLD, 60), (CX-EDIT_PANEL_W//2+20, sep_y), (CX+EDIT_PANEL_W//2-20, sep_y))
        # Enregistrer
        sv_y = sep_y + 30
        if pending_save:
            draw_btn("ENREGISTRER", CX, sv_y, 240, 40, accent=True)
        else:
            sv_lbl = font_tiny.render("Aucune modification en attente", True, GREY)
            screen.blit(sv_lbl, (CX-sv_lbl.get_width()//2, sv_y-sv_lbl.get_height()//2))
        # Bannir / Admin
        _ban_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 110
        _is_banned = p.get("is_banned", False)
        _is_adm    = p.get("is_admin",  False)
        draw_btn("BANNIR" if not _is_banned else "DÉBANNIR",
                 CX - 120, _ban_y, 180, 36, danger=not _is_banned, small=True)
        draw_btn("RETIRER ADMIN" if _is_adm else "RENDRE ADMIN",
                 CX + 80, _ban_y, 180, 36, accent=not _is_adm, small=True)
        # Fermer
        close_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 52
        draw_btn("FERMER", CX, close_y, 200, 40, small=True)
        # Réinitialiser — tout en bas, séparé
        rst_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 8
        if confirm_reset:
            msg_s = font_tiny.render("Confirmer la réinitialisation complète ?", True, RED_HOT)
            screen.blit(msg_s, (CX-msg_s.get_width()//2, rst_y - 38))
            draw_btn("OUI",     CX-80, rst_y, 130, 32, danger=True)
            draw_btn("ANNULER", CX+80, rst_y, 130, 32)
        else:
            draw_btn("RÉINITIALISER LE PROFIL", CX, rst_y, 280, 32, danger=True, small=True)

    def _load_all_players():
        try:
            rows = _sb_get("players", "order=name.asc&limit=200")
            return [_row_to_player(r) for r in rows]
        except:
            return list(data.get("players", {}).values())

    all_players = _load_all_players()

    while True:
        clock.tick(FPS)
        t += 0.04
        mx, my = pygame.mouse.get_pos()
        if feedback_timer > 0: feedback_timer -= 1
        if admin_feedback_timer > 0: admin_feedback_timer -= 1
        if bug_copied_timer > 0: bug_copied_timer -= 1

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if bug_popup: bug_popup = None; continue
                    if admin_input_active: admin_input_active = False; continue
                    if banner_editing: banner_editing = False; continue
                    if selected_player: selected_player = None; continue
                    return
                if admin_input_active and current_tab == TAB_ADMINS:
                    if event.key == K_BACKSPACE: admin_input_text = admin_input_text[:-1]
                    elif event.unicode and len(admin_input_text) < 30: admin_input_text += event.unicode
                    continue
                if banner_editing and current_tab == TAB_BANNER:
                    if event.key == K_RETURN:
                        banner_editing = False
                    elif event.key == K_BACKSPACE:
                        if banner_cursor > 0:
                            banner_message = banner_message[:banner_cursor-1] + banner_message[banner_cursor:]
                            banner_cursor -= 1
                    elif event.key == K_DELETE:
                        if banner_cursor < len(banner_message):
                            banner_message = banner_message[:banner_cursor] + banner_message[banner_cursor+1:]
                    elif event.key == K_LEFT:
                        if pygame.key.get_mods() & KMOD_CTRL:
                            # Aller au mot précédent
                            pos = banner_cursor - 1
                            while pos > 0 and banner_message[pos-1] == ' ': pos -= 1
                            while pos > 0 and banner_message[pos-1] != ' ': pos -= 1
                            banner_cursor = pos
                        else:
                            banner_cursor = max(0, banner_cursor - 1)
                    elif event.key == K_RIGHT:
                        if pygame.key.get_mods() & KMOD_CTRL:
                            pos = banner_cursor
                            while pos < len(banner_message) and banner_message[pos] == ' ': pos += 1
                            while pos < len(banner_message) and banner_message[pos] != ' ': pos += 1
                            banner_cursor = pos
                        else:
                            banner_cursor = min(len(banner_message), banner_cursor + 1)
                    elif event.key == K_HOME:
                        banner_cursor = 0
                    elif event.key == K_END:
                        banner_cursor = len(banner_message)
                    elif event.unicode and event.unicode.isprintable() and len(banner_message) < 200:
                        banner_message = banner_message[:banner_cursor] + event.unicode + banner_message[banner_cursor:]
                        banner_cursor += 1
                    continue
                if edit_field is not None:
                    if event.key == K_RETURN: edit_field = None
                    elif event.key == K_BACKSPACE:
                        cur = edit_values.get(edit_field,""); edit_values[edit_field] = cur[:-1]; pending_save = True
                    elif event.unicode.isdigit() and len(edit_values.get(edit_field,"")) < 10:
                        edit_values[edit_field] = edit_values.get(edit_field,"") + event.unicode; pending_save = True
                # Ctrl+C dans la popup de bug
                if bug_popup is not None and event.key == K_c and (pygame.key.get_mods() & KMOD_CTRL):
                    try:
                        pygame.scrap.init()
                        _pop_full_text_ctrlc = str(bug_popup.get('text',''))
                        sel_ctrlc = _pop_full_text_ctrlc[min(bug_sel_start,bug_sel_end):max(bug_sel_start,bug_sel_end)] \
                                    if bug_sel_start != -1 and bug_sel_start != bug_sel_end \
                                    else _pop_full_text_ctrlc
                        pygame.scrap.put(pygame.SCRAP_TEXT, (sel_ctrlc + '\0').encode('utf-8'))
                        bug_copied_timer = 120
                    except Exception:
                        pass

            # Drag de sélection dans la popup
            if event.type == MOUSEMOTION and bug_sel_dragging and bug_popup is not None:
                _POP_W_m = min(PANEL_W - 60, 860); _POP_H_m = min(PANEL_H - 80, 520)
                _POP_CX_m = CX; _POP_CY_m = CY
                _POP_TXT_W_m = _POP_W_m - 48
                _POP_TXT_X_m = _POP_CX_m - _POP_W_m//2 + 24
                _POP_TXT_Y0_m = _POP_CY_m - _POP_H_m//2 + 56
                _pop_line_h_m = font_tiny.get_linesize()
                _pop_full_m = str(bug_popup.get('text',''))
                _pop_words_m = _pop_full_m.split(); _pop_lines_m = []; _pop_cur_m = ""; _starts_m = [0]
                for _pw_m in _pop_words_m:
                    _pt_m = (_pop_cur_m + " " + _pw_m).strip() if _pop_cur_m else _pw_m
                    if font_tiny.size(_pt_m)[0] <= _POP_TXT_W_m:
                        _pop_cur_m = _pt_m
                    else:
                        if _pop_cur_m:
                            _pop_lines_m.append(_pop_cur_m)
                            _starts_m.append(_starts_m[-1] + len(_pop_cur_m) + 1)
                        _pop_cur_m = _pw_m
                if _pop_cur_m: _pop_lines_m.append(_pop_cur_m)
                def _ptc_m(px, py):
                    li = max(0, min(int((py - _POP_TXT_Y0_m) / _pop_line_h_m), len(_pop_lines_m)-1))
                    line = _pop_lines_m[li]
                    best = len(line)
                    for ci in range(len(line)+1):
                        if _POP_TXT_X_m + font_tiny.size(line[:ci])[0] >= px:
                            best = ci; break
                    return _starts_m[li] + best
                bug_sel_end = _ptc_m(event.pos[0], event.pos[1])

            if event.type == MOUSEBUTTONUP and event.button == 1:
                bug_sel_dragging = False

            if event.type == MOUSEWHEEL:
                scroll_y = max(0, scroll_y - event.y * ROW_H)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                TAB_Y = PANEL_CY - PANEL_H//2 + TAB_Y_OFFSET
                for tab_idx, tab_x in [(TAB_STOP,TAB1_X),(TAB_PLAYERS,TAB2_X),(TAB_BANNER,TAB3_X),
                                       (TAB_PSEUDOS,TAB4_X),(TAB_BUGS,TAB5_X),(TAB_ADMINS,TAB6_X)]:
                    if btn_rect(tab_x+TAB_W//2, TAB_Y+TAB_H//2, TAB_W, TAB_H).collidepoint(event.pos):
                        current_tab = tab_idx; selected_player = None
                        edit_field = None; edit_values = {}; pending_save = False; confirm_reset = False
                        scroll_y = 0
                        if tab_idx == TAB_PSEUDOS: pseudo_requests = get_pending_requests()
                        if tab_idx == TAB_BUGS:
                            try: bug_reports_list = _sb_get("bug_reports","order=created_at.desc&limit=50") or []
                            except: bug_reports_list = []
                        if tab_idx == TAB_ADMINS: admin_input_text = ""; admin_input_active = False
                        break

                if btn_clicked(event, CX, BTN_BACK_Y, 260, 50): return

                if current_tab == TAB_STOP:
                    BTN_STOP_Y   = PANEL_CY + 30
                    BTN_REMOVE_Y = PANEL_CY + 140
                    if btn_clicked(event, CX, BTN_STOP_Y, 300, 46):
                        if create_stop_file(): set_feedback("Maintenance activée — tous les joueurs voient la page maintenance", ADMIN_COLOR, 220)
                        else: set_feedback("Erreur activation maintenance", RED_HOT)
                    if btn_clicked(event, CX, BTN_REMOVE_Y, 300, 46):
                        if remove_stop_file(): set_feedback("Maintenance désactivée", GREEN2, 200)
                        else: set_feedback("Erreur désactivation", ORANGE)

                elif current_tab == TAB_PLAYERS:
                    _edit_p = next((x for x in all_players if x["name"] == selected_player), None) if selected_player else None
                    if selected_player and _edit_p:
                        p = _edit_p
                        EY0, EX_L = _edit_coords()
                        # Clic direct sur les champs (plus de bouton EDITER)
                        _fw = FIELD_W + EDITBTN_W + 20
                        for fkey, row_y in [("total_coins",EY0),("mission_coins",EY0+56),("best_score",EY0+112)]:
                            _fx = EX_L + FIELD_LABEL_W + 20
                            if pygame.Rect(_fx, row_y, _fw, FIELD_H).collidepoint(event.pos):
                                edit_field = fkey
                                if fkey not in edit_values: edit_values[fkey] = str(p.get(fkey,0))
                                break
                        sv_y = EY0 + 218 + 30
                        if btn_clicked(event, CX, sv_y, 240, 40):
                            if pending_save:
                                ok = True
                                for fkey, txt in edit_values.items():
                                    try: p[fkey] = max(0, int(txt if txt else "0"))
                                    except ValueError: set_feedback(f"Valeur invalide pour {fkey}", RED_HOT); ok = False
                                if ok:
                                    _sb_post("players", _player_to_row(p), upsert=True); _pc_set(p["name"],p)
                                    all_players = _load_all_players()
                                    set_feedback("Modifications enregistrées !", GREEN2, 200)
                                    pending_save = False; edit_field = None
                            continue
                        mis_y = EY0 + 168
                        if btn_clicked(event, CX + 120, mis_y+FIELD_H//2, EDITBTN_W+80, EDITBTN_H):
                            p["missions"] = {}; p["missions_stats"] = {}
                            _sb_post("players", _player_to_row(p), upsert=True); _pc_set(p["name"],p)
                            set_feedback("Missions réinitialisées", ORANGE, 160); continue
                        _ban_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 110
                        if btn_clicked(event, CX-120, _ban_y, 180, 36):
                            p["is_banned"] = not p.get("is_banned",False)
                            _sb_post("players", _player_to_row(p), upsert=True); _pc_set(p["name"],p)
                            all_players = _load_all_players()
                            set_feedback(f"{'Banni' if p['is_banned'] else 'Débanni'} : {p['name']}", ADMIN_COLOR if p["is_banned"] else GREEN2, 180); continue
                        if btn_clicked(event, CX+80, _ban_y, 180, 36):
                            p["is_admin"] = not p.get("is_admin",False)
                            _sb_post("players", _player_to_row(p), upsert=True); _pc_set(p["name"],p)
                            all_players = _load_all_players()
                            set_feedback(f"{'Admin accordé' if p['is_admin'] else 'Admin retiré'} : {p['name']}", GOLD, 180); continue
                        close_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 52
                        if btn_clicked(event, CX, close_y, 200, 40):
                            selected_player = None; edit_field = None; edit_values = {}; pending_save = False; confirm_reset = False
                            continue
                        rst_y = EDIT_PANEL_CY + EDIT_PANEL_H//2 - 8
                        if confirm_reset:
                            if btn_clicked(event, CX-80, rst_y, 130, 32):
                                name = p["name"]
                                reset_p = {"name":name,"display_name":name,"best_score":0,"games_played":0,
                                           "total_score":0,"total_coins":0,"mission_coins":0,"owned_skins":["Flappy"],
                                           "owned_backgrounds":[],"owned_musics":[],"missions":{},"missions_stats":{},
                                           "avatar_color":[80,180,255],"avatar_image_path":None,
                                           "music_vol_menu":0.5,"music_vol_game":0.5,"sfx_vol_menu":0.7,"sfx_vol_game":0.7,
                                           "streak1_days":0,"streak1_last_day":"","completed_levels":[],"liked_levels":[],
                                           "is_admin":False,"is_banned":False}
                                _sb_post("players", _player_to_row(reset_p), upsert=True); _pc_clear(name)
                                all_players = _load_all_players()
                                set_feedback(f"Profil de {name} réinitialisé", GREEN2, 200)
                                selected_player = None; confirm_reset = False; edit_field = None; edit_values = {}; pending_save = False
                            elif btn_clicked(event, CX+80, rst_y, 130, 32):
                                confirm_reset = False
                            continue
                        if btn_clicked(event, CX, rst_y, 280, 32): confirm_reset = True; continue
                        continue
                    VISIBLE_H = PANEL_H - 140
                    if selected_player is None: all_players = _load_all_players()
                    for i, p in enumerate(all_players):
                        ry_abs = LIST_Y0 + i * ROW_H - scroll_y
                        if LIST_Y0 <= ry_abs <= LIST_Y0 + VISIBLE_H - ROW_H:
                            if pygame.Rect(LIST_X0, ry_abs, LIST_W, ROW_H-4).collidepoint(event.pos):
                                selected_player = p["name"]; edit_field = None; edit_values = {}
                                pending_save = False; confirm_reset = False; break

                elif current_tab == TAB_BANNER:
                    _ban_content_y = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET + 20
                    if btn_clicked(event, CX, _ban_content_y+50, 220, 44):
                        banner_enabled = not banner_enabled
                        set_banner_config(data, banner_enabled, banner_message)
                        set_feedback("Bandeau " + ("activé !" if banner_enabled else "désactivé !"), GREEN2 if banner_enabled else ORANGE, 160); continue
                    _ban_field_rect = pygame.Rect(CX-340, _ban_content_y+105, 680, 42)
                    if _ban_field_rect.collidepoint(event.pos):
                        banner_editing = True
                        # Positionner le curseur à l'endroit cliqué
                        _rel_x = event.pos[0] - (CX-340+10) + banner_scroll
                        best = len(banner_message)
                        for ci in range(len(banner_message)+1):
                            tw = font_tiny.size(banner_message[:ci])[0]
                            if tw >= _rel_x:
                                # Choisir le plus proche entre ci-1 et ci
                                tw_prev = font_tiny.size(banner_message[:max(0,ci-1)])[0]
                                if abs(tw_prev - _rel_x) < abs(tw - _rel_x):
                                    best = max(0, ci-1)
                                else:
                                    best = ci
                                break
                        banner_cursor = best
                        continue
                    if btn_clicked(event, CX, _ban_content_y+185, 260, 44):
                        set_banner_config(data, banner_enabled, banner_message)
                        set_feedback("Message enregistré !", GREEN2, 180); banner_editing = False; continue

                elif current_tab == TAB_BUGS:
                    # ── Gestion popup ouverte ─────────────────────────────────
                    if bug_popup is not None:
                        _POP_W = min(PANEL_W - 60, 860); _POP_H = min(PANEL_H - 80, 520)
                        _POP_CX = CX; _POP_CY = CY
                        _POP_TXT_W = _POP_W - 48
                        _POP_TXT_X = _POP_CX - _POP_W//2 + 24
                        _POP_TXT_Y0 = _POP_CY - _POP_H//2 + 56
                        _POP_BTN_AREA = 56
                        _POP_MAX_H = _POP_H - 56 - _POP_BTN_AREA
                        _pop_line_h = font_tiny.get_linesize()
                        # Rebuild lines (nécessaire pour les hit-tests)
                        _pop_full_text = str(bug_popup.get('text', ''))
                        _pop_words2 = _pop_full_text.split()
                        _pop_lines2 = []; _pop_cur2 = ""; _pop_line_starts = [0]
                        _char_idx = 0
                        for _pw2 in _pop_words2:
                            _pt2 = (_pop_cur2 + " " + _pw2).strip() if _pop_cur2 else _pw2
                            if font_tiny.size(_pt2)[0] <= _POP_TXT_W:
                                _pop_cur2 = _pt2
                            else:
                                if _pop_cur2:
                                    _pop_lines2.append(_pop_cur2)
                                    _pop_line_starts.append(_pop_line_starts[-1] + len(_pop_cur2) + 1)
                                _pop_cur2 = _pw2
                        if _pop_cur2: _pop_lines2.append(_pop_cur2)

                        def _pos_to_char(px, py):
                            """Convertit coordonnées souris → index dans _pop_full_text."""
                            li = int((py - _POP_TXT_Y0) / _pop_line_h)
                            li = max(0, min(li, len(_pop_lines2)-1))
                            line = _pop_lines2[li]
                            # Trouver la position dans la ligne
                            best = len(line)
                            for ci in range(len(line)+1):
                                tw = font_tiny.size(line[:ci])[0]
                                if _POP_TXT_X + tw >= px:
                                    best = ci; break
                            return _pop_line_starts[li] + best

                        # Bouton FERMER
                        if btn_clicked(event, _POP_CX + _POP_W//2 - 80, _POP_CY + _POP_H//2 - 30, 130, 36):
                            bug_popup = None; bug_sel_start = -1; bug_sel_end = -1
                        # Bouton COPIER TOUT
                        elif btn_clicked(event, _POP_CX - _POP_W//2 + 80, _POP_CY + _POP_H//2 - 30, 130, 36):
                            try:
                                pygame.scrap.init()
                                sel = _pop_full_text[min(bug_sel_start,bug_sel_end):max(bug_sel_start,bug_sel_end)] \
                                      if bug_sel_start != -1 and bug_sel_start != bug_sel_end \
                                      else _pop_full_text
                                pygame.scrap.put(pygame.SCRAP_TEXT, (sel + '\0').encode('utf-8'))
                                bug_copied_timer = 120
                            except Exception:
                                pass
                        # Clic dans la zone texte → début sélection
                        elif pygame.Rect(_POP_TXT_X, _POP_TXT_Y0, _POP_TXT_W, _POP_MAX_H).collidepoint(event.pos):
                            bug_sel_start = _pos_to_char(event.pos[0], event.pos[1])
                            bug_sel_end   = bug_sel_start
                            bug_sel_dragging = True
                        continue  # bloquer les clics derrière la popup
                    # ── Clic sur une carte → ouvre la popup ──────────────────
                    _bug_y02 = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET + 10
                    _BUG_LINE_H2 = font_tiny.get_linesize()
                    _BUG_CARD_MAX_W2 = PANEL_W - 40 - 120
                    def _bug_card_h2(br):
                        words = str(br.get('text', '')).split()
                        lines, cur = [], ""
                        for w in words:
                            test = (cur + " " + w).strip()
                            if font_tiny.size(test)[0] <= _BUG_CARD_MAX_W2:
                                cur = test
                            else:
                                if cur: lines.append(cur)
                                cur = w
                        if cur: lines.append(cur)
                        return 28 + max(1, len(lines)) * _BUG_LINE_H2 + 28
                    _cur_y2 = _bug_y02 - scroll_y
                    for _bi2, _br2 in enumerate(bug_reports_list):
                        _card_h2 = _bug_card_h2(_br2)
                        _by2 = _cur_y2
                        _cur_y2 += _card_h2 + 6
                        _del_cx2 = CX + PANEL_W//2 - 80; _del_cy2 = _by2 + _card_h2//2
                        if btn_clicked(event, _del_cx2, _del_cy2, 110, 32):
                            _sb_delete("bug_reports", f"id=eq.{_br2.get('id','')}")
                            bug_reports_list = [x for x in bug_reports_list if x.get('id') != _br2.get('id')]
                            set_feedback("Bug report supprimé.", GREEN2, 120); break
                        # Clic sur la carte (hors bouton SUPPR.) → popup
                        _card_rect = pygame.Rect(CX-PANEL_W//2+20, _by2, PANEL_W-40-120, _card_h2)
                        if _card_rect.collidepoint(event.pos):
                            bug_popup = _br2; bug_copied_timer = 0
                            bug_sel_start = -1; bug_sel_end = -1; bug_sel_dragging = False; break

                elif current_tab == TAB_ADMINS:
                    _add_y2 = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET + 200
                    _inp_w2 = min(420, PANEL_W-340); _inp_h2 = 46; _inp_x2 = CX - PANEL_W//2 + 30
                    if pygame.Rect(_inp_x2, _add_y2+26, _inp_w2, _inp_h2).collidepoint(event.pos):
                        admin_input_active = True
                    if btn_clicked(event, _inp_x2+_inp_w2+80, _add_y2+26+_inp_h2//2, 140, 42):
                        _tgt = admin_input_text.strip().lower()
                        if _tgt:
                            _rows_tgt = _sb_get("players", f"name=eq.{_tgt}&limit=1")
                            if _rows_tgt:
                                _sb_patch("players", f"name=eq.{_tgt}", {"is_admin":True})
                                admin_feedback_msg = f"✓ {_tgt} est maintenant admin"; admin_feedback_col = GREEN2
                                push_notif(f"Admin accordé à {_tgt}", GREEN2)
                            else:
                                admin_feedback_msg = f"✗ Joueur '{_tgt}' introuvable"; admin_feedback_col = ADMIN_COLOR
                            admin_feedback_timer = 200; admin_input_text = ""
                    if btn_clicked(event, _inp_x2+_inp_w2+240, _add_y2+26+_inp_h2//2, 150, 42):
                        _tgt = admin_input_text.strip().lower()
                        if _tgt:
                            _sb_patch("players", f"name=eq.{_tgt}", {"is_admin":False})
                            admin_feedback_msg = f"Admin retiré à {_tgt}"; admin_feedback_col = ORANGE
                            admin_feedback_timer = 200; admin_input_text = ""

                elif current_tab == TAB_PSEUDOS:
                    pseudo_requests = get_pending_requests()
                    _preq_y0 = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET + 10; _preq_row_h = 72
                    for _ri, _req in enumerate(pseudo_requests):
                        _ry = _preq_y0 + _ri * _preq_row_h; _sess = _req.get("session","")
                        if btn_clicked(event, CX+160, _ry+_preq_row_h//2, 120, 36):
                            accept_pseudo_request(_sess); pseudo_requests = get_pending_requests()
                            set_feedback(f"Pseudo « {_req['pseudo']} » accepté !", GREEN2, 200); continue
                        if btn_clicked(event, CX+300, _ry+_preq_row_h//2, 120, 36):
                            reject_pseudo_request(_sess); pseudo_requests = get_pending_requests()
                            set_feedback("Demande refusée.", ORANGE, 160); continue

        # ══ RENDU ══
        screen.blit(BACKGROUND, (0, 0)); draw_overlay(215)
        draw_panel(CX, PANEL_CY, PANEL_W, PANEL_H, radius=18, border=ADMIN_COLOR)
        tit = font_small.render("ADMINISTRATION", True, ADMIN_COLOR)
        screen.blit(tit, (CX-tit.get_width()//2, PANEL_CY-PANEL_H//2+TITLE_OFFSET))

        TAB_Y = PANEL_CY - PANEL_H//2 + TAB_Y_OFFSET
        _nb_pending = len(pseudo_requests)
        _pseudo_tab_label = f"PSEUDOS ({_nb_pending})" if _nb_pending > 0 else "PSEUDOS"
        for tab_idx, tab_label, tab_x in [
            (TAB_STOP,    "ARRÊT",           TAB1_X+TAB_W//2),
            (TAB_PLAYERS, "JOUEURS",         TAB2_X+TAB_W//2),
            (TAB_BANNER,  "BANDEAU",         TAB3_X+TAB_W//2),
            (TAB_PSEUDOS, _pseudo_tab_label, TAB4_X+TAB_W//2),
            (TAB_BUGS,    "BUG REPORTS",     TAB5_X+TAB_W//2),
            (TAB_ADMINS,  "ADMINS",          TAB6_X+TAB_W//2),
        ]:
            active   = (current_tab == tab_idx)
            has_badge = (tab_idx == TAB_PSEUDOS and _nb_pending > 0 and not active)
            tab_bg   = ADMIN_COLOR if active else ((80,20,20) if has_badge else (35,22,22))
            tab_brd  = ADMIN_BORDER if active else ((200,60,60) if has_badge else (80,40,40))
            ts = pygame.Surface((TAB_W,TAB_H), pygame.SRCALPHA)
            pygame.draw.rect(ts, (*tab_bg,220),  (0,0,TAB_W,TAB_H), border_radius=8)
            pygame.draw.rect(ts, (*tab_brd,230), (0,0,TAB_W,TAB_H), 2, border_radius=8)
            screen.blit(ts, (tab_x-TAB_W//2, TAB_Y))
            lbl_col = WHITE if active else ((255,160,160) if has_badge else (200,120,120))
            tl = font_tiny.render(tab_label, True, lbl_col)
            screen.blit(tl, (tab_x-tl.get_width()//2, TAB_Y+TAB_H//2-tl.get_height()//2))

        draw_sep(TAB_Y+TAB_H+6, w_margin=CX-PANEL_W//2+20)
        CONTENT_Y0 = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET

        if current_tab == TAB_STOP:
            file_present = stop_file_exists()
            STATUS_Y = CONTENT_Y0 + 20
            st_col = ADMIN_COLOR if file_present else GREEN2
            st_txt = "MAINTENANCE ACTIVE — page maintenance affichée pour tous" if file_present else "Aucune maintenance active"
            st_s = font_small.render(st_txt, True, st_col)
            screen.blit(st_s, (CX-st_s.get_width()//2, STATUS_Y))
            draw_sep(STATUS_Y+64, w_margin=CX-PANEL_W//2+40)
            BTN_STOP_Y = PANEL_CY+30; BTN_REMOVE_Y = PANEL_CY+140
            draw_btn("FERMER TOUS LES JEUX", CX, BTN_STOP_Y, 300, 46, danger=True, small=True)
            draw_btn("DÉSACTIVER L'ARRÊT GLOBAL", CX, BTN_REMOVE_Y, 300, 46, accent=True, small=True)

        elif current_tab == TAB_PLAYERS:
            _edit_p = next((x for x in all_players if x["name"] == selected_player), None) if selected_player else None
            if selected_player and _edit_p:
                _draw_edit_panel(_edit_p)
            else:
                VISIBLE_H = PANEL_H - 160
                total_h = len(all_players) * ROW_H; scroll_max = max(0, total_h-VISIBLE_H)
                scroll_y = max(0, min(scroll_y, scroll_max))
                hdr_y = CONTENT_Y0
                screen.blit(font_tiny.render("NOM", True, GOLD), (LIST_X0+14, hdr_y))
                screen.blit(font_tiny.render("COINS / MC / BEST", True, GOLD), (LIST_X0+LIST_W//3, hdr_y))
                clip_rect = pygame.Rect(LIST_X0, LIST_Y0, LIST_W, VISIBLE_H)
                screen.set_clip(clip_rect)
                for i, p in enumerate(all_players):
                    ry_abs = LIST_Y0 + i*ROW_H - scroll_y
                    if ry_abs+ROW_H < LIST_Y0 or ry_abs > LIST_Y0+VISIBLE_H: continue
                    hov = pygame.Rect(LIST_X0, ry_abs, LIST_W, ROW_H-4).collidepoint(mx, my)
                    sel = (p.get("name") == selected_player)
                    _draw_player_row(p, ry_abs, hov, sel)
                screen.set_clip(None)
                count_s = font_tiny.render(f"{len(all_players)} joueur(s) inscrits", True, GREY)
                screen.blit(count_s, (CX-count_s.get_width()//2, BTN_BACK_Y - 32))

        elif current_tab == TAB_BANNER:
            _ban_content_y = PANEL_CY - PANEL_H//2 + CONTENT_OFFSET + 20
            sec_lbl = font_tiny.render("MESSAGE DÉFILANT EN PAGE D'ACCUEIL", True, GREY)
            screen.blit(sec_lbl, (CX-sec_lbl.get_width()//2, _ban_content_y-10))
            draw_sep(_ban_content_y+14, w_margin=CX-PANEL_W//2+40)
            tog_label = "[ON]  BANDEAU ACTIVÉ" if banner_enabled else "[OFF] BANDEAU DÉSACTIVÉ"
            tog_col = GREEN2 if banner_enabled else (160,80,80)
            tg_s = pygame.Surface((220,44), pygame.SRCALPHA)
            pygame.draw.rect(tg_s, (10,40,20,200) if banner_enabled else (40,12,12,200), (0,0,220,44), border_radius=22)
            pygame.draw.rect(tg_s, (*tog_col,210), (0,0,220,44), 2, border_radius=22)
            screen.blit(tg_s, (CX-110, _ban_content_y+28))
            tg_txt = font_tiny.render(tog_label, True, tog_col)
            screen.blit(tg_txt, (CX-tg_txt.get_width()//2, _ban_content_y+50-tg_txt.get_height()//2))
            msg_lbl = font_tiny.render("Message du bandeau :", True, GOLD)
            screen.blit(msg_lbl, (CX-340, _ban_content_y+88))
            FIELD_X   = CX - 340
            FIELD_Y   = _ban_content_y + 105
            FIELD_W   = 680
            FIELD_H   = 42
            FIELD_PAD = 10
            field_rect = pygame.Rect(FIELD_X, FIELD_Y, FIELD_W, FIELD_H)
            fc     = (22,38,78,225) if banner_editing else (14,22,50,180)
            fb_col = (90,155,255)   if banner_editing else (50,70,120)
            fld_s  = pygame.Surface((FIELD_W, FIELD_H), pygame.SRCALPHA)
            pygame.draw.rect(fld_s, fc, (0,0,FIELD_W,FIELD_H), border_radius=8)
            pygame.draw.rect(fld_s, (*fb_col,200), (0,0,FIELD_W,FIELD_H), 2, border_radius=8)
            screen.blit(fld_s, (FIELD_X, FIELD_Y))
            # Calcul du scroll horizontal pour garder le curseur visible
            if banner_editing:
                cursor_px = font_tiny.size(banner_message[:banner_cursor])[0]
                inner_w   = FIELD_W - FIELD_PAD * 2
                if cursor_px - banner_scroll > inner_w - 8:
                    banner_scroll = cursor_px - inner_w + 8
                elif cursor_px - banner_scroll < 0:
                    banner_scroll = max(0, cursor_px - 20)
            else:
                banner_scroll = 0
            # Clipping + texte scrollé
            screen.set_clip(pygame.Rect(FIELD_X+FIELD_PAD, FIELD_Y, FIELD_W-FIELD_PAD*2, FIELD_H))
            msg_surf = font_tiny.render(banner_message, True, (80,220,255) if banner_editing else WHITE)
            screen.blit(msg_surf, (FIELD_X+FIELD_PAD - banner_scroll, FIELD_Y + FIELD_H//2 - msg_surf.get_height()//2))
            # Curseur clignotant
            if banner_editing and int(t*10)%2==0:
                cursor_draw_x = FIELD_X + FIELD_PAD + cursor_px - banner_scroll
                if FIELD_X+FIELD_PAD <= cursor_draw_x <= FIELD_X+FIELD_W-FIELD_PAD:
                    pygame.draw.line(screen, (80,220,255),
                        (cursor_draw_x, FIELD_Y+6), (cursor_draw_x, FIELD_Y+FIELD_H-6), 2)
            screen.set_clip(None)
            # Compteur caractères
            cc_s = font_tiny.render(f"{len(banner_message)}/200", True, (100,120,160))
            screen.blit(cc_s, (FIELD_X+FIELD_W-cc_s.get_width()-4, FIELD_Y-cc_s.get_height()-2))
            draw_btn("ENREGISTRER", CX, _ban_content_y+185, 260, 44, accent=True)

        elif current_tab == TAB_PSEUDOS:
            _preq_y0 = CONTENT_Y0+10; _preq_row_h = 72
            if not pseudo_requests:
                ns = font_small.render("Aucune demande en attente.", True, GREY)
                screen.blit(ns, (CX-ns.get_width()//2, CONTENT_Y0+40))
            for _ri, _req in enumerate(pseudo_requests):
                _ry = _preq_y0 + _ri*_preq_row_h
                _rs = pygame.Surface((PANEL_W-40, _preq_row_h-6), pygame.SRCALPHA)
                pygame.draw.rect(_rs, (20,16,45,200), (0,0,PANEL_W-40,_preq_row_h-6), border_radius=8)
                pygame.draw.rect(_rs, (60,40,100,180), (0,0,PANEL_W-40,_preq_row_h-6), 1, border_radius=8)
                screen.blit(_rs, (CX-PANEL_W//2+20, _ry))
                sess_s = font_small.render(f"{_req.get('session','')}  →  « {_req.get('pseudo','')} »", True, WHITE)
                screen.blit(sess_s, (CX-PANEL_W//2+34, _ry+8))
                date_s = font_tiny.render(_req.get("date",""), True, GREY)
                screen.blit(date_s, (CX-PANEL_W//2+34, _ry+32))
                draw_btn("ACCEPTER", CX+160, _ry+_preq_row_h//2, 120, 36, accent=True, small=True)
                draw_btn("REFUSER",  CX+300, _ry+_preq_row_h//2, 120, 36, danger=True, small=True)

        elif current_tab == TAB_BUGS:
            # ── Calcul dynamique de la hauteur de chaque carte (word-wrap) ──────
            _BUG_CARD_MAX_W = PANEL_W - 40 - 120  # largeur dispo pour le texte (réserver place bouton)
            _BUG_LINE_H = font_tiny.get_linesize()
            _BUG_HEADER_H = 28   # hauteur de la ligne d'entête [joueur] date
            _BUG_PAD = 14         # padding haut + bas dans la carte

            def _bug_wrap_text(text, max_w):
                """Découpe `text` en lignes qui tiennent dans max_w pixels."""
                words = text.split()
                lines = []
                current = ""
                for w in words:
                    test = (current + " " + w).strip()
                    if font_tiny.size(test)[0] <= max_w:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = w
                if current:
                    lines.append(current)
                return lines if lines else [""]

            def _bug_card_height(br):
                lines = _bug_wrap_text(str(br.get('text', '')), _BUG_CARD_MAX_W)
                return _BUG_HEADER_H + len(lines) * _BUG_LINE_H + _BUG_PAD * 2

            _bug_y0 = CONTENT_Y0 + 10
            _visible_bugs = PANEL_H - 160

            if not bug_reports_list:
                ns = font_small.render("Aucun bug report. (Clique sur l'onglet pour charger)", True, GREY)
                screen.blit(ns, (CX-ns.get_width()//2, CONTENT_Y0+40))
            else:
                screen.set_clip(pygame.Rect(CX-PANEL_W//2+20, _bug_y0, PANEL_W-40, _visible_bugs))
                _cur_y = _bug_y0 - scroll_y
                for _bi, _br in enumerate(bug_reports_list):
                    _card_h = _bug_card_height(_br)
                    _by = _cur_y
                    _cur_y += _card_h + 6  # 6 px de marge entre cartes
                    if _by + _card_h < _bug_y0 or _by > _bug_y0 + _visible_bugs:
                        continue
                    # Fond de la carte (surbrillance si survol)
                    _card_zone = pygame.Rect(CX-PANEL_W//2+20, _by, PANEL_W-40, _card_h)
                    _card_hov  = _card_zone.collidepoint(mx, my)
                    _bg_col    = (35, 24, 55, 220) if _card_hov else (25, 18, 40, 200)
                    _bd_col    = (120, 70, 180, 220) if _card_hov else (80, 40, 120, 180)
                    _bs = pygame.Surface((PANEL_W-40, _card_h), pygame.SRCALPHA)
                    pygame.draw.rect(_bs, _bg_col, (0,0,PANEL_W-40,_card_h), border_radius=8)
                    pygame.draw.rect(_bs, _bd_col, (0,0,PANEL_W-40,_card_h), 1, border_radius=8)
                    screen.blit(_bs, (CX-PANEL_W//2+20, _by))
                    # En-tête : joueur + date
                    screen.blit(font_tiny.render(
                        f"[{_br.get('player_name','?')}]  {str(_br.get('created_at',''))[:16].replace('T',' ')}",
                        True, (200,160,255)), (CX-PANEL_W//2+34, _by+_BUG_PAD))
                    # Description avec retour à la ligne
                    _desc_lines = _bug_wrap_text(str(_br.get('text', '')), _BUG_CARD_MAX_W)
                    for _li, _line in enumerate(_desc_lines):
                        screen.blit(font_tiny.render(_line, True, (200,200,220)),
                                    (CX-PANEL_W//2+34, _by + _BUG_HEADER_H + _BUG_PAD + _li*_BUG_LINE_H))
                    # Bouton supprimer centré verticalement sur la carte
                    draw_btn("SUPPR.", CX+PANEL_W//2-80, _by+_card_h//2, 110, 32, danger=True, small=True)
                screen.set_clip(None)
                screen.blit(font_tiny.render(f"{len(bug_reports_list)} rapport(s)", True, GREY), (CX-50, _bug_y0+_visible_bugs+8))

        elif current_tab == TAB_ADMINS:
            _adm_y0 = CONTENT_Y0+10
            try: _adm_rows = _sb_get("players","is_admin=eq.true&select=name,display_name&order=name.asc")
            except: _adm_rows = []
            screen.blit(font_small.render("Administrateurs actifs :", True, GOLD), (CX-PANEL_W//2+30, _adm_y0))
            if not _adm_rows:
                screen.blit(font_tiny.render("Aucun admin dans la base.", True, GREY), (CX-PANEL_W//2+30, _adm_y0+34))
            for _ai, _ar in enumerate(_adm_rows):
                _aname = _ar.get("display_name") or _ar.get("name","?")
                screen.blit(font_small.render(f"  ★  {_aname}  ({_ar.get('name','')})", True, (255,200,60)), (CX-PANEL_W//2+30, _adm_y0+34+_ai*32))
            _add_lbl = font_tiny.render("Nom de session exact du joueur à promouvoir / rétrograder :", True, (160,165,195))
            _add_y = _adm_y0+200
            screen.blit(_add_lbl, (CX-PANEL_W//2+30, _add_y))
            _inp_w = min(420, PANEL_W-340); _inp_h = 46; _inp_x = CX-PANEL_W//2+30
            _inp_bg = pygame.Surface((_inp_w,_inp_h), pygame.SRCALPHA)
            pygame.draw.rect(_inp_bg, (255,255,255,22 if admin_input_active else 12), (0,0,_inp_w,_inp_h), border_radius=8)
            screen.blit(_inp_bg, (_inp_x, _add_y+26))
            pygame.draw.rect(screen, GOLD if admin_input_active else (60,65,100), (_inp_x,_add_y+26,_inp_w,_inp_h), 2, border_radius=8)
            _it = font_small.render(admin_input_text+("|" if admin_input_active and int(t*10)%2==0 else ""), True, WHITE)
            screen.blit(_it, (_inp_x+10, _add_y+26+_inp_h//2-_it.get_height()//2))
            draw_btn("PROMOUVOIR",  _inp_x+_inp_w+80,  _add_y+26+_inp_h//2, 140, 42, accent=True, small=True)
            draw_btn("RÉTROGRADER", _inp_x+_inp_w+240, _add_y+26+_inp_h//2, 150, 42, danger=True, small=True)
            if admin_feedback_timer > 0:
                _afb = font_tiny.render(admin_feedback_msg, True, admin_feedback_col)
                screen.blit(_afb, (CX-PANEL_W//2+30, _add_y+82))

        if feedback_timer > 0:
            a = min(255, feedback_timer*4)
            fb = font_small.render(feedback_msg, True, feedback_col)
            fw = fb.get_width()+40; fh = fb.get_height()+16
            fb_bg = pygame.Surface((fw,fh), pygame.SRCALPHA)
            pygame.draw.rect(fb_bg, (8,8,20,210), (0,0,fw,fh), border_radius=10)
            pygame.draw.rect(fb_bg, (*feedback_col,160), (0,0,fw,fh), 2, border_radius=10)
            fb_bg.set_alpha(a); fb.set_alpha(a)
            screen.blit(fb_bg, (CX-fw//2, BTN_BACK_Y-50))
            screen.blit(fb, (CX-fb.get_width()//2, BTN_BACK_Y-50+8))

        # ── Popup de lecture du bug report ────────────────────────────────────
        if bug_popup is not None:
            _POP_W = min(PANEL_W - 60, 860); _POP_H = min(PANEL_H - 80, 520)
            _POP_CX = CX; _POP_CY = CY
            # Fond assombri
            _overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            _overlay.fill((0, 0, 0, 160))
            screen.blit(_overlay, (0, 0))
            # Panneau popup
            draw_panel(_POP_CX, _POP_CY, _POP_W, _POP_H, radius=14, border=(120, 60, 200))
            # En-tête
            _ph_txt = font_small.render(
                f"[{bug_popup.get('player_name','?')}]  "
                f"{str(bug_popup.get('created_at',''))[:16].replace('T',' ')}",
                True, (200, 160, 255))
            screen.blit(_ph_txt, (_POP_CX - _POP_W//2 + 24, _POP_CY - _POP_H//2 + 18))
            pygame.draw.line(screen, (80, 50, 130),
                             (_POP_CX - _POP_W//2 + 16, _POP_CY - _POP_H//2 + 44),
                             (_POP_CX + _POP_W//2 - 16, _POP_CY - _POP_H//2 + 44), 1)
            # Zone texte
            _POP_TXT_W = _POP_W - 48
            _POP_TXT_X = _POP_CX - _POP_W//2 + 24
            _POP_TXT_Y0 = _POP_CY - _POP_H//2 + 56
            _POP_BTN_AREA = 56
            _POP_MAX_H = _POP_H - 56 - _POP_BTN_AREA
            _pop_line_h = font_tiny.get_linesize()
            # Rebuild lines + line_starts pour highlight
            _pop_full_text = str(bug_popup.get('text', ''))
            _pop_words = _pop_full_text.split()
            _pop_lines = []; _pop_cur = ""; _pop_line_starts = [0]
            for _pw in _pop_words:
                _pt = (_pop_cur + " " + _pw).strip() if _pop_cur else _pw
                if font_tiny.size(_pt)[0] <= _POP_TXT_W:
                    _pop_cur = _pt
                else:
                    if _pop_cur:
                        _pop_lines.append(_pop_cur)
                        _pop_line_starts.append(_pop_line_starts[-1] + len(_pop_cur) + 1)
                    _pop_cur = _pw
            if _pop_cur: _pop_lines.append(_pop_cur)
            # Sélection normalisée
            _sel_a = min(bug_sel_start, bug_sel_end) if bug_sel_start != -1 else -1
            _sel_b = max(bug_sel_start, bug_sel_end) if bug_sel_start != -1 else -1
            # Clip zone texte
            screen.set_clip(pygame.Rect(_POP_TXT_X, _POP_TXT_Y0, _POP_TXT_W, _POP_MAX_H))
            for _pli, _pline in enumerate(_pop_lines):
                _ply = _POP_TXT_Y0 + _pli * _pop_line_h
                if _ply > _POP_TXT_Y0 + _POP_MAX_H: break
                _ls = _pop_line_starts[_pli]
                _le = _ls + len(_pline)
                # Highlight si cette ligne intersecte la sélection
                if _sel_a != _sel_b and _sel_a != -1 and _sel_b > _ls and _sel_a < _le:
                    _ha = max(_sel_a - _ls, 0); _hb = min(_sel_b - _ls, len(_pline))
                    _hx1 = _POP_TXT_X + font_tiny.size(_pline[:_ha])[0]
                    _hx2 = _POP_TXT_X + font_tiny.size(_pline[:_hb])[0]
                    _hs = pygame.Surface((_hx2 - _hx1, _pop_line_h), pygame.SRCALPHA)
                    _hs.fill((100, 120, 255, 120))
                    screen.blit(_hs, (_hx1, _ply))
                screen.blit(font_tiny.render(_pline, True, (215, 215, 235)), (_POP_TXT_X, _ply))
            screen.set_clip(None)
            # Hint sélection
            _hint_sel = font_tiny.render("Cliquer-glisser pour sélectionner • Ctrl+C pour copier", True, (120, 110, 160))
            screen.blit(_hint_sel, (_POP_CX - _hint_sel.get_width()//2, _POP_CY + _POP_H//2 - 56 - _hint_sel.get_height() - 4))
            # Boutons bas
            _pop_btn_y = _POP_CY + _POP_H//2 - 30
            _has_sel = _sel_a != -1 and _sel_a != _sel_b
            _copy_label = "COPIÉ !" if bug_copied_timer > 0 else ("COPIER SÉLEC." if _has_sel else "TOUT COPIER")
            draw_btn(_copy_label, _POP_CX - _POP_W//2 + 90, _pop_btn_y, 150, 36, accent=(bug_copied_timer == 0))
            draw_btn("FERMER", _POP_CX + _POP_W//2 - 80, _pop_btn_y, 130, 36)

        draw_btn("RETOUR", CX, BTN_BACK_Y, 260, 50)
        draw_notifs()
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  THREAD DE SURVEILLANCE STOP FILE
# ══════════════════════════════════════════════════════════════════════════════
_stop_watcher_active  = threading.Event()
_stop_watcher_active.set()
_maintenance_triggered = threading.Event()   # set() = afficher page maintenance

# ── Vérification pseudo accepté/refusé en arrière-plan ───────────────────────
_pseudo_notif_player_name  = None   # nom du joueur courant (initialisé dans main())
_pseudo_notif_player_ref   = None   # référence au dict player en mémoire (pour mise à jour directe)
_pseudo_notif_was_pending  = False
_pseudo_notif_last_check   = 0.0

def _pseudo_watcher():
    """Vérifie toutes les 8 secondes si une demande de pseudo a été traitée."""
    global _pseudo_notif_was_pending, _pseudo_notif_last_check
    while True:
        time.sleep(8.0)
        if not _pseudo_notif_player_name:
            continue
        try:
            _is_pending = has_pending_request(_pseudo_notif_player_name)
            if _pseudo_notif_was_pending and not _is_pending:
                # Demande disparue → lire le vrai display_name depuis Supabase
                # (ignorer complètement le cache local qui peut être périmé)
                _invalidate_display_name(_pseudo_notif_player_name)
                rows = _sb_get("players", f"name=eq.{_pseudo_notif_player_name}&select=display_name&limit=1")
                _new = (rows[0].get("display_name") or _pseudo_notif_player_name) if rows else _pseudo_notif_player_name
                _old_cache = _display_name_cache.get(_pseudo_notif_player_name, _pseudo_notif_player_name)

                if _new and _new != _pseudo_notif_player_name and _new != _old_cache:
                    # Pseudo accepté : mettre à jour le cache ET l'objet player en mémoire
                    _display_name_cache[_pseudo_notif_player_name] = _new
                    if _pseudo_notif_player_ref is not None:
                        _pseudo_notif_player_ref["display_name"] = _new
                    push_notif(f"✓ Pseudo changé en « {_new} » !", (60, 210, 110), 400)
                else:
                    # La demande a disparu mais le pseudo n'a pas changé → refusé
                    push_notif("✗ Demande de pseudo refusée.", (230, 80, 80), 400)
            _pseudo_notif_was_pending = _is_pending
        except Exception:
            pass

threading.Thread(target=_pseudo_watcher, daemon=True, name="PseudoWatcher").start()

def _stop_file_watcher(current_name, admin_users):
    """Vérifie Supabase config toutes les 5 secondes.
    Si stop_global actif ET joueur non admin → déclenche la page maintenance."""
    while _stop_watcher_active.is_set():
        try:
            if stop_file_exists() and current_name not in admin_users:
                _maintenance_triggered.set()
        except Exception:
            pass
        time.sleep(5.0)

def start_stop_watcher(current_name, admin_users):
    _stop_watcher_active.set()
    t = threading.Thread(
        target=_stop_file_watcher,
        args=(current_name, admin_users),
        daemon=True, name="StopWatcher"
    )
    t.start()
    return t

def draw_maintenance_screen():
    """Affiche une page de maintenance plein écran."""
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2
    clock_m = pygame.time.Clock()
    t = 0.0
    fn_big  = pygame.font.SysFont("Impact", 72)
    fn_med  = pygame.font.SysFont("Impact", 36)
    fn_sub  = pygame.font.SysFont("Verdana", 20)
    while True:
        t += 0.03
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                return
        if not stop_file_exists():
            _maintenance_triggered.clear()
            return
        screen.fill((6, 8, 20))
        for _py in range(0, SCREEN_HEIGHT, 4):
            _r = _py / SCREEN_HEIGHT
            pygame.draw.rect(screen, (int(6+10*_r), int(8+12*_r), int(20+30*_r)), (0, _py, SCREEN_WIDTH, 4))
        _pulse = int(200 + 55 * math.sin(t * 2))
        _title = fn_big.render("MAINTENANCE", True, (_pulse, 60, 60))
        _shad  = fn_big.render("MAINTENANCE", True, (0, 0, 0))
        screen.blit(_shad,  (CX - _title.get_width()//2 + 3, CY - 160 + 3))
        screen.blit(_title, (CX - _title.get_width()//2,     CY - 160))
        _sub = fn_med.render("Le jeu est temporairement indisponible", True, (220, 180, 180))
        screen.blit(_sub, (CX - _sub.get_width()//2, CY - 70))
        _msg = fn_sub.render("Reviens dans quelques minutes...", True, (150, 130, 130))
        screen.blit(_msg, (CX - _msg.get_width()//2, CY - 20))
        _dots = "." * (int(t * 1.5) % 4)
        _dot_s = fn_med.render(f"Vérification en cours{_dots}", True, (100, 100, 140))
        screen.blit(_dot_s, (CX - _dot_s.get_width()//2, CY + 40))
        _bx = CX + int(math.sin(t * 1.2) * 120)
        _by = CY + 120 + int(math.sin(t * 2.4) * 20)
        pygame.draw.circle(screen, (80, 180, 255), (_bx, _by), 18)
        pygame.draw.circle(screen, (255, 255, 255), (_bx, _by), 18, 2)
        pygame.draw.circle(screen, (255, 220, 60), (_bx + 12, _by), 8)
        pygame.draw.circle(screen, (0, 0, 0), (_bx + 6, _by - 5), 4)
        pygame.display.flip()
        clock_m.tick(60)

# ── Chargement des missions depuis Supabase config ────────────────────────────
def _load_missions_json(path="missions.json"):
    """Charge les missions depuis Supabase (table config, clé missions)."""
    def _to_tuple(m):
        return (m["id"], m["stat"], m["label"], m["description"], m["goal"], m["reward"])
    try:
        rows = _sb_get("config", "key=eq.missions")
        if rows:
            data = rows[0].get("value", {})
        else:
            raise ValueError("Pas de config missions dans Supabase")
        daily     = [_to_tuple(m) for m in data.get("daily",     [])]
        onetime   = [_to_tuple(m) for m in data.get("onetime",   [])]
        permanent = [_to_tuple(m) for m in data.get("permanent", [])]
    except Exception:
        daily = onetime = permanent = []
    all_m = {m[0]: m for m in daily + onetime + permanent}
    return daily, onetime, permanent, all_m

MISSIONS_DAILY, MISSIONS_ONETIME, MISSIONS_PERMANENT, ALL_MISSIONS = _load_missions_json()


def _today_str():
    return time.strftime("%Y-%m-%d")


def init_missions(player):
    """Initialise les données de missions dans le profil joueur si absentes."""
    if "missions" not in player:
        player["missions"] = {}
    if "missions_daily_date" not in player:
        player["missions_daily_date"] = ""
    if "missions_stats" not in player:
        player["missions_stats"] = {
            "pipes_today":      0,
            "coins_game_today": 0,
            "games_today":      0,
            "coins_spent_today":0,
            "pipes_total":      player.get("best_score", 0),
            "coins_total":      player.get("total_coins", 0),
            "games":            player.get("games_played", 0),
            "coins_spent":      0,
            "skins_owned":      len(player.get("owned_skins", ["Flappy"])),
            "bgs_owned":        len(player.get("owned_backgrounds", [])),
            "musics_owned":     len(player.get("owned_musics", [])),
            "chat_msgs":        0,
            "levels_done":      len(player.get("completed_levels", [])),
        }
    # S'assurer que tous les champs existent (migration)
    _ms = player["missions_stats"]
    for _k, _v in [
        ("coins_spent", 0), ("skins_owned", len(player.get("owned_skins", ["Flappy"]))),
        ("bgs_owned", len(player.get("owned_backgrounds", []))),
        ("musics_owned", len(player.get("owned_musics", []))),
        ("chat_msgs", 0), ("levels_done", len(player.get("completed_levels", []))),
        ("coins_spent_today", 0),
    ]:
        if _k not in _ms:
            _ms[_k] = _v
    # Reset des missions quotidiennes si nouveau jour
    # On stocke la date dans missions["_daily_date"] (persiste dans Supabase jsonb)
    today = _today_str()
    _stored_date = player["missions"].get("_daily_date", player.get("missions_daily_date", ""))
    if _stored_date != today:
        player["missions"]["_daily_date"] = today
        player["missions_daily_date"]     = today
        for mid, *_ in MISSIONS_DAILY:
            player["missions"][mid] = {"progress": 0, "claimed": False}
        player["missions_stats"]["pipes_today"]       = 0
        player["missions_stats"]["coins_game_today"]  = 0
        player["missions_stats"]["games_today"]       = 0
        player["missions_stats"]["coins_spent_today"] = 0
    # Init missions permanentes / one-time si absentes
    for mid, *_ in MISSIONS_ONETIME + MISSIONS_PERMANENT:
        if mid not in player["missions"]:
            player["missions"][mid] = {"progress": 0, "claimed": False}


def update_missions_after_game(player, score_pipes, coins_earned, data):
    """Appelé après chaque partie pour mettre à jour la progression des missions."""
    init_missions(player)
    s = player["missions_stats"]
    s["pipes_today"]      = s.get("pipes_today", 0)      + score_pipes
    s["coins_game_today"] = s.get("coins_game_today", 0) + coins_earned
    s["games_today"]      = s.get("games_today", 0)      + 1
    s["pipes_total"]      = s.get("pipes_total", 0)      + score_pipes
    s["coins_total"]      = s.get("coins_total", 0)      + coins_earned
    s["games"]            = s.get("games", 0)            + 1

    # Synchroniser les stats d'inventaire depuis le profil joueur
    s["skins_owned"]   = len(player.get("owned_skins", ["Flappy"]))
    s["bgs_owned"]     = len(player.get("owned_backgrounds", []))
    s["musics_owned"]  = len(player.get("owned_musics", []))
    s["levels_done"]   = len(player.get("completed_levels", []))

    stat_map = {
        "pipes":          s["pipes_today"],
        "coins_game":     s["coins_game_today"],
        "games":          s["games_today"],
        "score":          score_pipes,
        "pipes_total":    s["pipes_total"],
        "coins_total":    s["coins_total"],
        "coins_balance":  player.get("total_coins", 0),  # solde actuel du compte
        "coins_spent":    s.get("coins_spent", 0),
        "skins_owned":    s["skins_owned"],
        "bgs_owned":      s["bgs_owned"],
        "musics_owned":   s["musics_owned"],
        "chat_msgs":      s.get("chat_msgs", 0),
        "levels_done":    s["levels_done"],
    }

    newly_completed = []
    for mid, mtype, label, desc, goal, reward in ALL_MISSIONS.values():
        entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
        if entry["claimed"]:
            continue
        stat_key = mtype
        val = stat_map.get(stat_key, 0)
        old_prog = entry["progress"]
        new_prog = min(goal, val if mtype != "score" else max(old_prog, val))
        entry["progress"] = new_prog
        player["missions"][mid] = entry
        if new_prog >= goal and old_prog < goal:
            newly_completed.append(mid)

    save_data(data)
    return newly_completed


def claim_mission(player, mid, data):
    """Réclame la récompense d'une mission complète. Retourne nb mission_coins gagnés."""
    init_missions(player)
    entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
    _, _, _, _, goal, reward = ALL_MISSIONS[mid]
    if entry["progress"] >= goal and not entry["claimed"]:
        entry["claimed"] = True
        player["missions"][mid] = entry
        player["mission_coins"] = player.get("mission_coins", 0) + reward
        player["total_mission_coins_earned"] = player.get("total_mission_coins_earned", 0) + reward
        save_data(data)
        return reward
    return 0


def count_pending_missions(player):
    """Retourne le nb de missions complètes mais non réclamées."""
    init_missions(player)
    count = 0
    for mid, _, _, _, goal, _ in ALL_MISSIONS.values():
        entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
        if entry["progress"] >= goal and not entry["claimed"]:
            count += 1
    return count


# ── Animation de complétion de mission (in-game) ──────────────────────────────
class MissionCompleteEffect:
    """Bannière animée qui slide depuis le bas, reste 3s, puis disparaît."""
    DURATION   = 220   # frames totales
    SLIDE_IN   = 30    # frames pour entrer
    SLIDE_OUT  = 30    # frames pour sortir
    H          = 68
    W          = 480

    def __init__(self, label, reward):
        self.label   = label
        self.reward  = reward
        self.frame   = 0
        self.dead    = False

    def update(self):
        self.frame += 1
        if self.frame >= self.DURATION:
            self.dead = True

    def draw(self, surf):
        if self.dead:
            return
        f = self.frame
        # Position Y : slide depuis le bas
        if f < self.SLIDE_IN:
            progress = f / self.SLIDE_IN
            # ease-out cubic
            t = 1 - (1 - progress) ** 3
        elif f > self.DURATION - self.SLIDE_OUT:
            progress = (self.DURATION - f) / self.SLIDE_OUT
            t = progress
        else:
            t = 1.0

        target_y = SCREEN_HEIGHT - self.H - 80
        start_y  = SCREEN_HEIGHT + 10
        y = int(start_y + (target_y - start_y) * t)
        x = SCREEN_WIDTH // 2 - self.W // 2

        alpha = int(255 * min(1.0, t * 2))

        # Fond
        panel = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 40, 18, 230), (0, 0, self.W, self.H), border_radius=16)
        pygame.draw.rect(panel, (*GREEN_SOFT, alpha), (0, 0, self.W, self.H), width=3, border_radius=16)
        # Brillance
        sh = pygame.Surface((self.W - 6, self.H // 2), pygame.SRCALPHA)
        pygame.draw.rect(sh, (255, 255, 255, 18), (0, 0, self.W - 6, self.H // 2), border_radius=16)
        panel.blit(sh, (3, 3))
        surf.blit(panel, (x, y))

        # Icone check
        draw_checkmark(surf, x + 36, y + self.H // 2, 14, GREEN_SOFT)

        # Texte principal
        title = font_tiny.render("MISSION ACCOMPLIE !", True, GREEN_SOFT)
        title.set_alpha(alpha)
        surf.blit(title, (x + 62, y + 8))

        # Nom mission
        name_surf = font_small.render(self.label, True, WHITE)
        name_surf.set_alpha(alpha)
        surf.blit(name_surf, (x + 62, y + 30))

        # Récompense — pièce mission (image coin_mission.png)
        rew_txt = font_tiny.render(f"+{self.reward}", True, MISSION_COIN_COLOR2)
        rx = x + self.W - rew_txt.get_width() - 30
        mc_img = pygame.transform.smoothscale(MISSION_COIN_IMG, (34, 34))
        mc_img.set_alpha(alpha)
        surf.blit(mc_img, (rx - 26, y + self.H // 2 - 11))
        rew_txt.set_alpha(alpha)
        surf.blit(rew_txt, (rx, y + self.H // 2 - rew_txt.get_height() // 2))
        
def draw_rect_alpha(surface, color, rect, radius=0):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=radius)
    surface.blit(shape_surf, rect)

def draw_checkmark(surface, x, y, size, color):
    # Dessine un simple "V" pour les missions terminées
    points = [(x - size, y), (x - size//3, y + size), (x + size, y - size)]
    pygame.draw.lines(surface, color, False, points, 3)


def missions_screen(data, player):
    init_missions(player)
    CX, CY = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    # --- Configuration des Zones (Ratio-based pour éviter les débordements) ---
    PANEL_W = int(SCREEN_WIDTH * 0.85)
    if PANEL_W > 800: PANEL_W = 800
    PANEL_X = CX - PANEL_W // 2
    
    BTN_BACK_Y = SCREEN_HEIGHT - 60
    LIST_Y = 160 # Début de la liste après le titre et les onglets
    LIST_H = BTN_BACK_Y - LIST_Y - 40
    LIST_BOT = LIST_Y + LIST_H
    
    CARD_H = 100
    GAP = 12
    
    # Sous-zones internes à la carte (Relatif à PANEL_W)
    # [ Icône | Texte (Nom/Desc) | Barre Progrès | Récompense | Bouton ]
    COL_TEXT = 60
    COL_REWARD = PANEL_W - 240
    COL_BTN = PANEL_W - 130
    MAX_TXT_W = COL_REWARD - COL_TEXT - 20 # Limite stricte pour l'écriture

    t = 0.0
    sel_tab = 0
    scroll_y = 0
    tabs = ["QUOTIDIENNES", "UNIQUES", "PERMANENTES"]
    tab_missions = [MISSIONS_DAILY, MISSIONS_ONETIME, MISSIONS_PERMANENT]

    def draw_card(mid, label, desc, goal, reward, y):
        entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
        prog, claimed = entry["progress"], entry["claimed"]
        done = prog >= goal
        pct = min(1.0, prog / max(1, goal))
        
        # 1. Fond de la carte
        rect = pygame.Rect(PANEL_X, y, PANEL_W, CARD_H)
        bg_col = (20, 30, 50, 200)
        brd_col = (80, 100, 150)
        if claimed: 
            bg_col, brd_col = (15, 25, 15, 180), (40, 80, 40)
        elif done: 
            bg_col = (25, 50, 30, 230)
            brd_col = (100, 255, 150) if (int(t*5)%2==0) else (50, 200, 100)

        draw_rect_alpha(screen, bg_col, rect, 12)
        pygame.draw.rect(screen, brd_col, rect, 2, border_radius=12)

        # 2. Icône d'état (Pastille)
        ic_y = y + CARD_H // 2
        if claimed:
            draw_checkmark(screen, PANEL_X + 30, ic_y, 10, GREEN_SOFT)
        else:
            c = GREEN_SOFT if done else (100, 110, 140)
            pygame.draw.circle(screen, c, (PANEL_X + 30, ic_y), 10, 0 if done else 2)

        # 3. Textes (AVEC LIMITE DE LARGEUR)
        # Nom
        n_col = WHITE if not claimed else GREY
        txt_name = font_small.render(label.upper(), True, n_col)
        if txt_name.get_width() > MAX_TXT_W: # Si ça dépasse, on rétrécit
            txt_name = pygame.transform.smoothscale(txt_name, (MAX_TXT_W, txt_name.get_height()))
        screen.blit(txt_name, (PANEL_X + COL_TEXT, y + 15))
        
        # Description
        txt_desc = font_tiny.render(desc, True, (180, 190, 210))
        if txt_desc.get_width() > MAX_TXT_W:
            txt_desc = pygame.transform.smoothscale(txt_desc, (MAX_TXT_W, txt_desc.get_height()))
        screen.blit(txt_desc, (PANEL_X + COL_TEXT, y + 42))

        # 4. Barre de progression
        b_w = MAX_TXT_W
        pygame.draw.rect(screen, (40, 45, 70), (PANEL_X + COL_TEXT, y + 72, b_w, 8), border_radius=4)
        if pct > 0:
            pygame.draw.rect(screen, (0, 255, 200) if not done else GREEN_SOFT, 
                             (PANEL_X + COL_TEXT, y + 72, int(b_w * pct), 8), border_radius=4)
        
        # Texte X/Y
        txt_prog = font_tiny.render(f"{min(prog, goal)}/{goal}", True, WHITE)
        screen.blit(txt_prog, (PANEL_X + COL_TEXT + b_w + 10, y + 68))

        # 5. Zone Récompense & Bouton
        if not claimed:
            # Petite pièce bleue
            _draw_mission_coin_icon(screen, PANEL_X + COL_REWARD, ic_y, 17)
            txt_rew = font_small.render(f"+{reward}", True, MISSION_COIN_COLOR2)
            screen.blit(txt_rew, (PANEL_X + COL_REWARD + 25, ic_y - txt_rew.get_height()//2))
            
            if done:
                draw_btn("OK", PANEL_X + COL_BTN + 60, ic_y, 100, 45, accent=True)
        else:
            txt_done = font_tiny.render("COMPLÉTÉ", True, (100, 150, 100))
            screen.blit(txt_done, (PANEL_X + COL_BTN + 20, ic_y - txt_done.get_height()//2))

    while True:
        clock.tick(FPS)
        t += 0.04
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE: return
            
            if event.type == MOUSEWHEEL:
                scroll_y = max(0, scroll_y - event.y * 30)
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Retour
                if btn_clicked(event, CX, BTN_BACK_Y, 200, 50): return
                
                # Onglets
                for i in range(len(tabs)):
                    tw = PANEL_W // 3
                    if pygame.Rect(PANEL_X + i*tw, 100, tw, 40).collidepoint(event.pos):
                        sel_tab, scroll_y = i, 0
                
                # Clic Réclamer
                m_list = tab_missions[sel_tab]
                for i, m in enumerate(m_list):
                    card_y = LIST_Y + i*(CARD_H + GAP) - scroll_y
                    if LIST_Y <= card_y <= LIST_BOT - CARD_H:
                        entry = player["missions"].get(m[0], {"progress":0, "claimed":False})
                        if entry["progress"] >= m[4] and not entry["claimed"]:
                            # Hitbox du bouton OK
                            if pygame.Rect(PANEL_X + COL_BTN, card_y + 25, 120, 50).collidepoint(event.pos):
                                claim_mission(player, m[0], data)

        # --- Dessin ---
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(200)

        # Titre
        # Dessin de l'ombre (noir, décalé de 3 pixels)
        shadow_surf = font_med.render("CENTRE DES MISSIONS", True, (0, 0, 0))
        screen.blit(shadow_surf, (CX - shadow_surf.get_width()//2 + 3, 40 + 3))

        # Dessin du texte principal (Cyan)
        title_surf = font_med.render("CENTRE DES MISSIONS", True, CYAN)
        screen.blit(title_surf, (CX - title_surf.get_width()//2, 40))

        # Onglets (Design propre)
        for i, name in enumerate(tabs):
            tw = PANEL_W // 3
            tx = PANEL_X + i * tw
            active = (i == sel_tab)
            c = (40, 60, 100) if active else (20, 25, 40)
            pygame.draw.rect(screen, c, (tx, 100, tw-4, 40), border_radius=8)
            if active: pygame.draw.rect(screen, CYAN, (tx, 100, tw-4, 40), 2, 8)
            
            t_surf = font_tiny.render(name, True, WHITE if active else GREY)
            screen.blit(t_surf, (tx + (tw//2) - t_surf.get_width()//2, 112))

            # Notif point si mission complétée non réclamée dans cet onglet
            _has_notif = False
            for _mid, _mtype, _lbl, _desc, _goal, _rew in tab_missions[i]:
                _ent = player["missions"].get(_mid, {"progress": 0, "claimed": False})
                if _ent["progress"] >= _goal and not _ent["claimed"]:
                    _has_notif = True
                    break
            if _has_notif:
                notif_x = tx + tw - 12
                notif_y = 108
                pygame.draw.circle(screen, (220, 50, 50), (notif_x, notif_y), 7)
                pygame.draw.circle(screen, (255, 120, 120), (notif_x, notif_y), 4)

        # Liste clipsée (Pour que rien ne sorte du cadre)
        screen.set_clip(pygame.Rect(0, LIST_Y, SCREEN_WIDTH, LIST_H))
        current_missions = tab_missions[sel_tab]
        for i, (mid, mtype, label, desc, goal, reward) in enumerate(current_missions):
            card_y = LIST_Y + i * (CARD_H + GAP) - scroll_y
            # On ne dessine que si c'est visible pour économiser les ressources
            if card_y > LIST_BOT or card_y < LIST_Y - CARD_H: continue
            draw_card(mid, label, desc, goal, reward, card_y)
        screen.set_clip(None)

        # Bouton Retour
        draw_btn("RETOUR", CX, BTN_BACK_Y, 220, 50)
        
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()


# ── Pipe custom pour les niveaux (position fixe + mobile optionnel) ──────────
class LevelPipe(pygame.sprite.Sprite):
    """Tuyau de niveau : position déterministe, optionnellement mobile (vertical)."""
    _IMG = None; _IMG_FLIP = None

    @classmethod
    def _load(cls):
        if cls._IMG is None:
            raw = pygame.transform.scale(
                _pygame_load('assets/sprites/pipe-green.png').convert_alpha(),
                (PIPE_WIDTH, PIPE_HEIGHT))
            cls._IMG      = raw
            cls._IMG_FLIP = pygame.transform.flip(raw, False, True)

    def __init__(self, inverted, xpos, ysize, mobile=False, mob_amp=0, mob_speed=1.0,
                 mob_dir_v="up", mob_amp_h=0, mob_speed_h=1.0, mob_dir_h="none",
                 anim_v_dir="down", anim_v_px=0, anim_v_spd=0.0, anim_v_delay=0,
                 anim_h_dir="in",   anim_h_px=0, anim_h_spd=0.0, anim_h_delay=0):
        super().__init__()
        LevelPipe._load()
        self.inverted    = inverted
        self.mobile      = mobile
        self.mob_amp     = mob_amp
        self.mob_speed   = mob_speed
        self.mob_dir_v   = mob_dir_v
        self.mob_amp_h   = mob_amp_h
        self.mob_speed_h = mob_speed_h
        self.mob_dir_h   = mob_dir_h
        self.mob_phase   = 0.0
        self.mob_phase_h = 0.0
        # Animations déclenchées après délai
        self.anim_v_dir   = anim_v_dir
        self.anim_v_px    = anim_v_px
        self.anim_v_spd   = anim_v_spd
        self.anim_v_delay = anim_v_delay  # ms
        self.anim_h_dir   = anim_h_dir
        self.anim_h_px    = anim_h_px
        self.anim_h_spd   = anim_h_spd
        self.anim_h_delay = anim_h_delay  # ms
        self._anim_v_offset = 0.0
        self._anim_h_offset = 0.0
        self.score_passed = False
        self.float_x = float(xpos)

        if inverted:
            self.image = LevelPipe._IMG_FLIP
            self.rect  = self.image.get_rect()
            self.rect.x = xpos
            self._base_y = -(self.rect.height - ysize)
        else:
            self.image = LevelPipe._IMG
            self.rect  = self.image.get_rect()
            self.rect.x = xpos
            self._base_y = SCREEN_HEIGHT - ysize
        self.rect.y = self._base_y
        self.ysize  = ysize
        self.mask   = pygame.mask.from_surface(self.image)

    def update(self, game_speed, dt=1/60, elapsed_ms=0):
        self.float_x -= game_speed
        self.rect.x = round(self.float_x)

        # ── Animation verticale déclenchée après délai ────────────────────────
        if self.anim_v_px > 0 and self.anim_v_spd > 0 and elapsed_ms >= self.anim_v_delay:
            target_v = float(self.anim_v_px) if self.anim_v_dir == "down" else -float(self.anim_v_px)
            step_v = self.anim_v_spd * dt * 60
            if abs(self._anim_v_offset - target_v) > step_v:
                self._anim_v_offset += step_v if self._anim_v_offset < target_v else -step_v
            else:
                self._anim_v_offset = target_v

        # ── Animation horizontale déclenchée après délai ──────────────────────
        if self.anim_h_px > 0 and self.anim_h_spd > 0 and elapsed_ms >= self.anim_h_delay:
            # "in" = rapprochement : tuyau bas se déplace vers le haut (son bord supérieur monte)
            # côté inverted=True (tuyau haut) : se déplace vers le bas, donc y augmente → offset +
            # côté inverted=False (tuyau bas) : se déplace vers le haut → offset -
            if self.anim_h_dir == "in":
                target_h = -float(self.anim_h_px) if not self.inverted else float(self.anim_h_px)
            else:  # "out" = écartement
                target_h = float(self.anim_h_px) if not self.inverted else -float(self.anim_h_px)
            step_h = self.anim_h_spd * dt * 60
            if abs(self._anim_h_offset - target_h) > step_h:
                self._anim_h_offset += step_h if self._anim_h_offset < target_h else -step_h
            else:
                self._anim_h_offset = target_h

        v_off = int(self._anim_v_offset)
        # Offset horizontal = déplacement vertical du gap (rapprochement/écartement)
        h_off = int(self._anim_h_offset)

        if self.mobile:
            # Mouvement vertical sinusoïdal legacy
            self.mob_phase += dt * self.mob_speed
            raw_v = math.sin(self.mob_phase) * self.mob_amp
            if self.mob_dir_v == "down":
                offset = int(raw_v)
            else:
                offset = int(-raw_v)
            # Mouvement horizontal sinusoïdal legacy
            if self.mob_amp_h > 0 and self.mob_dir_h != "none":
                self.mob_phase_h += dt * self.mob_speed_h
                raw_h = math.sin(self.mob_phase_h) * self.mob_amp_h
                if self.mob_dir_h == "in":
                    h_offset = int(-abs(raw_h)) if not self.inverted else int(abs(raw_h))
                else:
                    h_offset = int(abs(raw_h)) if not self.inverted else int(-abs(raw_h))
                self.float_x += h_offset * dt * 2
            self.rect.y = self._base_y + offset + v_off + h_off
        else:
            self.rect.y = self._base_y + v_off + h_off


def _build_level_pipes(level_def, offset_x=0):
    """Crée les sprites LevelPipe à partir d'un dict de niveau."""
    sprites = []
    _game_zone = SCREEN_HEIGHT - GROUND_HEIGHT
    for p in level_def.get("pipes", []):
        x        = p["x"] + offset_x
        # Clamp gap_y/gap_h dans la zone jouable pour absorber les vieux niveaux
        # stockés en pixels absolus d'une autre résolution
        raw_gap_y = p["gap_y"]
        raw_gap_h = p["gap_h"]
        gap_h = max(80, min(int(raw_gap_h), int(_game_zone * 0.75)))
        gap_y = max(40, min(int(raw_gap_y), _game_zone - gap_h - 20))
        mobile   = p.get("mobile", False)
        amp      = p.get("mob_amp", 0)
        spd      = p.get("mob_speed", 1.0)
        dir_v    = p.get("mob_dir_v", "up")
        amp_h    = p.get("mob_amp_h", 0)
        spd_h    = p.get("mob_speed_h", 1.0)
        dir_h    = p.get("mob_dir_h", "none")
        # Nouvelles animations
        av_dir   = p.get("anim_v_dir",   "down")
        av_px    = p.get("anim_v_px",    0)
        av_spd   = p.get("anim_v_spd",   0.0)
        av_delay = p.get("anim_v_delay", 0)
        ah_dir   = p.get("anim_h_dir",   "in")
        ah_px    = p.get("anim_h_px",    0)
        ah_spd   = p.get("anim_h_spd",   0.0)
        ah_delay = p.get("anim_h_delay", 0)

        bot_size = SCREEN_HEIGHT - (gap_y + gap_h)
        top_size = gap_y

        sprites.append(LevelPipe(False, x, bot_size, mobile, amp, spd, dir_v, amp_h, spd_h, dir_h,
                                 av_dir, av_px, av_spd, av_delay, ah_dir, ah_px, ah_spd, ah_delay))
        sprites.append(LevelPipe(True,  x, top_size, mobile, amp, spd, dir_v, amp_h, spd_h, dir_h,
                                 av_dir, av_px, av_spd, av_delay, ah_dir, ah_px, ah_spd, ah_delay))
    return sprites


# ══════════════════════════════════════════════════════════════════════════════
#  LECTEUR DE NIVEAU (jouer un niveau officiel ou communautaire)
# ══════════════════════════════════════════════════════════════════════════════
def play_level(level_def, player, data, selected_skin, is_editor_test=False):
    """
    Lance un niveau fixe. Boucle tant que le joueur veut rejouer apres une mort.
    Retourne: 'completed', 'dead', 'quit', 'back_to_editor'
    """
    while True:
        result = _play_level_once(level_def, player, data, selected_skin, is_editor_test)
        if result == 'dead':
            action = _level_dead_screen(is_editor_test)
            if action == 'retry':
                continue   # relancer le niveau depuis le debut
            else:
                return result
        return result


def _play_level_once(level_def, player, data, selected_skin, is_editor_test=False):
    """
    Lance une tentative du niveau.
    Retourne: 'completed', 'dead', 'quit', 'back_to_editor'
    """
    CX = SCREEN_WIDTH // 2
    GAME_SPD = float(level_def.get("speed", 7.0))   # vitesse du niveau (configurable dans l'éditeur)

    bird_grp   = pygame.sprite.Group()
    ground_grp = pygame.sprite.Group()
    pipe_grp   = pygame.sprite.Group()
    coin_grp   = pygame.sprite.Group()

    bird = Bird(SKIN_ASSET_NAMES.get(selected_skin, "Flappy"))
    bird.rect.center = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)
    bird_grp.add(bird)

    for i in range(2):
        ground_grp.add(Ground(GROUND_WIDTH * i))

    # Tous les tuyaux du niveau ajoutés d'un coup
    for sp in _build_level_pipes(level_def, offset_x=0):
        pipe_grp.add(sp)

    # Ligne d'arrivée
    finish_x   = float(level_def.get("length", 3000))
    camera_x   = 0.0         # défilement de la caméra
    coins_col  = 0
    coin_anim  = 0
    t          = 0.0
    result     = None
    elapsed_ms = 0
    QUIT_RECT  = pygame.Rect(SCREEN_WIDTH - 150, 20, 130, 40)

    global coin_pop_effects
    coin_pop_effects = []

    # ── Phase TAP TO START ────────────────────────────────────────────────────
    waiting = True
    bird_base_y = SCREEN_HEIGHT // 2
    bob_t = 0.0
    while waiting:
        clock.tick(FPS)
        bob_t += 0.05
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return 'back_to_editor' if is_editor_test else 'quit'
                if event.key in (K_SPACE, K_UP): waiting = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if QUIT_RECT.collidepoint(event.pos):
                    return 'back_to_editor' if is_editor_test else 'quit'
                waiting = False

        bird.rect.centery = int(bird_base_y + math.sin(bob_t) * 8)
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(140)
        ground_grp.draw(screen)
        pipe_grp.draw(screen)
        bird_grp.draw(screen)

        # Dessiner la ligne d'arrivée (aperçu)
        finish_screen_x = int(finish_x - camera_x)
        if 0 <= finish_screen_x <= SCREEN_WIDTH:
            _draw_finish_line(finish_screen_x)

        hint = font_small.render("APPUIE POUR COMMENCER", True, GOLD)
        screen.blit(hint, (CX - hint.get_width()//2, SCREEN_HEIGHT//2 - 120))

        lbl = font_tiny.render(level_def["name"].upper(), True, (180, 180, 220))
        screen.blit(lbl, (CX - lbl.get_width()//2, SCREEN_HEIGHT//2 - 155))

        pygame.draw.rect(screen, (220, 50, 50), QUIT_RECT, border_radius=10)
        qt = font_tiny.render("QUITTER", True, WHITE)
        screen.blit(qt, qt.get_rect(center=QUIT_RECT.center))
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()

    # ── Boucle de jeu du niveau ───────────────────────────────────────────────
    while result is None:
        dt = clock.tick_busy_loop(FPS) / 1000.0
        dt = min(dt, 1/30)
        t  += dt * 2.4
        elapsed_ms += dt * 1000
        coin_anim += 1

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    result = 'back_to_editor' if is_editor_test else 'quit'
                elif event.key in (K_SPACE, K_UP):
                    bird.bump()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if QUIT_RECT.collidepoint(event.pos):
                    result = 'back_to_editor' if is_editor_test else 'quit'
                else:
                    bird.bump()

        # Maintien souris/espace
        keys = pygame.key.get_pressed()
        mouse_held = pygame.mouse.get_pressed()[0] and not QUIT_RECT.collidepoint(pygame.mouse.get_pos())
        held = bool(keys[K_SPACE] or keys[K_UP] or mouse_held)

        # Déplacement caméra
        camera_x += GAME_SPD * dt * 60

        # Mise à jour sprites
        bird_grp.update(dt, held)
        ground_grp.update(GAME_SPD * dt * 60)
        for pipe in pipe_grp.sprites():
            pipe.update(GAME_SPD * dt * 60, dt=dt, elapsed_ms=elapsed_ms)
        coin_grp.update(GAME_SPD * dt * 60)

        # Déplacer aussi les tuyaux par caméra (leurs float_x déjà mis à jour)
        # Pièces hors écran
        for c in list(coin_grp.sprites()):
            if off_screen(c): coin_grp.remove(c)

        # Collision sol/plafond
        if (bird.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT or bird.rect.top <= 0):
            result = 'dead'

        # Collision tuyaux
        if pygame.sprite.groupcollide(bird_grp, pipe_grp, False, False, pygame.sprite.collide_mask):
            play_sound(hit_snd)
            result = 'dead'

        # Collecte pièces
        for c in pygame.sprite.spritecollide(bird_grp.sprites()[0], coin_grp, True, pygame.sprite.collide_mask):
            coins_col += 1
            coin_pop_effects.append(CoinPopEffect(c.rect.centerx, c.rect.top - 10))

        coin_pop_effects = [e for e in coin_pop_effects if not e.dead]
        for e in coin_pop_effects: e.update()

        # Ligne d'arrivée
        finish_screen_x = int(finish_x - camera_x)

        # DESSIN
        bg_x_draw = -(camera_x % SCREEN_WIDTH)
        screen.blit(BACKGROUND, (int(bg_x_draw), 0))
        screen.blit(BACKGROUND, (int(bg_x_draw) + SCREEN_WIDTH, 0))
        pipe_grp.draw(screen)
        coin_grp.draw(screen)
        ground_grp.draw(screen)
        bird_grp.draw(screen)

        for e in coin_pop_effects: e.draw(screen)

        # Ligne d'arrivée visible
        if finish_screen_x <= SCREEN_WIDTH + 20:
            _draw_finish_line(finish_screen_x)

        # HUD
        _draw_level_hud(level_def, coin_anim, coins_col, camera_x, finish_x)

        # Bouton quitter
        pygame.draw.rect(screen, (220, 50, 50), QUIT_RECT, border_radius=10)
        qt = font_tiny.render("QUITTER", True, WHITE)
        screen.blit(qt, qt.get_rect(center=QUIT_RECT.center))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()

        # L'oiseau atteint la ligne d'arrivée
        if bird.rect.centerx + camera_x >= finish_x - 20:
            result = 'completed'

    # ── Écran résultat ────────────────────────────────────────────────────────
    if result == 'completed':
        _level_complete_screen(level_def, player, data, coins_col, is_editor_test)

    return result


def _draw_finish_line(screen_x):
    """Dessine la ligne d'arrivée animée."""
    t = time.time()
    for y in range(0, SCREEN_HEIGHT - GROUND_HEIGHT, 12):
        alpha = int(180 + 60 * math.sin(t * 4 + y * 0.05))
        col = (255, int(200 + 55 * math.sin(t * 3 + y * 0.08)), 0, alpha)
        s = pygame.Surface((6, 8), pygame.SRCALPHA)
        s.fill(col)
        screen.blit(s, (screen_x - 3, y))
    lbl = font_tiny.render("ARRIVÉE", True, GOLD)
    screen.blit(lbl, (screen_x - lbl.get_width()//2, 30))


def _draw_level_hud(level_def, coin_anim, coins_col, camera_x, finish_x):
    """HUD minimal pendant un niveau."""
    progress = min(1.0, camera_x / max(1, finish_x))
    bar_w = 300; bar_x = SCREEN_WIDTH//2 - bar_w//2; bar_y = 14
    # Fond barre
    pygame.draw.rect(screen, (20, 22, 40), (bar_x - 2, bar_y - 2, bar_w + 4, 18), border_radius=8)
    # Remplissage
    pygame.draw.rect(screen, GOLD, (bar_x, bar_y, int(bar_w * progress), 14), border_radius=7)
    # Bordure
    pygame.draw.rect(screen, (*GOLD, 180), (bar_x - 2, bar_y - 2, bar_w + 4, 18), 2, border_radius=8)
    lbl = font_tiny.render(f"{int(progress*100)}%", True, WHITE)
    screen.blit(lbl, (bar_x + bar_w + 10, bar_y - 2))
    # Nom niveau
    nm = font_tiny.render(level_def["name"].upper(), True, (180, 180, 220))
    screen.blit(nm, (bar_x - nm.get_width() - 10, bar_y - 2))


def _level_complete_screen(level_def, player, data, coins_col, is_editor_test):
    """Écran de victoire après un niveau."""
    CX = SCREEN_WIDTH // 2; CY = SCREEN_HEIGHT // 2
    t = 0.0
    coins_r = level_def.get("reward_coins", 0)
    mc_r    = level_def.get("reward_mission_coins", 0)
    first   = False
    if not is_editor_test:
        first = mark_level_completed(player, data, level_def["id"], coins_r, mc_r)
        # Tracker levels_done dans missions
        if "missions_stats" in player:
            player["missions_stats"]["levels_done"] = len(get_player_completed_levels(player))
            for mid, mtype, lbl, desc, goal, rew in ALL_MISSIONS.values():
                if mtype == "levels_done":
                    entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
                    if not entry["claimed"]:
                        entry["progress"] = min(goal, player["missions_stats"]["levels_done"])
                        player["missions"][mid] = entry

    while True:
        clock.tick(FPS); t += 0.05
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type in (KEYDOWN, MOUSEBUTTONDOWN): return

        screen.blit(BACKGROUND, (0, 0)); draw_overlay(180)
        draw_panel(CX, CY, 460, 340, radius=18, border=GOLD)

        title = font_big.render("NIVEAU TERMINÉ !", True, GOLD)
        screen.blit(title, (CX - title.get_width()//2, CY - 120))

        if first and not is_editor_test:
            sub = font_small.render("PREMIÈRE COMPLÉTION !", True, GREEN_SOFT)
            screen.blit(sub, (CX - sub.get_width()//2, CY - 70))
            r1 = font_tiny.render(f"+ {coins_r} pièces", True, GOLD)
            r2 = font_tiny.render(f"+ {mc_r} pièces mission", True, (100, 180, 255))
            screen.blit(r1, (CX - r1.get_width()//2, CY - 35))
            screen.blit(r2, (CX - r2.get_width()//2, CY - 10))
        elif is_editor_test:
            sub = font_small.render("Niveau réussi ! Tu peux le publier.", True, GREEN_SOFT)
            screen.blit(sub, (CX - sub.get_width()//2, CY - 60))
        else:
            sub = font_small.render("Déjà complété.", True, GREY)
            screen.blit(sub, (CX - sub.get_width()//2, CY - 60))

        hint = font_tiny.render("Appuie pour continuer", True, (150, 150, 180))
        screen.blit(hint, (CX - hint.get_width()//2, CY + 110))
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


def _level_dead_screen(is_editor_test):
    """Ecran de mort dans un niveau. Retourne 'retry' ou 'quit'."""
    # Flash rouge rapide
    for _ in range(18):
        clock.tick(FPS)
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((200, 20, 20, 80))
        screen.blit(ov, (0, 0))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == QUIT: pygame.quit(); sys.exit()

    # Ecran avec boutons
    fn_title = pygame.font.SysFont("Impact",  52)
    fn_sub   = pygame.font.SysFont("Verdana", 16)
    fn_btn   = pygame.font.SysFont("Verdana", 14, bold=True)
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2

    BTN_W, BTN_H = 260, 56
    BTN_RETRY_Y = CY + 40
    BTN_BACK_Y  = CY + 110

    clock_d = pygame.time.Clock()
    t = 0.0
    while True:
        clock_d.tick(FPS)
        t += 0.05
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(ev): continue
                if _GLOBAL_CHAT.handle_event(ev): continue
            if ev.type == KEYDOWN:
                if ev.key in (K_SPACE, K_UP, K_RETURN):
                    return 'retry'
                if ev.key == K_ESCAPE:
                    return 'quit'
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                retry_rect = pygame.Rect(CX - BTN_W//2, BTN_RETRY_Y - BTN_H//2, BTN_W, BTN_H)
                back_rect  = pygame.Rect(CX - BTN_W//2, BTN_BACK_Y  - BTN_H//2, BTN_W, BTN_H)
                if retry_rect.collidepoint(mx, my):
                    return 'retry'
                if back_rect.collidepoint(mx, my):
                    return 'quit'

        # Fond assombri
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        # Titre
        flash = int(220 + 35 * math.sin(t * 4))
        title = fn_title.render("PERDU !", True, (flash, 60, 60))
        screen.blit(title, (CX - title.get_width()//2, CY - 80))

        hint = fn_sub.render("ESPACE / CLIC pour recommencer", True, (160, 160, 200))
        screen.blit(hint, (CX - hint.get_width()//2, CY - 20))

        # Bouton Recommencer
        retry_rect = pygame.Rect(CX - BTN_W//2, BTN_RETRY_Y - BTN_H//2, BTN_W, BTN_H)
        back_rect  = pygame.Rect(CX - BTN_W//2, BTN_BACK_Y  - BTN_H//2, BTN_W, BTN_H)
        h_retry = retry_rect.collidepoint(mx, my)
        h_back  = back_rect.collidepoint(mx, my)

        pygame.draw.rect(screen, (50, 180, 100) if not h_retry else (70, 210, 120), retry_rect, border_radius=12)
        pygame.draw.rect(screen, (80, 220, 130), retry_rect, 2, border_radius=12)
        rt = fn_btn.render("RECOMMENCER", True, (255, 255, 255))
        screen.blit(rt, (retry_rect.centerx - rt.get_width()//2, retry_rect.centery - rt.get_height()//2))

        pygame.draw.rect(screen, (50, 55, 100) if not h_back else (70, 75, 130), back_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 110, 180), back_rect, 2, border_radius=12)
        bt = fn_btn.render("MENU DES NIVEAUX", True, (200, 210, 255))
        screen.blit(bt, (back_rect.centerx - bt.get_width()//2, back_rect.centery - bt.get_height()//2))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  POPUP ADMIN — Choix de publication (Officiel / Communauté)
# ══════════════════════════════════════════════════════════════════════════════
def _admin_publish_popup(player):
    """
    Affiche un popup permettant aux admins de choisir entre publier
    en OFFICIEL ou en COMMUNAUTÉ.
    Retourne 'official', 'community', ou None si annulé.
    """
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    PW, PH = 520, 280

    clock_local = pygame.time.Clock()
    t = 0.0
    while True:
        clock_local.tick(FPS)
        t += 0.05
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return None
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Bouton OFFICIEL
                if btn_rect(CX - 120, CY + 50, 200, 52).collidepoint(event.pos):
                    return "official"
                # Bouton COMMUNAUTÉ
                if btn_rect(CX + 120, CY + 50, 200, 52).collidepoint(event.pos):
                    return "community"
                # Bouton ANNULER
                if btn_rect(CX, CY + 120, 160, 40).collidepoint(event.pos):
                    return None

        # Dessin fond semi-transparent
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))

        # Panel
        draw_panel(CX, CY, PW, PH, radius=18, border=GOLD)

        # Titre
        crown = "👑 "
        title_s = font_med.render("OÙ PUBLIER CE NIVEAU ?", True, GOLD)
        screen.blit(title_s, (CX - title_s.get_width()//2, CY - PH//2 + 22))

        sub_s = font_tiny.render("Vous êtes administrateur — choisissez la destination.", True, GREY)
        screen.blit(sub_s, (CX - sub_s.get_width()//2, CY - PH//2 + 58))

        # Séparateur
        pygame.draw.line(screen, (*GOLD, 60), (CX - PW//2 + 20, CY - 10), (CX + PW//2 - 20, CY - 10), 1)

        # Bouton OFFICIEL (vert)
        hov_off = btn_rect(CX - 120, CY + 50, 200, 52).collidepoint(mx, my)
        draw_btn("OFFICIEL", CX - 120, CY + 50, 200, 52,
                 color_override=((20,55,20),(30,75,30),GREEN_SOFT) if hov_off else ((12,40,12),(18,55,18),(50,160,80)))

        # Bouton COMMUNAUTÉ (cyan)
        hov_com = btn_rect(CX + 120, CY + 50, 200, 52).collidepoint(mx, my)
        draw_btn("COMMUNAUTÉ", CX + 120, CY + 50, 200, 52,
                 color_override=((15,40,70),(22,55,95),CYAN) if hov_com else ((10,28,55),(14,38,70),(40,130,200)))

        # Labels descriptifs sous les boutons
        off_desc = font_tiny.render("Visible dans l'onglet Officiel", True, (80, 180, 100))
        screen.blit(off_desc, (CX - 120 - off_desc.get_width()//2, CY + 80))
        com_desc = font_tiny.render("Visible dans Niveaux Publics", True, (60, 160, 210))
        screen.blit(com_desc, (CX + 120 - com_desc.get_width()//2, CY + 80))

        # Bouton ANNULER
        draw_btn("ANNULER", CX, CY + 120, 160, 40, small=True)

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  ÉDITEUR DE NIVEAU  — refonte complète
# ══════════════════════════════════════════════════════════════════════════════
def level_editor(player, data, lvl_data, existing_level=None):
    """
    Editeur de niveau — coordonnees gap_y fideles au jeu (y=0 = haut ecran).
    Clic gauche maintenu = scroll.  Clic droit = placer / supprimer tuyau.
    Poignees de gap sur chaque tuyau pour ajuster l'ouverture.
    Retourne le niveau sauvegarde ou None si annule.
    """
    GROUND_Y    = SCREEN_HEIGHT - GROUND_HEIGHT   # coordonnee sol identique au jeu
    TOPBAR_H    = 48
    BOTBAR_H    = 56
    # Le canvas couvre TOUTE la zone de jeu (y=0 à GROUND_Y), identique au jeu
    # La topbar est superposée par-dessus (semi-transparente)
    CANVAS_AREA = pygame.Rect(0, 0, SCREEN_WIDTH, GROUND_Y)

    # Palette
    E_FINISH   = (255, 200, 0)
    E_HANDLE   = (255, 220, 60)
    E_HANDLE_A = (255, 140, 30)

    # ── Données du niveau ─────────────────────────────────────────────────────
    if existing_level:
        lv = dict(existing_level)
        lv.setdefault("pipes",       [])
        lv.setdefault("length",      3000)
        lv.setdefault("name",        "Mon niveau")
        lv.setdefault("completable", False)
        lv.setdefault("published",   False)
        lv.setdefault("likes",       0)
        lv.setdefault("liked_by",    [])
        lv.setdefault("speed",       7.0)
        lv["pipes"] = [dict(p) for p in lv["pipes"]]
    else:
        lv = {
            "id":          new_level_id(player["name"]),
            "name":        "Mon niveau",
            "author":      player["name"],
            "difficulty":  1,
            "pipes":       [],
            "length":      3000,
            "speed":       7.0,
            "published":   False,
            "completable": False,
            "likes":       0,
            "liked_by":    [],
            "last_edited": int(time.time()),
        }

    # ── Etat éditeur ─────────────────────────────────────────────────────────
    scroll_x      = 0
    selected      = set()  # set d'indices sélectionnés (multi-sélection)
    clipboard     = []     # tuyaux copiés (Ctrl+C / Ctrl+V)
    # Scroll par clic gauche maintenu
    scroll_drag   = False
    scroll_drag_ox = 0; scroll_drag_sx = 0
    # Drag poignée gap (tuyau sélectionné)
    drag_mode     = None   # None / 'gap_top' / 'gap_bot' / 'finish'
    drag_pipe_idx = None   # index du tuyau en cours de drag
    drag_oy       = 0; drag_p0 = {}; drag_fin0 = 0
    # Champ nom
    editing_name  = False
    name_cursor   = len(lv["name"])
    # Ligne d'arrivée sélectable
    finish_selected = False
    # Champ vitesse
    editing_speed = False
    speed_str     = str(lv.get("speed", 7.0))
    t = 0.0
    feedback_msg = ""; feedback_col = WHITE; feedback_timer = 0
    saved_once   = existing_level is not None
    # ── Répétition continue des flèches ──────────────────────────────────────
    _arrow_held_key  = None   # touche flèche actuellement maintenue
    _arrow_held_time = 0.0    # temps (secondes) depuis qu'elle est enfoncée
    _ARROW_DELAY     = 0.35   # délai initial avant répétition (s)
    _ARROW_REPEAT    = 0.04   # intervalle entre répétitions (s)
    _arrow_next_rep  = 0.0    # temps auquel déclencher la prochaine répétition

    # ── Helpers coord ─────────────────────────────────────────────────────────
    def w2s(wx): return int(wx - scroll_x)   # world → screen X
    def s2w(sx): return sx + scroll_x        # screen → world X

    # Tuyau sous le curseur (pour survol / suppression)
    def _pipe_at(sx, sy):
        PW = PIPE_WIDTH // 2 + 4
        for i, p in enumerate(lv["pipes"]):
            px = w2s(p["x"])
            if abs(px - sx) > PW: continue
            # dans le tuyau haut ou bas (pas dans le gap)
            if sy < p["gap_y"] or sy > p["gap_y"] + p["gap_h"]:
                return i
        return None

    # Poignée de gap sous le curseur
    def _handle_at(sx, sy):
        for i, p in enumerate(lv["pipes"]):
            px = w2s(p["x"])
            if abs(px - sx) > PIPE_WIDTH // 2 + 8: continue
            if abs(sy - p["gap_y"]) <= 12:                  return i, 'gap_top'
            if abs(sy - (p["gap_y"] + p["gap_h"])) <= 12:   return i, 'gap_bot'
        return None, None

    def _finish_handle_at(sx, sy):
        fx = w2s(lv["length"])
        # Zone large : 20px de chaque côté + toute la hauteur du canvas
        return abs(sx - fx) <= 20 and TOPBAR_H <= sy <= GROUND_Y

    # ── Dessin ────────────────────────────────────────────────────────────────
    def _draw_canvas_bg():
        """Affiche le vrai background du jeu + overlay + grille légère (sans le sol)."""
        # Background jeu scrollé (commence à y=0 comme en jeu)
        bg_x = -(scroll_x % SCREEN_WIDTH)
        screen.blit(BACKGROUND, (int(bg_x), 0))
        screen.blit(BACKGROUND, (int(bg_x) + SCREEN_WIDTH, 0))

        # Overlay très léger pour lisibilité de la grille
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 50))
        screen.blit(ov, (0, 0))

        # Grille verticale semi-transparente (entre topbar et sol) — sans alpha sur draw.line
        step_sm = 100; step_lg = 500
        start_wx = (scroll_x // step_sm) * step_sm
        grid_surf = pygame.Surface((SCREEN_WIDTH, GROUND_Y - TOPBAR_H), pygame.SRCALPHA)
        for wx in range(start_wx, start_wx + SCREEN_WIDTH + step_sm * 2, step_sm):
            sx = w2s(wx)
            if sx < 0 or sx > SCREEN_WIDTH: continue
            is_lg = (wx % step_lg == 0)
            col = (255, 255, 255, 40) if is_lg else (255, 255, 255, 12)
            pygame.draw.line(grid_surf, col, (sx, 0), (sx, GROUND_Y - TOPBAR_H), 1)
            if is_lg:
                lbl = font_tiny.render(str(wx), True, (200, 210, 255))
                lbl.set_alpha(110)
                grid_surf.blit(lbl, (sx + 3, 4))
        screen.blit(grid_surf, (0, TOPBAR_H))

    def _draw_ground():
        """Dessine le sol exactement à GROUND_Y, par-dessus les tuyaux."""
        Ground._load()
        gnd_scroll = int(scroll_x % GROUND_WIDTH)
        screen.blit(Ground._IMG, (-gnd_scroll, GROUND_Y))
        screen.blit(Ground._IMG, (-gnd_scroll + GROUND_WIDTH, GROUND_Y))

    def _draw_finish():
        fx = w2s(lv["length"])
        if fx < 0 or fx > SCREEN_WIDTH + 10: return
        dash_t = time.time() * 70

        if finish_selected:
            # Fond coloré semi-transparent sur toute la largeur autour de la ligne
            glow = pygame.Surface((44, GROUND_Y - TOPBAR_H), pygame.SRCALPHA)
            glow.fill((0, 200, 255, 35))
            screen.blit(glow, (fx - 22, TOPBAR_H))
            # Ligne épaisse cyan pleine (pas pointillée)
            pygame.draw.line(screen, (0, 220, 255), (fx, TOPBAR_H), (fx, GROUND_Y), 4)
            # Contour blanc pour contraste
            pygame.draw.line(screen, (255, 255, 255), (fx, TOPBAR_H), (fx, GROUND_Y), 1)
            fin_col = (0, 230, 255)
        else:
            fin_col = E_FINISH
            for y in range(TOPBAR_H, GROUND_Y, 14):
                if int((y + dash_t) // 14) % 2 == 0:
                    pygame.draw.line(screen, fin_col, (fx, y), (fx, y + 8), 3)

        # Label
        lbl_text = "ARRIVEE [SELEC]" if finish_selected else "ARRIVEE"
        lbl_s = font_tiny.render(lbl_text, True, fin_col)
        bw = lbl_s.get_width() + 16; bh = lbl_s.get_height() + 8
        bx = max(4, min(SCREEN_WIDTH - bw - 4, fx - bw // 2))
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg_col = (0, 40, 60, 240) if finish_selected else (40, 30, 0, 210)
        pygame.draw.rect(bg, bg_col, (0, 0, bw, bh), border_radius=6)
        border_col = (0, 230, 255, 255) if finish_selected else (*E_FINISH, 220)
        pygame.draw.rect(bg, border_col, (0, 0, bw, bh), 2, border_radius=6)
        screen.blit(bg, (bx, TOPBAR_H + 6))
        screen.blit(lbl_s, (bx + 8, TOPBAR_H + 10))

        # Triangle indicateur en haut
        hcol = (0, 230, 255) if finish_selected else ((255, 230, 80) if _finish_handle_at(*pygame.mouse.get_pos()) else E_FINISH)
        tri_size = 12 if finish_selected else 8
        pygame.draw.polygon(screen, hcol, [(fx-tri_size, TOPBAR_H), (fx+tri_size, TOPBAR_H), (fx, TOPBAR_H+tri_size*2)])
        if finish_selected:
            pygame.draw.polygon(screen, (255,255,255), [(fx-tri_size, TOPBAR_H), (fx+tri_size, TOPBAR_H), (fx, TOPBAR_H+tri_size*2)], 1)

        # Hint "clic droit" quand la souris survole mais pas sélectionnée
        if not finish_selected and _finish_handle_at(*pygame.mouse.get_pos()):
            hint_s = font_tiny.render("CLIC GAUCHE pour selectionner", True, (255, 230, 80))
            hbx = max(4, min(SCREEN_WIDTH - hint_s.get_width() - 12, fx - hint_s.get_width()//2))
            hbg = pygame.Surface((hint_s.get_width()+12, hint_s.get_height()+6), pygame.SRCALPHA)
            pygame.draw.rect(hbg, (40, 30, 0, 200), (0,0,hbg.get_width(),hbg.get_height()), border_radius=5)
            screen.blit(hbg, (hbx-6, TOPBAR_H + bh + 14))
            screen.blit(hint_s, (hbx, TOPBAR_H + bh + 17))

    def _draw_pipes():
        """Dessine les vrais sprites tuyaux avec des coordonnées fidèles au jeu."""
        Pipe._load()
        mx_c, my_c = pygame.mouse.get_pos()
        hi, hmode  = _handle_at(mx_c, my_c)
        hov_idx    = _pipe_at(mx_c, my_c)

        for i, p in enumerate(lv["pipes"]):
            sx = w2s(p["x"])
            if sx < -PIPE_WIDTH - 10 or sx > SCREEN_WIDTH + 10: continue

            PW      = PIPE_WIDTH // 2
            gap_y   = p["gap_y"]
            gap_h   = p["gap_h"]
            bot_top = gap_y + gap_h   # haut du tuyau bas

            is_sel = (i in selected)
            is_hov = (i == hov_idx and not is_sel)

            # ── Tuyau haut (inversé) — descend depuis y=0 jusqu'à gap_y ──────
            top_h = max(0, gap_y)   # gap_y = coordonnée réelle depuis y=0
            if top_h > 0:
                # On prend la partie basse de l'image retournée
                src_h = min(top_h, Pipe._IMG_FLIP.get_height())
                src_y = Pipe._IMG_FLIP.get_height() - src_h
                screen.blit(Pipe._IMG_FLIP, (sx - PW, 0), pygame.Rect(0, src_y, PIPE_WIDTH, src_h))

            # ── Tuyau bas — monte depuis bot_top jusqu'en bas de l'écran (comme le jeu)
            # Le sol (dessiné par-dessus) cache la partie en dessous de GROUND_Y
            bot_h = max(0, SCREEN_HEIGHT - bot_top)
            if bot_h > 0:
                src_h = min(bot_h, Pipe._IMG.get_height())
                screen.blit(Pipe._IMG, (sx - PW, bot_top), pygame.Rect(0, 0, PIPE_WIDTH, src_h))

            # ── Overlay sélection / survol ─────────────────────────────────────
            if is_sel or is_hov:
                alpha = 70 if is_sel else 35
                col   = (255, 255, 255, alpha)
                if top_h > 0:
                    ov = pygame.Surface((PIPE_WIDTH, top_h), pygame.SRCALPHA); ov.fill(col)
                    screen.blit(ov, (sx - PW, 0))
                bot_ov_h = max(0, GROUND_Y - bot_top)  # overlay visible jusqu'au sol
                if bot_ov_h > 0:
                    ov2 = pygame.Surface((PIPE_WIDTH, bot_ov_h), pygame.SRCALPHA); ov2.fill(col)
                    screen.blit(ov2, (sx - PW, bot_top))
                brd = (220, 255, 220) if is_sel else (180, 230, 180)
                if top_h > 0:
                    pygame.draw.rect(screen, brd, (sx - PW, 0, PIPE_WIDTH, top_h), 3)
                if bot_ov_h > 0:
                    pygame.draw.rect(screen, brd, (sx - PW, bot_top, PIPE_WIDTH, bot_ov_h), 3)

            # ── Surlignage du gap ──────────────────────────────────────────────
            if is_sel:
                gap_surf = pygame.Surface((PIPE_WIDTH + 20, gap_h), pygame.SRCALPHA)
                gap_surf.fill((100, 200, 255, 20))
                pygame.draw.rect(gap_surf, (100, 200, 255, 90), (0, 0, PIPE_WIDTH + 20, gap_h), 2)
                screen.blit(gap_surf, (sx - PW - 10, gap_y))

            # ── Poignées gap ──────────────────────────────────────────────────
            for handle_y, hk in [(gap_y, 'gap_top'), (bot_top, 'gap_bot')]:
                is_hh = (hi == i and hmode == hk)
                hcol  = E_HANDLE_A if is_hh else (E_HANDLE if is_sel else (200, 220, 140))
                hr    = 10 if is_hh else (8 if is_sel else 5)
                pygame.draw.circle(screen, hcol, (sx, handle_y), hr)
                pygame.draw.circle(screen, WHITE, (sx, handle_y), hr, 2)

            # ── Numéro discret ──────────────────────────────────────────────
            if is_sel or is_hov:
                nb = font_tiny.render(f"#{i+1}", True, (230,255,230) if is_sel else (180,200,180))
                bg_nb = pygame.Surface((nb.get_width()+8, nb.get_height()+4), pygame.SRCALPHA)
                pygame.draw.rect(bg_nb, (0,0,0,160), (0,0,bg_nb.get_width(),bg_nb.get_height()), border_radius=4)
                screen.blit(bg_nb, (sx - bg_nb.get_width()//2, GROUND_Y + 3))
                screen.blit(nb, (sx - nb.get_width()//2, GROUND_Y + 5))

    def _draw_topbar():
        # Topbar semi-transparente superposée sur le canvas (ne masque rien)
        bar = pygame.Surface((SCREEN_WIDTH, TOPBAR_H), pygame.SRCALPHA)
        pygame.draw.rect(bar, (4, 6, 18, 210), (0, 0, SCREEN_WIDTH, TOPBAR_H))
        pygame.draw.line(bar, (*GOLD, 140), (0, TOPBAR_H-1), (SCREEN_WIDTH, TOPBAR_H-1), 2)
        screen.blit(bar, (0, 0))
        ed_s  = font_tiny.render("EDITEUR", True, GOLD)
        ed_bw = ed_s.get_width() + 18; ed_bh = ed_s.get_height() + 8
        ed_bg = pygame.Surface((ed_bw, ed_bh), pygame.SRCALPHA)
        pygame.draw.rect(ed_bg, (*GOLD, 28), (0, 0, ed_bw, ed_bh), border_radius=5)
        pygame.draw.rect(ed_bg, (*GOLD, 110), (0, 0, ed_bw, ed_bh), 1, border_radius=5)
        screen.blit(ed_bg, (10, TOPBAR_H//2 - ed_bh//2))
        screen.blit(ed_s,  (19, TOPBAR_H//2 - ed_s.get_height()//2))
        nm_col   = GOLD if editing_name else WHITE
        nm_text  = lv["name"] if lv["name"] else "Sans titre"
        nm_s     = font_small.render(nm_text, True, nm_col)
        nm_bw    = max(200, min(340, nm_s.get_width() + 28))
        nm_bx    = 10 + ed_bw + 12
        nm_by    = TOPBAR_H//2 - (TOPBAR_H-14)//2
        nm_bh    = TOPBAR_H - 14
        nm_surf  = pygame.Surface((nm_bw, nm_bh), pygame.SRCALPHA)
        pygame.draw.rect(nm_surf, (28, 24, 6, 220) if editing_name else (14, 16, 36, 200), (0,0,nm_bw,nm_bh), border_radius=7)
        pygame.draw.rect(nm_surf, (*nm_col, 200 if editing_name else 80), (0,0,nm_bw,nm_bh), 2 if editing_name else 1, border_radius=7)
        screen.blit(nm_surf, (nm_bx, nm_by))
        screen.set_clip(pygame.Rect(nm_bx+6, nm_by, nm_bw-12, nm_bh))
        screen.blit(nm_s, (nm_bx+12, TOPBAR_H//2 - nm_s.get_height()//2))
        screen.set_clip(None)
        if editing_name and int(t*6)%2==0:
            cx2 = min(nm_bx+12+font_small.size(nm_text[:name_cursor])[0], nm_bx+nm_bw-8)
            pygame.draw.line(screen, GOLD, (cx2, nm_by+4), (cx2, nm_by+nm_bh-4), 2)
        if lv.get("completable"):
            cs = font_tiny.render("COMPLETABLE", True, GREEN_SOFT)
            bw2=cs.get_width()+20; bh2=cs.get_height()+10
            bx2=SCREEN_WIDTH//2-bw2//2; by2=TOPBAR_H//2-bh2//2
            bg2=pygame.Surface((bw2,bh2),pygame.SRCALPHA)
            pygame.draw.rect(bg2,(8,45,16,220),(0,0,bw2,bh2),border_radius=8)
            pygame.draw.rect(bg2,(*GREEN_SOFT,200),(0,0,bw2,bh2),2,border_radius=8)
            screen.blit(bg2,(bx2,by2)); screen.blit(cs,(bx2+10,by2+5))
        # ── Champ vitesse ──────────────────────────────────────────────────────
        spd_lbl  = font_tiny.render("VIT:", True, (180, 200, 255))
        spd_bx   = SCREEN_WIDTH - 160
        spd_by   = TOPBAR_H//2 - (TOPBAR_H-14)//2
        spd_bh   = TOPBAR_H - 14
        spd_bw   = 70
        spd_col  = (100, 200, 255) if editing_speed else (160, 175, 230)
        spd_bg   = pygame.Surface((spd_bw, spd_bh), pygame.SRCALPHA)
        pygame.draw.rect(spd_bg, (10, 20, 50, 220) if editing_speed else (14, 16, 36, 200), (0,0,spd_bw,spd_bh), border_radius=7)
        pygame.draw.rect(spd_bg, (*spd_col, 200 if editing_speed else 80), (0,0,spd_bw,spd_bh), 2 if editing_speed else 1, border_radius=7)
        screen.blit(spd_lbl, (spd_bx - spd_lbl.get_width() - 6, TOPBAR_H//2 - spd_lbl.get_height()//2))
        screen.blit(spd_bg, (spd_bx, spd_by))
        spd_disp = speed_str if editing_speed else f"{lv.get('speed', 7.0):.1f}"
        spd_s    = font_small.render(spd_disp, True, spd_col)
        screen.set_clip(pygame.Rect(spd_bx+4, spd_by, spd_bw-8, spd_bh))
        screen.blit(spd_s, (spd_bx + 8, TOPBAR_H//2 - spd_s.get_height()//2))
        screen.set_clip(None)
        if editing_speed and int(t*6)%2==0:
            cx3 = spd_bx + 8 + font_small.size(spd_disp)[0]
            pygame.draw.line(screen, spd_col, (cx3, spd_by+3), (cx3, spd_by+spd_bh-3), 2)
        info1 = font_tiny.render(f"{len(lv['pipes'])} tuyaux", True, (160,175,230))
        ix = SCREEN_WIDTH - info1.get_width() - 14
        screen.blit(info1, (ix, TOPBAR_H + 8))

    def _draw_botbar():
        BOTBAR_H = 60
        bar = pygame.Surface((SCREEN_WIDTH, BOTBAR_H), pygame.SRCALPHA)
        pygame.draw.rect(bar, (5, 7, 20, 252), (0, 0, SCREEN_WIDTH, BOTBAR_H))
        pygame.draw.line(bar, (*GOLD, 110), (0, 0), (SCREEN_WIDTH, 0), 2)
        screen.blit(bar, (0, SCREEN_HEIGHT - BOTBAR_H))
        BY = SCREEN_HEIGHT - BOTBAR_H//2
        draw_btn("RETOUR",  76,                   BY, 130, 42, small=True)
        can_test = len(lv["pipes"]) > 0
        draw_btn("TESTER",  SCREEN_WIDTH//2-215,  BY, 130, 42, accent=can_test, small=True,
                 color_override=None if can_test else ((20,22,44),(26,28,52),(55,60,95)))
        draw_btn("SAUVER",  SCREEN_WIDTH//2,       BY, 130, 42, small=True)
        _admin_can_pub = is_admin(player) and len(lv["pipes"]) > 0 and not lv.get("published", False)
        can_pub = (lv.get("completable",False) or _admin_can_pub) and not lv.get("published",False)
        already_pub = lv.get("published",False)
        draw_btn("PUBLIE" if already_pub else "PUBLIER",
                 SCREEN_WIDTH//2+145, BY, 130, 42, accent=can_pub, small=True,
                 color_override=((16,50,16),(24,68,24),(70,180,70)) if can_pub else None)
        if selected:
            draw_btn("EFFACER", SCREEN_WIDTH-76, BY, 130, 42, danger=True, small=True)

    def _draw_hint():
        BOTBAR_H = 60
        mx2, my2 = pygame.mouse.get_pos()
        hi2, _   = _handle_at(mx2, my2)
        hov2     = _pipe_at(mx2, my2)
        if _finish_handle_at(mx2, my2):       msg = "Clic gauche: selectionner arrivee  |  (selectionnee: fleches G/D pour deplacer)"
        elif finish_selected:                 msg = "Ligne d arrivee selectionnee  |  Fleches G/D: deplacer  |  Clic ailleurs: deselectionnee"
        elif hi2 is not None:                 msg = "Glisser: ajuster le gap"
        elif hov2 is not None:                msg = "Clic droit: supprimer  |  G. maintenu: deplacer vue"
        elif selected:
                                              msg = "Fleches: deplacer  |  Suppr: effacer  |  Ctrl+C: copier  |  Ctrl+V: coller"
        else:                                 msg = "Clic droit: placer tuyau  |  G. maintenu: deplacer vue  |  Molette: defiler"
        hs = font_tiny.render(msg, True, (120, 135, 180))
        screen.blit(hs, (SCREEN_WIDTH//2 - hs.get_width()//2, SCREEN_HEIGHT - BOTBAR_H - hs.get_height() - 5))

    # ── Helper : déplacer la ligne d'arrivée d'une flèche ───────────────────
    FINISH_MIN = 500    # distance minimale depuis le début
    FINISH_MAX = 20000  # distance maximale

    def _do_finish_arrow_move(key):
        nonlocal feedback_msg, feedback_col, feedback_timer
        step = 50
        cur = lv["length"]
        if key == K_LEFT:
            # Vérifier qu'aucun tuyau ne serait derrière la nouvelle position
            new_len = max(FINISH_MIN, cur - step)
            pipes_after = [p for p in lv["pipes"] if p["x"] >= new_len]
            if pipes_after:
                feedback_msg = "Des tuyaux bloquent le deplacement !"; feedback_col = RED_HOT; feedback_timer = 120
            else:
                lv["length"] = new_len
                lv["completable"] = False; lv["published"] = False
        elif key == K_RIGHT:
            lv["length"] = min(FINISH_MAX, cur + step)
            lv["completable"] = False; lv["published"] = False

    # ── Helper : déplacer les tuyaux sélectionnés d'une flèche ──────────────
    def _do_arrow_move(key):
        nonlocal selected, feedback_msg, feedback_col, feedback_timer
        if not selected: return
        step = 10
        _sel_pipes = [lv["pipes"][i] for i in sorted(selected) if i < len(lv["pipes"])]
        if key == K_LEFT:
            for _p in _sel_pipes:
                _p["x"] = max(200, _p["x"] - step)
            lv["pipes"].sort(key=lambda pp: pp["x"])
            selected = {next(ii for ii, pp in enumerate(lv["pipes"]) if pp is _p) for _p in _sel_pipes}
            lv["completable"] = False; lv["published"] = False
        elif key == K_RIGHT:
            if any(_p["x"] + step >= lv["length"] for _p in _sel_pipes):
                feedback_msg = "Impossible de deplacer un tuyau apres l arrivee !"
                feedback_col = RED_HOT; feedback_timer = 120
            else:
                for _p in _sel_pipes:
                    _p["x"] += step
                lv["pipes"].sort(key=lambda pp: pp["x"])
                selected = {next(ii for ii, pp in enumerate(lv["pipes"]) if pp is _p) for _p in _sel_pipes}
                lv["completable"] = False; lv["published"] = False
        elif key == K_UP:
            for _p in _sel_pipes:
                _p["gap_y"] = max(40, _p["gap_y"] - step)
            lv["completable"] = False; lv["published"] = False
        elif key == K_DOWN:
            for _p in _sel_pipes:
                _p["gap_y"] = min(GROUND_Y - _p["gap_h"] - 20, _p["gap_y"] + step)
            lv["completable"] = False; lv["published"] = False

    # ── Boucle principale ─────────────────────────────────────────────────────
    BOTBAR_H = 60
    _prop_zones = []

    while True:
        # _prop_zones est rempli pendant le dessin (fin de boucle) et consommé ici
        dt = clock.tick(FPS) / 1000.0
        t += dt * 2.0
        mx, my = pygame.mouse.get_pos()
        if feedback_timer > 0: feedback_timer -= 1
        in_canvas = CANVAS_AREA.collidepoint(mx, my)

        # ── Répétition continue des flèches ──────────────────────────────────
        if _arrow_held_key is not None and not editing_name and not editing_speed:
            _arrow_held_time += dt
            if _arrow_held_time >= _arrow_next_rep:
                if finish_selected and _arrow_held_key in (K_LEFT, K_RIGHT):
                    _do_finish_arrow_move(_arrow_held_key)
                elif selected:
                    _do_arrow_move(_arrow_held_key)
                _arrow_next_rep = _arrow_held_time + _ARROW_REPEAT

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                _orig_tog_y2 = _GLOBAL_CHAT.TOG_Y
                _GLOBAL_CHAT.TOG_Y = TOPBAR_H + 10
                _handled = _GLOBAL_CHAT.handle_btn_click(event)
                _GLOBAL_CHAT.TOG_Y = _orig_tog_y2
                if _handled: continue
                if _GLOBAL_CHAT.handle_event(event): continue

            # ── CLAVIER ──────────────────────────────────────────────────────
            if event.type == KEYDOWN:
                if not editing_name and not editing_speed and event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                    _arrow_held_key  = event.key
                    _arrow_held_time = 0.0
                    _arrow_next_rep  = _ARROW_DELAY
                if editing_speed:
                    if event.key in (K_RETURN, K_ESCAPE):
                        # Valider la vitesse saisie
                        try:
                            v = float(speed_str.replace(",", "."))
                            v = max(1.0, min(15.0, round(v, 1)))
                            lv["speed"] = v
                            speed_str = str(v)
                            lv["completable"] = False; lv["published"] = False
                        except ValueError:
                            speed_str = str(lv.get("speed", 7.0))
                        editing_speed = False
                    elif event.key == K_BACKSPACE:
                        speed_str = speed_str[:-1]
                    elif event.unicode and event.unicode in "0123456789." and len(speed_str) < 5:
                        speed_str += event.unicode
                elif editing_name:
                    if event.key in (K_RETURN, K_ESCAPE): editing_name = False
                    elif event.key == K_BACKSPACE:
                        if name_cursor > 0:
                            lv["name"] = lv["name"][:name_cursor-1] + lv["name"][name_cursor:]
                            name_cursor -= 1
                    elif event.key == K_LEFT:  name_cursor = max(0, name_cursor-1)
                    elif event.key == K_RIGHT: name_cursor = min(len(lv["name"]), name_cursor+1)
                    elif event.unicode and event.unicode.isprintable() and len(lv["name"]) < 32:
                        lv["name"] = lv["name"][:name_cursor] + event.unicode + lv["name"][name_cursor:]
                        name_cursor += 1
                else:
                    if event.key == K_ESCAPE:
                        if finish_selected:
                            finish_selected = False
                        else:
                            return None
                    if event.key in (K_DELETE, K_BACKSPACE):
                        if selected:
                            for _di in sorted(selected, reverse=True):
                                if _di < len(lv["pipes"]): lv["pipes"].pop(_di)
                            selected = set()
                            lv["completable"] = False; lv["published"] = False
                    # Ctrl+C : copier les tuyaux sélectionnés
                    if event.key == K_c and (pygame.key.get_mods() & KMOD_CTRL):
                        if selected:
                            clipboard = [dict(lv["pipes"][i]) for i in sorted(selected) if i < len(lv["pipes"])]
                            feedback_msg = f"{len(clipboard)} tuyau(x) copié(s)"; feedback_col = CYAN; feedback_timer = 120
                    # Ctrl+V : coller
                    if event.key == K_v and (pygame.key.get_mods() & KMOD_CTRL):
                        if clipboard:
                            offset_x = 150
                            new_indices = set()
                            for cp in clipboard:
                                new_p = dict(cp); new_p["x"] = cp["x"] + offset_x
                                lv["pipes"].append(new_p)
                            lv["pipes"].sort(key=lambda pp: pp["x"])
                            # Retrouver les indices des nouveaux tuyaux collés
                            pasted_xs = [cp["x"] + offset_x for cp in clipboard]
                            selected = set()
                            for px_target in pasted_xs:
                                for ii, pp in enumerate(lv["pipes"]):
                                    if pp["x"] == px_target and ii not in selected:
                                        selected.add(ii); break
                            lv["completable"] = False; lv["published"] = False
                            feedback_msg = f"{len(clipboard)} tuyau(x) collé(s)"; feedback_col = GOLD; feedback_timer = 120
                    # Déplacement ligne d'arrivée sélectionnée
                    if finish_selected and event.key in (K_LEFT, K_RIGHT):
                        _do_finish_arrow_move(event.key)
                    # Déplacement de tous les tuyaux sélectionnés avec les flèches
                    elif selected and event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                        _do_arrow_move(event.key)

            # ── RELÂCHER FLÈCHE ───────────────────────────────────────────────
            if event.type == KEYUP and event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                if _arrow_held_key == event.key:
                    _arrow_held_key = None

            # ── MOLETTE : scroll ──────────────────────────────────────────────
            if event.type == MOUSEWHEEL:
                scroll_x = max(0, scroll_x - event.y * 80)

            # ── CLIC GAUCHE ───────────────────────────────────────────────────
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # ── Panneau propriétés (zones calculées au rendu) ────────────
                _handled_z = False
                if len(selected) == 1 and list(selected)[0] < len(lv["pipes"]):
                    for _act_z, _rect_z in _prop_zones:
                        if _rect_z.collidepoint(mx, my):
                            _p2 = lv["pipes"][list(selected)[0]]
                            if _act_z == "toggle_dyn":
                                _p2["mobile"] = not _p2.get("mobile", False)
                            elif _act_z.startswith("dir_v:"):
                                _p2["mob_dir_v"] = _act_z.split(":")[1]
                            elif _act_z.startswith("dir_h:"):
                                _v2 = _act_z.split(":")[1]
                                _p2["mob_dir_h"] = _v2 if _p2.get("mob_dir_h","none") != _v2 else "none"
                            elif _act_z.startswith("amp_v:"):
                                _p2["mob_amp"] = max(10, min(300, _p2.get("mob_amp",40) + int(float(_act_z.split(":")[1]))))
                            elif _act_z.startswith("spd_v:"):
                                _p2["mob_speed"] = max(0.5, min(10.0, round(_p2.get("mob_speed",1.0) + float(_act_z.split(":")[1]),1)))
                            elif _act_z.startswith("amp_h:"):
                                _p2["mob_amp_h"] = max(10, min(300, _p2.get("mob_amp_h",30) + int(float(_act_z.split(":")[1]))))
                            elif _act_z.startswith("spd_h:"):
                                _p2["mob_speed_h"] = max(0.5, min(10.0, round(_p2.get("mob_speed_h",1.0) + float(_act_z.split(":")[1]),1)))
                            # ── Nouvelles animations ───────────────────────────────────────
                            elif _act_z.startswith("anim_v_dir:"):
                                _p2["anim_v_dir"] = _act_z.split(":")[1]
                            elif _act_z.startswith("anim_v_px:"):
                                _p2["anim_v_px"] = max(0, min(500, _p2.get("anim_v_px", 0) + int(float(_act_z.split(":")[1]))))
                            elif _act_z.startswith("anim_v_spd:"):
                                _p2["anim_v_spd"] = max(0.0, min(20.0, round(_p2.get("anim_v_spd", 0.0) + float(_act_z.split(":")[1]), 1)))
                            elif _act_z.startswith("anim_v_delay:"):
                                _p2["anim_v_delay"] = max(0, _p2.get("anim_v_delay", 0) + int(float(_act_z.split(":")[1])))
                            elif _act_z.startswith("anim_h_dir:"):
                                _p2["anim_h_dir"] = _act_z.split(":")[1]
                            elif _act_z.startswith("anim_h_px:"):
                                _p2["anim_h_px"] = max(0, min(500, _p2.get("anim_h_px", 0) + int(float(_act_z.split(":")[1]))))
                            elif _act_z.startswith("anim_h_spd:"):
                                _p2["anim_h_spd"] = max(0.0, min(20.0, round(_p2.get("anim_h_spd", 0.0) + float(_act_z.split(":")[1]), 1)))
                            elif _act_z.startswith("anim_h_delay:"):
                                _p2["anim_h_delay"] = max(0, _p2.get("anim_h_delay", 0) + int(float(_act_z.split(":")[1])))
                            lv["completable"] = False; lv["published"] = False
                            _handled_z = True
                            break
                if _handled_z: continue

                # Topbar : clic sur le nom ou la vitesse
                if my < TOPBAR_H:
                    ed_bw2 = font_tiny.size("EDITEUR")[0] + 18
                    nm_bx2 = 10 + ed_bw2 + 12
                    nm_bw2 = max(200, font_small.size(lv["name"])[0] + 28)
                    spd_bx2 = SCREEN_WIDTH - 160
                    spd_bw2 = 70
                    if nm_bx2 <= mx <= nm_bx2 + nm_bw2:
                        editing_name = True; editing_speed = False; name_cursor = len(lv["name"])
                    elif spd_bx2 <= mx <= spd_bx2 + spd_bw2:
                        editing_speed = True; editing_name = False
                        speed_str = str(lv.get("speed", 7.0))
                    continue
                # Botbar : boutons
                if my >= SCREEN_HEIGHT - BOTBAR_H:
                    editing_name = False
                    BY2 = SCREEN_HEIGHT - BOTBAR_H//2
                    if btn_rect(76, BY2, 130, 42).collidepoint(event.pos): return None
                    if btn_rect(SCREEN_WIDTH//2-215, BY2, 130, 42).collidepoint(event.pos):
                        if len(lv["pipes"]) > 0:
                            res = play_level(lv, player, data, player.get("selected_skin","Flappy"), is_editor_test=True)
                            if res == 'completed':
                                lv["completable"] = True
                                feedback_msg = "Niveau reussi ! Publier debloque."
                                feedback_col = GREEN_SOFT; feedback_timer = 240
                    elif btn_rect(SCREEN_WIDTH//2, BY2, 130, 42).collidepoint(event.pos):
                        lv["last_edited"] = int(time.time())
                        ids = [l["id"] for l in lvl_data["community"]]
                        if lv["id"] in ids: lvl_data["community"][ids.index(lv["id"])] = lv
                        else: lvl_data["community"].append(lv)
                        save_level(lv); saved_once = True
                        feedback_msg = "Niveau sauvegarde !"; feedback_col = GOLD; feedback_timer = 180
                    elif btn_rect(SCREEN_WIDTH//2+145, BY2, 130, 42).collidepoint(event.pos):
                        _admin_ok = is_admin(player) and len(lv["pipes"]) > 0
                        if (lv.get("completable") or _admin_ok) and not lv.get("published"):
                            if is_admin(player):
                                # Popup de choix : Officiel ou Communauté
                                pub_choice = _admin_publish_popup(player)
                                if pub_choice == "official":
                                    lv["published"] = True; lv["last_edited"] = int(time.time())
                                    lv["official"] = True
                                    lv["level_type"] = "official"
                                    if "official" not in lvl_data:
                                        lvl_data["official"] = []
                                    off_ids = [l["id"] for l in lvl_data["official"]]
                                    if lv["id"] in off_ids:
                                        lvl_data["official"][off_ids.index(lv["id"])] = lv
                                    else:
                                        lvl_data["official"].append(lv)
                                    # Retirer de community si présent
                                    lvl_data["community"] = [l for l in lvl_data["community"] if l["id"] != lv["id"]]
                                    _sb_post("levels", _level_to_row(lv), upsert=True)
                                    feedback_msg = "Niveau publie en OFFICIEL !"; feedback_col = GREEN_SOFT; feedback_timer = 200
                                elif pub_choice == "community":
                                    lv["published"] = True; lv["last_edited"] = int(time.time())
                                    lv.pop("official", None)
                                    lv["level_type"] = "community"
                                    ids = [l["id"] for l in lvl_data["community"]]
                                    if lv["id"] in ids: lvl_data["community"][ids.index(lv["id"])] = lv
                                    else: lvl_data["community"].append(lv)
                                    _sb_post("levels", _level_to_row(lv), upsert=True)
                                    feedback_msg = "Niveau publie en COMMUNAUTE !"; feedback_col = CYAN; feedback_timer = 200
                            else:
                                lv["published"] = True; lv["last_edited"] = int(time.time())
                                lv["level_type"] = "community"
                                ids = [l["id"] for l in lvl_data["community"]]
                                if lv["id"] in ids: lvl_data["community"][ids.index(lv["id"])] = lv
                                else: lvl_data["community"].append(lv)
                                _sb_post("levels", _level_to_row(lv), upsert=True)
                                feedback_msg = "Niveau publie !"; feedback_col = GREEN_SOFT; feedback_timer = 200
                    elif btn_rect(SCREEN_WIDTH-76, BY2, 130, 42).collidepoint(event.pos):
                        if selected:
                            for _di in sorted(selected, reverse=True):
                                if _di < len(lv["pipes"]): lv["pipes"].pop(_di)
                            selected = set()
                    continue
                # Canvas : poignée gap / clic tuyau / scroll
                if in_canvas:
                    editing_name = False; editing_speed = False
                    # Clic gauche sur la ligne d'arrivée : sélectionner/désélectionner
                    if _finish_handle_at(mx, my):
                        finish_selected = not finish_selected
                        selected = set()
                        if finish_selected:
                            feedback_msg = "Ligne d arrivee selectionnee — Fleches G/D pour deplacer"; feedback_col = (100,240,255); feedback_timer = 180
                        continue
                    finish_selected = False  # clic ailleurs = désélection arrivée
                    hi3, hm3 = _handle_at(mx, my)
                    if hi3 is not None:
                        # Clic sur poignée : sélectionner CE tuyau et démarrer drag
                        selected = {hi3}; drag_mode = hm3
                        drag_pipe_idx = hi3
                        drag_oy = my; drag_p0 = dict(lv["pipes"][hi3])
                        continue
                    # Clic sur un tuyau
                    _clicked_pipe = _pipe_at(mx, my)
                    if _clicked_pipe is not None:
                        _shift = bool(pygame.key.get_mods() & KMOD_SHIFT)
                        if _shift:
                            # Shift : toggle dans la sélection
                            if _clicked_pipe in selected: selected.discard(_clicked_pipe)
                            else: selected.add(_clicked_pipe)
                        else:
                            selected = {_clicked_pipe}
                        continue
                    # Clic dans le vide : désélectionner et commencer scroll
                    selected = set()
                    scroll_drag = True; scroll_drag_ox = mx; scroll_drag_sx = scroll_x

            # ── CLIC DROIT : placer ou supprimer ─────────────────────────────
            if event.type == MOUSEBUTTONDOWN and event.button == 3:
                if in_canvas and my < SCREEN_HEIGHT - BOTBAR_H:
                    editing_name = False; editing_speed = False
                    p_at = _pipe_at(mx, my)
                    finish_selected = False  # clic droit = désélection arrivée
                    if p_at is not None:
                        lv["pipes"].pop(p_at)
                        # Réindexer selected après suppression
                        new_sel = set()
                        for _si in selected:
                            if _si < p_at: new_sel.add(_si)
                            elif _si > p_at: new_sel.add(_si - 1)
                            # _si == p_at → supprimé, on l'enlève
                        selected = new_sel
                    else:
                        wx    = s2w(mx)
                        gap_h = 260
                        # Bloquer le placement après la ligne d arrivée
                        if int(wx) >= lv["length"]:
                            feedback_msg = "Impossible de placer un tuyau apres l arrivee !"
                            feedback_col = RED_HOT; feedback_timer = 120
                        else:
                            # Centre du gap = position du curseur
                            gy    = max(40, min(GROUND_Y - gap_h - 20, my - gap_h // 2))
                            new_p = {"x": max(200, int(wx)), "gap_y": gy, "gap_h": gap_h}
                            lv["pipes"].append(new_p)
                            lv["pipes"].sort(key=lambda pp: pp["x"])
                            _ni = next((ii for ii, pp in enumerate(lv["pipes"]) if pp is new_p), None)
                            if _ni is None:
                                _ni = next((ii for ii, pp in enumerate(lv["pipes"]) if pp["x"] == new_p["x"] and pp["gap_y"] == new_p["gap_y"]), None)
                            selected = {_ni} if _ni is not None else set()
                            lv["completable"] = False; lv["published"] = False

            # ── MOUVEMENT : scroll / drag poignée ─────────────────────────────
            if event.type == MOUSEMOTION:
                if scroll_drag:
                    scroll_x = max(0, scroll_drag_sx - (mx - scroll_drag_ox))
                elif drag_mode == 'gap_top' and drag_pipe_idx is not None and drag_pipe_idx < len(lv["pipes"]):
                    p = lv["pipes"][drag_pipe_idx]
                    new_gy = max(40, min(drag_p0["gap_y"]+drag_p0["gap_h"]-80, drag_p0["gap_y"]+(my-drag_oy)))
                    shrink = new_gy - drag_p0["gap_y"]
                    p["gap_y"] = new_gy
                    p["gap_h"] = max(80, drag_p0["gap_h"] - shrink)
                elif drag_mode == 'gap_bot' and drag_pipe_idx is not None and drag_pipe_idx < len(lv["pipes"]):
                    p = lv["pipes"][drag_pipe_idx]
                    new_bot = max(drag_p0["gap_y"]+80, min(GROUND_Y-20, drag_p0["gap_y"]+drag_p0["gap_h"]+(my-drag_oy)))
                    p["gap_h"] = max(80, new_bot - p["gap_y"])

            # ── RELÂCHEMENT ───────────────────────────────────────────────────
            if event.type == MOUSEBUTTONUP and event.button == 1:
                if drag_mode in ('gap_top', 'gap_bot'):
                    # Déplacement de poignée = modification du niveau
                    lv["completable"] = False; lv["published"] = False
                scroll_drag = False; drag_mode = None; drag_pipe_idx = None

        # ── DESSIN ───────────────────────────────────────────────────────────
        _draw_canvas_bg()
        screen.set_clip(CANVAS_AREA)
        _draw_finish()
        _draw_pipes()

        # ── Indicateur de spawn ──────────────────────────────────────────────
        _spawn_sx = w2s(SCREEN_WIDTH // 6)   # position monde → écran
        _spawn_sy = SCREEN_HEIGHT // 2
        if -20 < _spawn_sx < SCREEN_WIDTH + 20:
            # Ligne verticale pointillée
            _t_spawn = time.time() * 60
            for _sy in range(TOPBAR_H, GROUND_Y, 12):
                if int((_sy + _t_spawn) // 12) % 2 == 0:
                    pygame.draw.line(screen, (80, 220, 120, 160), (_spawn_sx, _sy), (_spawn_sx, _sy + 7), 2)
            # Icône oiseau simplifié (cercle + bec)
            pygame.draw.circle(screen, (80, 200, 110), (_spawn_sx, _spawn_sy), 16, 2)
            pygame.draw.circle(screen, (80, 200, 110, 80), (_spawn_sx, _spawn_sy), 16)
            pygame.draw.polygon(screen, (80, 200, 110),
                [(_spawn_sx + 12, _spawn_sy), (_spawn_sx + 20, _spawn_sy - 4), (_spawn_sx + 20, _spawn_sy + 4)])
            # Label
            _sp_s = font_tiny.render("SPAWN", True, (80, 220, 120))
            _sp_bg = pygame.Surface((_sp_s.get_width() + 10, _sp_s.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(_sp_bg, (10, 30, 14, 210), (0, 0, _sp_bg.get_width(), _sp_bg.get_height()), border_radius=5)
            pygame.draw.rect(_sp_bg, (80, 200, 110, 200), (0, 0, _sp_bg.get_width(), _sp_bg.get_height()), 1, border_radius=5)
            screen.blit(_sp_bg, (_spawn_sx - _sp_bg.get_width()//2, _spawn_sy - 32))
            screen.blit(_sp_s,  (_spawn_sx - _sp_s.get_width()//2,  _spawn_sy - 29))

        screen.set_clip(None)
        _draw_ground()
        _draw_topbar()
        _draw_botbar()
        _draw_hint()

        # ── PANNEAU PROPRIÉTÉS TUYAU ─────────────────────────────────────
        if len(selected) == 1 and list(selected)[0] < len(lv["pipes"]):
            _p        = lv["pipes"][list(selected)[0]]
            _PAD      = 16
            _PW       = 380
            _PX       = SCREEN_WIDTH - _PW - 10
            BOTBAR_H2 = 60
            _PY       = TOPBAR_H + 8
            _PH       = (SCREEN_HEIGHT - TOPBAR_H - BOTBAR_H2 + 56) // 2
            _ROW_H    = 34   # hauteur d'une ligne de paramètre
            _BTN_W    = 30   # largeur bouton +/-
            _BTN_H    = 26
            _VAL_W    = 90   # largeur champ valeur
            _mxp, _myp = pygame.mouse.get_pos()
            _new_zones = []  # zones construites ce frame

            # ── Fond du panneau ───────────────────────────────────────────
            _bg = pygame.Surface((_PW, _PH), pygame.SRCALPHA)
            pygame.draw.rect(_bg, (5, 8, 22, 252), (0, 0, _PW, _PH), border_radius=12)
            pygame.draw.rect(_bg, (65, 100, 210, 210), (0, 0, _PW, _PH), 2, border_radius=12)
            _sh = pygame.Surface((_PW - 6, 10), pygame.SRCALPHA)
            pygame.draw.rect(_sh, (255, 255, 255, 14), (0, 0, _PW - 6, 10), border_radius=12)
            _bg.blit(_sh, (3, 3))
            screen.blit(_bg, (_PX, _PY))

            _cy = _PY + _PAD
            _IW = _PW - _PAD * 2  # inner width

            # ── helper : texte tronqué centré dans une zone ───────────────
            def _fit_text(txt, font, max_w, col):
                s = font.render(txt, True, col)
                if s.get_width() <= max_w:
                    return s
                # tronquer
                while len(txt) > 1 and font.size(txt + "…")[0] > max_w:
                    txt = txt[:-1]
                return font.render(txt + "…", True, col)

            # ── helper : dessine un header de section ─────────────────────
            def _section_header(title, col, y):
                _hs = pygame.Surface((_IW, 24), pygame.SRCALPHA)
                pygame.draw.rect(_hs, (*col, 35), (0, 0, _IW, 24), border_radius=7)
                pygame.draw.rect(_hs, (*col, 180), (0, 0, _IW, 24), 1, border_radius=7)
                screen.blit(_hs, (_PX + _PAD, y))
                _ht = _fit_text(title, font_tiny, _IW - 16, col)
                screen.blit(_ht, (_PX + _PAD + _IW // 2 - _ht.get_width() // 2, y + 12 - _ht.get_height() // 2))
                return y + 30

            # ── helper : switch 2 boutons pleine largeur ──────────────────
            def _switch2(lbl_a, val_a, lbl_b, val_b, cur, col, y):
                _BH = 28
                _BW = (_IW - 6) // 2
                rects = []
                _LABELS = {"down": "Vers le bas", "up": "Vers le haut",
                           "in": "Rapprochement", "out": "Ecartement"}
                for _bi, (_lbl, _val) in enumerate([(lbl_a, val_a), (lbl_b, val_b)]):
                    _bx = _PX + _PAD + _bi * (_BW + 6)
                    _act = (cur == _val)
                    _bs = pygame.Surface((_BW, _BH), pygame.SRCALPHA)
                    _bgc = (*col, 210) if _act else (18, 22, 55, 210)
                    pygame.draw.rect(_bs, _bgc, (0, 0, _BW, _BH), border_radius=7)
                    pygame.draw.rect(_bs, (*col, 200), (0, 0, _BW, _BH), 2 if _act else 1, border_radius=7)
                    _display = _LABELS.get(_val, _val.upper())
                    _bt = _fit_text(_display, font_tiny, _BW - 10, (255,255,255) if _act else (130,145,185))
                    _bs.blit(_bt, (_BW // 2 - _bt.get_width() // 2, _BH // 2 - _bt.get_height() // 2))
                    screen.blit(_bs, (_bx, y))
                    rects.append(pygame.Rect(_bx, y, _BW, _BH))
                return rects[0], rects[1], y + _BH + 8

            # ── helper : ligne paramètre  label | valeur | - | + ─────────
            def _param_row(label, val, k_m, k_p, col, y, unit=""):
                _LW = _IW - _VAL_W - _BTN_W * 2 - 18  # largeur label
                _VX = _PX + _PAD + _LW + 8
                _M_X = _VX + _VAL_W + 4
                _P_X = _M_X + _BTN_W + 4
                _row_cy = y + _ROW_H // 2

                # label
                _lt = _fit_text(label, font_tiny, _LW, (185, 200, 240))
                screen.blit(_lt, (_PX + _PAD, _row_cy - _lt.get_height() // 2))

                # champ valeur
                _vs = pygame.Surface((_VAL_W, _BTN_H), pygame.SRCALPHA)
                pygame.draw.rect(_vs, (12, 18, 52, 250), (0, 0, _VAL_W, _BTN_H), border_radius=6)
                pygame.draw.rect(_vs, (*col, 150), (0, 0, _VAL_W, _BTN_H), 1, border_radius=6)
                screen.blit(_vs, (_VX, _row_cy - _BTN_H // 2))
                _vt = _fit_text(f"{val}{unit}", font_tiny, _VAL_W - 8, col)
                screen.blit(_vt, (_VX + _VAL_W // 2 - _vt.get_width() // 2,
                                  _row_cy - _vt.get_height() // 2))

                # boutons - et +
                _rm2 = pygame.Rect(_M_X, _row_cy - _BTN_H // 2, _BTN_W, _BTN_H)
                _rp2 = pygame.Rect(_P_X, _row_cy - _BTN_H // 2, _BTN_W, _BTN_H)
                for _rect2, _lch, _bcol in [(_rm2, "-", (210,70,70)), (_rp2, "+", (55,195,80))]:
                    _hov2 = _rect2.collidepoint(_mxp, _myp)
                    _bs3 = pygame.Surface((_BTN_W, _BTN_H), pygame.SRCALPHA)
                    _bc2 = tuple(min(255, c + 45) for c in _bcol) if _hov2 else _bcol
                    pygame.draw.rect(_bs3, (*_bc2, 90), (0, 0, _BTN_W, _BTN_H), border_radius=6)
                    pygame.draw.rect(_bs3, (*_bcol, 220), (0, 0, _BTN_W, _BTN_H), 1, border_radius=6)
                    screen.blit(_bs3, (_rect2.x, _rect2.y))
                    _ct2 = font_small.render(_lch, True, (255, 255, 255))
                    screen.blit(_ct2, (_rect2.x + _BTN_W // 2 - _ct2.get_width() // 2,
                                       _rect2.y + _BTN_H // 2 - _ct2.get_height() // 2))
                return _rm2, _rp2, y + _ROW_H

            # ══ ZONE 1 : DÉPLACEMENT DU BLOC ════════════════════════════
            _cy = _section_header("DÉPLACEMENT DU BLOC", (100, 155, 255), _cy)

            _cur_vdir = _p.get("anim_v_dir", "down")
            _ra1, _rb1, _cy = _switch2("Vers le bas", "down", "Vers le haut", "up",
                                       _cur_vdir, (100, 170, 255), _cy)
            _new_zones += [("anim_v_dir:down", _ra1), ("anim_v_dir:up", _rb1)]

            _rm, _rp, _cy = _param_row("Déplacement", _p.get("anim_v_px", 0),
                                       "anim_v_px:-5", "anim_v_px:5", (130,185,255), _cy, " px")
            _new_zones += [("anim_v_px:-5", _rm), ("anim_v_px:5", _rp)]

            _rm, _rp, _cy = _param_row("Vitesse", _p.get("anim_v_spd", 0.0),
                                       "anim_v_spd:-0.5", "anim_v_spd:0.5", (130,185,255), _cy)
            _new_zones += [("anim_v_spd:-0.5", _rm), ("anim_v_spd:0.5", _rp)]

            _rm, _rp, _cy = _param_row("Délai", _p.get("anim_v_delay", 0),
                                       "anim_v_delay:-50", "anim_v_delay:50", (130,185,255), _cy, " ms")
            _new_zones += [("anim_v_delay:-50", _rm), ("anim_v_delay:50", _rp)]

            _cy += 10

            # ══ ZONE 2 : OUVERTURE DU GAP ════════════════════════════════
            _cy = _section_header("OUVERTURE DU GAP", (255, 170, 55), _cy)

            _cur_hdir = _p.get("anim_h_dir", "in")
            _ra2, _rb2, _cy = _switch2("Rapprochement", "in", "Ecartement", "out",
                                       _cur_hdir, (255, 170, 55), _cy)
            _new_zones += [("anim_h_dir:in", _ra2), ("anim_h_dir:out", _rb2)]

            _rm, _rp, _cy = _param_row("Déplacement", _p.get("anim_h_px", 0),
                                       "anim_h_px:-5", "anim_h_px:5", (255,190,90), _cy, " px")
            _new_zones += [("anim_h_px:-5", _rm), ("anim_h_px:5", _rp)]

            _rm, _rp, _cy = _param_row("Vitesse", _p.get("anim_h_spd", 0.0),
                                       "anim_h_spd:-0.5", "anim_h_spd:0.5", (255,190,90), _cy)
            _new_zones += [("anim_h_spd:-0.5", _rm), ("anim_h_spd:0.5", _rp)]

            _rm, _rp, _cy = _param_row("Délai", _p.get("anim_h_delay", 0),
                                       "anim_h_delay:-50", "anim_h_delay:50", (255,190,90), _cy, " ms")
            _new_zones += [("anim_h_delay:-50", _rm), ("anim_h_delay:50", _rp)]

            # Mettre à jour les zones après dessin (utilisées à la prochaine frame)
            _prop_zones = _new_zones

        else:
            _prop_zones = []  # pas de tuyau sélectionné → vider les zones

        if feedback_timer > 0:
            a  = min(255, feedback_timer * 5)
            fs = font_small.render(feedback_msg, True, feedback_col)
            fw = fs.get_width() + 32; fh = fs.get_height() + 14
            fb = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb, (6, 8, 20, 210), (0, 0, fw, fh), border_radius=10)
            pygame.draw.rect(fb, (*feedback_col, 180), (0, 0, fw, fh), 2, border_radius=10)
            fb.set_alpha(a); fs.set_alpha(a)
            screen.blit(fb, (SCREEN_WIDTH//2 - fw//2, SCREEN_HEIGHT - BOTBAR_H - fh - 28))
            screen.blit(fs, (SCREEN_WIDTH//2 - fs.get_width()//2, SCREEN_HEIGHT - BOTBAR_H - fh - 21))

        if _GLOBAL_CHAT:
            # Dans l'éditeur, décaler le bouton >> sous la topbar (48px)
            _orig_tog_y = _GLOBAL_CHAT.TOG_Y
            _GLOBAL_CHAT.TOG_Y = TOPBAR_H + 10
            _GLOBAL_CHAT.draw()
            _GLOBAL_CHAT.TOG_Y = _orig_tog_y
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()



def edit_official_reward_screen(lv_item):
    """
    Popup admin : saisie des récompenses (pièces normales + pièces mission) d'un niveau officiel.
    Retourne (reward_coins, reward_mission_coins) ou None si annulé.
    """
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2

    PANEL_W = 540
    PANEL_H = 320

    # Valeurs initiales
    fields = [
        {"label": "Pièces normales",  "key": "reward_coins",         "value": str(lv_item.get("reward_coins", 0))},
        {"label": "Pièces mission",   "key": "reward_mission_coins", "value": str(lv_item.get("reward_mission_coins", 0))},
    ]
    active_field = 0
    error_msg    = ""
    t            = 0.0

    FIELD_W  = 320
    FIELD_H  = 44
    FIELD_X  = CX - FIELD_W // 2
    F_SPACING = 72
    F_START_Y = CY - 60

    BTN_Y = CY + PANEL_H // 2 - 46

    while True:
        clock.tick(FPS)
        t += 0.04
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == K_TAB:
                    active_field = (active_field + 1) % len(fields)
                    error_msg = ""
                elif event.key == K_RETURN:
                    # Valider
                    try:
                        rc  = max(0, int(fields[0]["value"]))
                        rmc = max(0, int(fields[1]["value"]))
                        return rc, rmc
                    except ValueError:
                        error_msg = "Entrez des nombres entiers valides."
                elif event.key == K_BACKSPACE:
                    f = fields[active_field]
                    f["value"] = f["value"][:-1]
                    error_msg = ""
                else:
                    ch = event.unicode
                    if ch.isdigit() and len(fields[active_field]["value"]) < 7:
                        fields[active_field]["value"] += ch
                        error_msg = ""

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Clic sur champ
                for fi, fd_item in enumerate(fields):
                    fy = F_START_Y + fi * F_SPACING
                    if pygame.Rect(FIELD_X, fy, FIELD_W, FIELD_H).collidepoint(event.pos):
                        active_field = fi
                        error_msg = ""
                # Bouton confirmer
                if btn_rect(CX - 90, BTN_Y, 160, 46).collidepoint(event.pos):
                    try:
                        rc  = max(0, int(fields[0]["value"] or "0"))
                        rmc = max(0, int(fields[1]["value"] or "0"))
                        return rc, rmc
                    except ValueError:
                        error_msg = "Entrez des nombres entiers valides."
                # Bouton annuler
                if btn_rect(CX + 90, BTN_Y, 160, 46).collidepoint(event.pos):
                    return None

        # ── Dessin ────────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(210)
        draw_panel(CX, CY, PANEL_W, PANEL_H, radius=16, border=GOLD)

        # Titre
        title_s = font_small.render("RÉCOMPENSES DU NIVEAU (ADMIN)", True, GOLD)
        screen.blit(title_s, (CX - title_s.get_width() // 2, CY - PANEL_H // 2 + 18))

        # Nom du niveau
        name_s = font_tiny.render(lv_item.get("name", "?").upper(), True, (180, 200, 255))
        screen.blit(name_s, (CX - name_s.get_width() // 2, CY - PANEL_H // 2 + 48))

        # Champs
        for fi, fd_item in enumerate(fields):
            fy = F_START_Y + fi * F_SPACING
            is_active = (fi == active_field)
            # Label
            lbl_s = font_tiny.render(fd_item["label"], True, GOLD if is_active else GREY)
            screen.blit(lbl_s, (FIELD_X, fy - lbl_s.get_height() - 4))
            # Boîte
            brd = GOLD if is_active else (55, 60, 110)
            pygame.draw.rect(screen, (12, 14, 36), (FIELD_X, fy, FIELD_W, FIELD_H), border_radius=8)
            pygame.draw.rect(screen, brd, (FIELD_X, fy, FIELD_W, FIELD_H), 2, border_radius=8)
            # Valeur + curseur clignotant
            disp = fd_item["value"]
            if is_active and int(t * 3) % 2 == 0:
                disp += "|"
            val_s = font_small.render(disp, True, WHITE)
            screen.blit(val_s, (FIELD_X + 14, fy + FIELD_H // 2 - val_s.get_height() // 2))

        # Message d'erreur
        if error_msg:
            err_s = font_tiny.render(error_msg, True, (230, 80, 80))
            screen.blit(err_s, (CX - err_s.get_width() // 2, CY + 30))

        # Indication TAB
        hint_s = font_tiny.render("[TAB] changer de champ  |  [ENTRÉE] valider", True, (80, 85, 120))
        screen.blit(hint_s, (CX - hint_s.get_width() // 2, BTN_Y - 30))

        # Boutons
        draw_btn("CONFIRMER", CX - 90, BTN_Y, 160, 46, accent=True, small=True)
        draw_btn("ANNULER",   CX + 90, BTN_Y, 160, 46, danger=True,  small=True)

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


def levels_screen(data, player, selected_skin):
    CX = SCREEN_WIDTH // 2; CY = SCREEN_HEIGHT // 2
    lvl_data = load_levels()
    sel_tab  = 0   # 0=Officiel (défaut)  1=Communauté
    sel_sub  = 0   # 0=Niveaux publics  1=Mes niveaux
    scroll_y = 0
    t        = 0.0
    feedback_msg = ""; feedback_col = WHITE; feedback_timer = 0

    # ── Layout général ────────────────────────────────────────────────────────
    HEADER_H  = 54    # bande titre en haut
    TAB_H     = 48    # onglets principaux
    SUBTAB_H  = 40    # sous-onglets communauté
    FOOTER_H  = 58    # bouton retour en bas
    # Origine de la liste (varie selon onglet)
    def LIST_Y_OFF():
        return HEADER_H + TAB_H + (SUBTAB_H if sel_tab == 1 else 0) + 8

    LIST_BOT  = SCREEN_HEIGHT - FOOTER_H - 8
    CARD_H    = 88
    GAP       = 8
    CARD_W    = min(900, SCREEN_WIDTH - 80)
    CARD_X    = CX - CARD_W // 2

    # Colonnes internes à la carte
    STAT_COL  = 200    # largeur zone gauche (étoiles / infos)
    BTN_AREA  = 340    # largeur zone boutons à droite
    TEXT_MAX  = CARD_W - STAT_COL - BTN_AREA - 24  # largeur max texte central

    def _clip_text(text, font, max_w):
        """Tronque le texte avec '…' si trop large."""
        s = font.render(text, True, WHITE)
        if s.get_width() <= max_w: return text
        while len(text) > 1:
            text = text[:-1]
            if font.size(text + "…")[0] <= max_w: return text + "…"
        return "…"

    def _star_pts(cx, cy, r):
        pts = []
        for i in range(5):
            ao = math.radians(-90 + i * 72); ai = math.radians(-90 + i * 72 + 36)
            pts.append((cx + r * math.cos(ao), cy + r * math.sin(ao)))
            pts.append((cx + r * 0.42 * math.cos(ai), cy + r * 0.42 * math.sin(ai)))
        return pts

    def _get_list():
        if sel_tab == 0: return lvl_data.get("official", []) or OFFICIAL_LEVELS
        if sel_sub == 0:
            # Niveaux publics (triés par likes)
            return sorted([l for l in lvl_data["community"] if l.get("published")],
                          key=lambda l: l.get("likes", 0), reverse=True)
        # Mes niveaux
        return [l for l in lvl_data["community"] if l.get("author") == player["name"]]

    def _draw_card_base(cy, hov, completed=False):
        """Dessine le fond d'une carte et retourne la surface."""
        if completed:  bg=(15,45,22,228); brd=(60,200,90,200)
        elif hov:      bg=(28,30,68,240); brd=(*GOLD,200)
        else:          bg=(14,16,44,218); brd=(55,60,110,180)
        s = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        pygame.draw.rect(s, bg, (0,0,CARD_W,CARD_H), border_radius=12)
        # Reflet haut
        sh = pygame.Surface((CARD_W-6, 22), pygame.SRCALPHA)
        pygame.draw.rect(sh, (255,255,255, 16 if hov else 8), (0,0,CARD_W-6,22), border_radius=12)
        s.blit(sh, (3,3))
        pygame.draw.rect(s, brd, (0,0,CARD_W,CARD_H), 2, border_radius=12)
        screen.blit(s, (CARD_X, cy))

    def _draw_official_card(lv, cy, hov):
        completed = lv["id"] in get_player_completed_levels(player)
        _draw_card_base(cy, hov, completed)
        MID_Y = cy + CARD_H // 2

        # Zone gauche : étoiles de difficulté
        diff = lv.get("difficulty", 1)
        star_r = 8; star_gap = 20
        stars_total_w = 5 * star_gap - (star_gap - star_r * 2)
        sx0 = CARD_X + STAT_COL // 2 - stars_total_w // 2
        for si in range(5):
            col = GOLD if si < diff else (40, 44, 70)
            pts = _star_pts(sx0 + si * star_gap, MID_Y, star_r)
            pygame.draw.polygon(screen, col, pts)

        # Zone centrale : nom + sous-titre — clippé
        tx = CARD_X + STAT_COL + 12
        name_clipped = _clip_text(lv["name"].upper(), font_small, TEXT_MAX)
        nm_s = font_small.render(name_clipped, True, GREEN_SOFT if completed else WHITE)
        screen.blit(nm_s, (tx, MID_Y - nm_s.get_height() - 2))

        if completed:
            sub_s = font_tiny.render("Complete", True, GREEN_SOFT)
        else:
            sub_s = font_tiny.render(f"Récompense : {lv.get('reward_coins',0)} pièces", True, (170,170,110))
        screen.blit(sub_s, (tx, MID_Y + 4))

        # Zone droite : bouton JOUER + RÉCOMP + SUPPR (admin)
        if is_admin(player):
            draw_btn("JOUER",  CARD_X + CARD_W - BTN_AREA // 2 - 130, MID_Y, 100, 46, accent=True, small=True)
            draw_btn("RÉCOMP", CARD_X + CARD_W - BTN_AREA // 2 - 20,  MID_Y, 100, 38, small=True)
            draw_btn("SUPPR",  CARD_X + CARD_W - BTN_AREA // 2 + 90,  MID_Y, 80,  38, danger=True, small=True)
        else:
            draw_btn("JOUER", CARD_X + CARD_W - BTN_AREA // 2, MID_Y, 130, 46, accent=True)

    def _draw_community_card(lv, cy, hov, is_mine):
        completed_by_me = lv["id"] in get_player_completed_levels(player)
        liked = lv["id"] in get_player_liked_levels(player)
        published = lv.get("published", False)
        completable = lv.get("completable", False)
        _draw_card_base(cy, hov)
        MID_Y = cy + CARD_H // 2

        # Zone gauche : likes (centrés verticalement)
        lk_col = (255, 90, 120) if liked else (100, 110, 150)
        lk_s = font_med.render(f"{lv.get('likes',0)}", True, lk_col)
        screen.blit(lk_s, (CARD_X + STAT_COL//2 - lk_s.get_width()//2, MID_Y - lk_s.get_height()//2))
        # Petit label "likes" dessous
        lk_lbl_s = font_tiny.render("likes", True, (lk_col[0]//2, lk_col[1]//2, lk_col[2]//2))
        screen.blit(lk_lbl_s, (CARD_X + STAT_COL//2 - lk_lbl_s.get_width()//2, MID_Y + lk_s.get_height()//2 - 2))

        # Zone centrale : nom (haut) + auteur (bas)
        tx = CARD_X + STAT_COL + 12
        # Réserver de la place pour le badge si is_mine (22 px de hauteur)
        badge_h = 22 if is_mine else 0
        total_text_h = font_small.get_height() + 4 + font_tiny.get_height() + (4 + badge_h if is_mine else 0)
        text_start_y = cy + (CARD_H - total_text_h) // 2

        name_clipped = _clip_text(lv["name"].upper(), font_small, TEXT_MAX)
        nm_s = font_small.render(name_clipped, True, WHITE)
        screen.blit(nm_s, (tx, text_start_y))

        author_clipped = _clip_text(f"par {get_display_name(lv.get('author','?'))}", font_tiny, TEXT_MAX)
        au_s = font_tiny.render(author_clipped, True, (120, 130, 170))
        au_y = text_start_y + font_small.get_height() + 4
        screen.blit(au_s, (tx, au_y))

        # Badge statut (is_mine) — sous l'auteur, toujours dans la carte
        if is_mine:
            if published:
                badge_col = GREEN_SOFT; badge_txt = "PUBLIC"
            elif completable:
                badge_col = GOLD; badge_txt = "PRÊT"
            else:
                badge_col = (100, 110, 150); badge_txt = "BROUILLON"
            bw = font_tiny.size(badge_txt)[0] + 16
            badge_y = au_y + font_tiny.get_height() + 4
            # S'assure que le badge reste dans la carte
            badge_y = min(badge_y, cy + CARD_H - badge_h - 4)
            bs = pygame.Surface((bw, badge_h), pygame.SRCALPHA)
            pygame.draw.rect(bs, (0,0,0,140), (0,0,bw,badge_h), border_radius=5)
            pygame.draw.rect(bs, (*badge_col,200), (0,0,bw,badge_h), 1, border_radius=5)
            screen.blit(bs, (tx, badge_y))
            bt = font_tiny.render(badge_txt, True, badge_col)
            screen.blit(bt, (tx + bw//2 - bt.get_width()//2, badge_y + badge_h//2 - bt.get_height()//2))

        # Zone droite : boutons (centrés verticalement dans la carte)
        RX = CARD_X + CARD_W - BTN_AREA + 10
        if is_mine:
            draw_btn("EDITER",  RX + 55,  MID_Y, 100, 38, small=True)
            if lv.get("published"):
                draw_btn("DEPUB",   RX + 165, MID_Y, 100, 38, danger=True,  small=True)
            else:
                draw_btn("TESTER",  RX + 165, MID_Y, 100, 38, accent=True, small=True)
            draw_btn("SUPPR",   RX + 275, MID_Y, 80,  38, danger=True, small=True)
        elif is_admin(player):
            # Admin peut jouer, liker ET supprimer les niveaux des autres
            draw_btn("JOUER",   RX + 55,  MID_Y, 100, 44, accent=True)
            lk_lbl = "LIKE" if liked else "LIKER"
            draw_btn(lk_lbl,    RX + 175, MID_Y, 90,  38,
                     color_override=((120,20,40),(150,30,50),(255,100,130)) if liked else None,
                     small=True)
            draw_btn("SUPPR",   RX + 275, MID_Y, 80,  38, danger=True, small=True)
        else:
            draw_btn("JOUER",   RX + 65,  MID_Y, 120, 44, accent=True)
            lk_lbl = "LIKE" if liked else "LIKER"
            draw_btn(lk_lbl,    RX + 205, MID_Y, 110, 38,
                     color_override=((120,20,40),(150,30,50),(255,100,130)) if liked else None,
                     small=True)

    # ── BOUCLE ────────────────────────────────────────────────────────────────
    while True:
        clock.tick(FPS); t += 0.04
        mx, my = pygame.mouse.get_pos()
        if feedback_timer > 0: feedback_timer -= 1

        lv_list = _get_list()
        LIST_Y  = LIST_Y_OFF()
        LIST_H  = LIST_BOT - LIST_Y
        is_mine = (sel_tab == 1 and sel_sub == 1)

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE: return
            if event.type == MOUSEWHEEL:
                max_scroll = max(0, len(lv_list) * (CARD_H + GAP) - LIST_H)
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * 35))

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                FOOTER_Y = SCREEN_HEIGHT - FOOTER_H // 2

                # Retour
                if btn_rect(CX, FOOTER_Y, 220, 46).collidepoint(event.pos): return

                # Onglets principaux — OFFICIEL gauche (ti=0), COMMUNAUTE droite (ti=1)
                for ti in range(2):
                    tw = 280
                    tx_btn = CX - tw + ti * tw + tw // 2
                    if btn_rect(tx_btn, HEADER_H + TAB_H // 2, tw - 8, TAB_H - 6).collidepoint(event.pos):
                        if sel_tab != ti: scroll_y = 0
                        sel_tab = ti

                # Sous-onglets + bouton créer
                if sel_tab == 1:
                    sub_y = HEADER_H + TAB_H + SUBTAB_H // 2
                    for si in range(2):
                        sw  = 210
                        sx_b = CX - 240 + si * (sw + 10) + sw // 2
                        if btn_rect(sx_b, sub_y, sw, SUBTAB_H - 4).collidepoint(event.pos):
                            if sel_sub != si: scroll_y = 0
                            sel_sub = si
                    # Bouton + Créer (uniquement sur "Mes niveaux" = sel_sub==1)
                    if sel_sub == 1:
                        create_bx = CARD_X + CARD_W - 80
                        if btn_rect(create_bx, sub_y, 150, SUBTAB_H - 4).collidepoint(event.pos):
                            result = level_editor(player, data, lvl_data, None)
                            if result is not None:
                                feedback_msg = f"« {result['name']} » sauvegarde !"; feedback_col = GOLD; feedback_timer = 200
                            lvl_data = load_levels()
                            continue

                # Cartes
                for i, lv_item in enumerate(lv_list):
                    cy = LIST_Y + i * (CARD_H + GAP) - scroll_y
                    if cy + CARD_H < LIST_Y or cy > LIST_BOT: continue
                    MID_Y = cy + CARD_H // 2

                    if sel_tab == 0:
                        # Onglet OFFICIEL
                        if is_admin(player):
                            # Admin : JOUER + RÉCOMP + SUPPR
                            if btn_rect(CARD_X + CARD_W - BTN_AREA//2 - 130, MID_Y, 100, 46).collidepoint(event.pos):
                                play_level(lv_item, player, data, player.get("selected_skin","Flappy"))
                                lvl_data = load_levels()
                            elif btn_rect(CARD_X + CARD_W - BTN_AREA//2 - 20, MID_Y, 100, 38).collidepoint(event.pos):
                                result_rew = edit_official_reward_screen(lv_item)
                                if result_rew is not None:
                                    rc, rmc = result_rew
                                    new_data = update_official_level_reward_in_file(lv_item["id"], rc, rmc)
                                    if new_data is not None:
                                        lvl_data = new_data
                                    else:
                                        lvl_data = load_levels()
                                    feedback_msg = f"Récompenses mises à jour : {rc} pièces / {rmc} pièces mission"
                                    feedback_col = GOLD; feedback_timer = 220
                            elif btn_rect(CARD_X + CARD_W - BTN_AREA//2 + 90, MID_Y, 80, 38).collidepoint(event.pos):
                                new_data = delete_official_level_from_file(lv_item["id"])
                                if new_data is not None:
                                    lvl_data = new_data
                                else:
                                    lvl_data = load_levels()
                                scroll_y = max(0, scroll_y - (CARD_H + GAP))
                                feedback_msg = "Niveau officiel supprime."; feedback_col = RED_HOT; feedback_timer = 150
                        else:
                            if btn_rect(CARD_X + CARD_W - BTN_AREA//2, MID_Y, 130, 46).collidepoint(event.pos):
                                play_level(lv_item, player, data, player.get("selected_skin","Flappy"))
                                lvl_data = load_levels()
                    else:
                        RX = CARD_X + CARD_W - BTN_AREA + 10
                        if is_mine:
                            if btn_rect(RX+55,  MID_Y, 100, 38).collidepoint(event.pos):
                                result = level_editor(player, data, lvl_data, lv_item)
                                if result is not None:
                                    feedback_msg = "Niveau modifie !"; feedback_col = GOLD; feedback_timer = 160
                                lvl_data = load_levels()
                            elif btn_rect(RX+165, MID_Y, 100, 38).collidepoint(event.pos):
                                if lv_item.get("published"):
                                    # Bouton DÉPUBLIER
                                    new_data = unpublish_level_in_file(lv_item["id"])
                                    if new_data is not None:
                                        lvl_data = new_data
                                    else:
                                        lvl_data = load_levels()
                                    feedback_msg = "Niveau depublie."; feedback_col = GOLD; feedback_timer = 150
                                else:
                                    # Bouton TESTER
                                    play_level(lv_item, player, data, player.get("selected_skin","Flappy"), is_editor_test=True)
                                    lvl_data = load_levels()
                            elif btn_rect(RX+275, MID_Y, 80, 38).collidepoint(event.pos):
                                # Bouton SUPPRIMER — bypass merge
                                new_data = delete_level_from_file(lv_item["id"])
                                if new_data is not None:
                                    lvl_data = new_data
                                else:
                                    lvl_data = load_levels()
                                scroll_y = max(0, scroll_y - (CARD_H + GAP))
                                feedback_msg = "Niveau supprime."; feedback_col = RED_HOT; feedback_timer = 150
                        elif is_admin(player):
                            # Admin sur niveau d'un autre joueur (communauté publique)
                            if btn_rect(RX+55, MID_Y, 100, 44).collidepoint(event.pos):
                                play_level(lv_item, player, data, player.get("selected_skin","Flappy"))
                                lvl_data = load_levels()
                            elif btn_rect(RX+175, MID_Y, 90, 38).collidepoint(event.pos):
                                pname = player["name"]
                                already_liked = lv_item["id"] in player.get("liked_levels", [])
                                if not already_liked:
                                    # Lire les donnees fraiches depuis Supabase pour ne pas ecraser les likes des autres
                                    fresh_rows = _sb_get("levels", f"id=eq.{lv_item['id']}&limit=1")
                                    if fresh_rows:
                                        fresh = _row_to_level(fresh_rows[0])
                                        liked_by = fresh.get("liked_by", [])
                                        current_likes = fresh.get("likes", 0)
                                    else:
                                        liked_by = lv_item.get("liked_by", [])
                                        current_likes = lv_item.get("likes", 0)
                                    if pname not in liked_by:
                                        liked_by.append(pname)
                                        current_likes += 1
                                    lv_item["liked_by"] = liked_by
                                    lv_item["likes"] = current_likes
                                    pl = player.get("liked_levels", [])
                                    if lv_item["id"] not in pl: pl.append(lv_item["id"])
                                    player["liked_levels"] = pl
                                    save_data(data); save_level(lv_item)
                                    feedback_msg = "Niveau like !"; feedback_col = (255,100,130); feedback_timer = 130
                                else:
                                    feedback_msg = "Deja like."; feedback_col = GREY; feedback_timer = 90
                                lvl_data = load_levels()
                            elif btn_rect(RX+275, MID_Y, 80, 38).collidepoint(event.pos):
                                # Admin SUPPRIMER le niveau d'un autre
                                new_data = delete_level_from_file(lv_item["id"])
                                if new_data is not None:
                                    lvl_data = new_data
                                else:
                                    lvl_data = load_levels()
                                scroll_y = max(0, scroll_y - (CARD_H + GAP))
                                feedback_msg = "Niveau supprime (admin)."; feedback_col = RED_HOT; feedback_timer = 150
                        else:
                            if btn_rect(RX+65, MID_Y, 120, 44).collidepoint(event.pos):
                                play_level(lv_item, player, data, player.get("selected_skin","Flappy"))
                                lvl_data = load_levels()
                            elif btn_rect(RX+205, MID_Y, 110, 38).collidepoint(event.pos):
                                pname = player["name"]
                                already_liked = lv_item["id"] in player.get("liked_levels", [])
                                if not already_liked:
                                    # Lire les donnees fraiches depuis Supabase pour ne pas ecraser les likes des autres
                                    fresh_rows = _sb_get("levels", f"id=eq.{lv_item['id']}&limit=1")
                                    if fresh_rows:
                                        fresh = _row_to_level(fresh_rows[0])
                                        liked_by = fresh.get("liked_by", [])
                                        current_likes = fresh.get("likes", 0)
                                    else:
                                        liked_by = lv_item.get("liked_by", [])
                                        current_likes = lv_item.get("likes", 0)
                                    if pname not in liked_by:
                                        liked_by.append(pname)
                                        current_likes += 1
                                    lv_item["liked_by"] = liked_by
                                    lv_item["likes"] = current_likes
                                    pl = player.get("liked_levels", [])
                                    if lv_item["id"] not in pl: pl.append(lv_item["id"])
                                    player["liked_levels"] = pl
                                    save_data(data); save_level(lv_item)
                                    feedback_msg = "Niveau like !"; feedback_col = (255,100,130); feedback_timer = 130
                                else:
                                    feedback_msg = "Deja like."; feedback_col = GREY; feedback_timer = 90
                                lvl_data = load_levels()

        # ── DESSIN ───────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(190)

        # ── Header ───────────────────────────────────────────────────────────
        hdr = pygame.Surface((SCREEN_WIDTH, HEADER_H), pygame.SRCALPHA)
        pygame.draw.rect(hdr, (6, 8, 22, 240), (0, 0, SCREEN_WIDTH, HEADER_H))
        pygame.draw.line(hdr, (*GOLD, 80), (0, HEADER_H-1), (SCREEN_WIDTH, HEADER_H-1), 1)
        screen.blit(hdr, (0, 0))
        title_s = font_med.render("NIVEAUX", True, GOLD)
        screen.blit(title_s, (CX - title_s.get_width()//2, HEADER_H//2 - title_s.get_height()//2))

        # ── Onglets principaux ────────────────────────────────────────────────
        tab_display = [(0, "OFFICIEL"), (1, "COMMUNAUTE")]
        for draw_pos, (ti, tlbl) in enumerate(tab_display):
            tw = 280
            tx_b = CX - tw + draw_pos * tw + tw // 2
            active = (ti == sel_tab)
            if ti == 0:  # Officiel → vert
                col_ov = ((20,50,20),(30,70,30),GREEN_SOFT) if active else None
            else:        # Communauté → cyan
                col_ov = ((15,40,70),(22,55,95),CYAN) if active else None
            draw_btn(tlbl, tx_b, HEADER_H + TAB_H//2, tw - 8, TAB_H - 6, color_override=col_ov)

        # ── Sous-onglets communauté ───────────────────────────────────────────
        if sel_tab == 1:
            sub_y = HEADER_H + TAB_H + SUBTAB_H // 2
            sub_labels = ["NIVEAUX PUBLICS", "MES NIVEAUX"]  # 0=Publics (gauche), 1=Mes (droite)
            for si, slbl in enumerate(sub_labels):
                sw  = 210
                sx_b = CX - 240 + si * (sw + 10) + sw // 2
                active = (si == sel_sub)
                col_ov = ((15,40,70),(22,55,95),CYAN) if active else None
                draw_btn(slbl, sx_b, sub_y, sw, SUBTAB_H - 4, small=True, color_override=col_ov)
            # Bouton créer — visible seulement sur "Mes niveaux" (si=1)
            if sel_sub == 1:
                draw_btn("+ CREER", CARD_X + CARD_W - 80, sub_y, 150, SUBTAB_H - 4, accent=True, small=True)

        # ── Liste ─────────────────────────────────────────────────────────────
        screen.set_clip(pygame.Rect(0, LIST_Y, SCREEN_WIDTH, LIST_H))
        for i, lv_item in enumerate(_get_list()):
            cy = LIST_Y + i * (CARD_H + GAP) - scroll_y
            if cy + CARD_H < LIST_Y - 4 or cy > LIST_BOT + 4: continue
            hov = pygame.Rect(CARD_X, cy, CARD_W, CARD_H).collidepoint(mx, my)
            if sel_tab == 0: _draw_official_card(lv_item, cy, hov)
            else:            _draw_community_card(lv_item, cy, hov, is_mine)

        if not _get_list():
            if sel_tab == 0:
                empty_lines = ["Aucun niveau officiel pour l'instant.", "Les niveaux officiels arrivent bientot !"]
            elif sel_sub == 1:   # Mes niveaux
                empty_lines = ["Tu n'as pas encore cree de niveau.", "Clique sur + CREER pour commencer."]
            else:                # Niveaux publics
                empty_lines = ["Aucun niveau public disponible."]
            for ei, el in enumerate(empty_lines):
                es = (font_small if ei == 0 else font_tiny).render(el, True, GREY if ei == 0 else (80,85,110))
                screen.blit(es, (CX - es.get_width()//2, LIST_Y + LIST_H//2 - 20 + ei * 28))
        screen.set_clip(None)

        # ── Scrollbar (si nécessaire) ─────────────────────────────────────────
        total_content = len(_get_list()) * (CARD_H + GAP)
        if total_content > LIST_H:
            sb_h = int(LIST_H * LIST_H / total_content)
            sb_y = LIST_Y + int(scroll_y / total_content * LIST_H)
            pygame.draw.rect(screen, (35, 38, 65), (SCREEN_WIDTH - 8, LIST_Y, 6, LIST_H), border_radius=3)
            pygame.draw.rect(screen, (*GOLD, 160), (SCREEN_WIDTH - 8, sb_y, 6, max(20, sb_h)), border_radius=3)

        # ── Footer ───────────────────────────────────────────────────────────
        ftr = pygame.Surface((SCREEN_WIDTH, FOOTER_H), pygame.SRCALPHA)
        pygame.draw.rect(ftr, (6, 8, 22, 240), (0, 0, SCREEN_WIDTH, FOOTER_H))
        pygame.draw.line(ftr, (*GOLD, 60), (0, 0), (SCREEN_WIDTH, 0), 1)
        screen.blit(ftr, (0, SCREEN_HEIGHT - FOOTER_H))
        draw_btn("RETOUR", CX, SCREEN_HEIGHT - FOOTER_H//2, 220, 46)

        # ── Feedback toast ────────────────────────────────────────────────────
        if feedback_timer > 0:
            a  = min(255, feedback_timer * 6)
            fs = font_small.render(feedback_msg, True, feedback_col)
            fw = fs.get_width() + 36; fh = fs.get_height() + 14
            fb = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb, (6, 8, 20, 215), (0,0,fw,fh), border_radius=10)
            pygame.draw.rect(fb, (*feedback_col, 180), (0,0,fw,fh), 2, border_radius=10)
            fb.set_alpha(a); fs.set_alpha(a)
            screen.blit(fb, (CX - fw//2, SCREEN_HEIGHT - FOOTER_H - fh - 8))
            screen.blit(fs, (CX - fs.get_width()//2, SCREEN_HEIGHT - FOOTER_H - fh - 8 + 7))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()


def player_card_popup(viewed_player):
    """
    Affiche une carte modale en lecture seule pour n'importe quel joueur du classement.
    viewed_player : dict joueur (tel que retourné par get_leaderboard).
    Fermeture : clic, ESPACE, ENTRÉE ou ECHAP.
    """
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2

    PANEL_W = 480
    PANEL_H = 560

    TITLE_Y    = CY - PANEL_H // 2 + 26
    AV_R       = 52
    AV_Y       = TITLE_Y + font_med.get_height() + 18 + AV_R
    NM_Y       = AV_Y + AV_R + 10
    STATS_Y    = NM_Y + font_small.get_height() + 28
    STAT_ROW_H = 80
    STAT_BOX_H = 68
    STAT_COL_W = (PANEL_W - 72) // 2
    BTN_Y      = CY + PANEL_H // 2 - 38

    _games = viewed_player.get("games_played", 0)
    _total = viewed_player.get("total_score",  0)
    _avg   = round(_total / _games) if _games > 0 else 0

    stats = [
        ("PARTIES JOUÉES",  str(viewed_player.get("games_played",  0))),
        ("MEILLEUR SCORE",  str(viewed_player.get("best_score",    0))),
        ("SCORE TOTAL",     str(_total)),
        ("SCORE MOYEN",     str(_avg)),
        ("PIÈCES GAGNÉES",     str(viewed_player.get("missions_stats", {}).get("coins_total", viewed_player.get("total_coins", 0)))),
        ("P. MISSION GAGNÉES", str(viewed_player.get("total_mission_coins_earned", viewed_player.get("mission_coins", 0)))),
    ]

    t = 0.0
    while True:
        clock.tick(FPS)
        t += 0.04

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_SPACE, K_RETURN):
                    return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Clic bouton fermer OU clic en dehors du panneau = fermer
                panel_rect = pygame.Rect(CX - PANEL_W // 2, CY - PANEL_H // 2, PANEL_W, PANEL_H)
                if btn_clicked(event, CX, BTN_Y, 200, 46) or not panel_rect.collidepoint(event.pos):
                    return

        # ── Dessin ────────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(220)
        draw_panel(CX, CY, PANEL_W, PANEL_H, radius=20, border=GOLD, shine_ratio=2)

        # Titre
        title_s = font_med.render("PROFIL JOUEUR", True, GOLD)
        screen.blit(title_s, (CX - title_s.get_width() // 2, TITLE_Y))

        # Avatar
        draw_avatar(viewed_player, CX, AV_Y, radius=AV_R,
                    font=pygame.font.SysFont('Impact', 46))

        # Pseudo
        nm_s = font_small.render(get_display_name(viewed_player["name"]), True, WHITE)
        screen.blit(nm_s, (CX - nm_s.get_width() // 2, NM_Y))

        # Badge streak si dispo
        streak = viewed_player.get("streak1_days", 0)
        if streak >= 1:
            badge = get_streak_badge(streak)
            if badge:
                bx = CX + nm_s.get_width() // 2 + 8
                screen.blit(badge, (bx, NM_Y + nm_s.get_height() // 2 - badge.get_height() // 2))

        # Grille de stats (2 colonnes)
        for idx, (lbl, val) in enumerate(stats):
            col, row = idx % 2, idx // 2
            sx = CX - (PANEL_W - 72) // 2 + col * (STAT_COL_W + 20)
            sy = STATS_Y + row * STAT_ROW_H

            sb = pygame.Surface((STAT_COL_W, STAT_BOX_H), pygame.SRCALPHA)
            pygame.draw.rect(sb, (255, 255, 255, 18), (0, 0, STAT_COL_W, STAT_BOX_H), border_radius=12)
            pygame.draw.rect(sb, (*GOLD, 55),         (0, 0, STAT_COL_W, STAT_BOX_H), width=2, border_radius=12)
            screen.blit(sb, (sx, sy))

            lbl_s = font_tiny.render(lbl, True, (160, 165, 195))
            val_s = font_small.render(val, True, GOLD)
            screen.blit(lbl_s, (sx + STAT_COL_W // 2 - lbl_s.get_width() // 2, sy + 12))
            screen.blit(val_s, (sx + STAT_COL_W // 2 - val_s.get_width() // 2, sy + 34))

        # Bouton fermer
        draw_btn("FERMER", CX, BTN_Y, 200, 46, small=True)

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT EN TEMPS RÉEL (Supabase)
# ══════════════════════════════════════════════════════════════════════════════
CHAT_FILE = ":supabase:"
CHAT_MAX_MESSAGES = 200

# Instance globale (initialisée dans main() après chargement du joueur)
_GLOBAL_CHAT = None

def _chat_load():
    """Charge les 100 derniers messages depuis Supabase."""
    try:
        rows = _sb_get("chat_messages", "order=ts.asc&limit=100")
        return [{"author": r["author"], "text": r["text"],
                 "ts": r["ts"][11:16], "_id": r["id"]} for r in rows]
    except Exception as e:
        print(f"[CHAT] Erreur chargement: {e}")
        return []

def _chat_save(messages):
    """Non utilisé en mode Supabase — les messages sont postés individuellement."""
    pass

def _chat_post(author, text):
    """Envoie un message vers Supabase."""
    if not text.strip():
        return
    _sb_post("chat_messages", {
        "author": author,
        "text":   text.strip()[:200],
    })

def _chat_delete(index):
    """Supprime le message à l'index donné (admin seulement)."""
    # On ne peut pas supprimer par index en Supabase,
    # le ChatOverlay doit passer l'id du message
    pass

def _chat_delete_by_id(msg_id):
    """Supprime un message par son UUID Supabase."""
    _sb_delete("chat_messages", f"id=eq.{msg_id}")


class ChatOverlay:
    """Panneau de chat qui s'ouvre sur la gauche, au premier plan."""

    PANEL_W       = 390
    PANEL_H_RATIO = 0.82
    INPUT_H       = 46
    HEADER_H      = 46          # hauteur du header
    CLOSE_R       = 14          # rayon du bouton fermer (cercle)
    MSG_SPACING   = 10          # espace vertical entre bulles
    BUBBLE_MAX_W  = 320         # largeur max d'une bulle
    MSG_MAX_CHARS = 120         # limite de caractères par message
    POLL_INTERVAL = 300

    # constantes bouton toggle
    TOG_X, TOG_Y, TOG_W, TOG_H = 10, 10, 40, 40

    # Émojis disponibles dans le picker (8 colonnes, scrollable)
    EMOJI_LIST = [
        # Visages heureux
        "😀","😃","😄","😁","😆","😅","🤣","😂",
        "🙂","🙃","😉","😊","😇","🥰","😍","🤩",
        "😘","😗","😚","😙","🥲","😋","😛","😜",
        "🤪","😝","🤑","🤗","🤭","🫢","🫣","🤫",
        # Visages négatifs / neutres
        "🤔","🫡","🤐","🤨","😐","😑","😶","🫥",
        "😏","😒","🙄","😬","🤥","🫨","😌","😔",
        "😪","🤤","😴","😷","🤒","🤕","🤢","🤮",
        "🤧","🥵","🥶","🥴","😵","🤯","😎","🤓",
        "🥸","😭","😢","😤","😠","😡","🤬","🫠",
        "😈","👿","💀","☠️","💩","🤡","👹","👺",
        "👻","👽","👾","🤖","😺","😸","😹","😻",
        # Gestes / mains
        "👋","🤚","🖐️","✋","🖖","🫱","🫲","🤝",
        "👍","👎","👊","✊","🤛","🤜","🤞","🫰",
        "🤟","🤘","🤙","👈","👉","👆","🖕","👇",
        "☝️","🫵","👌","🤌","🤏","✌️","🤞","🖖",
        "💪","🦾","🙏","🫶","🤲","🫁","👐","🤷",
        # Cœurs & symboles
        "❤️","🧡","💛","💚","💙","💜","🖤","🤍",
        "🤎","💔","❣️","💕","💞","💓","💗","💖",
        "💘","💝","💟","☮️","✝️","🔥","✨","⭐",
        "🌟","💫","⚡","🌈","☀️","🌙","❄️","💧",
        # Objets & divers
        "🎉","🎊","🎮","🏆","🥇","🎯","🎲","🃏",
        "🎵","🎶","🎸","🎤","📱","💻","🖥️","⌨️",
        "🍕","🍔","🍟","🌮","🍜","🍣","🍦","🎂",
        "☕","🧃","🍺","🥂","💊","💉","🔑","🔒",
        "💰","💎","🚀","✈️","🚗","🏠","🌍","🤦",
    ]
    EMOJI_COLS = 8

    def __init__(self, player_name, is_admin_user, player=None, data=None):
        self.player_name  = player_name
        self.is_admin     = is_admin_user
        self.player       = player
        self.data         = data
        self.open         = False

        self.messages     = []
        self.poll_timer   = 0
        self.last_count   = 0
        self.unread       = False

        self.input_text   = ""
        self.input_active = False
        self.cursor_blink = 0
        self.cursor_pos   = 0   # position du curseur dans input_text (en caractères)
        self.view_offset  = 0   # index du 1er caractère visible (scroll horizontal)

        self.scroll_y     = 0   # 0 = tout en bas

        self.slide_x  = -self.PANEL_W
        self.target_x = -self.PANEL_W

        # Fonts texte normales
        self.font_msg  = pygame.font.SysFont('Verdana', 15)
        self.font_auth = pygame.font.SysFont('Verdana', 12)
        self.font_inp  = pygame.font.SysFont('Verdana', 15)
        self.font_btn  = pygame.font.SysFont('Impact',  16)

        # Font emoji couleur via PIL (NotoColorEmoji bitmap)
        # Chemin absolu pour que PIL puisse l'ouvrir sur Windows
        _rel = os.path.join('assets', 'fonts', 'Noto_Color_Emoji', 'NotoColorEmoji-Regular.ttf')
        self._EMOJI_FONT_PATH = os.path.abspath(_rel)
        self._pil_emoji_font_cache = {}   # size -> PIL ImageFont
        self._pygame_emoji_font_cache = {}  # size -> pygame.Font (fallback Segoe)
        try:
            from PIL import Image as _PILImage, ImageDraw as _PILDraw, ImageFont as _PILFont
            self._PIL_Image  = _PILImage
            self._PIL_Draw   = _PILDraw
            self._PIL_Font   = _PILFont
            # Vérifier que la font est réellement accessible
            test_f = _PILFont.truetype(self._EMOJI_FONT_PATH, 32)
            self._emoji_mode = 'pil'
        except Exception as e:
            self._PIL_Image  = None
            # Fallback: Segoe UI Emoji (Windows natif) via pygame
            try:
                _seg = pygame.font.SysFont('segoeuiemoji,seguiemj,segoeui', 32)
                self._emoji_mode = 'segoe'
                print(f"[CHAT] PIL indispo ({e}), utilisation Segoe UI Emoji")
            except Exception:
                self._emoji_mode = 'none'
                print(f"[CHAT] Aucune font emoji disponible ({e})")

        self._emoji_ok = (self._emoji_mode in ('pil', 'segoe'))
        # Cache surfaces emoji pré-rendues  {(emoji, size) -> pygame.Surface}
        self._emoji_cache = {}

        # Picker emoji
        self.picker_open   = False
        self.picker_scroll = 0   # décalage vertical en pixels (scroll)

        # Carte joueur à ouvrir (None ou dict joueur)
        self.pending_card = None

        self.messages    = []   # chargé en async au démarrage
        self.last_count  = -1   # -1 = pas encore chargé → ne pas marquer unread au 1er chargement
        self._first_load = True
        # Chargement initial en thread séparé
        threading.Thread(target=self._reload, daemon=True).start()

    # ── Propriétés ───────────────────────────────────────────────────────────
    @property
    def panel_h(self):
        return int(SCREEN_HEIGHT * self.PANEL_H_RATIO)

    @property
    def panel_y(self):
        return (SCREEN_HEIGHT - self.panel_h) // 2

    @property
    def area_y(self):
        return self.panel_y + self.HEADER_H + 4

    @property
    def area_h(self):
        return self.panel_h - self.HEADER_H - self.INPUT_H - 20

    # ── Hauteur d'une bulle ───────────────────────────────────────────────────
    # Helpers emoji
    def _is_emoji_char(self, ch):
        cp = ord(ch)
        return (
            (0x1F300 <= cp <= 0x1FAFF) or
            (0x2600  <= cp <= 0x27BF)  or
            (0xFE00  <= cp <= 0xFE0F)  or
            (0x1F1E0 <= cp <= 0x1F1FF) or
            cp in (0x200D, 0xFE0F, 0x20E3)
        )

    def _split_emoji(self, text):
        segments = []
        i = 0
        while i < len(text):
            if self._is_emoji_char(text[i]):
                j = i + 1
                while j < len(text) and self._is_emoji_char(text[j]):
                    j += 1
                segments.append((True, text[i:j]))
                i = j
            else:
                j = i + 1
                while j < len(text) and not self._is_emoji_char(text[j]):
                    j += 1
                segments.append((False, text[i:j]))
                i = j
        return segments

    def _pil_font(self, size):
        if size not in self._pil_emoji_font_cache:
            try:
                self._pil_emoji_font_cache[size] = self._PIL_Font.truetype(
                    self._EMOJI_FONT_PATH, size)
            except Exception:
                self._pil_emoji_font_cache[size] = None
        return self._pil_emoji_font_cache[size]

    def _segoe_font(self, size):
        if size not in self._pygame_emoji_font_cache:
            try:
                self._pygame_emoji_font_cache[size] = pygame.font.SysFont(
                    'segoeuiemoji,seguiemj,segoeui', size)
            except Exception:
                self._pygame_emoji_font_cache[size] = None
        return self._pygame_emoji_font_cache[size]

    def _emoji_to_surf(self, emoji_str, px_size):
        key = (emoji_str, px_size)
        if key in self._emoji_cache:
            return self._emoji_cache[key]
        result = None

        # ── Mode PIL (NotoColorEmoji) ─────────────────────────────────────────
        if self._emoji_mode == 'pil' and self._PIL_Image:
            try:
                pil_font = self._pil_font(px_size)
                if pil_font:
                    # NotoColorEmoji: rendu a 109px (taille native bitmap) puis redim
                    NATIVE = 109
                    native_font = self._pil_font(NATIVE)
                    if native_font is None:
                        native_font = pil_font
                    dummy = self._PIL_Image.new("RGBA", (1, 1))
                    dd = self._PIL_Draw.Draw(dummy)
                    bbox = dd.textbbox((0, 0), emoji_str, font=native_font)
                    w = max(bbox[2] - bbox[0], 1)
                    h = max(bbox[3] - bbox[1], 1)
                    img = self._PIL_Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
                    draw = self._PIL_Draw.Draw(img)
                    draw.text((-bbox[0] + 2, -bbox[1] + 2), emoji_str,
                              font=native_font, embedded_color=True)
                    # Vérifier qu on a des pixels non transparents
                    pixels = img.getdata()
                    has_content = any(p[3] > 10 for p in pixels)
                    if has_content:
                        raw = img.tobytes()
                        surf_native = pygame.image.fromstring(raw, img.size, "RGBA").convert_alpha()
                        # Redimensionner à px_size
                        scale = px_size / max(surf_native.get_height(), 1)
                        nw = max(1, int(surf_native.get_width() * scale))
                        result = pygame.transform.smoothscale(surf_native, (nw, px_size))
            except Exception:
                pass

        # ── Mode Segoe UI Emoji (pygame SysFont Windows) ─────────────────────
        if result is None and self._emoji_mode in ('pil', 'segoe'):
            try:
                seg = self._segoe_font(px_size)
                if seg:
                    surf = seg.render(emoji_str, True, (255, 255, 255))
                    # Vérifier que ce n est pas une boite vide (width trop petit)
                    if surf.get_width() > px_size // 3:
                        result = surf
            except Exception:
                pass

        # ── Fallback dessiné ─────────────────────────────────────────────────
        if result is None:
            # Petit cercle coloré (mieux que rien)
            s = pygame.Surface((px_size, px_size), pygame.SRCALPHA)
            hue_colors = [(255,80,80),(255,160,60),(255,220,60),(80,200,80),(60,160,255),(180,80,255)]
            color = hue_colors[hash(emoji_str) % len(hue_colors)]
            pygame.draw.circle(s, color, (px_size//2, px_size//2), px_size//2 - 1)
            # Premiere lettre visible
            try:
                tiny = pygame.font.SysFont('arial', max(8, px_size//3))
                lbl = tiny.render(emoji_str[0] if emoji_str else "?", True, (255,255,255))
                s.blit(lbl, (px_size//2 - lbl.get_width()//2, px_size//2 - lbl.get_height()//2))
            except Exception:
                pass
            result = s

        self._emoji_cache[key] = result
        return result

    def _render_mixed(self, text, font_text, target_h, color):
        segments = self._split_emoji(text)
        parts = []
        total_w = 0
        max_h = target_h
        for is_em, seg in segments:
            if not seg:
                continue
            if is_em:
                surf = self._emoji_to_surf(seg, target_h)
                if surf.get_height() != target_h and surf.get_height() > 0:
                    scale = target_h / surf.get_height()
                    nw = max(1, int(surf.get_width() * scale))
                    surf = pygame.transform.smoothscale(surf, (nw, target_h))
            else:
                try:
                    surf = font_text.render(seg, True, color)
                except Exception:
                    surf = font_text.render("?", True, color)
            parts.append(surf)
            total_w += surf.get_width()
            max_h = max(max_h, surf.get_height())
        if not parts:
            return pygame.Surface((1, max_h), pygame.SRCALPHA)
        result = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
        x = 0
        for surf in parts:
            result.blit(surf, (x, max_h // 2 - surf.get_height() // 2))
            x += surf.get_width()
        return result

    def _text_width_mixed(self, text, font_text, em_size):
        w = 0
        for is_em, seg in self._split_emoji(text):
            if not seg:
                continue
            if is_em:
                es = self._emoji_to_surf(seg, em_size)
                if es.get_height() > 0:
                    scale = em_size / es.get_height()
                    w += max(1, int(es.get_width() * scale))
                else:
                    w += em_size
            else:
                try:
                    w += font_text.size(seg)[0]
                except Exception:
                    w += font_text.size("?")[0]
        return w

    def _wrap_mixed(self, text, max_w, em_size=None):
        if em_size is None:
            em_size = self.font_msg.get_height()
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            # Si le mot seul dépasse max_w, le couper caractère par caractère
            if self._text_width_mixed(w, self.font_msg, em_size) > max_w:
                if cur:
                    lines.append(cur)
                    cur = ""
                tmp = ""
                for ch in w:
                    test_ch = tmp + ch
                    if self._text_width_mixed(test_ch, self.font_msg, em_size) <= max_w:
                        tmp = test_ch
                    else:
                        if tmp:
                            lines.append(tmp)
                        tmp = ch
                if tmp:
                    cur = tmp
                continue
            test = (cur + " " + w).strip()
            if self._text_width_mixed(test, self.font_msg, em_size) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines if lines else [""]

    def _get_emoji_pick_surf(self, emoji, size=24):
        return self._emoji_to_surf(emoji, size)

    def _picker_rect(self):
        CELL       = 40
        COLS       = self.EMOJI_COLS
        ROWS       = (len(self.EMOJI_LIST) + COLS - 1) // COLS
        VISIBLE_ROWS = 5   # lignes visibles à la fois
        px         = int(self.slide_x)
        py         = self.panel_y
        ph         = self.panel_h
        pck_w      = COLS * CELL + 16
        pck_h      = VISIBLE_ROWS * CELL + 10   # hauteur fixe (fenêtre scrollable)
        pck_x      = px + 8
        pck_y      = py + ph - self.INPUT_H - pck_h - 18
        return pygame.Rect(pck_x, pck_y, pck_w, pck_h), CELL, COLS, ROWS

    def _draw_picker(self, mx, my):
        CELL = 40
        COLS = self.EMOJI_COLS
        ROWS = (len(self.EMOJI_LIST) + COLS - 1) // COLS
        VISIBLE_ROWS = 5
        EM_SIZE = CELL - 10

        r, _, _, _ = self._picker_rect()
        total_h = ROWS * CELL + 10
        max_scroll = max(0, total_h - r.h)
        self.picker_scroll = max(0, min(self.picker_scroll, max_scroll))

        # Fond du picker
        ps = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(ps, (10, 16, 38, 248), (0, 0, r.w, r.h), border_radius=14)
        pygame.draw.rect(ps, (80, 130, 220, 210), (0, 0, r.w, r.h), 2, border_radius=14)
        screen.blit(ps, (r.x, r.y))

        # Clip pour ne dessiner que dans la fenêtre
        clip_rect = pygame.Rect(r.x + 4, r.y + 4, r.w - 14, r.h - 8)
        screen.set_clip(clip_rect)

        for idx, em in enumerate(self.EMOJI_LIST):
            row, col = divmod(idx, COLS)
            cx = r.x + 8 + col * CELL
            cy = r.y + 5 + row * CELL - self.picker_scroll
            # Ne pas dessiner hors zone visible
            if cy + CELL < r.y or cy > r.y + r.h:
                continue
            cell_r = pygame.Rect(cx, cy, CELL - 2, CELL - 2)
            hov = cell_r.collidepoint(mx, my) and clip_rect.collidepoint(mx, my)
            if hov:
                hs = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
                pygame.draw.rect(hs, (90, 140, 240, 150), (0, 0, CELL - 2, CELL - 2), border_radius=7)
                screen.blit(hs, (cx, cy))
            es = self._get_emoji_pick_surf(em, EM_SIZE)
            ew, eh = es.get_width(), es.get_height()
            screen.blit(es, (cx + (CELL - 2) // 2 - ew // 2, cy + (CELL - 2) // 2 - eh // 2))

        screen.set_clip(None)

        # Scrollbar verticale
        if max_scroll > 0:
            sb_x = r.x + r.w - 10
            sb_y = r.y + 6
            sb_h = r.h - 12
            pygame.draw.rect(screen, (30, 40, 80), (sb_x, sb_y, 5, sb_h), border_radius=3)
            ratio    = r.h / total_h
            thumb_h  = max(18, int(sb_h * ratio))
            thumb_y  = sb_y + int((self.picker_scroll / max_scroll) * (sb_h - thumb_h))
            pygame.draw.rect(screen, (100, 150, 255), (sb_x, thumb_y, 5, thumb_h), border_radius=3)

    def _bubble_h(self, msg):
        text  = msg.get("text", "")
        em_sz = self.font_msg.get_height()
        # Même largeur que dans draw() : aw - 20 = (PANEL_W - 20) - 20 = PANEL_W - 40
        wrap_w = min(self.PANEL_W - 40, self.BUBBLE_MAX_W - 24)
        lines = self._wrap_mixed(text, wrap_w, em_sz)
        lh    = em_sz
        return self.font_auth.get_height() + 4 + len(lines) * (lh + 2) + 14

    def _wrap_text(self, text, max_w):
        return self._wrap_mixed(text, max_w)

    def _total_content_h(self):
        total = 0
        for msg in self.messages:
            total += self._bubble_h(msg) + self.MSG_SPACING
        return total

    # ── Logique ───────────────────────────────────────────────────────────────
    def toggle(self):
        self.open = not self.open
        if self.open:
            self.target_x = 0
            self.unread   = False
            self._reload()
            self.scroll_y = 0   # aller tout en bas à l'ouverture
        else:
            self.target_x = -self.PANEL_W

    def _reload(self):
        """Recharge les messages dans un thread séparé pour ne pas bloquer pygame."""
        def _do_reload():
            try:
                msgs = _chat_load()
                new_count = len(msgs)
                if self._first_load:
                    # Premier chargement : on mémorise le nombre actuel sans marquer unread
                    self._first_load = False
                elif new_count > self.last_count and not self.open:
                    # Nouveaux messages arrivés depuis le dernier chargement
                    self.unread = True
                self.messages   = msgs
                self.last_count = new_count
            except Exception:
                pass
        threading.Thread(target=_do_reload, daemon=True).start()

    def send_message(self):
        txt = self.input_text.strip()
        if not txt:
            return
        self.input_text  = ""
        self.cursor_pos  = 0
        self.view_offset = 0
        # Mettre à jour la progression de la mission "envoyer un message"
        if self.player is not None and self.data is not None:
            try:
                s = self.player.setdefault("missions_stats", {})
                s["chat_msgs"] = s.get("chat_msgs", 0) + 1
                # Mettre à jour les missions dont le type est "chat_msgs"
                newly = []
                for mid, mtype, label, desc, goal, reward in ALL_MISSIONS.values():
                    if mtype != "chat_msgs":
                        continue
                    entry = self.player["missions"].get(mid, {"progress": 0, "claimed": False})
                    if entry["claimed"]:
                        continue
                    old_prog = entry["progress"]
                    new_prog = min(goal, s["chat_msgs"])
                    entry["progress"] = new_prog
                    self.player["missions"][mid] = entry
                    if new_prog >= goal and old_prog < goal:
                        newly.append(mid)
                save_data(self.data)
            except Exception:
                pass
        # Envoi en thread séparé pour ne pas bloquer pygame
        def _do_send():
            try:
                _chat_post(self.player_name, txt)
                self._reload()   # recharger après envoi
            except Exception:
                pass
        threading.Thread(target=_do_send, daemon=True).start()
    def _close_center(self):
        """Centre du bouton × (coordonnées écran)."""
        px = int(self.slide_x)
        py = self.panel_y
        pw = self.PANEL_W
        return px + pw - self.CLOSE_R - 10, py + self.HEADER_H // 2

    # ── Events ────────────────────────────────────────────────────────────────
    def handle_btn_click(self, event):
        """Clic sur le bouton toggle >> ou sur les boutons de la zone saisie."""
        if event.type != MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos

        # Bouton toggle >> (seulement si chat FERMÉ)
        if not self.open:
            if pygame.Rect(self.TOG_X, self.TOG_Y, self.TOG_W, self.TOG_H).collidepoint(mx, my):
                self.toggle()
                return True
            return False

        # Bouton fermer × (cercle)
        cx, cy = self._close_center()
        if math.hypot(mx - cx, my - cy) <= self.CLOSE_R + 4:
            self.picker_open = False
            self.toggle()
            return True

        px    = int(self.slide_x)
        py    = self.panel_y
        ph    = self.panel_h
        pw    = self.PANEL_W
        SEND_W   = 50
        EMOJI_W  = 36
        inp_x    = px + 8
        inp_y    = py + ph - self.INPUT_H - 6
        inp_w    = pw - 16
        inp_h    = self.INPUT_H
        field_w  = inp_w - SEND_W - EMOJI_W - 14

        # Bouton emoji
        em_btn_x = inp_x + field_w + 4
        em_btn_r = pygame.Rect(em_btn_x, inp_y + 4, EMOJI_W, inp_h - 8)
        if em_btn_r.collidepoint(mx, my):
            self.picker_open = not self.picker_open
            if self.picker_open:
                self.picker_scroll = 0
            return True

        # Clic dans le picker
        if self.picker_open:
            r, CELL, COLS, ROWS = self._picker_rect()
            if r.collidepoint(mx, my):
                col = (mx - r.x - 8) // CELL
                row = (my - r.y - 5 + self.picker_scroll) // CELL
                idx = row * COLS + col
                if 0 <= idx < len(self.EMOJI_LIST):
                    em = self.EMOJI_LIST[idx]
                    pos = self.cursor_pos
                    self.input_text = self.input_text[:pos] + em + self.input_text[pos:]
                    self.cursor_pos = pos + len(em)
                    self.input_active = True
                # Ne PAS fermer le picker → on reste dans la sélection
                return True
            else:
                # Clic hors picker = fermer picker
                self.picker_open = False

        # Bouton envoyer OK
        sx = inp_x + inp_w - SEND_W
        if pygame.Rect(sx, inp_y + 4, SEND_W, inp_h - 8).collidepoint(mx, my):
            self.send_message()
            return True

        return False

    def handle_event(self, event):
        """Consomme les events quand le panneau est ouvert."""
        if not self.open:
            return False

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            px = int(self.slide_x)
            py = self.panel_y
            pw = self.PANEL_W
            ph = self.panel_h

            # Clic admin → supprimer uniquement via la croix rouge du message
            if self.is_admin:
                del_idx = self._delete_btn_at(mx, my)
                if del_idx is not None and del_idx < len(self.messages):
                    msg = self.messages[del_idx]
                    msg_id = msg.get("_id")
                    if msg_id:
                        _chat_delete_by_id(msg_id)
                    else:
                        # Fallback : supprimer par auteur+texte si pas d'id
                        _sb_delete("chat_messages",
                            f"author=eq.{msg.get('author','')}&text=eq.{msg.get('text','')[:50]}")
                    self._reload()
                    return True

            # Clic sur le pseudo d'un message → ouvrir carte joueur
            author_idx = self._author_at(mx, my)
            if author_idx is not None:
                author_name = self.messages[author_idx].get("author", "")
                if author_name:
                    self.pending_card = author_name
                return True

            # Activer zone saisie + positionner curseur au clic
            SEND_W_  = 50
            EMOJI_W_ = 36
            inp_x_   = px + 8
            inp_y_   = py + ph - self.INPUT_H - 6
            inp_w_   = pw - 16
            field_w_ = inp_w_ - SEND_W_ - EMOJI_W_ - 14
            field_r  = pygame.Rect(inp_x_, inp_y_, field_w_, self.INPUT_H)
            if field_r.collidepoint(mx, my):
                self.input_active = True
                # Trouver la position du curseur la plus proche du clic
                rel_x = mx - inp_x_ - 8
                best_pos = len(self.input_text)
                best_dist = float('inf')
                visible_text = self.input_text[self.view_offset:]
                for i in range(len(visible_text) + 1):
                    w = self.font_inp.size(visible_text[:i])[0]
                    dist = abs(w - rel_x)
                    if dist < best_dist:
                        best_dist = dist
                        best_pos = self.view_offset + i
                self.cursor_pos = best_pos
                self.cursor_blink = 0
                return True

            # Consommer tout clic dans le panneau
            if pygame.Rect(px, py, pw, ph).collidepoint(mx, my):
                return True

        if event.type == MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            px = int(self.slide_x)
            # Si picker ouvert et souris dessus → scroller le picker
            if self.picker_open:
                r, CELL, COLS, ROWS = self._picker_rect()
                if r.collidepoint(mx, my):
                    self.picker_scroll = max(0, self.picker_scroll - event.y * CELL)
                    return True
            if px <= mx <= px + self.PANEL_W:
                self.scroll_y = max(0, self.scroll_y - event.y * 28)
                return True

        if event.type == KEYDOWN and self.input_active:
            txt = self.input_text
            pos = self.cursor_pos
            if event.key in (K_RETURN, K_KP_ENTER):
                self.send_message()
            elif event.key == K_BACKSPACE:
                if pos > 0:
                    self.input_text = txt[:pos-1] + txt[pos:]
                    self.cursor_pos = pos - 1
            elif event.key == K_DELETE:
                if pos < len(txt):
                    self.input_text = txt[:pos] + txt[pos+1:]
            elif event.key == K_LEFT:
                self.cursor_pos = max(0, pos - 1)
            elif event.key == K_RIGHT:
                self.cursor_pos = min(len(self.input_text), pos + 1)
            elif event.key == K_HOME:
                self.cursor_pos = 0
            elif event.key == K_END:
                self.cursor_pos = len(self.input_text)
            elif event.key == K_ESCAPE:
                self.input_active = False
            else:
                if event.unicode and len(txt) < self.MSG_MAX_CHARS:
                    self.input_text = txt[:pos] + event.unicode + txt[pos:]
                    self.cursor_pos = pos + 1
            self.cursor_blink = 0   # réinitialiser clignotement à chaque frappe
            return True

        return False

    def _msg_positions(self):
        """Retourne [(i, top, bh, msg), ...] pour tous les messages visibles."""
        ay    = self.area_y
        ah    = self.area_h
        total = self._total_content_h()
        draw_y = (ay + ah - total) if total < ah else (ay - (total - ah) + self.scroll_y)
        result = []
        for i, msg in enumerate(self.messages):
            bh  = self._bubble_h(msg)
            top = draw_y
            draw_y += bh + self.MSG_SPACING
            result.append((i, top, bh, msg))
        return result

    def _delete_btn_at(self, mx, my):
        """Index du message dont la croix admin est sous la souris."""
        px = int(self.slide_x)
        ax = px + 10
        aw = self.PANEL_W - 20
        ay = self.area_y
        ah = self.area_h
        DR = 8
        for i, top, bh, msg in self._msg_positions():
            if top + bh < ay or top > ay + ah:
                continue
            dcx = ax + aw - DR - 2
            dcy = int(top) + DR + 4
            if math.hypot(mx - dcx, my - dcy) <= DR + 3:
                return i
        return None

    def _author_at(self, mx, my):
        """Index du message dont l'auteur (pseudo) est sous la souris."""
        px = int(self.slide_x)
        ax = px + 10
        aw = self.PANEL_W - 20
        ay = self.area_y
        ah = self.area_h
        for i, top, bh, msg in self._msg_positions():
            if top + bh < ay or top > ay + ah:
                continue
            is_me = (msg.get("author", "") == self.player_name)
            auth_str = get_display_name(msg.get("author", "?")) + "  " + msg.get("ts", "")
            auth_w = self.font_auth.size(auth_str)[0]
            auth_h = self.font_auth.get_height()
            bw_msg = min(self.BUBBLE_MAX_W, auth_w + 16 + 16)
            bx = ax + aw - bw_msg if is_me else ax
            auth_rect = pygame.Rect(bx + 8, int(top) + 6, auth_w, auth_h)
            if auth_rect.collidepoint(mx, my):
                return i
        return None

    def _msg_at(self, mx, my):
        """Index du message sous la souris."""
        px  = int(self.slide_x)
        ay  = self.area_y
        ah  = self.area_h
        pw  = self.PANEL_W
        for i, top, bh, msg in self._msg_positions():
            if top + bh < ay or top > ay + ah:
                continue
            if px <= mx <= px + pw and top <= my <= top + bh:
                return i
        return None

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self):
        self.cursor_blink += 1
        diff = self.target_x - self.slide_x
        if abs(diff) > 0.5:
            self.slide_x += diff * 0.22
        else:
            self.slide_x = self.target_x
        self.poll_timer += 1
        if self.poll_timer >= self.POLL_INTERVAL:
            self.poll_timer = 0
            self._reload()

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        self.update()
        mx, my = pygame.mouse.get_pos()

        # ── Bouton toggle >> — masqué si chat ouvert (ou en train de s'ouvrir) ─
        if self.slide_x <= -self.PANEL_W + 2:
            # Panneau hors écran → afficher le bouton >>
            hov = pygame.Rect(self.TOG_X, self.TOG_Y, self.TOG_W, self.TOG_H).collidepoint(mx, my)
            bs  = pygame.Surface((self.TOG_W, self.TOG_H), pygame.SRCALPHA)
            bg  = (60, 120, 220, 220) if hov else (30, 60, 130, 190)
            pygame.draw.rect(bs, bg, (0, 0, self.TOG_W, self.TOG_H), border_radius=10)
            pygame.draw.rect(bs, (100, 160, 255, 200), (0, 0, self.TOG_W, self.TOG_H), 2, border_radius=10)
            lbl = self.font_btn.render(">>", True, (255, 255, 255))
            bs.blit(lbl, (self.TOG_W//2 - lbl.get_width()//2, self.TOG_H//2 - lbl.get_height()//2))
            screen.blit(bs, (self.TOG_X, self.TOG_Y))
            # Point rouge
            if self.unread:
                pygame.draw.circle(screen, (230, 50, 50),   (self.TOG_X + self.TOG_W - 2, self.TOG_Y + 2), 7)
                pygame.draw.circle(screen, (255, 130, 130), (self.TOG_X + self.TOG_W - 2, self.TOG_Y + 2), 7, 2)
            return   # panneau pas visible, stop

        px = int(self.slide_x)
        py = self.panel_y
        pw = self.PANEL_W
        ph = self.panel_h

        # ── Fond panneau ─────────────────────────────────────────────────────
        ps = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(ps, (8, 12, 30, 240),    (0, 0, pw, ph), border_radius=18)
        pygame.draw.rect(ps, (60, 110, 220, 180), (0, 0, pw, ph), 2, border_radius=18)
        shine = pygame.Surface((pw - 8, ph // 6), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 10), (0, 0, pw - 8, ph // 6), border_radius=18)
        ps.blit(shine, (4, 4))
        screen.blit(ps, (px, py))

        # ── Header ───────────────────────────────────────────────────────────
        hdr_s = self.font_btn.render("CHAT", True, (140, 195, 255))
        screen.blit(hdr_s, (px + 16, py + self.HEADER_H // 2 - hdr_s.get_height() // 2))

        # Bouton fermer × (cercle)
        cx, cy = self._close_center()
        hov_cl = math.hypot(mx - cx, my - cy) <= self.CLOSE_R + 4
        cl_col = (220, 70, 70) if hov_cl else (140, 40, 40)
        pygame.draw.circle(screen, cl_col, (cx, cy), self.CLOSE_R)
        pygame.draw.circle(screen, (255, 130, 130), (cx, cy), self.CLOSE_R, 2)
        # Croix dessinée avec des lignes (pas de caractère unicode)
        off = 5
        pygame.draw.line(screen, (255, 255, 255), (cx - off, cy - off), (cx + off, cy + off), 2)
        pygame.draw.line(screen, (255, 255, 255), (cx + off, cy - off), (cx - off, cy + off), 2)

        # Séparateur header
        pygame.draw.line(screen, (60, 110, 220, 140),
                         (px + 10, py + self.HEADER_H), (px + pw - 10, py + self.HEADER_H), 1)

        # ── Zone messages ─────────────────────────────────────────────────────
        ay  = self.area_y
        ah  = self.area_h
        ax  = px + 10
        aw  = pw - 20

        screen.set_clip(pygame.Rect(ax, ay, aw, ah))

        total_h = self._total_content_h()
        # Clamp scroll
        max_scroll = max(0, total_h - ah)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        # draw_y : position du 1er message
        if total_h <= ah:
            # Peu de messages → les coller en bas
            draw_y = ay + ah - total_h
        else:
            draw_y = ay - (total_h - ah) + self.scroll_y

        for i, msg in enumerate(self.messages):
            is_me  = (msg.get("author", "") == self.player_name)
            bh     = self._bubble_h(msg)
            top    = draw_y
            draw_y += bh + self.MSG_SPACING

            if top + bh < ay:
                continue
            if top > ay + ah:
                break

            text   = msg.get("text", "")
            ts     = msg.get("ts", "")
            author = get_display_name(msg.get("author", "?"))
            # Wrap limité à BUBBLE_MAX_W - padding pour ne pas déborder de la bulle
            WRAP_W = min(aw - 20, self.BUBBLE_MAX_W - 24)
            lines  = self._wrap_mixed(text, WRAP_W)

            # Largeur de bulle = min(BUBBLE_MAX_W, contenu + padding)
            max_line_w = max((self._text_width_mixed(l, self.font_msg, self.font_msg.get_height()) for l in lines), default=40)
            auth_w     = self.font_auth.size(f"{author}  {ts}")[0]
            bw         = min(self.BUBBLE_MAX_W, max(max_line_w, auth_w) + 24)

            # Alignement : moi → droite, autres → gauche
            if is_me:
                bx = ax + aw - bw
                bubble_col = (35, 75, 155, 215)
                border_col = (90, 155, 255, 200)
                auth_col   = (140, 195, 255)
                txt_col    = (225, 235, 255)
            else:
                bx = ax
                bubble_col = (22, 30, 55, 215)
                border_col = (70, 90, 140, 180)
                auth_col   = (170, 175, 210)
                txt_col    = (215, 220, 245)

            # Fond bulle
            bs = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(bs, bubble_col, (0, 0, bw, bh), border_radius=12)
            pygame.draw.rect(bs, border_col, (0, 0, bw, bh), 1, border_radius=12)
            screen.blit(bs, (bx, int(top)))

            # Auteur + heure (cliquable → carte joueur)
            auth_str = f"{author}  {ts}"
            a_s = self.font_auth.render(auth_str, True, auth_col)
            auth_rect = pygame.Rect(bx + 8, int(top) + 6, a_s.get_width(), a_s.get_height())
            # Soulignement au survol
            if auth_rect.collidepoint(mx, my):
                pygame.draw.line(screen, auth_col,
                    (auth_rect.x, auth_rect.bottom),
                    (auth_rect.x + a_s.get_width(), auth_rect.bottom), 1)
            screen.blit(a_s, (bx + 8, int(top) + 6))

            # Lignes de texte avec emojis
            lh_em = self.font_msg.get_height()
            ty = int(top) + 6 + self.font_auth.get_height() + 4
            for ln in lines:
                ls = self._render_mixed(ln, self.font_msg, self.font_msg.get_height(), txt_col)
                screen.blit(ls, (bx + 8, ty))
                ty += lh_em + 2

            # Bouton supprimer admin — croix rouge en haut à droite de la bulle
            if self.is_admin:
                DR = 8
                dcx = ax + aw - DR - 2
                dcy = int(top) + DR + 4
                hov_del = math.hypot(mx - dcx, my - dcy) <= DR + 3
                del_col = (240, 60, 60) if hov_del else (180, 45, 45)
                pygame.draw.circle(screen, del_col, (dcx, dcy), DR)
                pygame.draw.circle(screen, (255, 130, 130), (dcx, dcy), DR, 1)
                off = 4
                pygame.draw.line(screen, (255, 220, 220), (dcx - off, dcy - off), (dcx + off, dcy + off), 2)
                pygame.draw.line(screen, (255, 220, 220), (dcx + off, dcy - off), (dcx - off, dcy + off), 2)

        screen.set_clip(None)

        # Séparateur input
        sep_y = py + ph - self.INPUT_H - 12
        pygame.draw.line(screen, (60, 110, 220, 120),
                         (px + 10, sep_y), (px + pw - 10, sep_y), 1)

        # ── Zone saisie ───────────────────────────────────────────────────────
        SEND_W   = 50
        EMOJI_W  = 36   # bouton emoji
        inp_x    = px + 8
        inp_y    = py + ph - self.INPUT_H - 6
        inp_w    = pw - 16
        inp_h    = self.INPUT_H
        # Disposition : [champ texte][btn emoji][btn OK]
        field_w  = inp_w - SEND_W - EMOJI_W - 14

        # Fond champ texte
        fc = (22, 38, 78, 225) if self.input_active else (14, 22, 50, 205)
        fb = (90, 155, 255)    if self.input_active else (55, 85, 150)
        fs = pygame.Surface((field_w, inp_h), pygame.SRCALPHA)
        pygame.draw.rect(fs, fc, (0, 0, field_w, inp_h), border_radius=10)
        pygame.draw.rect(fs, (*fb, 220), (0, 0, field_w, inp_h), 2, border_radius=10)
        screen.blit(fs, (inp_x, inp_y))

        # Texte / placeholder avec emojis
        max_tw = field_w - 14
        if self.input_text:
            txt_col2 = (220, 235, 255)
            # Calculer view_offset pour que le curseur reste visible
            # S'assurer que cursor_pos est dans les bornes
            self.cursor_pos = max(0, min(self.cursor_pos, len(self.input_text)))
            # Avancer view_offset si curseur sort à droite
            while True:
                visible = self.input_text[self.view_offset:self.cursor_pos]
                if self.font_inp.size(visible)[0] <= max_tw - 4:
                    break
                self.view_offset += 1
            # Reculer view_offset si curseur sort à gauche
            if self.cursor_pos < self.view_offset:
                self.view_offset = self.cursor_pos
            # Afficher le texte à partir de view_offset, tronqué à max_tw
            display_text = self.input_text[self.view_offset:]
            # Couper si le texte affiché est trop long
            for cut in range(len(display_text) + 1):
                if self.font_inp.size(display_text[:cut])[0] > max_tw:
                    display_text = display_text[:cut - 1]
                    break
            rendered = self._render_mixed(display_text, self.font_inp, self.font_inp.get_height(), txt_col2)
        else:
            self.view_offset = 0
            txt_col2 = (100, 115, 150)
            rendered = self.font_inp.render("Message...", True, txt_col2)
        screen.blit(rendered, (inp_x + 8, inp_y + inp_h // 2 - rendered.get_height() // 2))

        # Curseur à la bonne position
        if self.input_active and (self.cursor_blink // 45) % 2 == 0:
            cursor_text = self.input_text[self.view_offset:self.cursor_pos]
            cur_w = self.font_inp.size(cursor_text)[0]
            cur_x = inp_x + 8 + min(cur_w, max_tw)
            pygame.draw.line(screen, (160, 210, 255),
                             (cur_x, inp_y + 6), (cur_x, inp_y + inp_h - 6), 2)

        # Bouton emoji 😊
        em_btn_x = inp_x + field_w + 4
        em_btn_r = pygame.Rect(em_btn_x, inp_y + 4, EMOJI_W, inp_h - 8)
        hov_em   = em_btn_r.collidepoint(mx, my)
        em_bg    = (60, 100, 200, 180) if (hov_em or self.picker_open) else (35, 55, 120, 160)
        em_s     = pygame.Surface((EMOJI_W, inp_h - 8), pygame.SRCALPHA)
        pygame.draw.rect(em_s, em_bg, (0, 0, EMOJI_W, inp_h - 8), border_radius=8)
        if self.picker_open:
            pygame.draw.rect(em_s, (100, 160, 255, 200), (0, 0, EMOJI_W, inp_h - 8), 2, border_radius=8)
        # Icone smiley dessinee (si emoji font dispo, utiliser emoji sinon dessin)
        try:
            icon_size = inp_h - 16
            em_icon = self._emoji_to_surf("😊", icon_size)
            ew, eh = em_icon.get_width(), em_icon.get_height()
            em_s.blit(em_icon, (EMOJI_W // 2 - ew // 2, (inp_h - 8) // 2 - eh // 2))
        except Exception:
            # Fallback: cercle jaune simple
            pygame.draw.circle(em_s, (255, 210, 60), (EMOJI_W // 2, (inp_h - 8) // 2), 10)
        screen.blit(em_s, em_btn_r.topleft)

        # Bouton envoyer OK
        sx      = inp_x + inp_w - SEND_W
        sy      = inp_y
        hov_snd = pygame.Rect(sx, sy + 4, SEND_W, inp_h - 8).collidepoint(mx, my)
        sd_col  = (70, 165, 70, 225) if hov_snd else (45, 115, 45, 200)
        sd_s    = pygame.Surface((SEND_W, inp_h - 8), pygame.SRCALPHA)
        pygame.draw.rect(sd_s, sd_col, (0, 0, SEND_W, inp_h - 8), border_radius=9)
        sl      = self.font_btn.render("OK", True, (210, 255, 210))
        sd_s.blit(sl, (SEND_W // 2 - sl.get_width() // 2, (inp_h - 8) // 2 - sl.get_height() // 2))
        screen.blit(sd_s, (sx, sy + 4))

        # Compteur de caractères (affiché au-dessus du champ si proche limite)
        char_count = len(self.input_text)
        remaining  = self.MSG_MAX_CHARS - char_count
        if char_count > 0:
            if remaining <= 20:
                cnt_col = (255, 80, 80) if remaining <= 5 else (255, 180, 60)
            else:
                cnt_col = (120, 130, 160)
            cnt_s = self.font_auth.render(f"{char_count}/{self.MSG_MAX_CHARS}", True, cnt_col)
            screen.blit(cnt_s, (inp_x + field_w - cnt_s.get_width(), inp_y - cnt_s.get_height() - 2))

        # Picker emoji (par dessus tout le reste)
        if self.picker_open:
            self._draw_picker(mx, my)


def main_menu(data, player, selected_skin, selected_bg=None, selected_music=None, selected_music_menu=None):
    t = 0.0
    dropdown_open  = False
    tryhard_panel_open = False   # sous-panel tryharder dans le dropdown

    # ── Bandeau défilant ──────────────────────────────────────────────────────
    _banner_cfg     = get_banner_config(data)
    _banner_enabled = _banner_cfg["enabled"]
    _banner_msg     = _banner_cfg["message"]
    _banner_last_check = time.time()   # pour rechargement périodique
    _banner_x       = float(SCREEN_WIDTH)   # position X courante du texte
    _BANNER_H       = 28                    # hauteur du bandeau en pixels
    _BANNER_SPEED   = 1.8                   # pixels par frame
    _banner_surf    = None                  # surface pré-rendue du texte (recalcul si msg change)
    _banner_unit_w  = 1                     # largeur d'une unité de répétition
    _banner_closed  = False                 # True = fermé par le joueur pour cette session

    # ── Options Tryharder (lues depuis player, avec défauts) ─────────────────
    def _th_get():
        return player.get("tryharder_opts", {})
    def _th_set(key, val):
        if "tryharder_opts" not in player:
            player["tryharder_opts"] = {}
        player["tryharder_opts"][key] = val
        save_data_async(data)

    TRYHARD_OPTIONS = [
        ("hitbox_pipes",  "Hitbox tuyaux",       "Affiche les rectangles de collision des tuyaux"),
        ("hitbox_player", "Hitbox joueur",        "Affiche le rectangle de collision du personnage"),
        ("vector",        "Vecteur direction",    "Trait indiquant la trajectoire exacte"),
        ("fps",           "Compteur FPS",         "Affiche les FPS en temps réel"),
        ("gamespeed",     "Vitesse du jeu",       "Affiche la game_speed actuelle"),
        ("hitbox_coins",  "Hitbox des pièces",    "Affiche les rectangles de collision des pièces"),
    ]
    coin_anim_t    = 0
    lb_click_rects = []   # [(rect, player_dict), ...] — rempli chaque frame

    # ── Chat overlay (instance globale) ──────────────────────────────────────
    # _GLOBAL_CHAT est initialisé dans main() avant d'appeler main_menu

    LB_X    = SCREEN_WIDTH * 0.18
    LB_W    = 400
    LB_ROW_H = 48
    CX      = SCREEN_WIDTH // 2

    # --- Tailles des hitboxes (indépendantes de la taille des images) ---
    PLAY_W, PLAY_H = 340, 90
    SHOP_W, SHOP_H = 320, 80
    # Missions et Niveaux côte à côte sur la même ligne
    MISS_W, MISS_H = 330, 95   # agrandi (MISS_W controle la largeur visuelle de l image)
    LVL_W,  LVL_H  = 220, 65
    PAIR_GAP = 8     # espace entre les deux boutons

    # Espacement vertical entre les boutons
    PLAY_Y = SCREEN_HEIGHT // 2 - 10
    SHOP_Y = PLAY_Y + 105
    PAIR_Y = SHOP_Y + 94   # ligne Missions + Niveaux
    MISS_Y = PAIR_Y
    LVL_Y  = PAIR_Y
    # Centrer les deux boutons ensemble autour de CX
    _total_pair_w = MISS_W + PAIR_GAP + LVL_W
    MISS_X = CX - _total_pair_w // 2 + MISS_W // 2
    LVL_X  = CX + _total_pair_w // 2 - LVL_W // 2

    # Position du bloc de mission (Placé BIEN AU-DESSUS du bouton JOUER)
    MISS_BLOCK_Y = PLAY_Y - 185

    AV_R, AV_X, AV_Y = 32, SCREEN_WIDTH - 60, 50
    DD_W, DD_H_item   = 220, 55

    # ── Sélecteurs Skin + Background : bas au centre, côte à côte ──
    SEL_CY      = SCREEN_HEIGHT - 80          # rangée du bas (centre vertical)
    SEL_OFFSET  = SCREEN_WIDTH // 5           # espacement horizontal conservé
    SKIN_CX     = CX - SEL_OFFSET // 2        # légèrement à gauche du centre
    BG_SEL_CX   = CX + SEL_OFFSET // 2        # légèrement à droite du centre

    # ── Sélecteurs Audio : milieu droit, alignés verticalement ──
    AUDIO_X         = SCREEN_WIDTH - SCREEN_WIDTH // 7   # colonne droite
    AUDIO_MENU_CY   = SCREEN_HEIGHT // 2 - 100           # musique menu au-dessus
    AUDIO_GAME_CY   = SCREEN_HEIGHT // 2 + 100           # musique jeu en-dessous

    owned = player.get("owned_skins", ["Flappy"])
    skin_idx = owned.index(selected_skin) if selected_skin in owned else 0

    # Backgrounds possédés (None = fond par défaut)
    owned_bgs  = [None] + player.get("owned_backgrounds", [])
    # Restaure l'index du fond sélectionné précédemment
    if selected_bg in owned_bgs:
        bg_idx = owned_bgs.index(selected_bg)
    else:
        bg_idx = 0

    # Musiques disponibles :
    # None                   = Défaut selon contexte (menu_music pour menu, background_music pour jeu)
    # _MUSIC_KEY_DEFAULT_MENU = musique menu utilisée dans le jeu
    # _MUSIC_KEY_DEFAULT_GAME = musique jeu utilisée dans le menu
    # + les musiques achetées
    _base_musics = [None, _MUSIC_KEY_DEFAULT_MENU, _MUSIC_KEY_DEFAULT_GAME]
    owned_musics = _base_musics + player.get("owned_musics", [])
    # Restaure l'index de la musique de JEU sélectionnée
    if selected_music in owned_musics:
        music_idx = owned_musics.index(selected_music)
    else:
        music_idx = 0
    # Restaure l'index de la musique de MENU sélectionnée
    if selected_music_menu in owned_musics:
        music_menu_idx = owned_musics.index(selected_music_menu)
    else:
        music_menu_idx = 0

    ARR_R    = 22
    ARR_OFFX = 90
    # Timers d'animation flèche cliquée {clé: frames_restantes}
    _arrow_anim = {}   # clé = ("skin","left"), ("skin","right"), ("bg",...), etc.

    _is_admin_user = (player.get("name", "") in ADMIN_USERS)
    DD_ITEMS = ["Mon Profil", "Pseudo", "Préférences", "Tryharder", "Signaler un bug", "Crédits"]
    if _is_admin_user:
        DD_ITEMS = ["Mon Profil", "Pseudo", "Préférences", "Tryharder", "Signaler un bug", "Crédits", "Administration"]

    # ── Animations hover boutons (scale smooth + glow) ──
    btn_scales = {"play": 1.0, "shop": 1.0, "miss": 1.0, "lvl": 1.0}
    BTN_SCALE_MAX  = 1.07
    BTN_SCALE_STEP = 0.025

    # ── Cache des surfaces pré-calculées pour éviter smoothscale à chaque frame ──
    PLAY_W_BASE = int(PLAY_BTN_IMG.get_width() * 1.5)
    PLAY_H_BASE = int(PLAY_BTN_IMG.get_height() * 1.5)
    SHOP_W_BASE = int(SHOP_BTN_IMG.get_width() * 1.4)
    SHOP_H_BASE = int(SHOP_BTN_IMG.get_height() * 1.4)
    MISS_W_BASE = int(MISS_BTN_IMG.get_width() * 1.90)
    MISS_H_BASE = int(MISS_BTN_IMG.get_height() * 1.90)
    LVL_W_BASE  = int(LEVEL_BTN_IMG.get_width() * 1.90)
    LVL_H_BASE  = int(LEVEL_BTN_IMG.get_height() * 1.90)

    _btn_cache = {}  # (key, w, h) -> surface
    def _get_btn_img(img, key, sc):
        w = max(int(img.get_width()  * sc), 4)
        h = max(int(img.get_height() * sc), 4)
        k = (key, w, h)
        if k not in _btn_cache:
            _btn_cache[k] = pygame.transform.scale(img, (w, h))
        return _btn_cache[k]

    PREV_W, PREV_H = 100, 62
    _bg_preview_cache = {}  # bg_key -> surface (100x62)
    def _get_bg_preview(bg_key):
        if bg_key not in _bg_preview_cache:
            raw = BG_PREVIEW_IMAGES.get(bg_key)
            if raw:
                _bg_preview_cache[bg_key] = pygame.transform.scale(raw, (PREV_W, PREV_H))
            else:
                try:
                    _raw = _pygame_load('assets/sprites/background-day.png').convert()
                    _bg_preview_cache[bg_key] = pygame.transform.scale(_raw, (PREV_W, PREV_H))
                except Exception:
                    _bg_preview_cache[bg_key] = pygame.transform.scale(BACKGROUND, (PREV_W, PREV_H))
        return _bg_preview_cache[bg_key]

    _skin_preview_cache = {}  # skin_key -> surface (max 62x62)
    def _get_skin_preview(skin_key):
        if skin_key not in _skin_preview_cache:
            raw = skin_images[skin_key]
            max_dim = 62
            sf = min(max_dim / raw.get_width(), max_dim / raw.get_height())
            _skin_preview_cache[skin_key] = pygame.transform.smoothscale(
                raw, (int(raw.get_width() * sf), int(raw.get_height() * sf)))
        return _skin_preview_cache[skin_key]

    # ── Pré-allocation des surfaces de badges (évite 4 new Surface() par frame) ──
    _badge_w, _badge_h = 230, 52
    _badge_surf   = pygame.Surface((_badge_w, _badge_h), pygame.SRCALPHA)
    _shine_bs     = pygame.Surface((_badge_w - 6, _badge_h // 2 - 2), pygame.SRCALPHA)
    pygame.draw.rect(_shine_bs, (255, 255, 255, 16), (0, 0, _badge_w - 6, _badge_h // 2 - 2), border_radius=26)
    _badge_mission_w = 300
    _badge_mission_surf = pygame.Surface((_badge_mission_w, _badge_h), pygame.SRCALPHA)
    _shine_mc     = pygame.Surface((_badge_mission_w - 6, _badge_h // 2 - 2), pygame.SRCALPHA)
    pygame.draw.rect(_shine_mc, (255, 255, 255, 14), (0, 0, _badge_mission_w - 6, _badge_h // 2 - 2), border_radius=26)
    # Titres menu pré-rendus
    _title_shadow = font_big.render("FLAPPY BIRD", True, (10, 10, 10))
    _title_surf   = font_big.render("FLAPPY BIRD", True, GOLD)
    _head_surf    = font_small.render("CLASSEMENT", True, GOLD)
    _head_sh      = font_small.render("CLASSEMENT", True, (0, 0, 0))
    _mc_lbl_surf  = font_tiny.render("Pièce mission", True, (100, 160, 200))
    # Cache pièces/mission coins pour éviter re-render si valeur inchangée
    _last_total_coins = -1;  _ct_surf_cache = None
    _last_mc_val      = -1;  _mc_surf_cache = None

    while True:
        dt = clock.tick(FPS) / 1000.0  # secondes réelles écoulées
        dt = min(dt, 0.05)             # plafonner à 50ms pour éviter les sauts
        t += dt * 2.4                  # vitesse équivalente à l'ancien += 0.04 @ 60fps
        coin_anim_t += 1
        mx, my = pygame.mouse.get_pos()
        current_skin = owned[skin_idx]

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == _MUSIC_END_EVENT:
                handle_music_end_event(player)

            # ── Bouton chat >> (priorité haute) ──────────────────────────────
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # ── Bouton fermer bandeau ─────────────────────────────────
                if _banner_enabled and _banner_msg and not _banner_closed:
                    _close_r = pygame.Rect(SCREEN_WIDTH - 28, 0, 28, 28)
                    if _close_r.collidepoint(event.pos):
                        _banner_closed = True
                        continue
                if math.hypot(mx - AV_X, my - AV_Y) <= AV_R + 8:
                    dropdown_open = not dropdown_open
                    if not dropdown_open:
                        tryhard_panel_open = False
                elif dropdown_open:
                    dd_x = AV_X - DD_W + AV_R
                    # ── Clic dans le sous-panel tryharder ────────────────────
                    if tryhard_panel_open:
                        th_panel_x = dd_x - 270
                        th_panel_y = (AV_Y + AV_R + 20) + 2 * (DD_H_item + 5)
                        th_panel_w = 260
                        th_row_h   = 42
                        for j, (opt_key, opt_label, _) in enumerate(TRYHARD_OPTIONS):
                            ry = th_panel_y + 12 + j * th_row_h
                            cb_r = pygame.Rect(th_panel_x + 14, ry + 9, 22, 22)
                            row_r = pygame.Rect(th_panel_x + 4, ry, th_panel_w - 8, th_row_h)
                            if cb_r.collidepoint(event.pos) or row_r.collidepoint(event.pos):
                                cur = _th_get().get(opt_key, False)
                                _th_set(opt_key, not cur)
                        # Clic à l'extérieur du sous-panel → ferme tout
                        panel_rect = pygame.Rect(th_panel_x, th_panel_y, th_panel_w,
                                                 12 + len(TRYHARD_OPTIONS) * th_row_h + 12)
                        dd_rect = pygame.Rect(dd_x, AV_Y + AV_R + 20,
                                              DD_W, len(DD_ITEMS) * (DD_H_item + 5))
                        if not panel_rect.collidepoint(event.pos) and not dd_rect.collidepoint(event.pos):
                            tryhard_panel_open = False
                            dropdown_open = False
                    else:
                        for i, item in enumerate(DD_ITEMS):
                            iy = (AV_Y + AV_R + 20) + i * (DD_H_item + 5)
                            if dd_x <= mx <= dd_x + DD_W and iy <= my <= iy + DD_H_item:
                                dropdown_open = False
                                tryhard_panel_open = False
                                if item == "Mon Profil":
                                    return ('profile', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                                if item == "Pseudo":
                                    return ('pseudo', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                                if item == "Préférences":
                                    return ('settings', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                                if item == "Tryharder":
                                    dropdown_open = True
                                    tryhard_panel_open = True
                                if item == "Signaler un bug":
                                    return ('bugreport', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                                if item == "Crédits":
                                    return ('credits', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                                if item == "Administration" and _is_admin_user:
                                    return ('admin', player), current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                        if not tryhard_panel_open:
                            dropdown_open = False
                else:
                    if btn_clicked(event, CX, PLAY_Y, PLAY_W, PLAY_H):
                        return 'play', current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                    if btn_clicked(event, CX, SHOP_Y, SHOP_W, SHOP_H):
                        return 'shop', current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                    if btn_clicked(event, MISS_X, MISS_Y, MISS_W, MISS_H):
                        return 'missions', current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]
                    if btn_clicked(event, LVL_X, LVL_Y, LVL_W, LVL_H):
                        return 'levels', current_skin, owned_bgs[bg_idx], owned_musics[music_idx], owned_musics[music_menu_idx]

                    # Clic sur un joueur du classement → carte joueur
                    for rect, lb_p in lb_click_rects:
                        if rect.collidepoint(event.pos):
                            player_card_popup(lb_p)
                            break
                    
                    # Logique de réclamer (Coordonnées du bouton alignées sur le dessin)
                    _am = []
                    for _mid, _mtype, _lbl, _desc, _goal, _rew in MISSIONS_DAILY + MISSIONS_ONETIME + MISSIONS_PERMANENT:
                        _ent = player["missions"].get(_mid, {"progress": 0, "claimed": False})
                        if not _ent["claimed"]:
                            _am.append((_mid, _lbl, _desc, _goal, _rew, _ent["progress"]))
                    _am.sort(key=lambda x: (-(x[5] >= x[3]), -x[5]/max(1, x[3])))
                    
                    if _am:
                        _top_mid, _, _, _top_goal, _top_rew, _top_prog = _am[0]
                        if _top_prog >= _top_goal:
                            # Zone de clic corrigée pour correspondre au texte "À RÉCLAMER"
                            _rect_claim = pygame.Rect(CX + 25, MISS_BLOCK_Y, 120, 30)
                            if _rect_claim.collidepoint(event.pos):
                                claim_mission(player, _top_mid, data)

                    if len(owned) > 1:
                        if math.hypot(mx - (SKIN_CX - ARR_OFFX), my - SEL_CY) <= ARR_R + 6:
                            skin_idx = (skin_idx - 1) % len(owned)
                            player["selected_skin"] = owned[skin_idx]; save_player_async(player)
                            _arrow_anim[("skin","left")] = 12
                        elif math.hypot(mx - (SKIN_CX + ARR_OFFX), my - SEL_CY) <= ARR_R + 6:
                            skin_idx = (skin_idx + 1) % len(owned)
                            player["selected_skin"] = owned[skin_idx]; save_player_async(player)
                            _arrow_anim[("skin","right")] = 12

                    if len(owned_bgs) > 1:
                        changed = False
                        if math.hypot(mx - (BG_SEL_CX - ARR_OFFX), my - SEL_CY) <= ARR_R + 6:
                            bg_idx = (bg_idx - 1) % len(owned_bgs)
                            changed = True
                            _arrow_anim[("bg","left")] = 12
                        elif math.hypot(mx - (BG_SEL_CX + ARR_OFFX), my - SEL_CY) <= ARR_R + 6:
                            bg_idx = (bg_idx + 1) % len(owned_bgs)
                            changed = True
                            _arrow_anim[("bg","right")] = 12
                        if changed:
                            global BACKGROUND
                            new_bg_key = owned_bgs[bg_idx]
                            if new_bg_key is not None and new_bg_key in BG_PREVIEW_IMAGES and BG_PREVIEW_IMAGES[new_bg_key]:
                                BACKGROUND = BG_PREVIEW_IMAGES[new_bg_key]
                            else:
                                BACKGROUND = pygame.transform.scale(
                                    _pygame_load('assets/sprites/background-day.png').convert(),
                                    (SCREEN_WIDTH, SCREEN_HEIGHT))
                            player["selected_bg"] = new_bg_key; save_player_async(player)

                    if len(owned_musics) > 1:
                        # Sélecteur musique JEU
                        if math.hypot(mx - (AUDIO_X - ARR_OFFX), my - AUDIO_GAME_CY) <= ARR_R + 6:
                            music_idx = (music_idx - 1) % len(owned_musics)
                            player["selected_music"] = owned_musics[music_idx]; save_player_async(player)
                            _arrow_anim[("mgame","left")] = 12
                        elif math.hypot(mx - (AUDIO_X + ARR_OFFX), my - AUDIO_GAME_CY) <= ARR_R + 6:
                            music_idx = (music_idx + 1) % len(owned_musics)
                            player["selected_music"] = owned_musics[music_idx]; save_player_async(player)
                            _arrow_anim[("mgame","right")] = 12

                        # Sélecteur musique MENU
                        changed_menu = False
                        if math.hypot(mx - (AUDIO_X - ARR_OFFX), my - AUDIO_MENU_CY) <= ARR_R + 6:
                            music_menu_idx = (music_menu_idx - 1) % len(owned_musics)
                            changed_menu = True
                            _arrow_anim[("mmenu","left")] = 12
                        elif math.hypot(mx - (AUDIO_X + ARR_OFFX), my - AUDIO_MENU_CY) <= ARR_R + 6:
                            music_menu_idx = (music_menu_idx + 1) % len(owned_musics)
                            changed_menu = True
                            _arrow_anim[("mmenu","right")] = 12
                        if changed_menu:
                            new_menu_key = owned_musics[music_menu_idx]
                            new_menu_file = _resolve_music_file(new_menu_key)
                            play_menu_music(new_menu_file)
                            player["selected_music_menu"] = new_menu_key; save_player_async(player)

        # ── Mise à jour animation scale boutons ──
        for key, (cx, cy, w, h) in [("play", (CX, PLAY_Y, PLAY_W, PLAY_H)),
                                     ("shop", (CX, SHOP_Y, SHOP_W, SHOP_H)),
                                     ("miss", (MISS_X, MISS_Y, MISS_W, MISS_H)),
                                     ("lvl",  (LVL_X,  LVL_Y,  LVL_W,  LVL_H))]:
            target = BTN_SCALE_MAX if is_hov(cx, cy, w, h) else 1.0
            diff = target - btn_scales[key]
            btn_scales[key] += diff * 0.18
        # Décrémenter timers animation flèches
        for k in list(_arrow_anim.keys()):
            _arrow_anim[k] = max(0, _arrow_anim[k] - 1)

        # ── DESSIN ──────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(150)

        # 1. TITRE (pré-rendu, pas de new Surface)
        title_y = 70 + int(math.sin(t * 1.2) * 6)
        tr = _title_surf.get_rect(center=(CX, title_y))
        screen.blit(_title_shadow, (tr.x + 4, tr.y + 4))
        screen.blit(_title_surf, tr)

        # 2. BADGES PIÈCES (surfaces pré-allouées, fill+draw à la place de new Surface)
        coins_y = title_y + 68
        total_coins = player.get("total_coins", 0)
        # Badge Jaune — pièces
        _badge_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(_badge_surf, (10, 10, 20, 210), (0, 0, _badge_w, _badge_h), border_radius=26)
        pygame.draw.rect(_badge_surf, (*GOLD, 200), (0, 0, _badge_w, _badge_h), width=2, border_radius=26)
        _badge_surf.blit(_shine_bs, (3, 3))
        screen.blit(_badge_surf, (CX - _badge_w - 8, coins_y - _badge_h // 2))
        cf = COIN_FRAMES_44[(coin_anim_t // 4) % len(COIN_FRAMES_44)]
        screen.blit(cf, (CX - _badge_w - 8 + 10, coins_y - cf.get_height() // 2))
        if total_coins != _last_total_coins:
            _last_total_coins = total_coins
            _ct_surf_cache = font_med.render(f"{total_coins} pièces", True, GOLD)
        screen.blit(_ct_surf_cache, (CX - _badge_w - 8 + 10 + cf.get_width() + 8, coins_y - _ct_surf_cache.get_height() // 2))

        # Badge Bleu — Pièce mission
        mc_val = player.get("mission_coins", 0)
        _badge_mission_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(_badge_mission_surf, (6, 14, 30, 210), (0, 0, _badge_mission_w, _badge_h), border_radius=26)
        pygame.draw.rect(_badge_mission_surf, (*MISSION_COIN_COLOR, 200), (0, 0, _badge_mission_w, _badge_h), width=2, border_radius=26)
        _badge_mission_surf.blit(_shine_mc, (3, 3))
        screen.blit(_badge_mission_surf, (CX + 8, coins_y - _badge_h // 2))
        _draw_mission_coin_icon(screen, CX + 8 + 28, coins_y, r=20)
        if mc_val != _last_mc_val:
            _last_mc_val = mc_val
            _mc_surf_cache = font_med.render(f"{mc_val}", True, MISSION_COIN_COLOR2)
        screen.blit(_mc_surf_cache, (CX + 8 + 62, coins_y - _mc_surf_cache.get_height() // 2))
        screen.blit(_mc_lbl_surf, (CX + 8 + 62 + _mc_surf_cache.get_width() + 8, coins_y - _mc_lbl_surf.get_height() // 2))
        
        # 3. CLASSEMENT — PODIUM PIXEL ART
        # Leaderboard mis en cache toutes les 10 secondes pour ne pas appeler
        # Supabase à chaque frame (60 fois/seconde = lag)
        _lb_now = time.time()
        if not hasattr(main_menu, '_lb_cache') or (_lb_now - main_menu._lb_cache[0]) > 10.0:
            main_menu._lb_cache = (_lb_now, get_leaderboard(data)[:10])
        lb_players = main_menu._lb_cache[1]
        top3   = lb_players[:3]
        rest   = lb_players[3:]
        lb_click_rects = []   # reset chaque frame

        # ── Dimensions ────────────────────────────────────────────────────
        PANEL_W    = 420
        panel_left = int(LB_X - PANEL_W // 2)

        # Titre fixe en haut
        TITLE_Y = SCREEN_HEIGHT // 2 - 240
        screen.blit(_head_sh,   (panel_left + PANEL_W // 2 - _head_surf.get_width() // 2 + 2, TITLE_Y + 2))
        screen.blit(_head_surf, (panel_left + PANEL_W // 2 - _head_surf.get_width() // 2,     TITLE_Y))
        # Ligne pixel sous le titre
        line_y = TITLE_Y + _head_surf.get_height() + 4
        for px in range(0, PANEL_W - 60, 2):   # pixels espacés style 8-bit
            a = int(180 * (1 - abs(px / (PANEL_W - 60) - 0.5) * 2))
            pygame.draw.rect(screen, (*GOLD, a), (panel_left + 30 + px, line_y, 2, 2))

        # ── PODIUM (poussé plus bas que le titre) ─────────────────────────
        _pending_tooltip = None
        PODIUM_CX     = panel_left + PANEL_W // 2
        PODIUM_BASE_Y = SCREEN_HEIGHT // 2 + 80   # bien en-dessous du titre

        BLOCK_W   = 98
        BLOCK_GAP = 10
        # (cx_offset, rank_index, couleur, hauteur_bloc)
        BLOCKS = [
            (-BLOCK_W - BLOCK_GAP, 1, SILVER, 85),
            (0,                    0, GOLD,   125),
            ( BLOCK_W + BLOCK_GAP, 2, BRONZE,  60),
        ]

        for (cx_off, rank_i, blk_col, blk_h) in BLOCKS:
            if rank_i >= len(top3):
                continue
            p      = top3[rank_i]
            blk_cx = PODIUM_CX + cx_off
            blk_x  = blk_cx - BLOCK_W // 2
            blk_y  = PODIUM_BASE_Y - blk_h
            is_me  = p["name"] == player["name"]

            # --- Bloc pixel art : rempli plat + bordure épaisse + ombre portée ---
            # Ombre portée (décalage 4px en bas-droite, couleur foncée)
            shd = pygame.Surface((BLOCK_W, blk_h), pygame.SRCALPHA)
            pygame.draw.rect(shd, (0, 0, 0, 90), (0, 0, BLOCK_W, blk_h))
            screen.blit(shd, (blk_x + 4, blk_y + 4))

            # Corps du bloc (couleur plate, style pixel)
            dark  = tuple(max(0, int(c * 0.45)) for c in blk_col[:3])
            mid_c = tuple(max(0, int(c * 0.65)) for c in blk_col[:3])
            light = tuple(min(255, int(c * 1.1))  for c in blk_col[:3])

            pygame.draw.rect(screen, mid_c,  (blk_x,     blk_y,     BLOCK_W,     blk_h))
            # Tranche claire en haut (style pixel highlight)
            pygame.draw.rect(screen, light,  (blk_x,     blk_y,     BLOCK_W,     4))
            # Tranche foncée en bas
            pygame.draw.rect(screen, dark,   (blk_x,     blk_y + blk_h - 4, BLOCK_W, 4))
            # Tranche claire à gauche
            pygame.draw.rect(screen, light,  (blk_x,     blk_y,     4,           blk_h))
            # Tranche foncée à droite
            pygame.draw.rect(screen, dark,   (blk_x + BLOCK_W - 4, blk_y, 4,     blk_h))
            # Bordure noire pixel (1px)
            pygame.draw.rect(screen, (0, 0, 0), (blk_x, blk_y, BLOCK_W, blk_h), 2)

            # Numéro sur le bloc — centré, couleur claire
            num_lbl = font_med.render(str(rank_i + 1), True, light)
            num_sh  = font_med.render(str(rank_i + 1), True, (0, 0, 0))
            num_y   = blk_y + blk_h // 2 - num_lbl.get_height() // 2
            screen.blit(num_sh,  (blk_cx - num_lbl.get_width() // 2 + 2, num_y + 2))
            screen.blit(num_lbl, (blk_cx - num_lbl.get_width() // 2,     num_y))

            # --- Badge au-dessus du bloc ---
            medal_size = STREAK_BADGE_SIZE
            medal_y    = blk_y - medal_size - 6
            if rank_i == 0:
                # Badge streak pour le 1er
                streak_days = p.get("streak1_days", 0)
                badge_img   = get_streak_badge(streak_days) if streak_days >= 1 else None
                if badge_img is not None:
                    screen.blit(badge_img, (blk_cx - badge_img.get_width() // 2, medal_y))
                    # Tooltip au survol — stocké pour être dessiné en dernier
                    badge_rect = pygame.Rect(blk_cx - badge_img.get_width()//2, medal_y, badge_img.get_width(), badge_img.get_height())
                    if badge_rect.collidepoint(mx, my):
                        _pending_tooltip = (f"1er pendant {streak_days} jour{'s' if streak_days > 1 else ''} d'affilée !", blk_cx, medal_y)

            # --- Nom (juste au-dessus de la médaille, sans fond) ---
            name_col  = (255, 255, 100) if is_me else WHITE
            _disp_nm  = get_display_name(p["name"])[:10]
            nm_surf   = font_tiny.render(_disp_nm, True, name_col)
            nm_sh     = font_tiny.render(_disp_nm, True, (0, 0, 0))
            nm_y      = medal_y - nm_surf.get_height() - 4
            screen.blit(nm_sh,  (blk_cx - nm_surf.get_width() // 2 + 1, nm_y + 1))
            screen.blit(nm_surf,(blk_cx - nm_surf.get_width() // 2,      nm_y))
            # Zone cliquable (nom + bloc podium)
            click_rect = pygame.Rect(blk_x, nm_y - 4, BLOCK_W, (blk_y + blk_h) - nm_y + 4)
            lb_click_rects.append((click_rect, p))
            # Curseur pointer au survol
            if click_rect.collidepoint(mx, my):
                nm_surf  = font_tiny.render(_disp_nm, True, GOLD)
                screen.blit(nm_surf, (blk_cx - nm_surf.get_width() // 2, nm_y))

            # --- Score (au-dessus du nom, sans fond) ---
            sc_surf = font_tiny.render(str(p.get("best_score", 0)), True, blk_col)
            sc_sh   = font_tiny.render(str(p.get("best_score", 0)), True, (0, 0, 0))
            sc_y    = nm_y - sc_surf.get_height() - 2
            screen.blit(sc_sh,  (blk_cx - sc_surf.get_width() // 2 + 1, sc_y + 1))
            screen.blit(sc_surf,(blk_cx - sc_surf.get_width() // 2,      sc_y))

            # (badge streak géré au-dessus du bloc)

        # ── LISTE COMPACTE rang 4-7 (sous le podium, sans fond de ligne) ──
        if rest:
            LIST_Y     = PODIUM_BASE_Y + 18
            LIST_ROW_H = 28
            LIST_LEFT  = panel_left + 30
            LIST_W     = PANEL_W - 60

            # Ligne de séparation pixel entre podium et liste
            for px in range(0, LIST_W, 2):
                a = int(100 * (1 - abs(px / LIST_W - 0.5) * 2))
                pygame.draw.rect(screen, (*GOLD, a), (LIST_LEFT + px, LIST_Y - 8, 2, 2))

            for j, p in enumerate(rest):
                ry    = LIST_Y + j * LIST_ROW_H
                rcy   = ry + LIST_ROW_H // 2
                is_me = p["name"] == player["name"]

                rank_col = (255, 255, 100) if is_me else (160, 165, 185)

                # Zone cliquable toute la ligne
                row_rect = pygame.Rect(LIST_LEFT, ry, LIST_W, LIST_ROW_H)
                lb_click_rects.append((row_rect, p))
                hov_row = row_rect.collidepoint(mx, my)
                if hov_row:
                    hover_surf = pygame.Surface((LIST_W, LIST_ROW_H), pygame.SRCALPHA)
                    pygame.draw.rect(hover_surf, (255, 215, 60, 28), (0, 0, LIST_W, LIST_ROW_H), border_radius=6)
                    screen.blit(hover_surf, (LIST_LEFT, ry))
                    rank_col = GOLD if not is_me else rank_col

                # Rang #N
                rank_surf = font_tiny.render(f"#{j+4}", True, rank_col)
                rank_sh   = font_tiny.render(f"#{j+4}", True, (0, 0, 0))
                screen.blit(rank_sh,   (LIST_LEFT + 1,  rcy - rank_surf.get_height() // 2 + 1))
                screen.blit(rank_surf, (LIST_LEFT,       rcy - rank_surf.get_height() // 2))

                # Nom
                nm_col   = (255, 255, 100) if is_me else WHITE
                _disp_nm = get_display_name(p["name"])[:16]
                nm_surf  = font_tiny.render(_disp_nm, True, nm_col)
                nm_sh    = font_tiny.render(_disp_nm, True, (0, 0, 0))
                screen.blit(nm_sh,  (LIST_LEFT + 42,  rcy - nm_surf.get_height() // 2 + 1))
                screen.blit(nm_surf,(LIST_LEFT + 41,   rcy - nm_surf.get_height() // 2))

                # Score aligné à droite
                sc_surf = font_tiny.render(str(p.get("best_score", 0)), True, rank_col)
                sc_sh   = font_tiny.render(str(p.get("best_score", 0)), True, (0, 0, 0))
                sc_x    = LIST_LEFT + LIST_W - sc_surf.get_width()
                screen.blit(sc_sh,  (sc_x + 1, rcy - sc_surf.get_height() // 2 + 1))
                screen.blit(sc_surf,(sc_x,      rcy - sc_surf.get_height() // 2))

                # Séparateur pixel entre lignes
                if j < len(rest) - 1:
                    for px in range(0, LIST_W, 4):
                        pygame.draw.rect(screen, (255, 255, 255, 25), (LIST_LEFT + px, ry + LIST_ROW_H - 1, 2, 1))

        """# 3b. AFFICHAGE DE LA MISSION (Remonté et aéré)
        init_missions(player)
        active_missions = []
        for mid, mtype, label, desc, goal, reward in MISSIONS_DAILY + MISSIONS_ONETIME + MISSIONS_PERMANENT:
            entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
            if not entry["claimed"]:
                active_missions.append((mid, label, desc, goal, reward, entry["progress"]))
        
        active_missions.sort(key=lambda x: (-(x[5] >= x[3]), -x[5]/max(1, x[3])))

        if active_missions:
            mid_m, label_m, desc_m, goal_m, reward_m, prog_m = active_missions[0]
            done_m = prog_m >= goal_m
            pct_m  = min(1.0, prog_m / max(1, goal_m))
            
            M_Y = MISS_BLOCK_Y
            M_X = CX - 145

            # 1. Pastille + Titre
            dot_col = (50, 255, 100) if done_m else (0, 200, 255)
            pygame.draw.circle(screen, dot_col, (M_X, M_Y + 10), 6)
            lbl_txt = font_small.render(label_m.upper(), True, WHITE)
            screen.blit(lbl_txt, (M_X + 20, M_Y))

            # 2. Description
            desc_txt = font_tiny.render(desc_m, True, (160, 170, 190))
            screen.blit(desc_txt, (M_X + 20, M_Y + 30))

            # 3. Barre de progression
            BAR_W, BAR_H = 210, 8
            pygame.draw.rect(screen, (25, 25, 40), (M_X + 20, M_Y + 60, BAR_W, BAR_H), border_radius=4)
            if pct_m > 0:
                pygame.draw.rect(screen, dot_col, (M_X + 20, M_Y + 60, int(BAR_W * pct_m), BAR_H), border_radius=4)

            # 4. Score numérique
            val_txt = font_tiny.render(f"{min(prog_m, goal_m)} / {goal_m}", True, (220, 220, 220))
            screen.blit(val_txt, (M_X + 25 + BAR_W, M_Y + 56))

            # Dimensions du badge
            BADGE_W = 190
            BADGE_H = 30

            # 5. Badge "PRÊT À RÉCLAMER" uniquement si complétée
            if done_m:
                badge_surf = pygame.Surface((BADGE_W, BADGE_H), pygame.SRCALPHA)

                # fond
                pygame.draw.rect(
                    badge_surf,
                    (20, 80, 30, 220),
                    (0, 0, BADGE_W, BADGE_H),
                    border_radius=int(BADGE_H * 0.3) 
                )

                # contour
                pygame.draw.rect(
                    badge_surf,
                    (*GREEN_SOFT, 255),
                    (0, 0, BADGE_W, BADGE_H),
                    width=max(1, BADGE_H // 10),
                    border_radius=int(BADGE_H * 0.3)
                )

                screen.blit(badge_surf, (M_X + 20, M_Y + 76))

                rdy_txt = font_tiny.render("PRÊT À RÉCLAMER", True, (50, 255, 100))

                # centrage automatique du texte
                screen.blit(
                    rdy_txt,
                    (
                        M_X + 20 + BADGE_W//2 - rdy_txt.get_width()//2,
                        M_Y + 76 + BADGE_H//2 - rdy_txt.get_height()//2
                    )
                )"""

        # 4. BOUTONS MENU — scale depuis cache, ratio préservé
        # JOUER
        sc_play = btn_scales["play"]
        play_img = _get_btn_img(PLAY_BTN_IMG, "play", PLAY_W * sc_play / PLAY_BTN_IMG.get_width())
        screen.blit(play_img, (CX - play_img.get_width()//2, PLAY_Y - play_img.get_height()//2))

        # BOUTIQUE
        sc_shop = btn_scales["shop"]
        shop_img = _get_btn_img(SHOP_BTN_IMG, "shop", SHOP_W * sc_shop / SHOP_BTN_IMG.get_width())
        screen.blit(shop_img, (CX - shop_img.get_width()//2, SHOP_Y - shop_img.get_height()//2))

        # MISSIONS
        sc_miss = btn_scales["miss"]
        miss_img = _get_btn_img(MISS_BTN_IMG, "miss", MISS_W * sc_miss / MISS_BTN_IMG.get_width())
        screen.blit(miss_img, (MISS_X - miss_img.get_width()//2, MISS_Y - miss_img.get_height()//2))

        # NIVEAUX (bouton texte stylisé, pas d'image dédiée)
        sc_lvl = btn_scales["lvl"]
        lvl_img = _get_btn_img(LEVEL_BTN_IMG, "lvl", LEVEL_BTN_IMG.get_width() * sc_lvl / LEVEL_BTN_IMG.get_width())
        screen.blit(lvl_img, (LVL_X - lvl_img.get_width()//2, LVL_Y - lvl_img.get_height()//2))

        # ----- PARAMÈTRES DU BADGE -----
        BADGE_RADIUS = 13        # taille du badge
        BADGE_OFFSET_X = -50      # décalage horizontal
        BADGE_OFFSET_Y = 90      # décalage vertical
        BADGE_BORDER = 1         # épaisseur contour

        # Badge rouge missions
        pending_count = count_pending_missions(player)

        if pending_count > 0:

            # position du centre
            badge_cx = MISS_X + miss_img.get_width()//2 + BADGE_OFFSET_X
            badge_cy = MISS_Y - miss_img.get_height()//2 + BADGE_OFFSET_Y

            # fond
            pygame.draw.circle(screen, RED_HOT, (badge_cx, badge_cy), BADGE_RADIUS)

            # contour (amélioration visuelle)
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (badge_cx, badge_cy),
                BADGE_RADIUS,
                BADGE_BORDER
            )

            # texte
            nb_s = font_tiny.render(str(pending_count), True, WHITE)

            screen.blit(
                nb_s,
                (
                    badge_cx - nb_s.get_width()//2,
                    badge_cy - nb_s.get_height()//2
                )
            )

        # 5. SÉLECTEURS
        # ── Skin (bas centre gauche) ──
        prv = _get_skin_preview(current_skin)
        screen.blit(prv, (SKIN_CX - prv.get_width()//2, SEL_CY - prv.get_height()//2 + int(math.sin(t * 2.5) * 4)))
        sn_txt = font_tiny.render(SKIN_DISPLAY_NAMES[current_skin].upper(), True, (210, 210, 210))
        screen.blit(sn_txt, (SKIN_CX - sn_txt.get_width()//2, SEL_CY + 40))
        lbl_skin = font_tiny.render("SKIN", True, GOLD)
        screen.blit(lbl_skin, (SKIN_CX - lbl_skin.get_width()//2, SEL_CY - 55))
        if len(owned) > 1:
            for acx in [SKIN_CX - ARR_OFFX, SKIN_CX + ARR_OFFX]:
                _is_left = acx < SKIN_CX
                _ak = ("skin", "left" if _is_left else "right")
                _clicked = _arrow_anim.get(_ak, 0) > 0
                ahov = math.hypot(mx - acx, my - SEL_CY) <= ARR_R + 6
                if _is_left:
                    aimg = ARROW_LEFT_2 if _clicked else ARROW_LEFT_1
                else:
                    aimg = ARROW_RIGHT_2 if _clicked else ARROW_RIGHT_1
                screen.blit(aimg, (acx - aimg.get_width()//2, SEL_CY - aimg.get_height()//2))

        # ── Background (bas centre droit) ──
        current_bg_key = owned_bgs[bg_idx]
        lbl_bg = font_tiny.render("FOND D'ÉCRAN", True, (60, 200, 255))
        screen.blit(lbl_bg, (BG_SEL_CX - lbl_bg.get_width()//2, SEL_CY - 55))
        bg_prv = _get_bg_preview(current_bg_key)
        prv_rect = pygame.Rect(BG_SEL_CX - PREV_W//2, SEL_CY - PREV_H//2, PREV_W, PREV_H)
        screen.blit(bg_prv, prv_rect)
        border_col = (60, 200, 255) if current_bg_key else (130, 130, 160)
        pygame.draw.rect(screen, border_col, prv_rect, width=2, border_radius=5)
        bg_name = "Défaut" if current_bg_key is None else next((b["name"] for b in BG_ITEMS if b["key"] == current_bg_key), current_bg_key)
        bg_name_txt = font_tiny.render(bg_name.upper(), True, (210, 210, 210))
        screen.blit(bg_name_txt, (BG_SEL_CX - bg_name_txt.get_width()//2, SEL_CY + 40))
        if len(owned_bgs) > 1:
            for acx in [BG_SEL_CX - ARR_OFFX, BG_SEL_CX + ARR_OFFX]:
                _is_left = acx < BG_SEL_CX
                _ak = ("bg", "left" if _is_left else "right")
                _clicked = _arrow_anim.get(_ak, 0) > 0
                ahov = math.hypot(mx - acx, my - SEL_CY) <= ARR_R + 6
                if _is_left:
                    aimg = ARROW_LEFT_2 if _clicked else ARROW_LEFT_1
                else:
                    aimg = ARROW_RIGHT_2 if _clicked else ARROW_RIGHT_1
                screen.blit(aimg, (acx - aimg.get_width()//2, SEL_CY - aimg.get_height()//2))

        # ── Musique MENU (milieu gauche, au-dessus) ──
        current_music_menu_key = owned_musics[music_menu_idx]
        lbl_mm = font_tiny.render("MUSIQUE MENU", True, (200, 120, 255))
        screen.blit(lbl_mm, (AUDIO_X - lbl_mm.get_width()//2, AUDIO_MENU_CY - 55))
        # Bouton ? à droite du label musique menu
        _mm_q_r = 10
        _mm_q_cx = AUDIO_X + lbl_mm.get_width()//2 + _mm_q_r + 6
        _mm_q_cy = AUDIO_MENU_CY - 55 + lbl_mm.get_height()//2
        _mm_q_hov = math.hypot(mx - _mm_q_cx, my - _mm_q_cy) <= _mm_q_r + 4
        pygame.draw.circle(screen, (80, 40, 130), (_mm_q_cx, _mm_q_cy), _mm_q_r)
        pygame.draw.circle(screen, (200, 120, 255), (_mm_q_cx, _mm_q_cy), _mm_q_r, 2)
        _q_surf = font_tiny.render("?", True, (220, 180, 255))
        screen.blit(_q_surf, (_mm_q_cx - _q_surf.get_width()//2, _mm_q_cy - _q_surf.get_height()//2))
        if _mm_q_hov:
            _pending_tooltip = ("Si la même musique est choisie pour le menu et le jeu, elle ne s'arrêtera pas.", _mm_q_cx, _mm_q_cy - _mm_q_r - 4)
        NOTE_W, NOTE_H = 52, 52
        note_surf2 = pygame.Surface((NOTE_W, NOTE_H), pygame.SRCALPHA)
        note_col_m = (200, 120, 255) if current_music_menu_key is None else (220, 160, 255)
        pygame.draw.ellipse(note_surf2, note_col_m, (4, 34, 20, 14))
        pygame.draw.line(note_surf2, note_col_m, (24, 6), (24, 41), 4)
        pygame.draw.line(note_surf2, note_col_m, (24, 6), (44, 2), 3)
        note_surf2.set_alpha(int(200 + math.sin(t * 2.5 + 1) * 40))
        screen.blit(note_surf2, (AUDIO_X - NOTE_W//2, AUDIO_MENU_CY - NOTE_H//2 + int(math.sin(t * 2.5 + 1) * 4)))
        mm_name = ("Défaut Menu" if current_music_menu_key is None
                   else "Défaut Jeu"  if current_music_menu_key == _MUSIC_KEY_DEFAULT_GAME
                   else "Défaut Menu" if current_music_menu_key == _MUSIC_KEY_DEFAULT_MENU
                   else next((m["name"] for m in MUSIC_ITEMS if m["key"] == current_music_menu_key), current_music_menu_key))
        mm_txt = font_tiny.render(mm_name.upper(), True, (210, 210, 210))
        screen.blit(mm_txt, (AUDIO_X - mm_txt.get_width()//2, AUDIO_MENU_CY + 40))
        if len(owned_musics) > 1:
            for acx in [AUDIO_X - ARR_OFFX, AUDIO_X + ARR_OFFX]:
                _is_left = acx < AUDIO_X
                _ak = ("mmenu", "left" if _is_left else "right")
                _clicked = _arrow_anim.get(_ak, 0) > 0
                ahov = math.hypot(mx - acx, my - AUDIO_MENU_CY) <= ARR_R + 6
                if _is_left:
                    aimg = ARROW_LEFT_2 if _clicked else ARROW_LEFT_1
                else:
                    aimg = ARROW_RIGHT_2 if _clicked else ARROW_RIGHT_1
                screen.blit(aimg, (acx - aimg.get_width()//2, AUDIO_MENU_CY - aimg.get_height()//2))

        # ── Musique EN JEU (milieu gauche, en-dessous) ──
        current_music_key = owned_musics[music_idx]
        lbl_mg = font_tiny.render("MUSIQUE JEU", True, (255, 160, 60))
        screen.blit(lbl_mg, (AUDIO_X - lbl_mg.get_width()//2, AUDIO_GAME_CY - 55))
        # Bouton ? à droite du label musique jeu
        _mg_q_r = 10
        _mg_q_cx = AUDIO_X + lbl_mg.get_width()//2 + _mg_q_r + 6
        _mg_q_cy = AUDIO_GAME_CY - 55 + lbl_mg.get_height()//2
        _mg_q_hov = math.hypot(mx - _mg_q_cx, my - _mg_q_cy) <= _mg_q_r + 4
        pygame.draw.circle(screen, (100, 60, 20), (_mg_q_cx, _mg_q_cy), _mg_q_r)
        pygame.draw.circle(screen, (255, 160, 60), (_mg_q_cx, _mg_q_cy), _mg_q_r, 2)
        _q_surf2 = font_tiny.render("?", True, (255, 200, 100))
        screen.blit(_q_surf2, (_mg_q_cx - _q_surf2.get_width()//2, _mg_q_cy - _q_surf2.get_height()//2))
        if _mg_q_hov:
            _pending_tooltip = ("Si la même musique est choisie pour le menu et le jeu, elle ne s'arrêtera pas.", _mg_q_cx, _mg_q_cy - _mg_q_r - 4)
        note_surf = pygame.Surface((NOTE_W, NOTE_H), pygame.SRCALPHA)
        note_col_g = (255, 160, 60) if current_music_key is None else (255, 200, 80)
        pygame.draw.ellipse(note_surf, note_col_g, (4, 34, 20, 14))
        pygame.draw.line(note_surf, note_col_g, (24, 6), (24, 41), 4)
        pygame.draw.line(note_surf, note_col_g, (24, 6), (44, 2), 3)
        note_surf.set_alpha(int(200 + math.sin(t * 2.5) * 40))
        screen.blit(note_surf, (AUDIO_X - NOTE_W//2, AUDIO_GAME_CY - NOTE_H//2 + int(math.sin(t * 2.5) * 4)))
        mg_name = ("Défaut Jeu"  if current_music_key is None
                   else "Défaut Menu" if current_music_key == _MUSIC_KEY_DEFAULT_MENU
                   else "Défaut Jeu"  if current_music_key == _MUSIC_KEY_DEFAULT_GAME
                   else next((m["name"] for m in MUSIC_ITEMS if m["key"] == current_music_key), current_music_key))
        mg_txt = font_tiny.render(mg_name.upper(), True, (210, 210, 210))
        screen.blit(mg_txt, (AUDIO_X - mg_txt.get_width()//2, AUDIO_GAME_CY + 40))
        if len(owned_musics) > 1:
            for acx in [AUDIO_X - ARR_OFFX, AUDIO_X + ARR_OFFX]:
                _is_left = acx < AUDIO_X
                _ak = ("mgame", "left" if _is_left else "right")
                _clicked = _arrow_anim.get(_ak, 0) > 0
                ahov = math.hypot(mx - acx, my - AUDIO_GAME_CY) <= ARR_R + 6
                if _is_left:
                    aimg = ARROW_LEFT_2 if _clicked else ARROW_LEFT_1
                else:
                    aimg = ARROW_RIGHT_2 if _clicked else ARROW_RIGHT_1
                screen.blit(aimg, (acx - aimg.get_width()//2, AUDIO_GAME_CY - aimg.get_height()//2))

        # 6. AVATAR
        draw_avatar(player, AV_X, AV_Y, AV_R)
        if dropdown_open:
            dd_x = AV_X - DD_W + AV_R
            th_opts = _th_get()
            any_tryhard_on = any(th_opts.get(k, False) for k, _, _ in TRYHARD_OPTIONS)

            for i, item in enumerate(DD_ITEMS):
                iy  = (AV_Y + AV_R + 20) + i * (DD_H_item + 5)
                hov = (dd_x <= mx <= dd_x + DD_W and iy <= my <= iy + DD_H_item)
                is_tryhard = (item == "Tryharder")
                is_tryhard_active = is_tryhard and tryhard_panel_open

                # Fond item
                bg_col = (55, 20, 20) if (is_tryhard and any_tryhard_on) else ((40, 45, 75) if hov else (15, 18, 30))
                pygame.draw.rect(screen, bg_col, (dd_x, iy, DD_W, DD_H_item), border_radius=10)
                # Bordure rouge si tryhard actif
                if is_tryhard and any_tryhard_on:
                    pygame.draw.rect(screen, (200, 50, 50), (dd_x, iy, DD_W, DD_H_item), 1, border_radius=10)
                elif is_tryhard_active:
                    pygame.draw.rect(screen, (255, 80, 80), (dd_x, iy, DD_W, DD_H_item), 1, border_radius=10)

                # Icône "►" pour l'item tryharder
                if is_tryhard:
                    lbl_col = (255, 120, 120) if any_tryhard_on else ((255, 180, 180) if hov else (220, 120, 120))
                    it = font_small.render(item, True, lbl_col)
                    screen.blit(it, (dd_x + 20, iy + DD_H_item//2 - it.get_height()//2))
                    # Triangle dessiné (remplace le caractère unicode ► non supporté)
                    _ax = dd_x + DD_W - 18
                    _ay = iy + DD_H_item // 2
                    pygame.draw.polygon(screen, lbl_col, [(_ax, _ay - 7), (_ax, _ay + 7), (_ax + 10, _ay)])
                    # Petits points rouges si options activées
                    if any_tryhard_on:
                        n_on = sum(1 for k, _, _ in TRYHARD_OPTIONS if th_opts.get(k, False))
                        badge_s = pygame.Surface((22, 18), pygame.SRCALPHA)
                        pygame.draw.rect(badge_s, (200, 40, 40, 230), (0, 0, 22, 18), border_radius=5)
                        nb_t = font_tiny.render(str(n_on), True, WHITE)
                        badge_s.blit(nb_t, (11 - nb_t.get_width()//2, 9 - nb_t.get_height()//2))
                        screen.blit(badge_s, (dd_x + DD_W - 52, iy + DD_H_item//2 - 9))
                elif item == "Administration":
                    # Item admin : fond rouge fonce + badge ADMIN
                    adm_bg = (70, 18, 18) if hov else (48, 10, 10)
                    pygame.draw.rect(screen, adm_bg, (dd_x, iy, DD_W, DD_H_item), border_radius=10)
                    pygame.draw.rect(screen, (200, 50, 50, 200), (dd_x, iy, DD_W, DD_H_item), 2, border_radius=10)
                    adm_col = (255, 140, 140) if hov else (220, 90, 90)
                    it = font_small.render("Administration", True, adm_col)
                    screen.blit(it, (dd_x + 20, iy + DD_H_item//2 - it.get_height()//2))
                else:
                    it = font_small.render(item, True, WHITE)
                    screen.blit(it, (dd_x + 20, iy + DD_H_item//2 - it.get_height()//2))

            # ── Sous-panel Tryharder ──────────────────────────────────────────
            if tryhard_panel_open:
                th_panel_x = dd_x - 270
                th_panel_y = (AV_Y + AV_R + 20) + 2 * (DD_H_item + 5)
                th_panel_w = 260
                th_row_h   = 42
                th_panel_h = 12 + len(TRYHARD_OPTIONS) * th_row_h + 12

                # Fond panel
                th_surf = pygame.Surface((th_panel_w, th_panel_h), pygame.SRCALPHA)
                pygame.draw.rect(th_surf, (18, 8, 8, 235), (0, 0, th_panel_w, th_panel_h), border_radius=12)
                pygame.draw.rect(th_surf, (200, 50, 50, 200), (0, 0, th_panel_w, th_panel_h), 1, border_radius=12)
                screen.blit(th_surf, (th_panel_x, th_panel_y))

                # Titre du panel
                th_title = font_tiny.render("TRYHARDER", True, (255, 100, 100))
                screen.blit(th_title, (th_panel_x + th_panel_w//2 - th_title.get_width()//2, th_panel_y + 4 - th_title.get_height()//2 + 6))

                for j, (opt_key, opt_label, opt_desc) in enumerate(TRYHARD_OPTIONS):
                    ry    = th_panel_y + 12 + j * th_row_h
                    val   = th_opts.get(opt_key, False)
                    row_r = pygame.Rect(th_panel_x + 4, ry, th_panel_w - 8, th_row_h)
                    hov_r = row_r.collidepoint(mx, my)

                    # Fond ligne hover
                    if hov_r:
                        hov_s = pygame.Surface((th_panel_w - 8, th_row_h), pygame.SRCALPHA)
                        pygame.draw.rect(hov_s, (255, 80, 80, 30), (0, 0, th_panel_w - 8, th_row_h), border_radius=7)
                        screen.blit(hov_s, (th_panel_x + 4, ry))

                    # Checkbox
                    cb_x, cb_y = th_panel_x + 14, ry + 9
                    cb_col_bg  = (140, 30, 30, 240) if val else (30, 14, 14, 200)
                    cb_col_bd  = (255, 80, 80) if val else ((180, 80, 80) if hov_r else (80, 40, 40))
                    cb_s = pygame.Surface((22, 22), pygame.SRCALPHA)
                    pygame.draw.rect(cb_s, cb_col_bg, (0, 0, 22, 22), border_radius=5)
                    pygame.draw.rect(cb_s, cb_col_bd, (0, 0, 22, 22), 2, border_radius=5)
                    if val:
                        pygame.draw.line(cb_s, (255, 100, 100), (4, 11), (9, 17), 3)
                        pygame.draw.line(cb_s, (255, 100, 100), (9, 17), (18, 5), 3)
                    screen.blit(cb_s, (cb_x, cb_y))

                    # Label
                    lbl_col = (255, 150, 150) if val else ((220, 180, 180) if hov_r else (160, 130, 130))
                    lbl_s = font_small.render(opt_label, True, lbl_col)
                    screen.blit(lbl_s, (th_panel_x + 44, ry + th_row_h//2 - lbl_s.get_height()//2))

                    # Séparateur fin entre lignes
                    if j < len(TRYHARD_OPTIONS) - 1:
                        pygame.draw.line(screen, (60, 20, 20),
                                         (th_panel_x + 10, ry + th_row_h - 1),
                                         (th_panel_x + th_panel_w - 10, ry + th_row_h - 1), 1)

        # Tooltip (dessiné en tout dernier pour être au-dessus de tout)
        if _pending_tooltip:
            draw_tooltip(_pending_tooltip[0], _pending_tooltip[1], _pending_tooltip[2])

        # ── Chat overlay (au premier plan, par dessus tout) ───────────────────
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass

        # ── Bandeau défilant admin (tout en haut, par-dessus tout) ───────────
        if _banner_enabled and _banner_msg and not _banner_closed:
            # Construire la surface de texte si besoin
            if _banner_surf is None:
                _unit = f"  --  {_banner_msg}"
                _unit_surf = font_tiny.render(_unit, True, GOLD)
                _unit_w    = max(1, _unit_surf.get_width())
                # Répéter pour couvrir au moins 3× l'écran
                _repeats   = max(3, SCREEN_WIDTH * 3 // _unit_w + 2)
                _banner_surf = pygame.Surface((_unit_w * _repeats, _unit_surf.get_height()), pygame.SRCALPHA)
                for _ri in range(_repeats):
                    _banner_surf.blit(_unit_surf, (_ri * _unit_w, 0))
                _banner_unit_w = _unit_w

            # Avancer le texte
            _banner_x -= _BANNER_SPEED
            if _banner_x < -_banner_unit_w:
                _banner_x += _banner_unit_w

            # Fond du bandeau
            _ban_bg = pygame.Surface((SCREEN_WIDTH, _BANNER_H), pygame.SRCALPHA)
            pygame.draw.rect(_ban_bg, (10, 8, 0, 210),      (0, 0, SCREEN_WIDTH, _BANNER_H))
            pygame.draw.rect(_ban_bg, (*GOLD_DARK, 180),    (0, _BANNER_H - 2, SCREEN_WIDTH, 2))
            pygame.draw.rect(_ban_bg, (*GOLD_DARK, 80),     (0, 0, SCREEN_WIDTH, 1))
            screen.blit(_ban_bg, (0, 0))

            # Texte défilant (clippé dans le bandeau, zone hors bouton X)
            screen.set_clip(pygame.Rect(0, 0, SCREEN_WIDTH - 30, _BANNER_H))
            _ty = _BANNER_H // 2 - _banner_surf.get_height() // 2
            screen.blit(_banner_surf, (int(_banner_x), _ty))
            screen.set_clip(None)

            # Bouton X pour fermer
            _cx_btn = pygame.Rect(SCREEN_WIDTH - 28, 0, 28, _BANNER_H)
            _hov_x  = _cx_btn.collidepoint(mx, my)
            _xbg    = pygame.Surface((28, _BANNER_H), pygame.SRCALPHA)
            pygame.draw.rect(_xbg, (180, 40, 40, 200) if _hov_x else (80, 20, 20, 160),
                             (0, 0, 28, _BANNER_H))
            screen.blit(_xbg, (SCREEN_WIDTH - 28, 0))
            _x_lbl = font_tiny.render("X", True, WHITE)
            screen.blit(_x_lbl, (SCREEN_WIDTH - 14 - _x_lbl.get_width() // 2,
                                  _BANNER_H // 2 - _x_lbl.get_height() // 2))

        draw_notifs()
        pygame.display.flip()
# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS BOUTIQUE
# ══════════════════════════════════════════════════════════════════════════════
def draw_checkmark(surf, cx, cy, r, color):
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, (255, 255, 255, 60), (cx, cy), r, 2)
    lw = max(2, r // 3)
    x1, y1 = cx - r//2,     cy
    x2, y2 = cx - r//6,     cy + r//3
    x3, y3 = cx + r//2 - 1, cy - r//3
    pygame.draw.line(surf, WHITE, (x1, y1), (x2, y2), lw)
    pygame.draw.line(surf, WHITE, (x2, y2), (x3, y3), lw)

def draw_lock(surf, cx, cy, color):
    bw, bh = 18, 14
    bx, by = cx - bw//2, cy
    pygame.draw.rect(surf, color, (bx, by, bw, bh), border_radius=3)
    ar = 8
    pygame.draw.arc(surf, color,
                    (cx - ar, cy - ar - 2, ar*2, ar*2),
                    0, math.pi, 3)


# ══════════════════════════════════════════════════════════════════════════════
#  BOUTIQUE
# ══════════════════════════════════════════════════════════════════════════════
def _draw_shop_coin_badge(player, coin_anim_t):
    total_coins = player.get("total_coins", 0)
    bw, bh = 185, 40
    bx, by = SCREEN_WIDTH - bw - 22, 18
    bsurf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(bsurf, (8, 8, 18, 220), (0, 0, bw, bh), border_radius=20)
    pygame.draw.rect(bsurf, (*GOLD, 210), (0, 0, bw, bh), width=2, border_radius=20)
    shine = pygame.Surface((bw - 8, bh // 2 - 2), pygame.SRCALPHA)
    pygame.draw.rect(shine, (255, 255, 255, 14), (0, 0, bw - 8, bh//2 - 2), border_radius=20)
    bsurf.blit(shine, (4, 3))
    screen.blit(bsurf, (bx, by))
    cf_img = COIN_FRAMES_34[(coin_anim_t // 4) % len(COIN_FRAMES_34)]
    ci_sm  = cf_img
    ct_txt = font_small.render(str(total_coins), True, GOLD)
    total_content_w = ci_sm.get_width() + 8 + ct_txt.get_width()
    start_x = bx + (bw - total_content_w) // 2
    content_y = by + (bh - ci_sm.get_height()) // 2
    screen.blit(ci_sm, (start_x, content_y))
    screen.blit(ct_txt, (start_x + ci_sm.get_width() + 8, by + (bh - ct_txt.get_height()) // 2))


MISSION_COIN_COLOR  = (60, 180, 255)   # bleu vif
MISSION_COIN_COLOR2 = (120, 210, 255)  # bleu clair

# ── Chargement de la pièce mission ───────────────────────────────────────────
try:
    _mcoin_raw = _pygame_load('assets/sprites/coin_mission.png').convert_alpha()
    MISSION_COIN_IMG = pygame.transform.smoothscale(_mcoin_raw, (80, 80))
except Exception as e:
    print(f"Impossible de charger coin_mission.png : {e}")
    # Fallback : cercle bleu avec M
    _mcoin_fb = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(_mcoin_fb, MISSION_COIN_COLOR,  (40, 40), 38)
    pygame.draw.circle(_mcoin_fb, MISSION_COIN_COLOR2, (40, 40), 38, 2)
    MISSION_COIN_IMG = _mcoin_fb

def play_purchase_animation(item_name, item_type="skin", item_img=None):
    """Animation spectaculaire lors d'un achat : confettis, flash, texte animé."""
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2

    # Confetti particles
    CONFETTI_COLORS = [
        (255, 80, 80), (255, 200, 60), (60, 220, 120),
        (80, 180, 255), (220, 80, 255), (255, 140, 60),
        (60, 255, 220), (255, 255, 80), (255, 120, 200),
    ]
    confettis = []
    for _ in range(120):
        confettis.append({
            "x": random.uniform(CX - 350, CX + 350),
            "y": random.uniform(-60, CY - 50),
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(2, 9),
            "rot": random.uniform(0, 360),
            "rot_v": random.uniform(-8, 8),
            "w": random.randint(8, 22),
            "h": random.randint(5, 12),
            "color": random.choice(CONFETTI_COLORS),
            "alpha": 255,
        })

    # Burst particles (étoiles depuis le centre)
    bursts = []
    for i in range(36):
        angle = math.radians(i * 10)
        spd = random.uniform(4, 14)
        bursts.append({
            "x": float(CX), "y": float(CY),
            "vx": math.cos(angle) * spd,
            "vy": math.sin(angle) * spd,
            "life": random.randint(30, 55),
            "max_life": 55,
            "r": random.uniform(3, 7),
            "color": random.choice(CONFETTI_COLORS),
        })

    # Type label
    type_labels = {"skin": "SKIN", "background": "FOND D'ÉCRAN", "music": "MUSIQUE"}
    type_colors = {"skin": (220, 100, 255), "background": (60, 200, 255), "music": (255, 160, 60)}
    type_label = type_labels.get(item_type, "ITEM")
    type_color = type_colors.get(item_type, GOLD)

    duration = 165  # frames (~2.75s @ 60fps)
    for frame in range(duration):
        clock.tick(FPS)
        t_ratio = frame / duration  # 0→1

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type in (KEYDOWN, MOUSEBUTTONDOWN):
                # Skip animation on any key/click
                return

        # ── Fond
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(190)

        # ── Flash blanc au début
        if frame < 12:
            flash_alpha = int(200 * (1 - frame / 12))
            fl = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fl.fill((255, 255, 255, flash_alpha))
            screen.blit(fl, (0, 0))

        # ── Burst particles
        burst_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for b in bursts:
            if b["life"] > 0:
                b["x"] += b["vx"]
                b["y"] += b["vy"]
                b["vy"] += 0.3
                b["life"] -= 1
                a = int(255 * (b["life"] / b["max_life"]))
                r = max(1, int(b["r"] * (b["life"] / b["max_life"])))
                pygame.draw.circle(burst_surf, (*b["color"], a), (int(b["x"]), int(b["y"])), r)
        screen.blit(burst_surf, (0, 0))

        # ── Confettis
        conf_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for c in confettis:
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["vy"] += 0.18
            c["vx"] *= 0.99
            c["rot"] += c["rot_v"]
            if frame > duration - 40:
                c["alpha"] = max(0, c["alpha"] - 8)
            if c["y"] > SCREEN_HEIGHT + 30:
                c["y"] = random.uniform(-80, -20)
                c["x"] = random.uniform(CX - 400, CX + 400)
                c["vy"] = random.uniform(2, 7)
            # Dessine le confetti comme rectangle rotatif
            csurf = pygame.Surface((c["w"], c["h"]), pygame.SRCALPHA)
            col_a = (*c["color"], max(0, int(c["alpha"])))
            pygame.draw.rect(csurf, col_a, (0, 0, c["w"], c["h"]), border_radius=2)
            rotated = pygame.transform.rotate(csurf, c["rot"])
            conf_surf.blit(rotated, (int(c["x"]) - rotated.get_width()//2,
                                     int(c["y"]) - rotated.get_height()//2))
        screen.blit(conf_surf, (0, 0))

        # ── Panel central avec animation d'entrée (pop depuis 0)
        scale_in = min(1.0, frame / 18) if frame < 18 else 1.0 - max(0, (frame - 145) / 20) * 0.15
        panel_w = int(480 * scale_in)
        panel_h = int(320 * scale_in)
        if panel_w > 10 and panel_h > 10:
            ps = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(ps, (10, 12, 28, 240), (0, 0, panel_w, panel_h), border_radius=24)
            # Bordure animée multicolore
            border_hue = (frame * 4) % 360
            r_b = int(128 + 127 * math.sin(math.radians(border_hue)))
            g_b = int(128 + 127 * math.sin(math.radians(border_hue + 120)))
            b_b = int(128 + 127 * math.sin(math.radians(border_hue + 240)))
            pygame.draw.rect(ps, (r_b, g_b, b_b, 255), (0, 0, panel_w, panel_h), width=4, border_radius=24)
            # Reflet
            shine = pygame.Surface((panel_w - 8, panel_h // 3), pygame.SRCALPHA)
            pygame.draw.rect(shine, (255, 255, 255, 20), (0, 0, panel_w - 8, panel_h // 3), border_radius=24)
            ps.blit(shine, (4, 4))
            screen.blit(ps, (CX - panel_w // 2, CY - panel_h // 2))

        # ── Texte "DÉBLOQUÉ !" avec effet scale+glow
        if frame > 6:
            txt_scale = min(1.0, (frame - 6) / 14)
            unlock_txt = font_big.render("DÉBLOQUÉ !", True, GOLD)
            if txt_scale < 1.0:
                tw = max(1, int(unlock_txt.get_width() * txt_scale))
                th = max(1, int(unlock_txt.get_height() * txt_scale))
                unlock_txt = pygame.transform.smoothscale(unlock_txt, (tw, th))
            # Glow
            for off in (5, 3, 2):
                glow = font_big.render("DÉBLOQUÉ !", True, type_color)
                g_alpha = max(0, int(120 / off) - frame // 3)
                gw = max(1, int(glow.get_width() * txt_scale))
                gh = max(1, int(glow.get_height() * txt_scale))
                glow = pygame.transform.smoothscale(glow, (gw, gh))
                glow.set_alpha(max(0, g_alpha))
                screen.blit(glow, (CX - gw // 2 + off, CY - 110 - gh // 2 + off))
                screen.blit(glow, (CX - gw // 2 - off, CY - 110 - gh // 2 - off))
            screen.blit(unlock_txt, (CX - unlock_txt.get_width() // 2, CY - 110 - unlock_txt.get_height() // 2))

        # ── Image du skin/fond si dispo (bounce)
        if item_img and frame > 10:
            bounce = math.sin((frame - 10) * 0.18) * 8
            img_scale = min(1.0, (frame - 10) / 14)
            iw = max(1, int(100 * img_scale))
            ih = max(1, int(100 * img_scale * item_img.get_height() / max(1, item_img.get_width())))
            scaled_img = pygame.transform.smoothscale(item_img, (iw, ih))
            # Halo
            if img_scale >= 1.0:
                halo_r = int(62 + 8 * math.sin(frame * 0.15))
                halo_alpha = int(80 + 40 * math.sin(frame * 0.12))
                halo = pygame.Surface((halo_r*2, halo_r*2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*type_color, halo_alpha), (halo_r, halo_r), halo_r)
                screen.blit(halo, (CX - halo_r, int(CY - 10 + bounce) - halo_r))
            screen.blit(scaled_img, (CX - iw//2, int(CY - 10 + bounce) - ih//2))

        # ── Nom de l'item
        if frame > 20:
            name_alpha = min(255, (frame - 20) * 16)
            type_surf = font_tiny.render(type_label, True, type_color)
            type_surf.set_alpha(name_alpha)
            screen.blit(type_surf, (CX - type_surf.get_width()//2, CY + 70))
            name_surf = font_med.render(item_name.upper(), True, WHITE)
            name_surf.set_alpha(name_alpha)
            screen.blit(name_surf, (CX - name_surf.get_width()//2, CY + 94))

        # ── Étoiles scintillantes autour du panel
        if frame > 8:
            for i in range(8):
                angle = math.radians(frame * 2.5 + i * 45)
                dist = 175 + math.sin(frame * 0.08 + i) * 18
                sx = int(CX + math.cos(angle) * dist)
                sy = int(CY + math.sin(angle) * dist)
                star_size = max(1, int(3 + 2 * math.sin(frame * 0.12 + i * 0.8)))
                star_alpha = int(160 + 80 * math.sin(frame * 0.14 + i))
                star_col = CONFETTI_COLORS[i % len(CONFETTI_COLORS)]
                s_surf = pygame.Surface((star_size*2+2, star_size*2+2), pygame.SRCALPHA)
                pygame.draw.circle(s_surf, (*star_col, star_alpha), (star_size+1, star_size+1), star_size)
                screen.blit(s_surf, (sx - star_size - 1, sy - star_size - 1))

        # ── Hint "Appuie pour continuer" (après 90 frames)
        if frame > 90:
            hint_alpha = int(150 + 100 * math.sin(frame * 0.12))
            hint = font_tiny.render("Appuie pour continuer", True, (180, 180, 180))
            hint.set_alpha(hint_alpha)
            screen.blit(hint, (CX - hint.get_width()//2, CY + 132))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


def _draw_mission_coin_icon(surf, cx, cy, r=18):
    """Dessine une pièce mission (image coin_mission.png redimensionnée)."""
    size = r * 2
    img = pygame.transform.smoothscale(MISSION_COIN_IMG, (size, size))
    surf.blit(img, (cx - size // 2, cy - size // 2))

def _draw_mission_coin_badge(player, bx=None, by=18):
    mc = player.get("mission_coins", 0)
    bw, bh = 240, 40
    if bx is None:
        bx = SCREEN_WIDTH - bw - 22 - 185 - 12

    bsurf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(bsurf, (6, 14, 30, 225), (0, 0, bw, bh), border_radius=20)
    pygame.draw.rect(bsurf, (*MISSION_COIN_COLOR, 210), (0, 0, bw, bh), width=2, border_radius=20)

    shine = pygame.Surface((bw - 8, bh // 2 - 2), pygame.SRCALPHA)
    pygame.draw.rect(shine, (255, 255, 255, 12), (0, 0, bw - 8, bh//2 - 2), border_radius=20)
    bsurf.blit(shine, (4, 3))

    screen.blit(bsurf, (bx, by))
    _draw_mission_coin_icon(screen, bx + 24, by + bh//2, r=17)

    ct_txt = font_small.render(str(mc), True, MISSION_COIN_COLOR2)
    screen.blit(ct_txt, (bx + 50, by + bh//2 - ct_txt.get_height()//2))

    lbl = font_tiny.render("pièces mission", True, (100, 160, 200))
    screen.blit(lbl, (bx + 50 + ct_txt.get_width() + 8, by + bh//2 - lbl.get_height()//2))
def _draw_shop_title(CX):
    t_surf = font_med.render("BOUTIQUE", True, (220, 180, 255))
    t_shad = font_med.render("BOUTIQUE", True, (5, 5, 15))
    tx = CX - t_surf.get_width()//2
    screen.blit(t_shad, (tx + 3, 28))
    screen.blit(t_surf,  (tx,     26))
    line_w = t_surf.get_width() + 60
    lx = CX - line_w // 2
    for i in range(line_w):
        alpha = int(180 * (1 - abs(i / line_w - 0.5) * 2))
        s = pygame.Surface((1, 2), pygame.SRCALPHA)
        s.fill((180, 100, 255, alpha))
        screen.blit(s, (lx + i, 26 + t_surf.get_height() + 4))


def shop_category_screen(data, player):
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    t = 0.0
    coin_anim_t = 0
    CATEGORIES = [
        ("SKINS",       "Personnages & costumes", (180, 100, 255), "skin"),
        ("BACKGROUNDS", "Fonds d'ecran",           (60,  200, 255), "background"),
        ("MUSIQUE",     "Pistes musicales",        (255, 160,  60), "music"),
    ]
    BTN_W = 340; BTN_H = 100; GAP = 28
    total_h = len(CATEGORIES) * BTN_H + (len(CATEGORIES) - 1) * GAP
    START_Y = CY - total_h // 2 + 30
    BTN_BACK_Y = SCREEN_HEIGHT - 52

    while True:
        clock.tick(FPS)
        t += 0.04; coin_anim_t += 1
        # Vérifier si pseudo accepté/refusé (toutes les 15 secondes)
        if not hasattr(main_menu, '_pseudo_check_ts'):
            main_menu._pseudo_check_ts = 0.0
            main_menu._pseudo_was_pending = False
        _now_ts = time.time()
        if _now_ts - main_menu._pseudo_check_ts > 15.0:
            main_menu._pseudo_check_ts = _now_ts
            _is_pending = has_pending_request(player["name"])
            if main_menu._pseudo_was_pending and not _is_pending:
                # La demande a disparu → soit acceptée soit refusée
                # Stocker l'ancien pseudo AVANT d'invalider le cache
                _old_dn = _display_name_cache.get(player["name"], player["name"])
                # Forcer un rechargement frais depuis Supabase
                _invalidate_display_name(player["name"])
                try:
                    rows = _sb_get("players", f"name=eq.{player['name']}&select=display_name&limit=1")
                    if rows and rows[0].get("display_name"):
                        _new_dn = rows[0]["display_name"]
                        _display_name_cache[player["name"]] = _new_dn
                    else:
                        _new_dn = player["name"]
                except:
                    _new_dn = get_display_name(player["name"])
                if _new_dn != _old_dn:
                    push_notif(f'✓ Pseudo changé en « {_new_dn} » !', (60, 210, 110), 400)
                else:
                    push_notif("✗ Demande de pseudo refusée.", (230, 80, 80), 400)
            main_menu._pseudo_was_pending = _is_pending

        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE: return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_clicked(event, CX, BTN_BACK_Y, 240, 48): return
                for i, (label, desc, color, key) in enumerate(CATEGORIES):
                    by_cat = START_Y + i * (BTN_H + GAP) + BTN_H // 2
                    rect = pygame.Rect(CX - BTN_W//2, by_cat - BTN_H//2, BTN_W, BTN_H)
                    if rect.collidepoint(event.pos):
                        if key == "skin": shop_screen(data, player)
                        elif key == "background": shop_background_screen(data, player)
                        elif key == "music": shop_music_screen(data, player)
        screen.blit(BACKGROUND, (0, 0)); draw_overlay(170)
        _draw_shop_title(CX); _draw_shop_coin_badge(player, coin_anim_t)
        _draw_mission_coin_badge(player)
        for i, (label, desc, color, key) in enumerate(CATEGORIES):
            by_cat = START_Y + i * (BTN_H + GAP) + BTN_H // 2
            rect = pygame.Rect(CX - BTN_W//2, by_cat - BTN_H//2, BTN_W, BTN_H)
            hov = rect.collidepoint(mx, my)
            sh = pygame.Surface((BTN_W + 8, BTN_H + 8), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0, 0, 0, 80), (0, 0, BTN_W + 8, BTN_H + 8), border_radius=20)
            screen.blit(sh, (CX - BTN_W//2 - 4, by_cat - BTN_H//2 + 6))
            bs = pygame.Surface((BTN_W, BTN_H), pygame.SRCALPHA)
            bg_col = (45, 30, 90, 240) if hov else (30, 22, 65, 210)
            pygame.draw.rect(bs, bg_col, (0, 0, BTN_W, BTN_H), border_radius=18)
            th = pygame.Surface((BTN_W - 4, BTN_H // 2), pygame.SRCALPHA)
            pygame.draw.rect(th, (255, 255, 255, 18 if hov else 8), (0, 0, BTN_W - 4, BTN_H // 2), border_radius=18)
            bs.blit(th, (2, 2))
            pygame.draw.rect(bs, (*color, 255 if hov else 180), (0, 0, BTN_W, BTN_H), width=3 if hov else 2, border_radius=18)
            screen.blit(bs, (CX - BTN_W//2, by_cat - BTN_H//2))
            icon_s = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.rect(icon_s, (*color, 60), (0, 0, 44, 44), border_radius=10)
            pygame.draw.rect(icon_s, (*color, 200), (0, 0, 44, 44), width=2, border_radius=10)
            screen.blit(icon_s, (CX - BTN_W//2 + 18, by_cat - 22))
            lbl_surf = font_small.render(label, True, color if hov else WHITE)
            screen.blit(lbl_surf, (CX - BTN_W//2 + 76, by_cat - lbl_surf.get_height() - 2))
            desc_surf = font_tiny.render(desc, True, (160, 155, 195))
            screen.blit(desc_surf, (CX - BTN_W//2 + 76, by_cat + 4))
            if hov:
                arrow_x = CX + BTN_W//2 - 38
                pygame.draw.polygon(screen, color, [(arrow_x, by_cat-10),(arrow_x+14, by_cat),(arrow_x, by_cat+10)])
        draw_btn("RETOUR", CX, BTN_BACK_Y, 240, 48)
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


def _bg_fullscreen_preview(bg, player, data):
    """Affiche le fond en plein écran avec bouton Acheter/Fermer."""
    CX = SCREEN_WIDTH // 2
    CY = SCREEN_HEIGHT // 2
    BTN_CLOSE_Y  = SCREEN_HEIGHT - 58
    BTN_BUY_Y    = SCREEN_HEIGHT - 58
    BTN_CLOSE_X  = CX + 160
    BTN_BUY_X    = CX - 160
    coin_anim_t  = 0
    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0
    overlay_alpha  = 0  # fade-in

    prv_surf = BG_PREVIEW_IMAGES.get(bg["key"])

    while True:
        clock.tick(FPS)
        coin_anim_t += 1
        if feedback_timer > 0:
            feedback_timer -= 1
        overlay_alpha = min(255, overlay_alpha + 18)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Fermer
                if btn_clicked(event, BTN_CLOSE_X, BTN_CLOSE_Y, 220, 52):
                    return
                # Acheter (seulement si pas possédé)
                owned = player_owns_background(player, bg["key"])
                if not owned and btn_clicked(event, BTN_BUY_X, BTN_BUY_Y, 220, 52):
                    price = bg["price"]
                    if player.get("mission_coins", 0) >= price:
                        ok = buy_background(data, player, bg["key"])
                        if ok:
                            bg_thumb = BG_PREVIEW_IMAGES.get(bg["key"])
                            thumb_scaled = pygame.transform.smoothscale(bg_thumb, (160, 100)) if bg_thumb else None
                            play_purchase_animation(bg["name"], "background", thumb_scaled)
                            feedback_msg   = f"{bg['name']} débloqué !"
                            feedback_col   = GREEN_SOFT
                            feedback_timer = 160
                    else:
                        needed = price - player.get("mission_coins", 0)
                        feedback_msg   = f"Il manque {needed} pièces mission"
                        feedback_col   = RED_HOT
                        feedback_timer = 120

        # ── Fond plein écran ──────────────────────────────────────────────────
        if prv_surf:
            surf = prv_surf.copy()
            surf.set_alpha(overlay_alpha)
            screen.blit(surf, (0, 0))
        else:
            # Placeholder dégradé si image absente
            screen.blit(BACKGROUND, (0, 0))
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((20, 30, 60, min(200, overlay_alpha)))
            screen.blit(ov, (0, 0))
            miss_txt = font_med.render("background_custom_1.png introuvable", True, (100, 150, 200))
            screen.blit(miss_txt, (CX - miss_txt.get_width()//2, CY - miss_txt.get_height()//2))

        # Bandeau bas semi-transparent
        bar_h = 150
        bar = pygame.Surface((SCREEN_WIDTH, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bar, (6, 8, 20, 215), (0, 0, SCREEN_WIDTH, bar_h))
        pygame.draw.line(bar, (*GOLD, 120), (0, 0), (SCREEN_WIDTH, 0), 2)
        screen.blit(bar, (0, SCREEN_HEIGHT - bar_h))

        # Nom du fond en haut du bandeau
        name_y = SCREEN_HEIGHT - bar_h + 14
        name_txt = font_small.render(bg["name"].upper(), True, WHITE)
        screen.blit(name_txt, (30, name_y))

        owned = player_owns_background(player, bg["key"])
        if owned:
            # Badge débloqué aligné à gauche (côté BTN_BUY_X)
            bdg_w, bdg_h = 260, 36
            bdg = pygame.Surface((bdg_w, bdg_h), pygame.SRCALPHA)
            pygame.draw.rect(bdg, (20,70,35,230), (0,0,bdg_w,bdg_h), border_radius=18)
            pygame.draw.rect(bdg, (*GREEN_SOFT, 210), (0,0,bdg_w,bdg_h), width=2, border_radius=18)
            screen.blit(bdg, (BTN_BUY_X - bdg_w//2, BTN_BUY_Y - bdg_h//2))
            draw_checkmark(screen, BTN_BUY_X - bdg_w//2 + 20, BTN_BUY_Y, 9, GREEN_SOFT)
            dtxt = font_small.render("DÉBLOQUÉ", True, GREEN_SOFT)
            screen.blit(dtxt, (BTN_BUY_X - bdg_w//2 + 40, BTN_BUY_Y - dtxt.get_height()//2))
        else:
            # Prix affiché en haut du bandeau, sous le nom
            price      = bg["price"]
            can_afford = player.get("mission_coins", 0) >= price
            mc_icon    = pygame.transform.smoothscale(MISSION_COIN_IMG, (24, 24))
            price_col  = MISSION_COIN_COLOR2 if can_afford else (215,75,75)
            ptxt       = font_med.render(str(price), True, price_col)
            lbl        = font_tiny.render("pièces mission", True, (100, 160, 200))
            # Ligne prix centrée horizontalement côté gauche (autour de BTN_BUY_X)
            row_w  = 24 + 8 + ptxt.get_width() + 10 + lbl.get_width()
            rx0    = BTN_BUY_X - row_w // 2
            ry     = name_y + 2
            screen.blit(mc_icon, (rx0, ry))
            screen.blit(ptxt,    (rx0 + 32, ry - 2))
            screen.blit(lbl,     (rx0 + 32 + ptxt.get_width() + 10, ry + 8))

            if can_afford:
                draw_btn("ACHETER", BTN_BUY_X, BTN_BUY_Y, 220, 52, accent=True)
            else:
                hov_b = is_hov(BTN_BUY_X, BTN_BUY_Y, 220, 52)
                bs = pygame.Surface((220, 52), pygame.SRCALPHA)
                pygame.draw.rect(bs, (70,22,22,230) if hov_b else (48,14,14,210), (0,0,220,52), border_radius=12)
                pygame.draw.rect(bs, (160,55,55,200), (0,0,220,52), width=2, border_radius=12)
                screen.blit(bs, (BTN_BUY_X - 110, BTN_BUY_Y - 26))
                bt = font_small.render("ACHETER", True, (210,120,120))
                screen.blit(bt, (BTN_BUY_X - bt.get_width()//2, BTN_BUY_Y - bt.get_height()//2))

        draw_btn("FERMER", BTN_CLOSE_X, BTN_CLOSE_Y, 220, 52)

        # Hint clavier
        hint = font_tiny.render("[ECHAP] Fermer", True, (110, 120, 150))
        screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 20, SCREEN_HEIGHT - 28))

        # Feedback
        if feedback_timer > 0:
            a  = min(255, feedback_timer * 4)
            fb = font_small.render(feedback_msg, True, feedback_col)
            fw, fh = fb.get_width() + 44, fb.get_height() + 18
            fb_bg  = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb_bg, (8, 8, 20, 210), (0, 0, fw, fh), border_radius=12)
            pygame.draw.rect(fb_bg, (*feedback_col, 160), (0, 0, fw, fh), width=2, border_radius=12)
            fb_bg.set_alpha(a); fb.set_alpha(a)
            fy = SCREEN_HEIGHT // 2 - fh // 2
            screen.blit(fb_bg, (CX - fw//2, fy))
            if feedback_col == GREEN_SOFT:
                draw_checkmark(screen, CX - fb.get_width()//2 - 16, fy + fh//2, 8, GREEN_SOFT)
            screen.blit(fb, (CX - fb.get_width()//2, fy + 9))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()


def shop_background_screen(data, player):
    CX = SCREEN_WIDTH // 2
    BTN_BACK_Y  = SCREEN_HEIGHT - 52
    coin_anim_t = 0
    t           = 0.0

    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0

    # Dimensions des cartes fond d'écran
    CARD_W  = 320
    CARD_H  = 240
    GAP     = 36
    N       = len(BG_ITEMS)
    COLS    = min(N, 3)
    ROWS    = math.ceil(N / COLS)
    GRID_W  = COLS * CARD_W + (COLS - 1) * GAP
    GRID_X0 = CX - GRID_W // 2
    GRID_Y0 = 90

    BTN_W_CARD = CARD_W - 20
    BTN_H_CARD = 38

    while True:
        clock.tick(FPS)
        t += 0.04
        coin_anim_t += 1
        if feedback_timer > 0:
            feedback_timer -= 1
        mx, my = pygame.mouse.get_pos()

        # ── Calcul des zones interactives pour chaque carte ──────────────────
        card_rects   = []  # (Rect de la carte entière, Rect du bouton acheter ou None)
        preview_rects = [] # Rect de la miniature cliquable
        PREVIEW_H = 130
        PREVIEW_W = CARD_W - 20
        for ci, bg in enumerate(BG_ITEMS):
            col_i   = ci % COLS
            row_i   = ci // COLS
            card_x  = GRID_X0 + col_i * (CARD_W + GAP)
            card_y  = GRID_Y0 + row_i * (CARD_H + GAP)
            cx_card = card_x + CARD_W // 2
            card_rects.append(pygame.Rect(card_x, card_y, CARD_W, CARD_H))
            preview_rects.append(pygame.Rect(card_x + 10, card_y + 8, PREVIEW_W, PREVIEW_H))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_clicked(event, CX, BTN_BACK_Y, 240, 48):
                    return
                for ci, bg in enumerate(BG_ITEMS):
                    # Clic sur la miniature → aperçu plein écran
                    if preview_rects[ci].collidepoint(event.pos):
                        _bg_fullscreen_preview(bg, player, data)
                        break
                    # Clic sur bouton acheter
                    owned = player_owns_background(player, bg["key"])
                    if not owned:
                        col_i    = ci % COLS
                        row_i    = ci // COLS
                        cx_card  = GRID_X0 + col_i * (CARD_W + GAP) + CARD_W // 2
                        card_y   = GRID_Y0 + row_i * (CARD_H + GAP)
                        abs_btn_y = card_y + CARD_H - 10 - BTN_H_CARD // 2
                        if btn_clicked(event, cx_card, abs_btn_y, BTN_W_CARD, BTN_H_CARD):
                            price = bg["price"]
                            if player.get("mission_coins", 0) >= price:
                                ok = buy_background(data, player, bg["key"])
                                if ok:
                                    bg_thumb = BG_PREVIEW_IMAGES.get(bg["key"])
                                    thumb_scaled = pygame.transform.smoothscale(bg_thumb, (160, 100)) if bg_thumb else None
                                    play_purchase_animation(bg["name"], "background", thumb_scaled)
                                    feedback_msg   = f"{bg['name']} débloqué !"
                                    feedback_col   = GREEN_SOFT
                                    feedback_timer = 150
                            else:
                                needed         = price - player.get("mission_coins", 0)
                                feedback_msg   = f"Il manque {needed} pièces mission"
                                feedback_col   = RED_HOT
                                feedback_timer = 120

        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(170)
        _draw_shop_title(CX)
        _draw_shop_coin_badge(player, coin_anim_t)
        _draw_mission_coin_badge(player)

        for ci, bg in enumerate(BG_ITEMS):
            col_i   = ci % COLS
            row_i   = ci // COLS
            card_x  = GRID_X0 + col_i * (CARD_W + GAP)
            card_y  = GRID_Y0 + row_i * (CARD_H + GAP)
            cx_card = card_x + CARD_W // 2

            owned      = player_owns_background(player, bg["key"])
            price      = bg["price"]
            can_afford = player.get("mission_coins", 0) >= price
            hov_card   = card_rects[ci].collidepoint(mx, my)
            hov_prev   = preview_rects[ci].collidepoint(mx, my)

            if owned:
                bg_top=(22,60,35,235); bg_bot=(14,38,22,235); brd=(60,210,110,230); brd_w=2
            elif not can_afford:
                bg_top=(42,20,20,220); bg_bot=(28,12,12,220); brd=(140,55,55,190); brd_w=2
            else:
                if hov_card:
                    bg_top=(20,50,75,240); bg_bot=(12,30,55,240); brd=(*bg["color"],240); brd_w=3
                else:
                    bg_top=(14,35,60,225); bg_bot=(8,20,42,225); brd=(*bg["color"],160); brd_w=2

            cs = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            pygame.draw.rect(cs, bg_bot, (0, 0, CARD_W, CARD_H), border_radius=16)
            th = pygame.Surface((CARD_W-4, CARD_H//2), pygame.SRCALPHA)
            pygame.draw.rect(th, bg_top, (0, 0, CARD_W-4, CARD_H//2), border_radius=16)
            cs.blit(th, (2, 2))
            pygame.draw.rect(cs, brd, (0, 0, CARD_W, CARD_H), width=brd_w, border_radius=16)
            screen.blit(cs, (card_x, card_y))

            # ── Miniature cliquable ──────────────────────────────────────────
            prv_surf = BG_PREVIEW_IMAGES.get(bg["key"])
            bob = 0
            prv_rect = pygame.Rect(card_x + 10, card_y + 8, PREVIEW_W, PREVIEW_H)
            if prv_surf:
                prv_mini = pygame.transform.smoothscale(prv_surf, (PREVIEW_W, PREVIEW_H))
                screen.blit(prv_mini, prv_rect)
            else:
                ph = pygame.Surface((PREVIEW_W, PREVIEW_H), pygame.SRCALPHA)
                pygame.draw.rect(ph, (30, 40, 80, 200), (0, 0, PREVIEW_W, PREVIEW_H), border_radius=6)
                ph_txt = font_tiny.render("background_custom_1.png", True, (100, 150, 200))
                ph.blit(ph_txt, (PREVIEW_W//2 - ph_txt.get_width()//2, PREVIEW_H//2 - ph_txt.get_height()//2))
                screen.blit(ph, prv_rect)

            # Bordure de la miniature — surlignée au survol
            if hov_prev:
                pygame.draw.rect(screen, (255, 255, 255), prv_rect, width=3, border_radius=6)
                # Icône œil en coin (dessinée, sans fond carré)
                eye_cx = prv_rect.right - 20
                eye_cy = prv_rect.top + 18
                # Blanc de l'œil
                pygame.draw.ellipse(screen, (255,255,255), (eye_cx-14, eye_cy-8, 28, 16))
                # Pupille
                pygame.draw.circle(screen, (40, 100, 220), (eye_cx, eye_cy), 6)
                pygame.draw.circle(screen, (10, 30, 80),   (eye_cx, eye_cy), 3)
                pygame.draw.circle(screen, (255,255,255),  (eye_cx+2, eye_cy-2), 2)
                # Contour
                pygame.draw.ellipse(screen, (180,220,255), (eye_cx-14, eye_cy-8, 28, 16), 2)
            else:
                pygame.draw.rect(screen, brd[:3], prv_rect, width=2, border_radius=6)

            # Nom du fond
            SEP_Y = 8 + PREVIEW_H + 6
            nc    = WHITE if owned else (185, 200, 220)
            ntxt  = font_tiny.render(bg["name"].upper(), True, nc)
            screen.blit(ntxt, (cx_card - ntxt.get_width()//2, card_y + SEP_Y + 2))

            if owned:
                BADGE_Y = card_y + SEP_Y + 22 + 32
                bdg_w, bdg_h = CARD_W - 20, 30
                bdg = pygame.Surface((bdg_w, bdg_h), pygame.SRCALPHA)
                pygame.draw.rect(bdg, (25,85,45,220), (0,0,bdg_w,bdg_h), border_radius=15)
                pygame.draw.rect(bdg, (*GREEN_SOFT,200), (0,0,bdg_w,bdg_h), width=1, border_radius=15)
                screen.blit(bdg, (card_x + 10, BADGE_Y - bdg_h//2))
                draw_checkmark(screen, card_x + 10 + 18, BADGE_Y, 8, GREEN_SOFT)
                dtxt = font_tiny.render("DÉBLOQUÉ", True, GREEN_SOFT)
                screen.blit(dtxt, (cx_card - dtxt.get_width()//2 + 10, BADGE_Y - dtxt.get_height()//2))
            else:
                PRICE_Y   = card_y + SEP_Y + 22
                abs_btn_y = card_y + CARD_H - 10 - BTN_H_CARD // 2

                mc_icon   = pygame.transform.smoothscale(MISSION_COIN_IMG, (18, 18))
                price_col = MISSION_COIN_COLOR2 if can_afford else (215,75,75)
                ptxt      = font_tiny.render(str(price), True, price_col)
                label_txt = font_tiny.render("pièces mission", True, (100, 160, 200))
                row_w     = 18 + 4 + ptxt.get_width() + 6 + label_txt.get_width()
                px0       = cx_card - row_w // 2
                screen.blit(mc_icon,   (px0, PRICE_Y))
                screen.blit(ptxt,      (px0 + 22, PRICE_Y + 1))
                screen.blit(label_txt, (px0 + 22 + ptxt.get_width() + 6, PRICE_Y + 1))

                if can_afford:
                    draw_btn("ACHETER", cx_card, abs_btn_y, BTN_W_CARD, BTN_H_CARD, accent=True)
                else:
                    hov_b = is_hov(cx_card, abs_btn_y, BTN_W_CARD, BTN_H_CARD)
                    bs = pygame.Surface((BTN_W_CARD, BTN_H_CARD), pygame.SRCALPHA)
                    pygame.draw.rect(bs, (70,22,22,230) if hov_b else (48,14,14,210), (0,0,BTN_W_CARD,BTN_H_CARD), border_radius=10)
                    pygame.draw.rect(bs, (160,55,55,200), (0,0,BTN_W_CARD,BTN_H_CARD), width=2, border_radius=10)
                    screen.blit(bs, (cx_card - BTN_W_CARD//2, abs_btn_y - BTN_H_CARD//2))
                    bt = font_tiny.render("ACHETER", True, (210,120,120))
                    screen.blit(bt, (cx_card - bt.get_width()//2, abs_btn_y - bt.get_height()//2))

        # Feedback message
        if feedback_timer > 0:
            a      = min(255, feedback_timer * 5)
            fb     = font_small.render(feedback_msg, True, feedback_col)
            fw, fh = fb.get_width() + 44, fb.get_height() + 18
            fb_bg  = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb_bg, (8, 8, 20, 210), (0, 0, fw, fh), border_radius=12)
            pygame.draw.rect(fb_bg, (*feedback_col, 160), (0, 0, fw, fh), width=2, border_radius=12)
            fb_bg.set_alpha(a); fb.set_alpha(a)
            fy = GRID_Y0 + ROWS * (CARD_H + GAP) + 10
            screen.blit(fb_bg, (CX - fw//2, fy))
            if feedback_col == GREEN_SOFT:
                draw_checkmark(screen, CX - fb.get_width()//2 - 16, fy + fh//2, 8, GREEN_SOFT)
            screen.blit(fb, (CX - fb.get_width()//2, fy + 9))

        draw_btn("RETOUR", CX, BTN_BACK_Y, 240, 48)
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()




def shop_music_screen(data, player):
    """Boutique musique - grille scrollable, prete pour un afflux massif de pistes."""
    # Rechargement synchrone depuis Supabase pour garantir que les musiques sont dispo
    global MUSIC_ITEMS
    try:
        rows = _sb_get("config", "key=eq.musiques")
        if rows:
            data_m = rows[0].get("value", {"musiques": []})
            items = []
            for m in data_m.get("musiques", []):
                col = m.get("color", [255, 160, 60])
                if isinstance(col, list): col = tuple(col)
                items.append({"key": m["key"], "name": m["name"], "file": m["file"],
                               "price": m.get("price", 100), "color": col,
                               "artiste": m.get("artiste",""), "duree": m.get("duree","")})
            MUSIC_ITEMS = items
    except Exception as e:
        print(f"[SHOP_MUSIC] Erreur chargement: {e}")
        reload_music_items()

    CX          = SCREEN_WIDTH // 2
    BTN_BACK_Y  = SCREEN_HEIGHT - 52
    coin_anim_t = 0
    t           = 0.0
    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0
    MUSIC_COLOR = (255, 160, 60)

    CARD_W     = 380
    CARD_H     = 170
    GAP_X      = 28
    GAP_Y      = 18
    COLS       = max(1, min(3, (SCREEN_WIDTH - 80) // (CARD_W + GAP_X)))
    GRID_TOP   = 155
    SCROLL_BOT = SCREEN_HEIGHT - 70
    VISIBLE_H  = SCROLL_BOT - GRID_TOP
    GRID_W     = COLS * CARD_W + (COLS - 1) * GAP_X
    GRID_X0    = CX - GRID_W // 2
    BTN_W_CARD = CARD_W - 40
    BTN_H_CARD = 38

    scroll_y      = 0.0
    scroll_target = 0.0
    scroll_max    = 0

    preview_key     = None
    preview_playing = False

    def stop_preview():
        nonlocal preview_key, preview_playing
        if preview_playing:
            try: pygame.mixer.music.stop()
            except: pass
            preview_playing = False
            preview_key     = None

    def start_preview(music_key):
        nonlocal preview_key, preview_playing
        stop_preview()
        item = next((m for m in MUSIC_ITEMS if m["key"] == music_key), None)
        if item and os.path.exists(item["file"]):
            try:
                pygame.mixer.music.load(item["file"])
                pygame.mixer.music.set_volume(_music_volume() * 0.7)
                pygame.mixer.music.play(-1)
                preview_key     = music_key
                preview_playing = True
            except: pass

    FILTER_OPTIONS = ["TOUT", "POSSEDE", "ABORDABLE", "NON POSSEDE"]
    filter_idx = [0]

    def filtered_items():
        f = FILTER_OPTIONS[filter_idx[0]]
        owned_list = player.get("owned_musics", [])
        mc = player.get("mission_coins", 0)
        if f == "POSSEDE":
            return [m for m in MUSIC_ITEMS if m["key"] in owned_list]
        elif f == "ABORDABLE":
            return [m for m in MUSIC_ITEMS if m["key"] not in owned_list and m["price"] <= mc]
        elif f == "NON POSSEDE":
            return [m for m in MUSIC_ITEMS if m["key"] not in owned_list]
        return list(MUSIC_ITEMS)

    mc_icon_small = pygame.transform.smoothscale(MISSION_COIN_IMG, (18, 18))

    while True:
        clock.tick(FPS)
        t           += 0.04
        coin_anim_t += 1
        if feedback_timer > 0:
            feedback_timer -= 1
        mx, my = pygame.mouse.get_pos()

        scroll_y += (scroll_target - scroll_y) * 0.18

        items = filtered_items()
        N     = len(items)
        ROWS  = math.ceil(N / COLS) if N > 0 else 1
        total_h   = ROWS * CARD_H + (ROWS - 1) * GAP_Y
        scroll_max = max(0, total_h - VISIBLE_H)

        def card_screen_rect(ci):
            col_i = ci % COLS
            row_i = ci // COLS
            cx_ = GRID_X0 + col_i * (CARD_W + GAP_X)
            cy_ = GRID_TOP + row_i * (CARD_H + GAP_Y) - int(scroll_y)
            return pygame.Rect(cx_, cy_, CARD_W, CARD_H)

        def preview_btn_rect(ci):
            r = card_screen_rect(ci)
            return pygame.Rect(r.x + 12, r.y + CARD_H // 2 - 16, 32, 32)

        def buy_btn_y(ci):
            r = card_screen_rect(ci)
            return r.y + CARD_H - BTN_H_CARD // 2 - 14

        FILTER_Y   = GRID_TOP - 46
        FILTER_W   = 130
        FILTER_H   = 26
        FILTER_GAP = 8
        filter_total_w = len(FILTER_OPTIONS) * FILTER_W + (len(FILTER_OPTIONS) - 1) * FILTER_GAP
        FILTER_X0 = CX - filter_total_w // 2

        for event in pygame.event.get():
            if event.type == QUIT:
                stop_preview(); pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    stop_preview(); return
                if event.key == K_DOWN:
                    scroll_target = min(scroll_max, scroll_target + 60)
                if event.key == K_UP:
                    scroll_target = max(0, scroll_target - 60)
            if event.type == MOUSEWHEEL:
                scroll_target = max(0, min(scroll_max, scroll_target - event.y * 60))
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_clicked(event, CX, BTN_BACK_Y, 240, 48):
                    stop_preview(); return
                handled = False
                for fi, flbl in enumerate(FILTER_OPTIONS):
                    fx = FILTER_X0 + fi * (FILTER_W + FILTER_GAP)
                    frect = pygame.Rect(fx, FILTER_Y - FILTER_H // 2, FILTER_W, FILTER_H)
                    if frect.collidepoint(event.pos):
                        filter_idx[0] = fi
                        scroll_target = 0
                        handled = True
                        break
                if not handled and GRID_TOP <= my <= SCROLL_BOT:
                    for ci, music in enumerate(items):
                        cr = card_screen_rect(ci)
                        if cr.bottom < GRID_TOP or cr.top > SCROLL_BOT:
                            continue
                        pvr = preview_btn_rect(ci)
                        if pvr.collidepoint(event.pos):
                            if preview_key == music["key"]:
                                stop_preview()
                            else:
                                start_preview(music["key"])
                            break
                        owned = player_owns_music(player, music["key"])
                        if not owned:
                            cx_card = cr.x + CARD_W // 2
                            bby = buy_btn_y(ci)
                            if btn_clicked(event, cx_card, bby, BTN_W_CARD, BTN_H_CARD):
                                price = music["price"]
                                if player.get("mission_coins", 0) >= price:
                                    ok = buy_music(data, player, music["key"])
                                    if ok:
                                        play_purchase_animation(music["name"], "music", None)
                                        feedback_msg   = music["name"] + " debloque !"
                                        feedback_col   = GREEN_SOFT
                                        feedback_timer = 150
                                else:
                                    needed = price - player.get("mission_coins", 0)
                                    feedback_msg   = "Il manque " + str(needed) + " pieces mission"
                                    feedback_col   = RED_HOT
                                    feedback_timer = 120
                                break

        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(170)
        _draw_shop_title(CX)
        _draw_shop_coin_badge(player, coin_anim_t)
        _draw_mission_coin_badge(player)

        for fi, flbl in enumerate(FILTER_OPTIONS):
            fx    = FILTER_X0 + fi * (FILTER_W + FILTER_GAP)
            frect = pygame.Rect(fx, FILTER_Y - FILTER_H // 2, FILTER_W, FILTER_H)
            sel   = (fi == filter_idx[0])
            hov_f = frect.collidepoint(mx, my)
            fc_bg = (50, 30, 5, 240) if sel else ((30, 20, 5, 200) if hov_f else (15, 10, 4, 180))
            fc_br = (*MUSIC_COLOR, 255) if sel else ((*MUSIC_COLOR, 120) if hov_f else (*MUSIC_COLOR, 60))
            fs    = pygame.Surface((FILTER_W, FILTER_H), pygame.SRCALPHA)
            pygame.draw.rect(fs, fc_bg, (0, 0, FILTER_W, FILTER_H), border_radius=13)
            pygame.draw.rect(fs, fc_br, (0, 0, FILTER_W, FILTER_H), 2 if sel else 1, border_radius=13)
            screen.blit(fs, frect)
            ftxt = font_tiny.render(flbl, True, MUSIC_COLOR if sel else (180, 140, 80))
            screen.blit(ftxt, (fx + FILTER_W // 2 - ftxt.get_width() // 2,
                                FILTER_Y - ftxt.get_height() // 2))

        count_txt = font_tiny.render(str(N) + " musique" + ("s" if N > 1 else ""), True, (110, 110, 140))
        screen.blit(count_txt, (CX - count_txt.get_width() // 2, FILTER_Y + 16))

        clip_rect = pygame.Rect(0, GRID_TOP, SCREEN_WIDTH, VISIBLE_H)
        screen.set_clip(clip_rect)

        for ci, music in enumerate(items):
            cr       = card_screen_rect(ci)
            if cr.bottom < GRID_TOP or cr.top > SCROLL_BOT:
                continue
            owned      = player_owns_music(player, music["key"])
            price      = music["price"]
            can_afford = player.get("mission_coins", 0) >= price
            hov_card   = cr.collidepoint(mx, my)
            is_prev    = (preview_key == music["key"])
            color_raw  = music.get("color", [255, 160, 60])
            color      = tuple(color_raw) if isinstance(color_raw, list) else color_raw

            if owned:
                bg_col = (22, 60, 35, 235); brd = (*GREEN_SOFT, 230); brd_w = 2
            elif not can_afford:
                bg_col = (42, 20, 20, 220); brd = (140, 55, 55, 190); brd_w = 2
            else:
                if hov_card:
                    bg_col = (50, 35, 10, 240); brd = (*color, 240); brd_w = 3
                else:
                    bg_col = (35, 22, 8, 225); brd = (*color, 160); brd_w = 2

            cs = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            pygame.draw.rect(cs, bg_col, (0, 0, CARD_W, CARD_H), border_radius=14)
            shine = pygame.Surface((CARD_W - 4, CARD_H // 3), pygame.SRCALPHA)
            pygame.draw.rect(shine, (255, 255, 255, 12 if hov_card else 6), (0, 0, CARD_W - 4, CARD_H // 3), border_radius=14)
            cs.blit(shine, (2, 2))
            pygame.draw.rect(cs, brd, (0, 0, CARD_W, CARD_H), width=brd_w, border_radius=14)
            screen.blit(cs, cr)

            pvr     = preview_btn_rect(ci)
            prv_col = (255, 200, 80) if is_prev else (160, 110, 30)
            pvsurf  = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(pvsurf, (*prv_col, 200), (0, 0, 32, 32), border_radius=8)
            if is_prev:
                pygame.draw.rect(pvsurf, WHITE, (8, 8, 16, 16))
            else:
                pygame.draw.polygon(pvsurf, WHITE, [(8, 6), (8, 26), (26, 16)])
            screen.blit(pvsurf, pvr)

            NX = cr.x + 54; NY = cr.y + 26
            pygame.draw.ellipse(screen, color, (NX - 8, NY + 4, 16, 10))
            pygame.draw.line(screen, color, (NX + 8, NY - 14), (NX + 8, NY + 8), 3)
            pygame.draw.line(screen, color, (NX + 8, NY - 14), (NX + 22, NY - 18), 3)

            TX = cr.x + 78
            nc   = WHITE if owned else (220, 200, 170)
            ntxt = font_small.render(music["name"].upper(), True, nc)
            screen.blit(ntxt, (TX, cr.y + 12))

            artiste = music.get("artiste", "")
            duree   = music.get("duree", "")
            parts   = [p for p in [artiste, duree] if p]
            meta    = " - ".join(parts) if parts else ""
            if meta:
                mtxt = font_tiny.render(meta, True, (130, 130, 160))
                screen.blit(mtxt, (TX, cr.y + 40))

            if is_prev:
                pulse = int(200 + 55 * math.sin(t * 6))
                etxt  = font_tiny.render(">> EN LECTURE", True, (pulse, pulse, 0))
                screen.blit(etxt, (TX, cr.y + (58 if meta else 44)))

            cx_card = cr.x + CARD_W // 2
            bby = buy_btn_y(ci)

            if owned:
                bdg_y = cr.y + CARD_H * 3 // 4
                bdg_w, bdg_h = CARD_W - 20, 30
                bdg = pygame.Surface((bdg_w, bdg_h), pygame.SRCALPHA)
                pygame.draw.rect(bdg, (25, 85, 45, 220), (0, 0, bdg_w, bdg_h), border_radius=14)
                pygame.draw.rect(bdg, (*GREEN_SOFT, 200), (0, 0, bdg_w, bdg_h), 1, border_radius=14)
                screen.blit(bdg, (cr.x + 10, bdg_y - bdg_h // 2))
                draw_checkmark(screen, cr.x + 10 + 16, bdg_y, 7, GREEN_SOFT)
                dtxt = font_tiny.render("DEBLOQUE", True, GREEN_SOFT)
                screen.blit(dtxt, (cx_card - dtxt.get_width() // 2 + 8, bdg_y - dtxt.get_height() // 2))
            else:
                PRICE_Y   = cr.y + CARD_H - BTN_H_CARD - 46
                price_col = MISSION_COIN_COLOR2 if can_afford else (215, 75, 75)
                ptxt      = font_tiny.render(str(price), True, price_col)
                lbl_txt   = font_tiny.render("Pièce mission", True, (100, 160, 200))
                px0       = TX
                screen.blit(mc_icon_small, (px0, PRICE_Y - 1))
                screen.blit(ptxt,          (px0 + 22, PRICE_Y + 1))
                screen.blit(lbl_txt,       (px0 + 22 + ptxt.get_width() + 6, PRICE_Y + 1))

                if can_afford:
                    draw_btn("ACHETER", cx_card, bby, BTN_W_CARD, BTN_H_CARD, accent=True)
                else:
                    hov_b = is_hov(cx_card, bby, BTN_W_CARD, BTN_H_CARD)
                    bs = pygame.Surface((BTN_W_CARD, BTN_H_CARD), pygame.SRCALPHA)
                    pygame.draw.rect(bs, (70,22,22,230) if hov_b else (48,14,14,210), (0,0,BTN_W_CARD,BTN_H_CARD), border_radius=10)
                    pygame.draw.rect(bs, (160,55,55,200), (0,0,BTN_W_CARD,BTN_H_CARD), width=2, border_radius=10)
                    screen.blit(bs, (cx_card - BTN_W_CARD//2, bby - BTN_H_CARD//2))
                    bt = font_tiny.render("ACHETER", True, (210, 120, 120))
                    screen.blit(bt, (cx_card - bt.get_width()//2, bby - bt.get_height()//2))

        screen.set_clip(None)

        if scroll_max > 0:
            BAR_X  = SCREEN_WIDTH - 14
            BAR_H  = VISIBLE_H
            BAR_Y  = GRID_TOP
            thumb_h = max(30, int(BAR_H * VISIBLE_H / max(1, total_h)))
            thumb_y = BAR_Y + int((BAR_H - thumb_h) * scroll_y / max(1, scroll_max))
            pygame.draw.rect(screen, (30, 35, 60), (BAR_X, BAR_Y, 8, BAR_H), border_radius=4)
            pygame.draw.rect(screen, (*MUSIC_COLOR, 180), (BAR_X, thumb_y, 8, thumb_h), border_radius=4)

        if feedback_timer > 0:
            a      = min(255, feedback_timer * 5)
            fb     = font_small.render(feedback_msg, True, feedback_col)
            fw, fh = fb.get_width() + 44, fb.get_height() + 18
            fb_bg  = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb_bg, (8, 8, 20, 210), (0, 0, fw, fh), border_radius=12)
            pygame.draw.rect(fb_bg, (*feedback_col, 160), (0, 0, fw, fh), width=2, border_radius=12)
            fb_bg.set_alpha(a); fb.set_alpha(a)
            fy = SCREEN_HEIGHT // 2 - fh // 2
            screen.blit(fb_bg, (CX - fw // 2, fy))
            if feedback_col == GREEN_SOFT:
                draw_checkmark(screen, CX - fb.get_width() // 2 - 16, fy + fh // 2, 8, GREEN_SOFT)
            screen.blit(fb, (CX - fb.get_width() // 2, fy + 9))

        draw_btn("RETOUR", CX, BTN_BACK_Y, 240, 48)
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()


def shop_screen(data, player):
    SKIN_KEYS      = list(skin_images.keys())
    t              = 0.0
    coin_anim_t    = 0
    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0
    feedback_sk    = None

    CX = SCREEN_WIDTH // 2

    N      = len(SKIN_KEYS)
    COLS   = min(N, 5)
    ROWS   = math.ceil(N / COLS)
    CARD_W = 195
    CARD_H = 260
    GAP    = 28
    GRID_W  = COLS * CARD_W + (COLS - 1) * GAP
    GRID_X0 = CX - GRID_W // 2
    GRID_Y0 = 95

    BTN_BACK_Y = SCREEN_HEIGHT - 52

    while True:
        clock.tick(FPS)
        t           += 0.04
        coin_anim_t += 1
        if feedback_timer > 0:
            feedback_timer -= 1
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_clicked(event, CX, BTN_BACK_Y, 240, 48):
                    return
                for ci, sk in enumerate(SKIN_KEYS):
                    if player_owns_skin(player, sk):
                        continue
                    col_i   = ci % COLS
                    row_i   = ci // COLS
                    cx_card = GRID_X0 + col_i * (CARD_W + GAP) + CARD_W // 2
                    card_y_c = GRID_Y0 + row_i * (CARD_H + GAP)
                    abs_btn_y = card_y_c + CARD_H - 10 - 38 // 2
                    btn_w_c   = CARD_W - 20
                    if btn_clicked(event, cx_card, abs_btn_y, btn_w_c, 38):
                        price = SKIN_PRICES.get(sk, 9999)
                        if player.get("total_coins", 0) >= price:
                            ok = buy_skin(data, player, sk)
                            if ok:
                                skin_img = skin_images.get(sk)
                                play_purchase_animation(SKIN_DISPLAY_NAMES.get(sk, sk), "skin", skin_img)
                                feedback_msg   = f"{SKIN_DISPLAY_NAMES[sk]} debloque !"
                                feedback_col   = GREEN_SOFT
                                feedback_sk    = sk
                                feedback_timer = 150
                        else:
                            needed         = price - player.get("total_coins", 0)
                            feedback_msg   = f"Il manque {needed} pieces"
                            feedback_col   = RED_HOT
                            feedback_sk    = sk
                            feedback_timer = 120

        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(170)
        _draw_shop_title(CX)
        _draw_shop_coin_badge(player, coin_anim_t)
        _draw_mission_coin_badge(player)

        PAD       = 10
        IMG_TOP   = 12
        IMG_MAXH  = 80
        SEP_Y     = IMG_TOP + IMG_MAXH + 8
        NOM_Y     = SEP_Y + 6
        NOM_H     = font_tiny.get_height()
        BOT_START = NOM_Y + NOM_H + 6
        BTN_H     = 38
        BTN_Y     = CARD_H - PAD - BTN_H // 2
        PRICE_Y   = BTN_Y - BTN_H // 2 - NOM_H - 4
        BADGE_Y   = (BOT_START + CARD_H - PAD) // 2
        BTN_W     = CARD_W - PAD * 2

        for ci, sk in enumerate(SKIN_KEYS):
            col_i   = ci % COLS
            row_i   = ci // COLS
            card_x  = GRID_X0 + col_i * (CARD_W + GAP)
            card_y  = GRID_Y0 + row_i * (CARD_H + GAP)
            cx_card = card_x + CARD_W // 2

            owned_sk   = player_owns_skin(player, sk)
            price      = SKIN_PRICES.get(sk, 9999)
            can_afford = player.get("total_coins", 0) >= price
            hov_card   = pygame.Rect(card_x, card_y, CARD_W, CARD_H).collidepoint(mx, my)

            if owned_sk:
                bg_top=(22,60,35,235); bg_bot=(14,38,22,235); brd=(60,210,110,230); brd_w=2
            elif not can_afford:
                bg_top=(42,20,20,220); bg_bot=(28,12,12,220); brd=(140,55,55,190); brd_w=2
            else:
                if hov_card:
                    bg_top=(35,28,80,240); bg_bot=(20,16,55,240); brd=(*GOLD,240); brd_w=3
                else:
                    bg_top=(22,18,55,225); bg_bot=(14,10,36,225); brd=(110,85,200,200); brd_w=2

            cs = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            pygame.draw.rect(cs, bg_bot, (0, 0, CARD_W, CARD_H), border_radius=16)
            th = pygame.Surface((CARD_W-4, CARD_H//2), pygame.SRCALPHA)
            pygame.draw.rect(th, bg_top, (0, 0, CARD_W-4, CARD_H//2), border_radius=16)
            cs.blit(th, (2, 2))
            pygame.draw.rect(cs, brd, (0, 0, CARD_W, CARD_H), width=brd_w, border_radius=16)
            screen.blit(cs, (card_x, card_y))

            raw = skin_images[sk]
            sf  = min(IMG_MAXH / raw.get_width(), IMG_MAXH / raw.get_height())
            pw  = max(1, int(raw.get_width() * sf))
            ph  = max(1, int(raw.get_height() * sf))
            prv = pygame.transform.smoothscale(raw, (pw, ph))
            bob = int(math.sin(t*2.0+ci*0.9)*5) if owned_sk else 0
            screen.blit(prv, (cx_card - pw//2, card_y + IMG_TOP + (IMG_MAXH-ph)//2 + bob))

            sc = (60,210,110,70) if owned_sk else (100,80,180,55)
            ss = pygame.Surface((CARD_W-PAD*2, 1), pygame.SRCALPHA); ss.fill(sc)
            screen.blit(ss, (card_x+PAD, card_y+SEP_Y))

            nc   = WHITE if owned_sk else (185,180,210)
            ntxt = font_tiny.render(SKIN_DISPLAY_NAMES[sk].upper(), True, nc)
            if ntxt.get_width() > CARD_W - PAD*2:
                ntxt = pygame.transform.smoothscale(ntxt, (CARD_W-PAD*2, ntxt.get_height()))
            screen.blit(ntxt, (cx_card - ntxt.get_width()//2, card_y+NOM_Y))

            if owned_sk:
                bdg_w, bdg_h = CARD_W - PAD*2, 30
                bdg = pygame.Surface((bdg_w, bdg_h), pygame.SRCALPHA)
                pygame.draw.rect(bdg, (25,85,45,220), (0,0,bdg_w,bdg_h), border_radius=15)
                pygame.draw.rect(bdg, (*GREEN_SOFT,200), (0,0,bdg_w,bdg_h), width=1, border_radius=15)
                screen.blit(bdg, (card_x+PAD, card_y+BADGE_Y-bdg_h//2))
                draw_checkmark(screen, card_x+PAD+18, card_y+BADGE_Y, 8, GREEN_SOFT)
                dtxt = font_tiny.render("DEBLOQUE", True, GREEN_SOFT)
                screen.blit(dtxt, (cx_card - dtxt.get_width()//2 + 10, card_y+BADGE_Y - dtxt.get_height()//2))
            else:
                coin_ic   = pygame.transform.smoothscale(COIN_IMG, (18,18))
                price_col = GOLD if can_afford else (215,75,75)
                ptxt      = font_tiny.render(str(price), True, price_col)
                row_w     = 18 + 4 + ptxt.get_width()
                px0       = cx_card - row_w // 2
                screen.blit(coin_ic, (px0, card_y+PRICE_Y))
                screen.blit(ptxt,    (px0+22, card_y+PRICE_Y+1))

                abs_btn_y = card_y + BTN_Y
                if can_afford:
                    draw_btn("ACHETER", cx_card, abs_btn_y, BTN_W, BTN_H, accent=True)
                else:
                    hov_b = is_hov(cx_card, abs_btn_y, BTN_W, BTN_H)
                    bs = pygame.Surface((BTN_W, BTN_H), pygame.SRCALPHA)
                    pygame.draw.rect(bs, (70,22,22,230) if hov_b else (48,14,14,210), (0,0,BTN_W,BTN_H), border_radius=10)
                    pygame.draw.rect(bs, (160,55,55,200), (0,0,BTN_W,BTN_H), width=2, border_radius=10)
                    screen.blit(bs, (cx_card-BTN_W//2, abs_btn_y-BTN_H//2))
                    bt = font_tiny.render("ACHETER", True, (210,120,120))
                    screen.blit(bt, (cx_card-bt.get_width()//2, abs_btn_y-bt.get_height()//2))

        if feedback_timer > 0:
            a    = min(255, feedback_timer * 5)
            fb   = font_small.render(feedback_msg, True, feedback_col)
            fw, fh = fb.get_width() + 44, fb.get_height() + 18
            fb_bg = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(fb_bg, (8, 8, 20, 210), (0, 0, fw, fh), border_radius=12)
            pygame.draw.rect(fb_bg, (*feedback_col, 160), (0, 0, fw, fh), width=2, border_radius=12)
            fb_bg.set_alpha(a)
            fb.set_alpha(a)
            fy = GRID_Y0 + ROWS * (CARD_H + GAP) + 10
            screen.blit(fb_bg, (CX - fw//2, fy))
            if feedback_col == GREEN_SOFT:
                draw_checkmark(screen, CX - fb.get_width()//2 - 16, fy + fh//2, 8, GREEN_SOFT)
            screen.blit(fb, (CX - fb.get_width()//2, fy + 9))

        draw_btn("RETOUR", CX, BTN_BACK_Y, 240, 48)
        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()
# ══════════════════════════════════════════════════════════════════════════════
#  PROFIL
# ══════════════════════════════════════════════════════════════════════════════
AVATAR_COLORS = [
    (255, 80,  80),  (255, 140, 40), (255, 215, 60),
    (80,  220, 120), (60,  200, 255),(180, 80,  255),
    (255, 100, 180), (80,  255, 220),(200, 200, 200),
]

def _file_browser(start_dir=None):
    """
    Explorateur de fichiers intégré dans la fenêtre du jeu.
    Retourne le chemin absolu du fichier sélectionné, ou None si annulé.
    """
    EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

    if start_dir is None:
        home = os.path.expanduser("~")
        found = None
        for sub in ("Documents", "Mes documents", "My Documents"):
            p = os.path.join(home, sub)
            if os.path.isdir(p):
                found = p
                break
        start_dir = found if found else home

    current_dir   = os.path.abspath(start_dir)
    selected_idx  = None   # index dans entries
    scroll_offset = 0

    fn_title  = pygame.font.SysFont("Impact",  26)
    fn_item   = pygame.font.SysFont("Verdana", 14)
    fn_small  = pygame.font.SysFont("Verdana", 11)
    fn_btn    = pygame.font.SysFont("Verdana", 13, bold=True)

    CLR_BG      = (8,  10, 22)
    CLR_PANEL   = (18, 22, 45)
    CLR_BORDER  = (50, 60, 110)
    CLR_ITEM    = (26, 30, 56)
    CLR_ITEM_HL = (40, 50, 100)
    CLR_SEL     = (50, 80, 180)
    CLR_SEL_HL  = (70, 105, 220)
    CLR_GOLD    = (255, 215, 60)
    CLR_WHITE   = (255, 255, 255)
    CLR_GREY    = (130, 140, 170)
    CLR_DIR     = (120, 180, 255)
    CLR_FILE    = (200, 210, 240)
    CLR_GREEN   = (60, 200, 110)
    CLR_RED2    = (220, 60, 60)

    PANEL_W  = min(900, SCREEN_WIDTH  - 80)
    PANEL_H  = min(680, SCREEN_HEIGHT - 80)
    PANEL_X  = SCREEN_WIDTH  // 2 - PANEL_W // 2
    PANEL_Y  = SCREEN_HEIGHT // 2 - PANEL_H // 2

    ITEM_H   = 34
    LIST_X   = PANEL_X + 14
    LIST_W   = PANEL_W - 28
    LIST_TOP = PANEL_Y + 90
    LIST_BOT = PANEL_Y + PANEL_H - 70
    VISIBLE  = (LIST_BOT - LIST_TOP) // ITEM_H

    BTN_H  = 40
    BTN_W  = 140
    BTN_OK_CX  = PANEL_X + PANEL_W - BTN_W - 16
    BTN_ANN_CX = PANEL_X + PANEL_W - BTN_W * 2 - 28
    BTN_Y_CY   = PANEL_Y + PANEL_H - BTN_H // 2 - 14

    SB_W  = 12   # scrollbar width
    SB_X  = LIST_X + LIST_W - SB_W

    def load_entries(d):
        entries = []
        try:
            # Dossier parent
            parent = os.path.dirname(d)
            if parent != d:
                entries.append(("..", parent, True))
            names = sorted(os.listdir(d), key=lambda n: (not os.path.isdir(os.path.join(d, n)), n.lower()))
            for name in names:
                full = os.path.join(d, name)
                is_dir = os.path.isdir(full)
                if is_dir:
                    entries.append((name, full, True))
                elif os.path.splitext(name)[1].lower() in EXTS:
                    entries.append((name, full, False))
        except PermissionError:
            pass
        return entries

    entries = load_entries(current_dir)
    clock_fb = pygame.time.Clock()

    while True:
        clock_fb.tick(60)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key == pygame.K_RETURN:
                    if selected_idx is not None:
                        name, full, is_dir = entries[selected_idx]
                        if is_dir:
                            current_dir = full
                            entries = load_entries(current_dir)
                            selected_idx = None
                            scroll_offset = 0
                        else:
                            return full
                elif ev.key == pygame.K_UP:
                    if selected_idx is None:
                        selected_idx = 0
                    else:
                        selected_idx = max(0, selected_idx - 1)
                    if selected_idx < scroll_offset:
                        scroll_offset = selected_idx
                elif ev.key == pygame.K_DOWN:
                    if selected_idx is None:
                        selected_idx = 0
                    else:
                        selected_idx = min(len(entries) - 1, selected_idx + 1)
                    if selected_idx >= scroll_offset + VISIBLE:
                        scroll_offset = selected_idx - VISIBLE + 1
            elif ev.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(len(entries) - VISIBLE, scroll_offset - ev.y))
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Clic sur un item
                for i in range(VISIBLE):
                    idx = scroll_offset + i
                    if idx >= len(entries):
                        break
                    item_rect = pygame.Rect(LIST_X, LIST_TOP + i * ITEM_H, LIST_W - SB_W - 4, ITEM_H - 2)
                    if item_rect.collidepoint(mx, my):
                        if selected_idx == idx:
                            # Double-clic simulé par second clic sur même item
                            name, full, is_dir = entries[idx]
                            if is_dir:
                                current_dir = full
                                entries = load_entries(current_dir)
                                selected_idx = None
                                scroll_offset = 0
                            else:
                                return full
                        else:
                            selected_idx = idx
                        break
                # Bouton OK
                ok_rect  = pygame.Rect(BTN_OK_CX  - BTN_W//2, BTN_Y_CY - BTN_H//2, BTN_W, BTN_H)
                ann_rect = pygame.Rect(BTN_ANN_CX - BTN_W//2, BTN_Y_CY - BTN_H//2, BTN_W, BTN_H)
                if ok_rect.collidepoint(mx, my):
                    if selected_idx is not None:
                        name, full, is_dir = entries[selected_idx]
                        if not is_dir:
                            return full
                elif ann_rect.collidepoint(mx, my):
                    return None
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                pass

        # ── Dessin ──────────────────────────────────────────────────────────
        screen.fill(CLR_BG)

        # Panneau
        pygame.draw.rect(screen, CLR_PANEL,  (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), border_radius=14)
        pygame.draw.rect(screen, CLR_BORDER, (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 2, border_radius=14)

        # Titre
        t = fn_title.render("Choisir une photo de profil", True, CLR_GOLD)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, PANEL_Y + 14))

        # Chemin courant
        path_str = current_dir if len(current_dir) <= 70 else "..." + current_dir[-67:]
        pt = fn_small.render(path_str, True, CLR_GREY)
        screen.blit(pt, (LIST_X, PANEL_Y + 54))

        # Zone liste
        pygame.draw.rect(screen, (12, 15, 30), (LIST_X, LIST_TOP, LIST_W, LIST_BOT - LIST_TOP), border_radius=6)

        for i in range(VISIBLE):
            idx = scroll_offset + i
            if idx >= len(entries):
                break
            name, full, is_dir = entries[idx]
            iy = LIST_TOP + i * ITEM_H
            item_rect = pygame.Rect(LIST_X + 1, iy + 1, LIST_W - SB_W - 6, ITEM_H - 2)
            hov = item_rect.collidepoint(mx, my)
            if idx == selected_idx:
                col_bg = CLR_SEL_HL if hov else CLR_SEL
            else:
                col_bg = CLR_ITEM_HL if hov else CLR_ITEM
            pygame.draw.rect(screen, col_bg, item_rect, border_radius=5)

            # Icone dossier / fichier (petit carré coloré)
            icon_col = CLR_DIR if is_dir else CLR_FILE
            pygame.draw.rect(screen, icon_col, (item_rect.x + 6, iy + ITEM_H//2 - 7, 14, 14), border_radius=3)
            if is_dir:
                pygame.draw.rect(screen, CLR_DIR, (item_rect.x + 6, iy + ITEM_H//2 - 10, 8, 4), border_radius=2)

            label = name
            col_txt = CLR_DIR if is_dir else CLR_WHITE
            lt = fn_item.render(label, True, col_txt)
            screen.blit(lt, (item_rect.x + 28, iy + ITEM_H//2 - lt.get_height()//2))

        # Scrollbar
        total = len(entries)
        if total > VISIBLE:
            sb_h_total = LIST_BOT - LIST_TOP
            sb_h = max(30, sb_h_total * VISIBLE // total)
            sb_y = LIST_TOP + sb_h_total * scroll_offset // total
            pygame.draw.rect(screen, (30, 35, 70), (SB_X, LIST_TOP, SB_W, sb_h_total), border_radius=6)
            pygame.draw.rect(screen, CLR_GREY,     (SB_X + 2, sb_y, SB_W - 4, sb_h), border_radius=5)

        # Ligne séparatrice
        pygame.draw.line(screen, CLR_BORDER, (PANEL_X + 10, LIST_BOT + 4), (PANEL_X + PANEL_W - 10, LIST_BOT + 4), 1)

        # Hint fichier sélectionné
        if selected_idx is not None and selected_idx < len(entries):
            sname, sfull, sis_dir = entries[selected_idx]
            if not sis_dir:
                sel_txt = fn_small.render(sname, True, CLR_GOLD)
                screen.blit(sel_txt, (LIST_X, BTN_Y_CY - sel_txt.get_height()//2))

        # Bouton Ouvrir
        ok_rect  = pygame.Rect(BTN_OK_CX  - BTN_W//2, BTN_Y_CY - BTN_H//2, BTN_W, BTN_H)
        ann_rect = pygame.Rect(BTN_ANN_CX - BTN_W//2, BTN_Y_CY - BTN_H//2, BTN_W, BTN_H)
        ok_en = selected_idx is not None and selected_idx < len(entries) and not entries[selected_idx][2]

        for rect, label, enabled, accent in [
            (ok_rect,  "OUVRIR",  ok_en, True),
            (ann_rect, "ANNULER", True,  False),
        ]:
            hov = rect.collidepoint(mx, my)
            if accent and enabled:
                bg = (50, 180, 100) if not hov else (70, 210, 120)
                bdr = CLR_GREEN
            elif not enabled:
                bg  = (25, 28, 50)
                bdr = (50, 55, 80)
            else:
                bg  = (40, 44, 80) if not hov else (55, 62, 110)
                bdr = CLR_GREY
            pygame.draw.rect(screen, bg,  rect, border_radius=9)
            pygame.draw.rect(screen, bdr, rect, 2, border_radius=9)
            col_t = CLR_WHITE if enabled else (70, 75, 100)
            lt2 = fn_btn.render(label, True, col_t)
            screen.blit(lt2, (rect.centerx - lt2.get_width()//2, rect.centery - lt2.get_height()//2))

        # Hint bas
        hint = fn_small.render("Clic pour selectionner  |  Double-clic pour ouvrir  |  Entree pour valider  |  Echap pour annuler", True, CLR_GREY)
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, PANEL_Y + PANEL_H + 6))

        pygame.display.flip()


def _crop_photo_editor(path):
    """
    Éditeur interactif de recadrage de photo de profil.
    - Glisser-déposer pour déplacer l'image sous le cercle
    - Molette / boutons +/- pour zoomer
    - Aperçu en temps réel du résultat circulaire
    Retourne une surface pygame (carré) prête à être sauvegardée, ou None si annulé.
    """
    try:
        from PIL import Image as _PILImage
        import io as _io
        pil_img = _PILImage.open(path).convert("RGBA")
    except Exception:
        try:
            raw = _pygame_load(path).convert_alpha()
            pil_img = None
        except Exception:
            return None

    # ── Dimensions — rendu dans la fenetre du jeu existante ─────────────────
    WIN_W, WIN_H = SCREEN_WIDTH, SCREEN_HEIGHT
    PREVIEW_R    = min(200, SCREEN_HEIGHT // 3)
    CX, CY       = WIN_W // 2, WIN_H // 2 - 30
    editor_surf  = screen   # on dessine directement sur la surface du jeu

    # ── Charger l'image source ───────────────────────────────────────────────
    if pil_img is not None:
        pil_w, pil_h = pil_img.size
        # Convertir PIL → pygame
        def _pil_to_pg(pil):
            buf = _io.BytesIO()
            pil.save(buf, format="PNG")
            buf.seek(0)
            return pygame.image.load(buf).convert_alpha()
        src_pg = _pil_to_pg(pil_img)
    else:
        src_pg   = raw
        pil_w, pil_h = src_pg.get_size()

    # ── État initial : zoom pour que l'image remplisse le cercle ────────────
    min_dim   = min(pil_w, pil_h)
    zoom      = (PREVIEW_R * 2) / min_dim   # zoom de base
    zoom_min  = zoom * 0.3
    zoom_max  = zoom * 8.0

    # offset = coin haut-gauche de l'image affichée (dans l'espace de la fenêtre)
    img_w = int(pil_w * zoom)
    img_h = int(pil_h * zoom)
    off_x = CX - img_w // 2
    off_y = CY - img_h // 2

    dragging = False
    drag_start_mouse = (0, 0)
    drag_start_off   = (0, 0)

    font_title = pygame.font.SysFont("Impact",   26)
    font_btn   = pygame.font.SysFont("Verdana",  13, bold=True)
    font_hint  = pygame.font.SysFont("Verdana",  11)

    CLR_BG     = (8,  10, 22)
    CLR_PANEL  = (20, 24, 45)
    CLR_GOLD   = (255, 215, 60)
    CLR_WHITE  = (255, 255, 255)
    CLR_GREY   = (130, 140, 170)
    CLR_GREEN  = (60,  200, 110)
    CLR_RED    = (220,  60,  60)
    CLR_DARK   = (10,   12,  25)

    BTN_W, BTN_H = 160, 44
    BTN_OK_X  = WIN_W // 2 + 90
    BTN_ANN_X = WIN_W // 2 - 90
    BTN_Y     = WIN_H - 52

    ZOOM_BTN_SIZE = 38
    ZOOM_PLUS_X  = WIN_W // 2 + PREVIEW_R + 30
    ZOOM_MINUS_X = WIN_W // 2 + PREVIEW_R + 30
    ZOOM_PLUS_Y  = CY - 26
    ZOOM_MINUS_Y = CY + 26

    # Cache de la surface scalée (évite de recalculer à chaque frame si rien n'a changé)
    _cached_zoom  = None
    _cached_surf  = None

    def get_scaled():
        nonlocal _cached_zoom, _cached_surf
        if _cached_zoom != zoom:
            iw = max(1, int(pil_w * zoom))
            ih = max(1, int(pil_h * zoom))
            _cached_surf  = pygame.transform.smoothscale(src_pg, (iw, ih))
            _cached_zoom  = zoom
        return _cached_surf

    def clamp_offset(ox, oy, iw, ih):
        """Empêche l'image de sortir trop loin du cercle (garde toujours au moins 1/4 du cercle couvert)."""
        margin = PREVIEW_R // 2
        ox = min(ox, CX + PREVIEW_R - margin)
        ox = max(ox, CX - iw - PREVIEW_R + margin)
        oy = min(oy, CY + PREVIEW_R - margin)
        oy = max(oy, CY - ih - PREVIEW_R + margin)
        return ox, oy

    def render_preview_circle(scaled_surf, ox, oy):
        """Retourne une surface circulaire (2R x 2R) représentant l'aperçu final."""
        size = PREVIEW_R * 2
        result = pygame.Surface((size, size), pygame.SRCALPHA)
        # Coller l'image au bon décalage
        result.blit(scaled_surf, (ox - (CX - PREVIEW_R), oy - (CY - PREVIEW_R)))
        # Masque circulaire
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (PREVIEW_R, PREVIEW_R), PREVIEW_R)
        result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return result

    def draw_button(surf, label, cx, cy, w, h, accent=False, hover=False):
        col_bg  = (50, 180, 100) if accent else (40, 44, 80)
        col_bg  = tuple(min(255, c + 30) for c in col_bg) if hover else col_bg
        col_bdr = CLR_GREEN if accent else CLR_GREY
        rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
        pygame.draw.rect(surf, col_bg,  rect, border_radius=10)
        pygame.draw.rect(surf, col_bdr, rect, 2, border_radius=10)
        t = font_btn.render(label, True, CLR_WHITE)
        surf.blit(t, (cx - t.get_width()//2, cy - t.get_height()//2))
        return rect

    clock_ed = pygame.time.Clock()
    result_surf = None
    running = True

    while running:
        clock_ed.tick(60)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_RETURN:
                    result_surf = "confirm"
                    running = False
                elif ev.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    prev_zoom = zoom
                    zoom = min(zoom_max, zoom * 1.1)
                    # Zoom centré sur le centre du cercle
                    ratio = zoom / prev_zoom
                    off_x = CX - (CX - off_x) * ratio
                    off_y = CY - (CY - off_y) * ratio
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    prev_zoom = zoom
                    zoom = max(zoom_min, zoom / 1.1)
                    ratio = zoom / prev_zoom
                    off_x = CX - (CX - off_x) * ratio
                    off_y = CY - (CY - off_y) * ratio

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    # Vérifier clic boutons
                    scaled = get_scaled()
                    iw, ih = scaled.get_size()
                    ok_rect  = pygame.Rect(BTN_OK_X  - BTN_W//2, BTN_Y - BTN_H//2, BTN_W, BTN_H)
                    ann_rect = pygame.Rect(BTN_ANN_X - BTN_W//2, BTN_Y - BTN_H//2, BTN_W, BTN_H)
                    zp_rect  = pygame.Rect(ZOOM_PLUS_X  - ZOOM_BTN_SIZE//2, ZOOM_PLUS_Y  - ZOOM_BTN_SIZE//2, ZOOM_BTN_SIZE, ZOOM_BTN_SIZE)
                    zm_rect  = pygame.Rect(ZOOM_MINUS_X - ZOOM_BTN_SIZE//2, ZOOM_MINUS_Y - ZOOM_BTN_SIZE//2, ZOOM_BTN_SIZE, ZOOM_BTN_SIZE)
                    if ok_rect.collidepoint(mx, my):
                        result_surf = "confirm"; running = False
                    elif ann_rect.collidepoint(mx, my):
                        running = False
                    elif zp_rect.collidepoint(mx, my):
                        prev_zoom = zoom
                        zoom = min(zoom_max, zoom * 1.15)
                        ratio = zoom / prev_zoom
                        off_x = CX - (CX - off_x) * ratio
                        off_y = CY - (CY - off_y) * ratio
                    elif zm_rect.collidepoint(mx, my):
                        prev_zoom = zoom
                        zoom = max(zoom_min, zoom / 1.15)
                        ratio = zoom / prev_zoom
                        off_x = CX - (CX - off_x) * ratio
                        off_y = CY - (CY - off_y) * ratio
                    else:
                        dragging = True
                        drag_start_mouse = (mx, my)
                        drag_start_off   = (off_x, off_y)
                elif ev.button == 3:
                    dragging = False

            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    dragging = False

            elif ev.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = mx - drag_start_mouse[0]
                    dy = my - drag_start_mouse[1]
                    new_ox = drag_start_off[0] + dx
                    new_oy = drag_start_off[1] + dy
                    scaled = get_scaled()
                    iw, ih = scaled.get_size()
                    off_x, off_y = clamp_offset(new_ox, new_oy, iw, ih)

            elif ev.type == pygame.MOUSEWHEEL:
                prev_zoom = zoom
                factor = 1.08 if ev.y > 0 else 1/1.08
                zoom = max(zoom_min, min(zoom_max, zoom * factor))
                ratio = zoom / prev_zoom
                off_x = CX - (CX - off_x) * ratio
                off_y = CY - (CY - off_y) * ratio

        # ── Dessin ──────────────────────────────────────────────────────────
        editor_surf.fill(CLR_BG)

        # Titre
        title_t = font_title.render("Recadrer la photo de profil", True, CLR_GOLD)
        editor_surf.blit(title_t, (WIN_W//2 - title_t.get_width()//2, 18))

        scaled = get_scaled()
        iw, ih = scaled.get_size()

        # Fond sombre derrière la zone de travail
        work_rect = pygame.Rect(CX - PREVIEW_R - 4, CY - PREVIEW_R - 4, PREVIEW_R*2 + 8, PREVIEW_R*2 + 8)
        pygame.draw.rect(editor_surf, CLR_DARK, work_rect, border_radius=PREVIEW_R + 4)

        # Image source (en dehors du cercle aussi, semi-transparente)
        dimmed = scaled.copy()
        dimmed.set_alpha(70)
        editor_surf.blit(dimmed, (int(off_x), int(off_y)))

        # Découpe nette dans le cercle
        preview = render_preview_circle(scaled, int(off_x), int(off_y))
        editor_surf.blit(preview, (CX - PREVIEW_R, CY - PREVIEW_R))

        # Bordure dorée du cercle
        pygame.draw.circle(editor_surf, CLR_GOLD, (CX, CY), PREVIEW_R, 3)

        # Overlay sombre autour du cercle pour mettre en valeur
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 120), (0, 0, WIN_W, WIN_H))
        pygame.draw.circle(overlay, (0, 0, 0, 0), (CX, CY), PREVIEW_R)
        editor_surf.blit(overlay, (0, 0))
        # Redessiner le cercle par-dessus l'overlay
        editor_surf.blit(preview, (CX - PREVIEW_R, CY - PREVIEW_R))
        pygame.draw.circle(editor_surf, CLR_GOLD, (CX, CY), PREVIEW_R, 3)

        # Boutons zoom
        zp_rect = pygame.Rect(ZOOM_PLUS_X  - ZOOM_BTN_SIZE//2, ZOOM_PLUS_Y  - ZOOM_BTN_SIZE//2, ZOOM_BTN_SIZE, ZOOM_BTN_SIZE)
        zm_rect = pygame.Rect(ZOOM_MINUS_X - ZOOM_BTN_SIZE//2, ZOOM_MINUS_Y - ZOOM_BTN_SIZE//2, ZOOM_BTN_SIZE, ZOOM_BTN_SIZE)
        h_zp = zp_rect.collidepoint(mx, my)
        h_zm = zm_rect.collidepoint(mx, my)
        for rect, label, hov in [(zp_rect, "+", h_zp), (zm_rect, "–", h_zm)]:
            col = (80, 90, 140) if not hov else (110, 125, 200)
            pygame.draw.rect(editor_surf, col, rect, border_radius=8)
            pygame.draw.rect(editor_surf, CLR_GREY, rect, 2, border_radius=8)
            lt = font_btn.render(label, True, CLR_WHITE)
            editor_surf.blit(lt, (rect.centerx - lt.get_width()//2, rect.centery - lt.get_height()//2))

        # Indicateur de zoom
        zoom_pct = int(zoom / (PREVIEW_R * 2 / min(pil_w, pil_h)) * 100)
        zoom_txt = font_hint.render(f"{zoom_pct}%", True, CLR_GREY)
        editor_surf.blit(zoom_txt, (ZOOM_PLUS_X - zoom_txt.get_width()//2, CY - 6))

        # Hints
        hints = [
            "Cliquer-glisser pour deplacer l'image",
            "Molette / boutons +  -  pour zoomer",
            "Entree pour valider  |  Echap pour annuler",
        ]
        for i, h in enumerate(hints):
            ht = font_hint.render(h, True, CLR_GREY)
            editor_surf.blit(ht, (WIN_W//2 - ht.get_width()//2, CY + PREVIEW_R + 16 + i * 18))

        # Boutons Valider / Annuler
        ok_rect  = pygame.Rect(BTN_OK_X  - BTN_W//2, BTN_Y - BTN_H//2, BTN_W, BTN_H)
        ann_rect = pygame.Rect(BTN_ANN_X - BTN_W//2, BTN_Y - BTN_H//2, BTN_W, BTN_H)
        draw_button(editor_surf, "VALIDER",  BTN_OK_X,  BTN_Y, BTN_W, BTN_H, accent=True,  hover=ok_rect.collidepoint(mx, my))
        draw_button(editor_surf, "ANNULER", BTN_ANN_X, BTN_Y, BTN_W, BTN_H, accent=False, hover=ann_rect.collidepoint(mx, my))

        pygame.display.flip()

    if result_surf != "confirm":
        return None

    # ── Générer l'image finale recadrée (OUTPUT_SIZE x OUTPUT_SIZE) ──────────
    OUTPUT_SIZE = 256
    final_surf = pygame.Surface((OUTPUT_SIZE, OUTPUT_SIZE), pygame.SRCALPHA)
    # Calculer les coordonnées dans l'espace image source
    scale_factor = OUTPUT_SIZE / (PREVIEW_R * 2)
    # Position du coin haut-gauche du cercle dans la fenêtre
    circle_left = CX - PREVIEW_R
    circle_top  = CY - PREVIEW_R
    # Coordonnées dans l'image scalée
    src_x = circle_left - int(off_x)
    src_y = circle_top  - int(off_y)
    src_w = PREVIEW_R * 2
    src_h = PREVIEW_R * 2
    # Extraire la région et la scaler à OUTPUT_SIZE
    scaled = get_scaled()
    iw, ih = scaled.get_size()
    # Créer une surface de la zone du cercle
    crop_surf = pygame.Surface((src_w, src_h), pygame.SRCALPHA)
    crop_surf.blit(scaled, (-src_x, -src_y))
    final_pg = pygame.transform.smoothscale(crop_surf, (OUTPUT_SIZE, OUTPUT_SIZE))
    # Appliquer le masque circulaire
    mask_out = pygame.Surface((OUTPUT_SIZE, OUTPUT_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(mask_out, (255,255,255,255), (OUTPUT_SIZE//2, OUTPUT_SIZE//2), OUTPUT_SIZE//2)
    final_pg.blit(mask_out, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    return final_pg


def _import_profile_photo(player, data):
    """Ouvre l'explorateur Windows natif pour choisir l'image, puis lance l'editeur de recadrage dans le jeu."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        home = os.path.expanduser("~")
        docs = None
        for sub in ("Documents", "Mes documents", "My Documents"):
            p = os.path.join(home, sub)
            if os.path.isdir(p):
                docs = p
                break
        initial_dir = docs if docs else home
        path = filedialog.askopenfilename(
            title="Choisir une photo de profil",
            initialdir=initial_dir,
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("Tous", "*.*")]
        )
        root.destroy()
        if not path:
            return False, "Annule"

        cropped_surf = _crop_photo_editor(path)
        if cropped_surf is None:
            return False, "Annule"

        pp_dir = os.path.join("assets", "sprites", "pp")
        os.makedirs(pp_dir, exist_ok=True)
        safe_name = "".join(c for c in player["name"] if c.isalnum() or c in "_-") or "player"
        dest = os.path.join(pp_dir, f"{safe_name}_crop.png")
        pygame.image.save(cropped_surf, dest)
        player["avatar_image_path"] = dest
        save_data(data)
        return True, "Photo importee !"
    except Exception as e:
        return False, f"Erreur : {e}"
def pseudo_request_screen(player):
    """Écran de demande de changement de pseudo."""
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2

    PANEL_W  = min(900, SCREEN_WIDTH - 80)
    PANEL_H  = 480
    PANEL_CY = CY

    session_name  = player["name"]
    current_disp  = get_display_name(session_name)
    already_sent  = has_pending_request(session_name)

    INPUT_W  = min(700, PANEL_W - 120)
    INPUT_H  = 52
    INPUT_X  = CX - INPUT_W // 2
    INPUT_Y  = CY - 30

    input_text   = ""
    input_active = True
    cursor_vis   = True
    cursor_timer = 0

    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0

    BTN_SEND_Y = INPUT_Y + INPUT_H + 68
    BTN_BACK_Y = PANEL_CY + PANEL_H // 2 - 38

    t = 0.0

    while True:
        clock.tick(FPS)
        t += 0.04
        cursor_timer += 1
        if cursor_timer >= 45:
            cursor_timer = 0
            cursor_vis = not cursor_vis
        if feedback_timer > 0:
            feedback_timer -= 1

        # Rafraîchir l'état "demande en cours" toutes les 5 secondes
        if not hasattr(pseudo_request_screen, '_last_check') or time.time() - pseudo_request_screen._last_check > 5.0:
            pseudo_request_screen._last_check = time.time()
            already_sent = has_pending_request(session_name)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                if input_active:
                    if event.key == K_RETURN:
                        # Soumettre
                        clean = input_text.strip()
                        if len(clean) >= 2:
                            submit_pseudo_request(session_name, clean)
                            feedback_msg   = "Demande envoyée ! Un admin va la traiter."
                            feedback_col   = GREEN_SOFT
                            feedback_timer = 240
                            input_text     = ""
                        else:
                            feedback_msg   = "Le pseudo doit faire au moins 2 caractères."
                            feedback_col   = RED_HOT
                            feedback_timer = 180
                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode and len(input_text) < 24:
                        input_text += event.unicode

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if INPUT_X <= event.pos[0] <= INPUT_X + INPUT_W and INPUT_Y <= event.pos[1] <= INPUT_Y + INPUT_H:
                    input_active = True
                else:
                    input_active = False

                if btn_clicked(event, CX, BTN_SEND_Y, 320, 50):
                    clean = input_text.strip()
                    if len(clean) >= 2:
                        submit_pseudo_request(session_name, clean)
                        feedback_msg   = "Demande envoyée ! Un admin va la traiter."
                        feedback_col   = GREEN_SOFT
                        feedback_timer = 240
                        input_text     = ""
                    else:
                        feedback_msg   = "Le pseudo doit faire au moins 2 caractères."
                        feedback_col   = RED_HOT
                        feedback_timer = 180

                if btn_clicked(event, CX, BTN_BACK_Y, 300, 50):
                    return

        # ── DESSIN ────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(210)
        draw_panel(CX, PANEL_CY, PANEL_W, PANEL_H, radius=20, border=GOLD, shine_ratio=2)

        TITLE_Y = PANEL_CY - PANEL_H // 2 + 22
        title_s = font_med.render("DEMANDE DE PSEUDO", True, GOLD)
        screen.blit(title_s, (CX - title_s.get_width() // 2, TITLE_Y))

        # Pseudo actuel
        cur_lbl = font_tiny.render("Pseudo actuel :", True, (160, 165, 195))
        cur_val = font_small.render(current_disp, True, WHITE)
        screen.blit(cur_lbl, (CX - cur_lbl.get_width() // 2, TITLE_Y + font_med.get_height() + 14))
        screen.blit(cur_val, (CX - cur_val.get_width() // 2, TITLE_Y + font_med.get_height() + 14 + cur_lbl.get_height() + 4))

        # Indicateur demande en cours
        if already_sent:
            req = next((r for r in get_pending_requests() if r.get("session","").lower() == session_name.lower()), None)
            if req:
                pend_txt = font_tiny.render(
                    f"Demande en attente : « {req['pseudo']} » — envoyée le {req['date']}",
                    True, (255, 200, 60))
                screen.blit(pend_txt, (CX - pend_txt.get_width() // 2, INPUT_Y - 46))

        # Label champ
        lbl = font_tiny.render("Pseudo souhaité :", True, (160, 165, 195))
        screen.blit(lbl, (CX - lbl.get_width() // 2, INPUT_Y - lbl.get_height() - 6))

        # Champ de saisie
        border_col = GOLD if input_active else (80, 85, 120)
        inp_bg = pygame.Surface((INPUT_W, INPUT_H), pygame.SRCALPHA)
        pygame.draw.rect(inp_bg, (255, 255, 255, 22 if input_active else 12),
                         (0, 0, INPUT_W, INPUT_H), border_radius=10)
        screen.blit(inp_bg, (INPUT_X, INPUT_Y))
        pygame.draw.rect(screen, border_col,
                         (INPUT_X, INPUT_Y, INPUT_W, INPUT_H), width=2, border_radius=10)

        disp_txt = input_text + ("|" if input_active and cursor_vis else "")
        inp_surf = font_small.render(disp_txt if disp_txt else " ", True, WHITE)
        screen.blit(inp_surf, (INPUT_X + 14, INPUT_Y + INPUT_H // 2 - inp_surf.get_height() // 2))

        char_hint = font_tiny.render(f"{len(input_text)}/24", True, (100, 105, 145))
        screen.blit(char_hint, (INPUT_X + INPUT_W - char_hint.get_width() - 8,
                                 INPUT_Y + INPUT_H + 4))

        # (feedback maintenant affiché sous le bouton)

        draw_btn("ENVOYER LA DEMANDE", CX, BTN_SEND_Y, min(480, PANEL_W - 100), 54, accent=True)
        # Feedback déscendu sous le bouton
        if feedback_timer > 0:
            _alpha2 = min(255, feedback_timer * 3)
            _fb2 = font_small.render(feedback_msg, True, feedback_col)
            _fb2.set_alpha(_alpha2)
            screen.blit(_fb2, (CX - _fb2.get_width() // 2, BTN_SEND_Y + 36))
        draw_btn("RETOUR", CX, BTN_BACK_Y, 300, 50)

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
        draw_notifs()
        pygame.display.flip()


def credits_screen():
    """Écran de crédits simple."""
    CX = SCREEN_WIDTH  // 2
    CY = SCREEN_HEIGHT // 2
    t  = 0.0
    clock_c = pygame.time.Clock()
    while True:
        clock_c.tick(FPS)
        t += 0.04
        for ev in pygame.event.get():
            if ev.type == QUIT: pygame.quit(); sys.exit()
            if ev.type == KEYDOWN and ev.key == K_ESCAPE: return
            if ev.type == MOUSEBUTTONDOWN: return
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(210)
        # Panel
        PW, PH = min(600, SCREEN_WIDTH-80), 380
        draw_panel(CX, CY, PW, PH, radius=20, border=GOLD)
        # Titre
        title = font_big.render("CRÉDITS", True, GOLD)
        screen.blit(title, (CX - title.get_width()//2, CY - PH//2 + 20))
        draw_sep(CY - PH//2 + 70, w_margin=CX - PW//2 + 30)
        # Contenu
        lines_credits = [
            ("Développeur principal", (160, 165, 195), font_tiny),
            ("Pcquifume", WHITE, font_med),
            ("", WHITE, font_tiny),
            ("Merci à tous les joueurs !", (160, 165, 195), font_small),
        ]
        y = CY - PH//2 + 100
        for text, col, fnt in lines_credits:
            if text:
                surf = fnt.render(text, True, col)
                screen.blit(surf, (CX - surf.get_width()//2, y))
            y += fnt.get_height() + 12
        # Bouton retour
        draw_btn("FERMER", CX, CY + PH//2 - 36, 220, 46)
        draw_notifs()
        pygame.display.flip()


def profile_screen(data, player):
    t              = 0.0
    CX             = SCREEN_WIDTH  // 2
    CY             = SCREEN_HEIGHT // 2
    feedback_msg   = ""
    feedback_col   = WHITE
    feedback_timer = 0

    # ── Dimensions du panneau ────────────────────────────────────────────────
    PANEL_W    = 580
    PANEL_H    = 720
    PANEL_CY   = CY + 10

    # Tailles des boutons
    BTN_W        = 260
    BTN_W_BACK   = 340  # Bouton retour plus large sur les côtés
    BTN_W_LARGE  = 380  # Bouton d'importation allongé
    BTN_H        = 54   
    
    # Layout vertical recalibré
    TITLE_Y      = PANEL_CY - PANEL_H//2 + 28
    AV_R         = 60
    AV_Y         = TITLE_Y + font_med.get_height() + 20 + AV_R
    
    # Pseudo : Plus petit et remonté vers l'avatar
    NM_Y         = AV_Y + AV_R + 8

    # ── Pseudo éditable (admins seulement) ─────────────────────────────────
    session_name = player["name"]
    _is_admin    = session_name in ADMIN_USERS

    # Champ de saisie du pseudo
    INPUT_W      = 360
    INPUT_H      = 42
    INPUT_X      = CX - INPUT_W // 2
    INPUT_Y      = NM_Y + font_small.get_height() + 12
    input_active = False   # True = le champ est en cours d'édition
    # Valeur initiale = pseudo actuel (ou session si pas de pseudo défini)
    input_text   = get_display_name(session_name)
    cursor_vis   = True
    cursor_timer = 0

    # Si admin, le pseudo s'affiche dans le champ éditable ; sinon juste en texte
    # Bouton Importer positionné plus bas quand le champ d'édition est présent
    BTN_IMPORT_Y = (INPUT_Y + INPUT_H + 14) if _is_admin else (NM_Y + font_small.get_height() + 37)
    BTN_REMOVE_Y = BTN_IMPORT_Y + BTN_H + 12
    
    # Paramètres des Stats (remontées de 35px)
    STATS_Y_BASE = BTN_REMOVE_Y + BTN_H - 20
    STAT_ROW_H   = 85   # Espacement entre les lignes
    STAT_BOX_H   = 75   # Carré plus long vers le bas
    STAT_COL_W   = (PANEL_W - 80) // 2 

    BTN_BACK_Y   = PANEL_CY + PANEL_H//2 - 40

    while True:
        clock.tick(FPS)
        t += 0.04
        if feedback_timer > 0:
            feedback_timer -= 1

        # Curseur clignotant dans le champ input
        cursor_timer += 1
        if cursor_timer >= 45:
            cursor_timer = 0
            cursor_vis = not cursor_vis

        has_photo = bool(player.get("avatar_image_path") and
                         os.path.exists(player.get("avatar_image_path", "")))

        # Pseudo affiché (vient de pseudos.json ou session)
        display_name = get_display_name(session_name)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if input_active:
                    input_active = False
                else:
                    return

            # ── Gestion du champ de saisie (admins seulement) ──────────────
            if _is_admin and input_active and event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    # Valider et fermer le champ
                    set_display_name(session_name, input_text)
                    input_active = False
                    feedback_msg   = "Pseudo mis à jour !"
                    feedback_col   = GREEN_SOFT
                    feedback_timer = 150
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                    set_display_name(session_name, input_text)
                elif event.key == K_v and (pygame.key.get_mods() & KMOD_CTRL):
                    # Coller depuis le presse-papier
                    try:
                        clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clip:
                            pasted = clip.decode('utf-8', errors='ignore').replace('\x00', '').replace('\n', '').replace('\r', '')
                            input_text = (input_text + pasted)[:24]
                            set_display_name(session_name, input_text)
                    except Exception:
                        pass
                else:
                    if event.unicode and len(input_text) < 24:
                        input_text += event.unicode
                        # Sauvegarde à chaque caractère (pas de bouton valider)
                        set_display_name(session_name, input_text)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Clic dans le champ de saisie (admin)
                if _is_admin:
                    if INPUT_X <= mx <= INPUT_X + INPUT_W and INPUT_Y <= my <= INPUT_Y + INPUT_H:
                        input_active = True
                        cursor_vis   = True
                        cursor_timer = 0
                    else:
                        input_active = False

                # Clic sur le gros bouton d'importation
                if btn_clicked(event, CX, BTN_IMPORT_Y, BTN_W_LARGE, BTN_H):
                    ok, msg = _import_profile_photo(player, data)
                    feedback_msg, feedback_col, feedback_timer = msg, (GREEN_SOFT if ok else RED_HOT), 180
                elif btn_clicked(event, CX, BTN_BACK_Y, BTN_W_BACK, BTN_H):
                    return

        # ── DESSIN ────────────────────────────────────────────────────────────
        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(200)
        draw_panel(CX, PANEL_CY, PANEL_W, PANEL_H, radius=22, border=GOLD, shine_ratio=2)

        # Titre
        title_surf = font_med.render("MON PROFIL", True, GOLD)
        screen.blit(title_surf, (CX - title_surf.get_width()//2, TITLE_Y))

        # Avatar
        draw_avatar(player, CX, AV_Y, radius=AV_R, font=pygame.font.SysFont('Impact', 54))

        if _is_admin:
            # ── Champ de saisie du pseudo (admin) ───────────────────────────
            # Libellé au-dessus
            hint_surf = font_tiny.render("PSEUDO EN JEU", True, (160, 165, 195))
            screen.blit(hint_surf, (CX - hint_surf.get_width()//2, NM_Y))

            # Boîte du champ
            border_col = GOLD if input_active else (80, 85, 120)
            inp_bg = pygame.Surface((INPUT_W, INPUT_H), pygame.SRCALPHA)
            pygame.draw.rect(inp_bg, (255, 255, 255, 22 if input_active else 12),
                             (0, 0, INPUT_W, INPUT_H), border_radius=10)
            screen.blit(inp_bg, (INPUT_X, INPUT_Y))
            pygame.draw.rect(screen, border_col,
                             (INPUT_X, INPUT_Y, INPUT_W, INPUT_H), width=2, border_radius=10)

            # Texte dans le champ
            display_txt = input_text + ("|" if input_active and cursor_vis else "")
            inp_surf = font_small.render(display_txt if display_txt else " ", True, WHITE)
            screen.blit(inp_surf, (INPUT_X + 14, INPUT_Y + INPUT_H//2 - inp_surf.get_height()//2))

            # Petite indication sous le champ
            if input_active:
                tip = font_tiny.render("Tape ton pseudo — sauvegardé à chaque touche", True, (120, 125, 160))
            else:
                tip = font_tiny.render("Clique pour modifier", True, (100, 105, 145))
            screen.blit(tip, (CX - tip.get_width()//2, INPUT_Y + INPUT_H + 3))

        else:
            # ── Pseudo en lecture seule (non-admin) ──────────────────────────
            nm_surf = font_small.render(display_name, True, WHITE)
            screen.blit(nm_surf, (CX - nm_surf.get_width()//2, NM_Y))

        # Bouton Importer / Changer (Version Large)
        import_label = "CHANGER LA PHOTO" if has_photo else "IMPORTER UNE PHOTO"
        draw_btn(import_label, CX, BTN_IMPORT_Y, BTN_W_LARGE, BTN_H, accent=True)

        # Grille de Stats
        _games  = player.get("games_played", 0)
        _total  = player.get("total_score",  0)
        _avg    = round(_total / _games) if _games > 0 else 0
        stats = [
            ("PARTIES JOUÉES",  str(player.get("games_played",  0))),
            ("MEILLEUR SCORE",  str(player.get("best_score",    0))),
            ("SCORE TOTAL",     str(_total)),
            ("SCORE MOYEN",     str(_avg)),
            ("PIÈCES GAGNÉES",     str(player.get("missions_stats", {}).get("coins_total", player.get("total_coins", 0)))),
            ("P. MISSION GAGNÉES", str(player.get("total_mission_coins_earned", player.get("mission_coins", 0)))),
        ]
        
        for idx, (lbl, val) in enumerate(stats):
            col, row = idx % 2, idx // 2
            sx = CX - (PANEL_W-80)//2 + col * (STAT_COL_W + 20)
            sy = STATS_Y_BASE + row * STAT_ROW_H
            
            # Dessin de la case allongée
            sb = pygame.Surface((STAT_COL_W, STAT_BOX_H), pygame.SRCALPHA)
            pygame.draw.rect(sb, (255, 255, 255, 18), (0, 0, STAT_COL_W, STAT_BOX_H), border_radius=12)
            pygame.draw.rect(sb, (*GOLD, 60), (0, 0, STAT_COL_W, STAT_BOX_H), width=2, border_radius=12)
            screen.blit(sb, (sx, sy))
            
            # Textes décalés vers le bas de la case
            lbl_s = font_tiny.render(lbl, True, (160, 165, 195))
            val_s = font_small.render(val, True, GOLD)
            screen.blit(lbl_s, (sx + STAT_COL_W//2 - lbl_s.get_width()//2, sy + 15))
            screen.blit(val_s, (sx + STAT_COL_W//2 - val_s.get_width()//2, sy + 38))

        # Feedback (message de confirmation / erreur)
        if feedback_timer > 0:
            alpha = min(255, feedback_timer * 3)
            fb_surf = font_tiny.render(feedback_msg, True, feedback_col)
            fb_surf.set_alpha(alpha)
            screen.blit(fb_surf, (CX - fb_surf.get_width()//2, BTN_IMPORT_Y - 28))

        # Bouton Retour
        draw_btn("RETOUR AU MENU", CX, BTN_BACK_Y, BTN_W_BACK, BTN_H)

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        draw_notifs()
        pygame.display.flip()
# ══════════════════════════════════════════════════════════════════════════════
#  PARAMÈTRES
# ══════════════════════════════════════════════════════════════════════════════
def settings_screen(data, player):
    """Écran préférences audio — Layout compact, sliders bas et cadres élargis."""
    t         = 0.0
    CX        = SCREEN_WIDTH  // 2
    CY        = SCREEN_HEIGHT // 2

    vols = {
        "music_menu": player.get("music_vol_menu", player.get("music_volume", 0.5)),
        "sfx_menu":   player.get("sfx_vol_menu",   player.get("sfx_volume",   0.7)),
        "music_game": player.get("music_vol_game", player.get("music_volume", 0.5)),
        "sfx_game":   player.get("sfx_vol_game",   player.get("sfx_volume",   0.7)),
    }
    dragging = None

    def _apply(key, val):
        if   key == "music_menu": set_music_volume_menu(val)
        elif key == "sfx_menu":   set_sfx_volume_menu(val)
        elif key == "music_game": set_music_volume_game(val)
        elif key == "sfx_game":   set_sfx_volume_game(val)

    def _save_and_return():
        player["music_vol_menu"] = vols["music_menu"]
        player["sfx_vol_menu"]   = vols["sfx_menu"]
        player["music_vol_game"] = vols["music_game"]
        player["sfx_vol_game"]   = vols["sfx_game"]
        player["music_volume"]   = vols["music_menu"]
        player["sfx_volume"]     = vols["sfx_game"]
        save_data(data)

    PANEL_W   = 740
    PANEL_H   = 680
    PANEL_X   = CX
    PANEL_Y   = CY + 30
    PANEL_TOP = PANEL_Y - PANEL_H // 2

    SLIDER_W  = 540
    SLIDER_X0 = CX - SLIDER_W // 2

    SEC_W     = PANEL_W - 60
    SEC_H     = 250

    # ── OFFSET seulement pour MENU/JEU + sliders
    SLIDER_OFFSET = 40

    KNOB_MENU_MUSIC = PANEL_TOP + 145 + SLIDER_OFFSET
    KNOB_MENU_SFX   = KNOB_MENU_MUSIC + 100

    KNOB_GAME_MUSIC = PANEL_TOP + SEC_H + 20 + 145 + SLIDER_OFFSET
    KNOB_GAME_SFX   = KNOB_GAME_MUSIC + 100

    SLIDERS = [
        ("music_menu", "MUSIQUE",        "Volume de la musique dans les menus",    KNOB_MENU_MUSIC),
        ("sfx_menu",   "EFFETS SONORES", "Sons des boutons et interactions",       KNOB_MENU_SFX),
        ("music_game", "MUSIQUE",        "Volume de la musique pendant la partie", KNOB_GAME_MUSIC),
        ("sfx_game",   "EFFETS SONORES", "Battements d'ailes, collisions",         KNOB_GAME_SFX),
    ]

    BTN_Y = PANEL_TOP + PANEL_H - 42

    while True:
        clock.tick(FPS)
        t  += 0.04
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                _save_and_return(); return

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                hit_slider = False
                for key, _, _, cy in SLIDERS:
                    if abs(my - cy) <= 22 and SLIDER_X0 - 12 <= mx <= SLIDER_X0 + SLIDER_W + 12:
                        dragging  = key
                        hit_slider = True
                        val = max(0.0, min(1.0, (mx - SLIDER_X0) / SLIDER_W))
                        vols[key] = val
                        _apply(key, val)
                        break

                if not hit_slider:
                    if btn_clicked(event, CX, BTN_Y, 480, 58):
                        _save_and_return(); return

def settings_screen(data, player):

    # ───────── POSITIONS ─────────

    PANEL_X = 790
    PANEL_Y = 380
    PANEL_W = 740
    PANEL_H = 680

    TITLE_X = 800
    TITLE_Y = 70

    MENU_BOX_X = 500
    MENU_BOX_Y = 150

    GAME_BOX_X = 500
    GAME_BOX_Y = 370

    MENU_TITLE_X = 510
    MENU_TITLE_Y = 160

    GAME_TITLE_X = 510
    GAME_TITLE_Y = 380

    SLIDER1_X = 520
    SLIDER1_Y = 245

    SLIDER2_X = 520
    SLIDER2_Y = 315

    SLIDER3_X = 520
    SLIDER3_Y = 475

    SLIDER4_X = 520
    SLIDER4_Y = 545

    BTN_X = 790
    BTN_Y = 675

    SLIDER_W = 500
    BOX_W = 600
    BOX_H = 200

    # Position de la case à cocher (décalée à gauche)
    CHECKBOX_X = GAME_BOX_X + 10
    CHECKBOX_Y = GAME_BOX_Y + BOX_H + 22
    

    # ───────── VOLUMES ─────────

    vols = {
        "music_menu": player.get("music_vol_menu", 0.5),
        "sfx_menu": player.get("sfx_vol_menu", 0.7),
        "music_game": player.get("music_vol_game", 0.5),
        "sfx_game": player.get("sfx_vol_game", 0.7),
    }

    dragging = None

    def apply_volume(key, val):
        if key == "music_menu":
            set_music_volume_menu(val)
        elif key == "sfx_menu":
            set_sfx_volume_menu(val)
        elif key == "music_game":
            set_music_volume_game(val)
        elif key == "sfx_game":
            set_sfx_volume_game(val)

    # ── Case à cocher : musique suivante automatique ──────────────────────────
    auto_next = player.get("auto_next_music", False)

    def save_and_return():
        player["music_vol_menu"] = vols["music_menu"]
        player["sfx_vol_menu"] = vols["sfx_menu"]
        player["music_vol_game"] = vols["music_game"]
        player["sfx_vol_game"] = vols["sfx_game"]
        player["auto_next_music"] = auto_next
        set_auto_next(auto_next, player)
        save_data(data)

    sliders = [
        ("music_menu", "MUSIQUE", SLIDER1_X, SLIDER1_Y),
        ("sfx_menu", "EFFETS SONORES", SLIDER2_X, SLIDER2_Y),
        ("music_game", "MUSIQUE", SLIDER3_X, SLIDER3_Y),
        ("sfx_game", "EFFETS SONORES", SLIDER4_X, SLIDER4_Y),
    ]

    while True:

        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if _GLOBAL_CHAT:
                if _GLOBAL_CHAT.handle_btn_click(event): continue
                if _GLOBAL_CHAT.handle_event(event): continue
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    save_and_return()
                    return

            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                # Case à cocher auto-next
                checkbox_rect = pygame.Rect(CHECKBOX_X, CHECKBOX_Y, 24, 24)
                if checkbox_rect.collidepoint(event.pos):
                    auto_next = not auto_next

                for key, _, sx, sy in sliders:
                    if sx <= mx <= sx + SLIDER_W and sy - 10 <= my <= sy + 10:
                        dragging = key
                        val = max(0, min(1, (mx - sx) / SLIDER_W))
                        vols[key] = val
                        apply_volume(key, val)

                if btn_clicked(event, BTN_X, BTN_Y, 480, 58):
                    save_and_return()
                    return

            if event.type == MOUSEBUTTONUP:
                dragging = None

            if event.type == MOUSEMOTION and dragging:
                for key, _, sx, sy in sliders:
                    if key == dragging:
                        val = max(0, min(1, (mx - sx) / SLIDER_W))
                        vols[key] = val
                        apply_volume(key, val)

        # ───────── DESSIN ─────────

        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(215)

        draw_panel(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, radius=22, border=GOLD, shine=False)

        title = font_med.render("PRÉFÉRENCES AUDIO", True, GOLD)
        screen.blit(title, (TITLE_X - title.get_width() // 2, TITLE_Y))

        # ───────── BOX MENU ─────────

        menu_box = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
        pygame.draw.rect(menu_box, (255,255,255,12), (0,0,BOX_W,BOX_H), border_radius=14)
        pygame.draw.rect(menu_box, (*GOLD,60), (0,0,BOX_W,BOX_H), 1, border_radius=14)

        screen.blit(menu_box, (MENU_BOX_X, MENU_BOX_Y))

        badge = pygame.Surface((110,28), pygame.SRCALPHA)
        pygame.draw.rect(badge, (*GOLD,200), (0,0,110,28), border_radius=8)

        txt = font_tiny.render("MENU", True, NIGHT)
        badge.blit(txt,(55 - txt.get_width()//2,14 - txt.get_height()//2))

        screen.blit(badge,(MENU_TITLE_X, MENU_TITLE_Y))

        # ───────── BOX JEU ─────────

        game_box = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
        pygame.draw.rect(game_box, (255,255,255,12), (0,0,BOX_W,BOX_H), border_radius=14)
        pygame.draw.rect(game_box, (*GOLD,60), (0,0,BOX_W,BOX_H), 1, border_radius=14)

        screen.blit(game_box, (GAME_BOX_X, GAME_BOX_Y))

        badge2 = pygame.Surface((110,28), pygame.SRCALPHA)
        pygame.draw.rect(badge2, (*GOLD,200), (0,0,110,28), border_radius=8)

        txt2 = font_tiny.render("JEU", True, NIGHT)
        badge2.blit(txt2,(55 - txt2.get_width()//2,14 - txt2.get_height()//2))

        screen.blit(badge2,(GAME_TITLE_X, GAME_TITLE_Y))

        # ───────── SLIDERS ─────────

        for key, label, sx, sy in sliders:

            val = vols[key]
            fill = int(val * SLIDER_W)

            pygame.draw.rect(screen,(40,45,72),(sx,sy,SLIDER_W,10),border_radius=5)
            pygame.draw.rect(screen,GOLD,(sx,sy,fill,10),border_radius=5)

            knob_x = sx + fill
            pygame.draw.circle(screen,WHITE,(knob_x,sy+5),12)

            text = font_small.render(label,True,WHITE)
            screen.blit(text,(sx,sy-35))

            pct = font_small.render(f"{int(val*100)}%",True,GOLD)
            screen.blit(pct,(sx+SLIDER_W+20,sy-10))

        draw_btn("SAUVEGARDER ET RETOUR", BTN_X, BTN_Y, 480, 58, accent=True)

        # ── Case à cocher : Musique suivante automatique ──────────────────────
        checkbox_rect = pygame.Rect(CHECKBOX_X, CHECKBOX_Y, 24, 24)
        mx_s, my_s = pygame.mouse.get_pos()
        cb_hov = checkbox_rect.collidepoint(mx_s, my_s)
        # Fond de la case
        cb_bg = (40, 60, 100, 240) if cb_hov else (20, 28, 55, 220)
        cb_border = (60, 200, 255) if auto_next else ((120, 160, 220) if cb_hov else (60, 80, 130))
        cb_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(cb_surf, cb_bg, (0, 0, 24, 24), border_radius=5)
        pygame.draw.rect(cb_surf, cb_border, (0, 0, 24, 24), 2, border_radius=5)
        if auto_next:
            # Coche ✓
            pygame.draw.line(cb_surf, (60, 220, 120), (5, 12), (10, 18), 3)
            pygame.draw.line(cb_surf, (60, 220, 120), (10, 18), (19, 6), 3)
        screen.blit(cb_surf, (CHECKBOX_X, CHECKBOX_Y))
        # Label (position fixe, ne bouge pas avec la case)
        cb_lbl = font_small.render("Passer à la musique suivante automatiquement", True,
                                   (200, 230, 255) if auto_next else (140, 160, 200))
        screen.blit(cb_lbl, (CHECKBOX_X + 32, GAME_BOX_Y + BOX_H + 16))
        # Sous-label explicatif (position fixe)
        cb_sub = font_tiny.render("La musique change seule quand la piste est terminée", True, (90, 110, 150))
        screen.blit(cb_sub, (CHECKBOX_X + 32, GAME_BOX_Y + BOX_H + 40))

        if _GLOBAL_CHAT:
            _GLOBAL_CHAT.draw()
            if _GLOBAL_CHAT.pending_card:
                _n = _GLOBAL_CHAT.pending_card; _GLOBAL_CHAT.pending_card = None
                try:
                    _gd = load_data(); _gp = _gd.get('players', {}).get(_n)
                    if _gp is None: _gp = {'name': _n}
                    player_card_popup(_gp)
                except Exception: pass
        pygame.display.flip()
# ══════════════════════════════════════════════════════════════════════════════
#  TAP TO START
# ══════════════════════════════════════════════════════════════════════════════
def start_screen(selected_skin, bird_grp, ground_grp, pipe_grp):
    bird = Bird(SKIN_ASSET_NAMES[selected_skin])
    bird_grp.empty(); bird_grp.add(bird)
    bird_base_y = SCREEN_HEIGHT // 2
    bird.rect.center = (SCREEN_WIDTH // 2, bird_base_y)
    t = 0.0

    while True:
        clock.tick(FPS); t += 0.035
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: return None
                bird.bump(); return bird
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                bird.bump(); return bird

        screen.blit(BACKGROUND, (0, 0))
        pipe_grp.draw(screen); ground_grp.draw(screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110)); screen.blit(overlay, (0, 0))

        bird.rect.centery = bird_base_y + int(math.sin(t * 1.8) * 8)
        bird_grp.draw(screen)

        title_y = 150 + int(math.sin(t * 0.6) * 5)
        shadow_txt = font_big.render("FLAPPY BIRD", True, (10, 10, 10))
        screen.blit(shadow_txt, (SCREEN_WIDTH//2 - shadow_txt.get_width()//2 + 2, title_y + 3))
        text_glow("FLAPPY BIRD", font_big, GOLD, SCREEN_WIDTH//2, title_y, GOLD, 5)

        skin_name = SKIN_DISPLAY_NAMES[selected_skin].upper()
        name_txt  = font_tiny.render(f"PERSONNAGE : {skin_name}", True, GOLD)
        name_txt.set_alpha(180)
        screen.blit(name_txt, (SCREEN_WIDTH//2 - name_txt.get_width()//2, bird.rect.top - 25))

        alpha_val = int(170 + 85 * math.sin(t * 3.0))
        tap_text  = font_med.render("APPUYEZ POUR JOUER", True, WHITE)
        tap_rect  = tap_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 250))
        tap_surf  = tap_text.convert_alpha(); tap_surf.set_alpha(alpha_val)
        screen.blit(tap_surf, tap_rect)
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  COMPTE A REBOURS
# ══════════════════════════════════════════════════════════════════════════════
def countdown(bird_grp, ground_grp, pipe_grp):
    items = [("3", RED_HOT), ("2", GOLD), ("1", GREEN_SOFT), ("GO!", CYAN)]
    for num, color in items:
        for frame in range(60):
            clock.tick(FPS)
            screen.blit(BACKGROUND, (0, 0))
            pipe_grp.draw(screen); ground_grp.draw(screen); bird_grp.draw(screen)
            scale     = 1.0 + 0.18 * math.sin(frame / 60 * math.pi)
            base_surf = font_score.render(num, True, color)
            w = max(1, int(base_surf.get_width()  * scale))
            h = max(1, int(base_surf.get_height() * scale))
            scaled = pygame.transform.smoothscale(base_surf, (w, h))
            for off in range(4, 0, -1):
                gw, gh = w + off*8, h + off*8
                gs = pygame.transform.smoothscale(base_surf, (max(1,gw), max(1,gh)))
                gs.set_alpha(28)
                screen.blit(gs, (SCREEN_WIDTH//2 - gw//2, SCREEN_HEIGHT//2 - gh//2 - 20))
            screen.blit(scaled, (SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - h//2 - 20))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == QUIT: pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════════════════════════════
#  JEU
# ══════════════════════════════════════════════════════════════════════════════
def game_loop(bird, bird_grp, ground_grp, pipe_grp, player, data, music_file=None, menu_music_file=None):
    global score, best_score
    score      = 0
    coins_this_game = 0
    start_time = time.time()
    # Résoudre les pistes réelles pour la comparaison
    _resolved_game = music_file if music_file and os.path.exists(music_file) else background_music
    _resolved_menu = menu_music_file if menu_music_file and os.path.exists(menu_music_file) else menu_music
    play_game_music(music_file)

    ground_grp.empty(); pipe_grp.empty()
    coin_grp = pygame.sprite.Group()
    global coin_pop_effects
    coin_pop_effects = []

    mission_effects = []   # animations MissionCompleteEffect en cours

    for i in range(2):
        ground_grp.add(Ground(GROUND_WIDTH * i))
    for i in range(2):
        p1, p2 = random_pipes(SCREEN_WIDTH * i + 1600)
        pipe_grp.add(p1, p2)

    QUIT_RECT  = pygame.Rect(SCREEN_WIDTH - 150, 20, 130, 40)
    PAUSE_RECT = pygame.Rect(SCREEN_WIDTH - 290, 20, 130, 40)

    coin_anim_t  = 0
    score_anim_t = 0.0   # animation flash du score (1.0 → 0.0)
    paused       = False
    pause_start_time = None  # pour compenser start_time au reprise

    # ── Parallax background ───────────────────────────────────────────────
    BG_W = BACKGROUND.get_width()
    bg_x = 0.0

    # ── Pré-allocation HUD (évite les allocations GC à chaque frame) ─────
    _hud_w, _hud_h = 220, 130
    _hud_surface = pygame.Surface((_hud_w, _hud_h), pygame.SRCALPHA)
    _coin_hud_surf = pygame.Surface((240, 62), pygame.SRCALPHA)
    # Textes statiques pré-rendus
    _txt_label_static = font_tiny.render("SCORE",     True, GOLD)
    _txt_quitter      = font_tiny.render("QUITTER",   True, WHITE)
    _txt_pause_static = font_tiny.render("PAUSE",     True, WHITE)
    _txt_reprendre    = font_tiny.render("REPRENDRE", True, WHITE)
    _txt_p_hint       = font_tiny.render("[P]",       True, (180, 180, 180))
    _last_best_score  = -1   # cache pour éviter re-render du meilleur score
    _txt_best_cached  = None
    _last_score_val   = -1;  _last_score_col = None; _txt_score_cached = None
    _last_coins_val   = -1;  _txt_coins_cached = None
    _last_total_val   = -1;  _txt_total_cached = None

    COIN_SPAWN_INTERVAL_MIN = 2.0
    COIN_SPAWN_INTERVAL_MAX = 5.0
    COIN_SPAWN_CHANCE       = 0.55
    coin_spawn_timer = random.uniform(COIN_SPAWN_INTERVAL_MIN, COIN_SPAWN_INTERVAL_MAX)
    _flap_hold_timer = 0

    # Désactiver le GC automatique pendant le jeu pour éviter les saccades
    # On collecte manuellement toutes les 2 secondes entre les frames
    gc.collect()
    gc.disable()
    _gc_timer = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 1.0 / 30)
        if not paused:
            elapsed = time.time() - start_time
        # Boost de vitesse à partir du score 20 (plus prononcé)
        _speed_bonus = max(0, (score - 20) * 0.15) if score >= 20 else 0
        game_speed = (GAME_SPEED + elapsed * ACCELERATION + _speed_bonus) * dt * 60 if not paused else 0
        coin_anim_t += 1

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == _MUSIC_END_EVENT:
                handle_music_end_event(player)
            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                        pause_start_time = time.time()
                    else:
                        pygame.mixer.music.unpause()
                        if pause_start_time is not None:
                            start_time += time.time() - pause_start_time
                            pause_start_time = None
                elif event.key in (K_SPACE, K_UP) and not paused:
                    bird.bump()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if QUIT_RECT.collidepoint(event.pos): pygame.quit(); sys.exit()
                elif PAUSE_RECT.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                        pause_start_time = time.time()
                    else:
                        pygame.mixer.music.unpause()
                        if pause_start_time is not None:
                            start_time += time.time() - pause_start_time
                            pause_start_time = None
                elif not paused:
                    bird.bump()

        # Pause : on skip toute la physique
        if paused:
            keys = pygame.key.get_pressed()
            held = False
        else:
            keys = pygame.key.get_pressed()
            mouse_held = pygame.mouse.get_pressed()[0] and not QUIT_RECT.collidepoint(pygame.mouse.get_pos()) and not PAUSE_RECT.collidepoint(pygame.mouse.get_pos())
            held = bool(keys[K_SPACE] or keys[K_UP] or mouse_held)

        grounds = ground_grp.sprites()
        if not paused:
            if grounds and off_screen(grounds[0]):
                last_ground = grounds[-1] if len(grounds) > 1 else grounds[0]
                new_x = last_ground.rect.x + GROUND_WIDTH
                ground_grp.remove(grounds[0])
                ground_grp.add(Ground(new_x))

            if pipe_grp.sprites() and off_screen(pipe_grp.sprites()[0]):
                pipe_grp.remove(pipe_grp.sprites()[0])
                pipe_grp.remove(pipe_grp.sprites()[0])
                p1, p2 = random_pipes(SCREEN_WIDTH * 2)
                pipe_grp.add(p1, p2)

            coin_spawn_timer -= dt
            if coin_spawn_timer <= 0:
                coin_spawn_timer = random.uniform(COIN_SPAWN_INTERVAL_MIN, COIN_SPAWN_INTERVAL_MAX)
                if random.random() < COIN_SPAWN_CHANCE:
                    new_coin = try_spawn_random_coin(pipe_grp)
                    if new_coin:
                        coin_grp.add(new_coin)

            for coin in list(coin_grp.sprites()):
                if off_screen(coin):
                    coin_grp.remove(coin)

        if not paused:
            bird_grp.update(dt, held)
            ground_grp.update(game_speed)
        bob_active = score >= 20
        _th_opts = player.get("tryharder_opts", {})
        _any_tryhard = any(_th_opts.values()) if _th_opts else False
        if not paused:
            for pipe in pipe_grp.sprites():
                if bob_active:
                    _bob_amp = min(120, 60 + (score - 20) * 3)
                else:
                    _bob_amp = 0
                pipe._tryhard_amp = int(_bob_amp * 1.4) if _any_tryhard else _bob_amp
                pipe.update(game_speed, bob_active=bob_active, dt=dt)
            coin_grp.update(game_speed)

        # ── Score : incrémente au moment où l'oiseau franchit le bord droit d'un tuyau ──
        bird_x = bird_grp.sprites()[0].rect.centerx
        for pipe in pipe_grp.sprites():
            if not pipe.inverted and not pipe.score_passed:
                pipe_right = pipe.rect.right
                if bird_x > pipe_right:
                    pipe.score_passed = True
                    # Marquer le partenaire aussi (même xpos)
                    for other in pipe_grp.sprites():
                        if other is not pipe and abs(other.float_x - pipe.float_x) < 2:
                            other.score_passed = True
                    score += 1
                    best_score = max(best_score, score)
                    score_anim_t = 1.0   # déclenche l'animation
                    # Vérifie missions score en temps réel
                    init_missions(player)
                    _s = player["missions_stats"] if "missions_stats" in player else {}
                    _pipes_today = _s.get("pipes_today", 0) + score
                    for mid, mtype, label, desc, goal, reward in MISSIONS_DAILY + MISSIONS_ONETIME + MISSIONS_PERMANENT:
                        if mtype not in ("score", "pipes", "pipes_total"):
                            continue
                        entry = player["missions"].get(mid, {"progress": 0, "claimed": False})
                        if entry["claimed"]: continue
                        val = score if mtype == "score" else (_pipes_today if mtype == "pipes" else _s.get("pipes_total", 0) + score)
                        if val >= goal and entry["progress"] < goal:
                            entry["progress"] = goal
                            player["missions"][mid] = entry
                            mission_effects.append(MissionCompleteEffect(label, reward))

        collected = pygame.sprite.spritecollide(
            bird_grp.sprites()[0], coin_grp, True, pygame.sprite.collide_mask
        )
        for c in collected:
            coins_this_game += 1
            coin_pop_effects.append(CoinPopEffect(c.rect.centerx, c.rect.top - 10))
            try:
                snd = _get_sound(coin_snd)
                if snd:
                    snd.set_volume(min(1.0, _sfx_volume() * 0.8))
                    snd.play()
            except: pass

        coin_pop_effects = [e for e in coin_pop_effects if not e.dead]
        for e in coin_pop_effects:
            e.update()

        # ── Parallax background ───────────────────────────────────────────
        bg_x -= game_speed * 0.15
        if bg_x <= -BG_W:
            bg_x += BG_W

        screen.blit(BACKGROUND, (int(bg_x), 0))
        screen.blit(BACKGROUND, (int(bg_x) + BG_W, 0))
        pipe_grp.draw(screen)
        coin_grp.draw(screen)
        ground_grp.draw(screen)
        bird_grp.draw(screen)

        # ── OVERLAYS TRYHARDER ────────────────────────────────────────────────
        _tho = player.get("tryharder_opts", {})
        if _tho.get("hitbox_pipes", False):
            for pipe in pipe_grp.sprites():
                pygame.draw.rect(screen, (255, 40, 40), pipe.rect, 2)

        if _tho.get("hitbox_coins", False):
            for coin in coin_grp.sprites():
                pygame.draw.rect(screen, (255, 200, 0), coin.rect, 2)

        bird_sprite = bird_grp.sprites()[0]
        br = bird_sprite.rect

        if _tho.get("hitbox_player", False):
            # Pour l'Avion : afficher un rect réduit (corps visible seulement)
            if "Avion" in bird_sprite.skin_name:
                # Hitbox réduite au corps visible de l'avion (sans les ailes)
                _shrink_x = br.width  // 3
                _shrink_y = br.height // 3
                _small_br = pygame.Rect(
                    br.x + _shrink_x, br.y + _shrink_y,
                    br.width - _shrink_x * 2, br.height - _shrink_y * 2
                )
                pygame.draw.rect(screen, (0, 230, 255), _small_br, 2)
            else:
                pygame.draw.rect(screen, (0, 230, 255), br, 2)

        if _tho.get("vector", False):
            cx, cy = br.centerx, br.centery
            vx, vy = 6, bird_sprite.speed
            mag = math.sqrt(vx*vx + vy*vy) or 1
            vec_len = 60
            ex = int(cx + (vx / mag) * vec_len)
            ey = int(cy + (vy / mag) * vec_len)
            pygame.draw.line(screen, (0, 80, 140), (cx, cy), (ex, ey), 4)
            pygame.draw.line(screen, (0, 230, 255), (cx, cy), (ex, ey), 2)
            pygame.draw.circle(screen, (255, 255, 60), (ex, ey), 5)

        if _tho.get("fps", False) or _tho.get("gamespeed", False):
            _dbg_lines = []
            if _tho.get("fps", False):
                _dbg_lines.append(f"FPS : {int(clock.get_fps())}")
            if _tho.get("gamespeed", False):
                _dbg_lines.append(f"SPD : {game_speed:.2f}")
            for _li, _txt in enumerate(_dbg_lines):
                _ds = font_tiny.render(_txt, True, (255, 80, 80))
                screen.blit(_ds, (SCREEN_WIDTH - _ds.get_width() - 160, 70 + _li * 22))
        # ─────────────────────────────────────────────────────────────────────

        for e in coin_pop_effects:
            e.draw(screen)

        # Animations missions complétées
        mission_effects = [e for e in mission_effects if not e.dead]
        for e in mission_effects:
            e.update()
            e.draw(screen)

        # HUD score — surface pré-allouée, pas de new Surface() par frame
        _hud_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(_hud_surface, (10, 10, 15, 200), (0, 0, _hud_w, _hud_h), border_radius=15)
        pygame.draw.rect(_hud_surface, (*GOLD, 255), (0, 0, _hud_w, _hud_h), width=2, border_radius=15)
        _cur_best = player.get('best_score', 0)
        if _cur_best != _last_best_score:
            _last_best_score = _cur_best
            _txt_best_cached = font_tiny.render(f"MEILLEUR : {_cur_best}", True, (150, 150, 150))
        _hud_surface.blit(_txt_label_static, (20, 12))
        _hud_surface.blit(_txt_best_cached,  (20, 92))
        screen.blit(_hud_surface, (20, 20))

        # Score animé : grossit brièvement au passage d'un tuyau
        score_anim_t = max(0.0, score_anim_t - dt * 4.0)
        anim_scale = 1.0 + 0.45 * score_anim_t
        if score_anim_t > 0.01:
            # Animation active : re-render avec couleur animée
            score_color = (int(255), int(255 - score_anim_t * 100), int(255 - score_anim_t * 255))
            txt_score_base = font_hud.render(str(score), True, score_color)
            sw = max(1, int(txt_score_base.get_width()  * anim_scale))
            sh = max(1, int(txt_score_base.get_height() * anim_scale))
            txt_score = pygame.transform.smoothscale(txt_score_base, (sw, sh))
        else:
            # Pas d'animation : utiliser le cache
            if score != _last_score_val:
                _last_score_val   = score
                _txt_score_cached = font_hud.render(str(score), True, WHITE)
            txt_score = _txt_score_cached
        screen.blit(txt_score, (40, 58))

        coin_hud_x, coin_hud_y = 20, 165
        _coin_hud_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(_coin_hud_surf, (10, 10, 15, 185), (0, 0, 240, 62), border_radius=12)
        pygame.draw.rect(_coin_hud_surf, (*GOLD, 200), (0, 0, 240, 62), width=2, border_radius=12)
        screen.blit(_coin_hud_surf, (coin_hud_x, coin_hud_y))
        hud_coin_frame = COIN_FRAMES_54[(coin_anim_t // 4) % len(COIN_FRAMES_54)]
        screen.blit(hud_coin_frame, (coin_hud_x + 6, coin_hud_y + (62 - 54) // 2))
        if coins_this_game != _last_coins_val:
            _last_coins_val   = coins_this_game
            _txt_coins_cached = font_small.render(f"{coins_this_game}", True, GOLD)
            _last_total_val   = player.get('total_coins', 0) + coins_this_game
            _txt_total_cached = font_tiny.render(f"TOTAL: {_last_total_val}", True, GREY)
        screen.blit(_txt_coins_cached, (coin_hud_x + 66, coin_hud_y + (62 - _txt_coins_cached.get_height()) // 2))
        screen.blit(_txt_total_cached, (coin_hud_x + 106, coin_hud_y + (62 - _txt_total_cached.get_height()) // 2))

        # Bouton QUITTER
        pygame.draw.rect(screen, (220, 50, 50), QUIT_RECT, border_radius=10)
        screen.blit(_txt_quitter, _txt_quitter.get_rect(center=QUIT_RECT.center))

        # Bouton PAUSE
        _pause_col = (255, 160, 0) if paused else (40, 120, 220)
        pygame.draw.rect(screen, _pause_col, PAUSE_RECT, border_radius=10)
        _pause_lbl = _txt_reprendre if paused else _txt_pause_static
        screen.blit(_pause_lbl, _pause_lbl.get_rect(center=PAUSE_RECT.center))
        # Hint touche P à gauche du bouton
        screen.blit(_txt_p_hint, (PAUSE_RECT.left - _txt_p_hint.get_width() - 6, PAUSE_RECT.centery - _txt_p_hint.get_height()//2))

        # Overlay pause
        if paused:
            _ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            _ov.fill((0, 0, 0, 120))
            screen.blit(_ov, (0, 0))
            _ptxt = font_big.render("PAUSE", True, GOLD)
            _psh  = font_big.render("PAUSE", True, (0, 0, 0))
            _px   = SCREEN_WIDTH//2 - _ptxt.get_width()//2
            _py   = SCREEN_HEIGHT//2 - _ptxt.get_height()//2
            screen.blit(_psh,  (_px+3, _py+3))
            screen.blit(_ptxt, (_px, _py))
            _psub = font_small.render("Appuie sur P ou clique PAUSE pour reprendre", True, (200, 200, 200))
            screen.blit(_psub, (_psub.get_rect(centerx=SCREEN_WIDTH//2, top=_py + _ptxt.get_height() + 12)))

        pygame.display.flip()

        # GC manuel toutes les 2 secondes juste après le flip (entre les frames)
        _gc_timer += dt
        if _gc_timer >= 2.0:
            _gc_timer = 0.0
            gc.collect(0)  # génération 0 seulement = rapide (~0.1ms)

        if (pygame.sprite.groupcollide(bird_grp, ground_grp, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_grp, pipe_grp, False, False, pygame.sprite.collide_mask)):
            play_sound(hit_snd)
            # Courte pause propre sans effet visuel
            for _death_frame in range(36):
                clock.tick(FPS)
                for _ev in pygame.event.get():
                    if _ev.type == QUIT:
                        pygame.quit(); sys.exit()
            # Ne couper la musique que si la piste du menu est différente de celle du jeu
            if _resolved_game != _resolved_menu:
                stop_music()
            break

    gc.enable()   # réactiver le GC dès qu'on quitte le jeu
    gc.collect()  # nettoyage complet après la partie

    # [FIX] Une seule écriture Supabase après la partie (évite les écrasements croisés)
    _pc_clear(player["name"])
    _fresh = get_player(data, player["name"])
    _fresh["games_played"] = _fresh.get("games_played", 0) + 1
    _fresh["total_score"]  = _fresh.get("total_score",  0) + score
    _fresh["total_coins"]  = _fresh.get("total_coins",  0) + coins_this_game
    if score > _fresh.get("best_score", 0):
        _fresh["best_score"] = score
    # Copier les missions mises à jour depuis l'objet player en mémoire
    _fresh["missions"]       = player.get("missions", _fresh.get("missions", {}))
    _fresh["missions_stats"] = player.get("missions_stats", _fresh.get("missions_stats", {}))
    # Mise à jour des stats missions avec les données fraîches
    _ms = _fresh["missions_stats"]
    _ms["pipes_today"]      = _ms.get("pipes_today", 0)      + score
    _ms["coins_game_today"] = _ms.get("coins_game_today", 0) + coins_this_game
    _ms["games_today"]      = _ms.get("games_today", 0)      + 1
    _ms["pipes_total"]      = _ms.get("pipes_total", 0)      + score
    _ms["coins_total"]      = _ms.get("coins_total", 0)      + coins_this_game
    _ms["games"]            = _ms.get("games", 0)            + 1
    _ms["skins_owned"]      = len(_fresh.get("owned_skins", ["Flappy"]))
    _ms["bgs_owned"]        = len(_fresh.get("owned_backgrounds", []))
    _ms["musics_owned"]     = len(_fresh.get("owned_musics", []))
    _ms["levels_done"]      = len(_fresh.get("completed_levels", []))
    _stat_map = {
        "pipes":         _ms["pipes_today"],
        "coins_game":    _ms["coins_game_today"],
        "games":         _ms["games_today"],
        "score":         score,
        "pipes_total":   _ms["pipes_total"],
        "coins_total":   _ms["coins_total"],
        "coins_balance": _fresh.get("total_coins", 0),
        "coins_spent":   _ms.get("coins_spent", 0),
        "skins_owned":   _ms["skins_owned"],
        "bgs_owned":     _ms["bgs_owned"],
        "musics_owned":  _ms["musics_owned"],
        "chat_msgs":     _ms.get("chat_msgs", 0),
        "levels_done":   _ms["levels_done"],
    }
    for _mid, _mtype, _label, _desc, _goal, _reward in ALL_MISSIONS.values():
        _entry = _fresh["missions"].get(_mid, {"progress": 0, "claimed": False})
        if _entry["claimed"]:
            continue
        _val = _stat_map.get(_mtype, 0)
        _new_prog = min(_goal, _val if _mtype != "score" else max(_entry["progress"], _val))
        _entry["progress"] = _new_prog
        _fresh["missions"][_mid] = _entry
    # Une seule écriture atomique vers Supabase
    _sb_post("players", _player_to_row(_fresh), upsert=True)
    _pc_set(_fresh["name"], _fresh)
    data["players"][_fresh["name"]] = _fresh
    player.update(_fresh)
    best_score = _fresh.get("best_score", 0)
    return coins_this_game


# ══════════════════════════════════════════════════════════════════════════════
#  GAME OVER
# ══════════════════════════════════════════════════════════════════════════════
def game_over_screen(player, coins_earned=0):
    global score, best_score
    alpha_overlay = 0
    t = 0.0
    new_best = (score > 0 and score >= player.get("best_score", 0))

    PANEL_W = 380
    PANEL_H = 270 if new_best else 245
    PANEL_Y = SCREEN_HEIGHT // 2 - 20
    GO_Y    = SCREEN_HEIGHT // 2 - 210
    BTN_W   = 260
    B1_Y    = PANEL_Y + (PANEL_H // 2) + 75
    B2_Y    = B1_Y + 75
    offset_y = 100

    while True:
        clock.tick(FPS)
        t += 0.05
        alpha_overlay = min(190, alpha_overlay + 5)
        offset_y = max(0, offset_y - 6)

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key in (K_SPACE, K_RETURN): return 'replay'
                if event.key == K_ESCAPE: return 'menu'
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if btn_clicked(event, SCREEN_WIDTH//2, B1_Y + offset_y, BTN_W, 60): return 'replay'
                if btn_clicked(event, SCREEN_WIDTH//2, B2_Y + offset_y, BTN_W, 55): return 'menu'

        screen.blit(BACKGROUND, (0, 0))
        draw_overlay(alpha_overlay)

        go_y_final = GO_Y + int(math.sin(t * 1.2) * 6) + offset_y
        go_rect = GAMEOVER_IMG.get_rect(center=(SCREEN_WIDTH//2, go_y_final))
        screen.blit(GAMEOVER_IMG, go_rect)

        panel_y_final = PANEL_Y + offset_y
        draw_panel(SCREEN_WIDTH//2, panel_y_final, PANEL_W, PANEL_H, radius=15)

        lbl_txt = font_tiny.render("SCORE", True, GOLD)
        screen.blit(lbl_txt, (SCREEN_WIDTH//2 - lbl_txt.get_width()//2, panel_y_final - (PANEL_H//2) + 18))

        sc_lbl = font_big.render(str(score), True, WHITE)
        screen.blit(sc_lbl, (SCREEN_WIDTH//2 - sc_lbl.get_width()//2, panel_y_final - (PANEL_H//2) + 42))

        be_lbl = font_small.render(f"MEILLEUR : {player.get('best_score',0)}", True, (200, 200, 200))
        screen.blit(be_lbl, (SCREEN_WIDTH//2 - be_lbl.get_width()//2, panel_y_final - (PANEL_H//2) + 108))

        if new_best:
            flash  = int(200 + 55 * math.sin(t * 6))
            nb_txt = font_tiny.render("NOUVEAU RECORD !", True, (flash, flash, 0))
            screen.blit(nb_txt, (SCREEN_WIDTH//2 - nb_txt.get_width()//2, panel_y_final - (PANEL_H//2) + 140))

        coin_row_y = panel_y_final + (PANEL_H // 2) - 42
        coin_mini = COIN_IMG_36
        coin_line_x = SCREEN_WIDTH//2 - 90
        screen.blit(coin_mini, (coin_line_x, coin_row_y - 18))
        coin_earn_txt = font_small.render(f"+{coins_earned} pièces", True, GOLD)
        screen.blit(coin_earn_txt, (coin_line_x + 42, coin_row_y - coin_earn_txt.get_height()//2))

        draw_btn("REJOUER", SCREEN_WIDTH//2, B1_Y + offset_y, BTN_W, 60, accent=True)
        draw_btn("MENU",    SCREEN_WIDTH//2, B2_Y + offset_y, BTN_W, 55)

        if offset_y == 0:
            hint = font_tiny.render("[ESPACE] REJOUER  |  [ECHAP] MENU", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 40))

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    global best_score

    # Démarrage du thread de backup automatique (toutes les 60 s)
    start_backup_thread()

    data = load_data()

    current_name = get_system_username()
    data["current_player"] = current_name
    register_session(current_name)
    get_player(data, current_name)
    # Activer le watcher pseudo pour ce joueur
    global _pseudo_notif_player_name, _pseudo_notif_player_ref, _pseudo_notif_was_pending
    _pseudo_notif_player_name = current_name
    # Vérifier l'état initial pour ne pas déclencher de fausse notif au démarrage
    try:
        _pseudo_notif_was_pending = has_pending_request(current_name)
    except Exception:
        _pseudo_notif_was_pending = False
    save_data(data)

    # Démarrage du thread de surveillance du fichier STOP
    start_stop_watcher(current_name, ADMIN_USERS)

    player = get_player(data, current_name)
    # Donner la référence directe au player au watcher pour mise à jour en mémoire
    _pseudo_notif_player_ref = player
    load_volumes_from_player(player)
    init_missions(player)
    update_first_place_streak(data)
    save_data(data)
    best_score = player.get("best_score", 0)

    # ── Initialisation du chat global ─────────────────────────────────────────
    global _GLOBAL_CHAT
    _GLOBAL_CHAT = ChatOverlay(
        player_name   = current_name,
        is_admin_user = (current_name in ADMIN_USERS),
        player        = player,
        data          = data,
    )

    # Initialiser le mode auto-next depuis les préférences du joueur
    set_auto_next(player.get("auto_next_music", False), player)

    play_menu_music()

    # Restaurer les préférences sauvegardées du joueur
    owned_skins = player.get("owned_skins", ["Flappy"])
    _saved_skin = player.get("selected_skin", "Flappy")
    selected_skin = _saved_skin if _saved_skin in owned_skins else "Flappy"

    _saved_bg = player.get("selected_bg", None)
    owned_bgs_list = player.get("owned_backgrounds", [])
    selected_bg = _saved_bg if (_saved_bg is None or _saved_bg in owned_bgs_list) else None

    _saved_music = player.get("selected_music", None)
    _special_keys = [_MUSIC_KEY_DEFAULT_MENU, _MUSIC_KEY_DEFAULT_GAME]
    owned_musics_list = player.get("owned_musics", [])
    selected_music = _saved_music if (_saved_music is None or _saved_music in _special_keys or _saved_music in owned_musics_list) else None

    _saved_music_menu = player.get("selected_music_menu", None)
    selected_music_menu = _saved_music_menu if (_saved_music_menu is None or _saved_music_menu in _special_keys or _saved_music_menu in owned_musics_list) else None

    # Appliquer le fond sauvegardé dès le démarrage
    global BACKGROUND
    if selected_bg is not None and selected_bg in BG_PREVIEW_IMAGES and BG_PREVIEW_IMAGES[selected_bg]:
        BACKGROUND = BG_PREVIEW_IMAGES[selected_bg]

    # Appliquer la musique menu sauvegardée dès le démarrage (supporte clés croisées)
    if selected_music_menu is not None:
        _resolved = _resolve_music_file(selected_music_menu)
        if _resolved:
            play_menu_music(_resolved)

    bird_grp   = pygame.sprite.Group()
    ground_grp = pygame.sprite.Group()
    pipe_grp   = pygame.sprite.Group()
    for i in range(2): ground_grp.add(Ground(GROUND_WIDTH * i))
    for i in range(2):
        p1, p2 = random_pipes(SCREEN_WIDTH * i + 1600)
        pipe_grp.add(p1, p2)

    while True:
        # Vérifier si maintenance déclenchée par le stop watcher
        if _maintenance_triggered.is_set():
            draw_maintenance_screen()

        result, selected_skin, selected_bg, selected_music, selected_music_menu = main_menu(
            data, player, selected_skin, selected_bg, selected_music, selected_music_menu)

        # Sauvegarder les préférences du joueur dans game.dat
        player["selected_skin"]         = selected_skin
        player["selected_bg"]           = selected_bg
        player["selected_music"]        = selected_music
        player["selected_music_menu"]   = selected_music_menu
        save_data(data)

        # Appliquer le fond sélectionné
        if selected_bg is not None and selected_bg in BG_PREVIEW_IMAGES and BG_PREVIEW_IMAGES[selected_bg]:
            BACKGROUND = BG_PREVIEW_IMAGES[selected_bg]
        else:
            BACKGROUND = pygame.transform.scale(
                _pygame_load('assets/sprites/background-day.png').convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))

        if result == 'quit':
            return

        if isinstance(result, tuple):
            action, _ = result
            if action == 'profile':
                profile_screen(data, player)
            elif action == 'pseudo':
                pseudo_request_screen(player)
            elif action == 'settings':
                settings_screen(data, player)
                load_volumes_from_player(player)
                set_auto_next(player.get("auto_next_music", False), player)
            elif action == 'bugreport':
                bug_report_screen(player)
            elif action == 'credits':
                credits_screen()
            elif action == 'admin' and current_name in ADMIN_USERS:
                # Recharger les données fraîches avant d'ouvrir l'admin
                data = load_data()
                admin_screen(data, current_name)
                # Resynchroniser le joueur courant après modifications éventuelles
                player = get_player(data, current_name)
            continue

        if result == 'shop':
            shop_category_screen(data, player)
            if selected_skin not in player.get("owned_skins", ["Flappy"]):
                selected_skin = "Flappy"
            continue

        if result == 'missions':
            missions_screen(data, player)
            continue

        if result == 'levels':
            levels_screen(data, player, selected_skin)
            continue

        if result == 'play':
            # Résoudre la piste musicale de JEU (supporte les clés croisées)
            _game_music_file = _resolve_music_file(selected_music)
            if _game_music_file is None:
                _game_music_file = background_music  # fallback défaut jeu
            # Résoudre la piste musicale de MENU (pour retour)
            _menu_music_file = _resolve_music_file(selected_music_menu)
            # None = défaut menu, laissé tel quel pour play_menu_music()
            while True:
                bird = start_screen(selected_skin, bird_grp, ground_grp, pipe_grp)
                if bird is None: break
                coins_earned = game_loop(bird, bird_grp, ground_grp, pipe_grp, player, data, _game_music_file, _menu_music_file)
                _pc_clear(current_name)  # [FIX] forcer lecture fraîche après sauvegarde
                player = get_player(data, current_name)
                action = game_over_screen(player, coins_earned)
                if action == 'menu':
                    break
            play_menu_music(_menu_music_file)

main()