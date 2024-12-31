import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import time
import json
import os

# Constantes pour le jeu
LARGEUR, HAUTEUR = 1050, 670
VITESSE_JOUEUR = 5
VITESSE_LASER = 15
VITESSE_ENNEMI = 3
VITESSE_LASER_ENNEMI = 10
TAUX_APPARITION_ENNEMI = 1500
FPS = 60
INTERVALLE_NIVEAU = 1
TAUX_APPARITION_BONUS = 2000  # Réduit pour augmenter la fréquence d'apparition des bonus
DUREE_BONUS = 5

# Fichier pour stocker les scores
SCORE_FILE = "scores.json"

class AlienAttackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alien Attack")
        self.root.geometry(f"{LARGEUR}x{HAUTEUR}")
        self.root.resizable(False, False)

        # Charger les images
        self.img_fond = tk.PhotoImage(file="s.png")
        self.img_joueur = tk.PhotoImage(file="vaisseau.png")
        self.img_laser = tk.PhotoImage(file="pixel_laser_yellow.png")
        self.images_ennemis = [
            tk.PhotoImage(file="alien.png"),
            tk.PhotoImage(file="alien1.png"),
            tk.PhotoImage(file="alien2.png")
        ]
        self.img_laser_ennemi = tk.PhotoImage(file="pixel_laser_red.png")
        self.img_vie = tk.PhotoImage(file="vie.png")
        self.img_bouclier = tk.PhotoImage(file="bouclier.png")
        self.img_vitesse = tk.PhotoImage(file="speed.png")
        self.img_boss = tk.PhotoImage(file="freezer.png")
        self.img_warning = tk.PhotoImage(file="warning.png")
        self.img_orbe = tk.PhotoImage(file="orbe.png")

        # Configuration du canevas
        self.canvas = tk.Canvas(self.root, width=LARGEUR, height=HAUTEUR, bg="black")
        self.canvas.pack()

        # Afficher l'arrière-plan
        self.fond = self.canvas.create_image(0, 0, anchor="nw", image=self.img_fond)

        # Initialiser les variables de jeu
        self.player_name = ""
        self.joueur = None
        self.lasers = []
        self.lasers_ennemis = []
        self.ennemis = []
        self.bonus = []
        self.boss = None
        self.warning = None
        self.orbes = []
        self.direction_boss = 1  # Initialiser la direction du boss
        self.boss_sante = 200  # Santé du boss
        self.boss_sante_max = 200  # Santé maximale du boss
        self.en_cours = False
        self.sante = 100
        self.sante_max = 100
        self.niveau = 1
        self.score = 0
        self.temps_niveau = time.time()
        self.bouclier_actif = False
        self.boost_vitesse_actif = False
        self.deplacer_gauche = False
        self.deplacer_droite = False
        self.deplacer_haut = False
        self.deplacer_bas = False

        # Liaisons des touches
        self.root.bind("<Left>", lambda event: self.definir_mouvement(True, False, False, False))
        self.root.bind("<Right>", lambda event: self.definir_mouvement(False, True, False, False))
        self.root.bind("<Up>", lambda event: self.definir_mouvement(False, False, True, False))
        self.root.bind("<Down>", lambda event: self.definir_mouvement(False, False, False, True))
        self.root.bind("<KeyRelease-Left>", lambda event: self.definir_mouvement(False, self.deplacer_droite, self.deplacer_haut, self.deplacer_bas))
        self.root.bind("<KeyRelease-Right>", lambda event: self.definir_mouvement(self.deplacer_gauche, False, self.deplacer_haut, self.deplacer_bas))
        self.root.bind("<KeyRelease-Up>", lambda event: self.definir_mouvement(self.deplacer_gauche, self.deplacer_droite, False, self.deplacer_bas))
        self.root.bind("<KeyRelease-Down>", lambda event: self.definir_mouvement(self.deplacer_gauche, self.deplacer_droite, self.deplacer_haut, False))
        self.root.bind("<space>", self.tirer_laser)

        # Créer les boutons
        self.bouton_jouer = tk.Button(self.root, text="Jouer", command=self.demarrer_jeu, font=("Helvetica", 24))
        self.bouton_jouer.place(relx=0.5, rely=0.5, anchor="center")

        self.bouton_classement = tk.Button(self.root, text="Classement", command=self.afficher_classement, font=("Helvetica", 24))
        self.bouton_classement.place(relx=0.5, rely=0.6, anchor="center")

        self.bouton_rejouer = tk.Button(self.root, text="Rejouer", command=self.rejouer, font=("Helvetica", 24))
        self.bouton_accueil = tk.Button(self.root, text="Retour à l'accueil", command=self.retour_accueil, font=("Helvetica", 24))

        # Afficher la page d'accueil
        self.afficher_accueil()

    def definir_mouvement(self, gauche, droite, haut, bas):
        self.deplacer_gauche = gauche
        self.deplacer_droite = droite
        self.deplacer_haut = haut
        self.deplacer_bas = bas

    def deplacer_joueur(self):
        dx, dy = 0, 0
        if self.deplacer_gauche:
            dx -= VITESSE_JOUEUR * (2 if self.boost_vitesse_actif else 1)
        if self.deplacer_droite:
            dx += VITESSE_JOUEUR * (2 if self.boost_vitesse_actif else 1)
        if self.deplacer_haut:
            dy -= VITESSE_JOUEUR * (2 if self.boost_vitesse_actif else 1)
        if self.deplacer_bas:
            dy += VITESSE_JOUEUR * (2 if self.boost_vitesse_actif else 1)

        self.canvas.move(self.joueur, dx, dy)
        px, py = self.canvas.coords(self.joueur)
        px = max(0, min(LARGEUR, px))
        py = max(0, min(HAUTEUR, py))
        self.canvas.coords(self.joueur, px, py)

    def tirer_laser(self, event=None):
        px, py = self.canvas.coords(self.joueur)
        laser = self.canvas.create_image(px, py - 40, image=self.img_laser)
        self.lasers.append(laser)
        if self.boost_vitesse_actif:
            laser_gauche = self.canvas.create_image(px - 40, py - 40, image=self.img_laser)
            laser_droite = self.canvas.create_image(px + 40, py - 40, image=self.img_laser)
            laser_haut = self.canvas.create_image(px, py - 80, image=self.img_laser)
            laser_bas = self.canvas.create_image(px, py + 40, image=self.img_laser)
            laser_gauche_haut = self.canvas.create_image(px - 40, py - 80, image=self.img_laser)
            laser_droite_haut = self.canvas.create_image(px + 40, py - 80, image=self.img_laser)
            laser_gauche_bas = self.canvas.create_image(px - 40, py + 40, image=self.img_laser)
            laser_droite_bas = self.canvas.create_image(px + 40, py + 40, image=self.img_laser)
            self.lasers.append(laser_gauche)
            self.lasers.append(laser_droite)
            self.lasers.append(laser_haut)
            self.lasers.append(laser_bas)
            self.lasers.append(laser_gauche_haut)
            self.lasers.append(laser_droite_haut)
            self.lasers.append(laser_gauche_bas)
            self.lasers.append(laser_droite_bas)

    def apparition_ennemi(self):
        if self.en_cours and self.niveau < 10:
            for _ in range(self.niveau):
                ex = random.randint(50, LARGEUR - 50)
                img_ennemi = random.choice(self.images_ennemis)
                ennemi = self.canvas.create_image(ex, -50, image=img_ennemi)
                self.ennemis.append(ennemi)
            self.root.after(TAUX_APPARITION_ENNEMI, self.apparition_ennemi)

    def apparition_bonus(self):
        if self.en_cours and random.randint(1, 5) == 1:  # Augmenter la fréquence d'apparition des bonus
            px = random.randint(50, LARGEUR - 50)
            type_bonus = random.choice(["sante", "bouclier", "vitesse"])
            if type_bonus == "sante":
                img_bonus = self.img_vie
            elif type_bonus == "bouclier":
                img_bonus = self.img_bouclier
            else:
                img_bonus = self.img_vitesse
            bonus = self.canvas.create_image(px, -50, image=img_bonus)
            self.bonus.append((bonus, type_bonus, time.time()))
        self.root.after(TAUX_APPARITION_BONUS, self.apparition_bonus)

    def appliquer_bonus(self, bonus, type_bonus):
        if self.verifier_collision(bonus, self.joueur):
            if type_bonus == "sante":
                self.sante = min(self.sante_max, self.sante + 20)
            elif type_bonus == "bouclier":
                self.bouclier_actif = True
                self.root.after(DUREE_BONUS * 1000, self.retirer_bouclier)
            elif type_bonus == "vitesse":
                self.boost_vitesse_actif = True
                self.root.after(DUREE_BONUS * 1000, self.retirer_boost_vitesse)
            self.canvas.delete(bonus)
            self.bonus = [b for b in self.bonus if b[0] != bonus]

    def retirer_bouclier(self):
        self.bouclier_actif = False

    def retirer_boost_vitesse(self):
        self.boost_vitesse_actif = False

    def ennemi_tirer(self, ennemi):
        if self.en_cours:
            ex, ey = self.canvas.coords(ennemi)
            laser = self.canvas.create_image(ex, ey + 40, image=self.img_laser_ennemi)
            self.lasers_ennemis.append(laser)

    def dessiner_barre_sante(self):
        self.canvas.create_rectangle(10, 10, 210, 30, fill="red", outline="", tags="barre_sante")
        self.canvas.create_rectangle(10, 10, 10 + 200 * (self.sante / self.sante_max), 30, fill="green", outline="", tags="barre_sante")

    def dessiner_barre_sante_boss(self):
        bx, by = self.canvas.coords(self.boss)
        self.canvas.create_rectangle(bx - 50, by + 60, bx + 50, by + 80, fill="red", outline="", tags="barre_sante_boss")
        self.canvas.create_rectangle(bx - 50, by + 60, bx - 50 + 100 * (self.boss_sante / self.boss_sante_max), by + 80, fill="green", outline="", tags="barre_sante_boss")

    def dessiner_texte(self):
        self.canvas.create_text(1000, 50, text=f"Niveau: {self.niveau}", fill="white", font=("Helvetica", 16), tags="texte")
        self.canvas.create_text(1000, 80, text=f"Score: {self.score}", fill="white", font=("Helvetica", 16), tags="texte")

    def boucle_jeu(self):
        if not self.en_cours:
            return

        # Mise à jour de l'interface
        self.canvas.delete("barre_sante")
        self.canvas.delete("barre_sante_boss")
        self.canvas.delete("texte")
        self.dessiner_barre_sante()
        if self.boss:
            self.dessiner_barre_sante_boss()
        self.dessiner_texte()

        # Mouvement du joueur
        self.deplacer_joueur()

        # Mouvement des lasers
        for laser in self.lasers[:]:
            coords = self.canvas.coords(laser)
            if not coords:
                self.lasers.remove(laser)
                continue
            lx, ly = coords
            self.canvas.move(laser, 0, -VITESSE_LASER)
            if ly < 0:  # Laser hors écran
                self.canvas.delete(laser)
                self.lasers.remove(laser)

        # Mouvement des ennemis
        for ennemi in self.ennemis[:]:
            coords = self.canvas.coords(ennemi)
            if not coords:
                self.ennemis.remove(ennemi)
                continue
            ex, ey = coords
            self.canvas.move(ennemi, 0, VITESSE_ENNEMI)
            if ey > HAUTEUR:  # Ennemi hors écran
                self.canvas.delete(ennemi)
                self.ennemis.remove(ennemi)
            else:  # Ennemi peut tirer
                if random.randint(1, 60) == 1:
                    self.ennemi_tirer(ennemi)

        # Mouvement des lasers des ennemis
        for laser in self.lasers_ennemis[:]:
            coords = self.canvas.coords(laser)
            if not coords:
                self.lasers_ennemis.remove(laser)
                continue
            lx, ly = coords
            self.canvas.move(laser, 0, VITESSE_LASER_ENNEMI)
            if ly > HAUTEUR:  # Laser hors écran
                self.canvas.delete(laser)
                self.lasers_ennemis.remove(laser)
            elif self.verifier_collision(laser, self.joueur) and not self.bouclier_actif:  # Collision avec le joueur
                self.sante -= 10
                self.canvas.delete(laser)
                self.lasers_ennemis.remove(laser)
                if self.sante <= 0:
                    self.fin_jeu()

        # Mouvement et application des bonus
        temps_actuel = time.time()
        for bonus, type_bonus, temps_apparition in self.bonus[:]:
            coords = self.canvas.coords(bonus)
            if not coords:
                self.bonus.remove((bonus, type_bonus, temps_apparition))
                continue
            px, py = coords
            self.canvas.move(bonus, 0, VITESSE_ENNEMI)
            if temps_actuel - temps_apparition >= DUREE_BONUS:
                self.canvas.delete(bonus)
                self.bonus.remove((bonus, type_bonus, temps_apparition))
            else:
                self.appliquer_bonus(bonus, type_bonus)

        # Vérification des collisions entre les lasers et les ennemis
        for laser in self.lasers[:]:
            for ennemi in self.ennemis[:]:
                if self.verifier_collision(laser, ennemi):
                    self.score += 10
                    self.canvas.delete(laser)
                    self.canvas.delete(ennemi)
                    self.lasers.remove(laser)
                    self.ennemis.remove(ennemi)

        # Vérification des collisions entre les lasers et le boss
        if self.boss:
            for laser in self.lasers[:]:
                if self.verifier_collision(laser, self.boss):
                    self.boss_sante -= 10
                    self.canvas.delete(laser)
                    self.lasers.remove(laser)
                    if self.boss_sante <= 0:
                        self.fin_jeu_boss()

        # Augmentation du niveau toutes les 5 secondes
        if temps_actuel - self.temps_niveau >= INTERVALLE_NIVEAU:
            self.niveau += 1
            self.temps_niveau = temps_actuel  # Réinitialiser le compteur de temps

            if self.niveau == 10:
                self.apparition_boss()

        # Mouvement du boss
        if self.boss:
            self.deplacer_boss()
            self.boss_attaquer()

        # Planification de la prochaine frame
        self.root.after(1000 // FPS, self.boucle_jeu)

    def verifier_collision(self, obj1, obj2):
        coords1 = self.canvas.coords(obj1)
        coords2 = self.canvas.coords(obj2)
        if not coords1 or not coords2:
            return False
        x1, y1 = coords1
        x2, y2 = coords2
        return abs(x1 - x2) < 30 and abs(y1 - y2) < 30

    def fin_jeu(self):
        self.en_cours = False
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 2, text="GAME OVER", fill="red", font=("Helvetica", 48))
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 2 + 50, text=f"Score: {self.score}", fill="white", font=("Helvetica", 24))
        self.afficher_boutons_fin()

        # Enregistrer le score
        self.enregistrer_score()

    def fin_jeu_boss(self):
        self.en_cours = False
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 2, text="FÉLICITATIONS!", fill="green", font=("Helvetica", 48))
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 2 + 50, text=f"Score: {self.score}", fill="white", font=("Helvetica", 24))
        self.afficher_boutons_fin()

        # Enregistrer le score
        self.enregistrer_score()

    def rejouer(self):
        self.reinitialiser_jeu()
        self.afficher_jeu()

    def retour_accueil(self):
        self.reinitialiser_jeu()
        self.afficher_accueil()

    def enregistrer_score(self):
        scores = self.charger_scores()
        for score in scores:
            if score["nom"] == self.player_name:
                score["score"] = max(score["score"], self.score)
                break
        else:
            scores.append({"nom": self.player_name, "score": self.score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f)

    def charger_scores(self):
        if not os.path.exists(SCORE_FILE):
            return []
        with open(SCORE_FILE, "r") as f:
            return json.load(f)

    def apparition_boss(self):
        # Faire disparaître tous les aliens
        for ennemi in self.ennemis:
            self.canvas.delete(ennemi)
        self.ennemis = []

        # Faire apparaître le boss
        self.boss = self.canvas.create_image(LARGEUR // 2, 100, image=self.img_boss)

    def deplacer_boss(self):
        bx, by = self.canvas.coords(self.boss)
        if bx < 0 or bx > LARGEUR:
            self.direction_boss = -self.direction_boss
        self.canvas.move(self.boss, self.direction_boss * VITESSE_ENNEMI, 0)

    def boss_attaquer(self):
        if random.randint(1, 100) == 1:
            self.avertir_attaque()
            self.root.after(3000, self.lancer_orbe)
        if random.randint(1, 60) == 1:
            self.boss_tirer()

    def avertir_attaque(self):
        self.warning = self.canvas.create_image(LARGEUR // 2, HAUTEUR // 2, image=self.img_warning)
        self.root.after(500, self.clignoter_warning, 3)

    def clignoter_warning(self, count):
        if count > 0:
            self.canvas.itemconfig(self.warning, state=tk.HIDDEN if self.canvas.itemcget(self.warning, "state") == tk.NORMAL else tk.NORMAL)
            self.root.after(500, self.clignoter_warning, count - 1)
        else:
            self.canvas.delete(self.warning)

    def lancer_orbe(self):
        bx, by = self.canvas.coords(self.boss)
        orbe = self.canvas.create_image(bx, by + 50, image=self.img_orbe)
        self.orbes.append(orbe)
        self.deplacer_orbe(orbe)

    def deplacer_orbe(self, orbe):
        ox, oy = self.canvas.coords(orbe)
        if oy > HAUTEUR:
            self.canvas.delete(orbe)
            self.orbes.remove(orbe)
        else:
            self.canvas.move(orbe, 0, VITESSE_LASER_ENNEMI)
            self.root.after(1000 // FPS, self.deplacer_orbe, orbe)

    def verifier_collision_orbe(self, orbe, joueur):
        coords_orbe = self.canvas.coords(orbe)
        coords_joueur = self.canvas.coords(joueur)
        if not coords_orbe or not coords_joueur:
            return False
        ox, oy = coords_orbe
        jx, jy = coords_joueur
        return abs(ox - jx) < 30 and abs(oy - jy) < 30

    def boss_attaquer_special(self):
        if random.randint(1, 100) == 1:
            self.avertir_attaque()
            self.root.after(3000, self.lancer_orbe_special)

    def lancer_orbe_special(self):
        bx, by = self.canvas.coords(self.boss)
        orbe = self.canvas.create_image(bx, by + 50, image=self.img_orbe)
        self.orbes.append(orbe)
        self.deplacer_orbe_special(orbe)

    def deplacer_orbe_special(self, orbe):
        ox, oy = self.canvas.coords(orbe)
        if oy > HAUTEUR:
            self.canvas.delete(orbe)
            self.orbes.remove(orbe)
        else:
            self.canvas.move(orbe, 0, VITESSE_LASER_ENNEMI)
            self.root.after(1000 // FPS, self.deplacer_orbe_special, orbe)
            if self.verifier_collision_orbe(orbe, self.joueur):
                self.sante -= 50  # L'attaque spéciale inflige plus de dégâts
                self.canvas.delete(orbe)
                self.orbes.remove(orbe)
                if self.sante <= 0:
                    self.fin_jeu()

    def afficher_accueil(self):
        self.canvas.delete("all")
        self.fond = self.canvas.create_image(0, 0, anchor="nw", image=self.img_fond)
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 4, text="Alien Attack", fill="yellow", font=("Helvetica", 48))
        self.bouton_jouer.place(relx=0.5, rely=0.5, anchor="center")
        self.bouton_classement.place(relx=0.5, rely=0.6, anchor="center")
        self.bouton_rejouer.place_forget()
        self.bouton_accueil.place_forget()

    def afficher_classement(self):
        self.canvas.delete("all")
        self.fond = self.canvas.create_image(0, 0, anchor="nw", image=self.img_fond)
        scores = self.charger_scores()
        classement_text = "Classement:\n"
        for i, score in enumerate(scores, start=1):
            classement_text += f"{i}. {score['nom']} - {score['score']}\n"
        self.canvas.create_text(LARGEUR // 2, HAUTEUR // 2, text=classement_text, fill="white", font=("Helvetica", 24), anchor="center")
        self.bouton_accueil.config(text="Retour à l'accueil", command=self.retour_accueil)
        self.bouton_accueil.place(relx=0.5, rely=0.8, anchor="center")
        self.bouton_jouer.place_forget()
        self.bouton_classement.place_forget()
        self.bouton_rejouer.place_forget()

    def demarrer_jeu(self):
        self.player_name = simpledialog.askstring("Nom du joueur", "Entrez votre nom:")
        if self.player_name:
            self.reinitialiser_jeu()
            self.afficher_jeu()

    def afficher_jeu(self):
        self.canvas.delete("all")
        self.fond = self.canvas.create_image(0, 0, anchor="nw", image=self.img_fond)
        self.joueur = self.canvas.create_image(LARGEUR // 2, HAUTEUR - 100, image=self.img_joueur)
        self.en_cours = True
        self.apparition_ennemi()
        self.apparition_bonus()
        self.boucle_jeu()
        self.cacher_boutons()

    def reinitialiser_jeu(self):
        self.joueur = None
        self.lasers = []
        self.lasers_ennemis = []
        self.ennemis = []
        self.bonus = []
        self.boss = None
        self.warning = None
        self.orbes = []
        self.direction_boss = 1  # Initialiser la direction du boss
        self.boss_sante = 200  # Santé du boss
        self.boss_sante_max = 200  # Santé maximale du boss
        self.en_cours = False
        self.sante = 100
        self.sante_max = 100
        self.niveau = 1
        self.score = 0
        self.temps_niveau = time.time()
        self.bouclier_actif = False
        self.boost_vitesse_actif = False
        self.deplacer_gauche = False
        self.deplacer_droite = False
        self.deplacer_haut = False
        self.deplacer_bas = False

    def cacher_boutons(self):
        self.bouton_jouer.place_forget()
        self.bouton_classement.place_forget()
        self.bouton_rejouer.place_forget()
        self.bouton_accueil.place_forget()

    def afficher_boutons_fin(self):
        self.bouton_rejouer.place(relx=0.5, rely=0.7, anchor="center")
        self.bouton_accueil.place(relx=0.5, rely=0.8, anchor="center")

    def boss_tirer(self):
        if self.en_cours and self.boss:
            bx, by = self.canvas.coords(self.boss)
            laser = self.canvas.create_image(bx, by + 50, image=self.img_laser_ennemi)
            self.lasers_ennemis.append(laser)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlienAttackApp(root)
    root.mainloop()
