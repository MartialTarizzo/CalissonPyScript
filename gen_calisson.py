# %% Jeu du calisson
# gen_calisson.py : fonctions de génération automatique d'énigme
#
# ============================================================================
# Auteur : Martial Tarizzo
#
# Licence : CC BY-NC-SA 4.0 DEED
# https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr
# ============================================================================


import math
import random as rd
import numpy as np
import time

from calisson import projection, doSolve, encodage, encodeSolution, encodeSolution3D, placeSommet

# %% Section 1 : génération d'un empilement
# --------------------------------------------
"""
représentation de l'empilement des petits cubes dans un grand cube de côté n :
liste de n**2 élements, représentant le nombre de petits cubes empilés
au dessus du carré de coordonnées (i,j) dans le plan horizontal.
L'index du carré (i,j) dans la liste est i * n + j , i=0..n-1, j=0..n-1
le carré (0,0) est le plus éloigné de l'observateur, base i,j,k directe
"""


# génération d'une configuration contenant nbCubes dans un grand cube de côté n
# La config est obtenue en ajoutant les cubes un à un à partir de la config vide,
# et en prenant une config au hasard à chaque étape.
def make_config(n, nbCubes):
    # le jeu, vide de tout cube
    def kVide(n):
        return [0]*n**2

    def ajouteCube(k):
        """retourne la liste de toutes les configurations de jeu possibles en
        ajoutant un cube à la configuration k fournie en argument."""
        l = []
        for i in range(n):
            for j in range(n):
                hok = k[i * n + j] < n
                iok = i > 0 and k[(i - 1) * n + j] > k[i * n + j]
                jok = j > 0 and k[i * n + j - 1] > k[i * n + j]
                # print(i,j,hok,iok,jok)
                if i == 0:
                    if j == 0:
                        ok = hok
                    else:
                        ok = hok and jok
                else:
                    if j == 0:
                        ok = hok and iok
                    else:
                        ok = hok and iok and jok
                if ok:
                    newk = k.copy()
                    newk[i * n + j] = newk[i * n + j] + 1
                    l.append(newk)
        return l

    k = kVide(n)
    f = 1   # pour estimer le nombre de façons différentes d'empiler les nbCubes
    for i in range(nbCubes):
        lk = ajouteCube(k)
        m = len(lk)
        f *= m
        k = rd.choice(lk)
    return k, f

# La représentation précédente (matrice n x n) de l'empilement est commode pour le générer,
#  mais n'est pas commode pour le tracé et la résolution.
# On va changer pour une matrice de dimension 3 : n x n x n
# Les arêtes des petits cubes sont donc de longueur 1.
# Chaque élément de la matrice est un entier dans {-1,0,+1} indiquant l'état
# d'un petit cube dont l'origine a pour coordonnées le point (i,j,k)
# état : -1 -> état inconnu, 0 -> cube absent, +1 -> cube présent

# Passage de la représentation compacte à la matrice de dimension 3
def matrice_jeu(konfig):
    # jeu est la matrice de taille n**3 obtenue à partir de la configuration k
    n = math.isqrt(len(konfig))
    jeu = np.zeros([n, n, n], dtype='int')
    for i in range(n):
        for j in range(n):
            for k in range(konfig[n*i+j]):
                jeu[i, j, k] = 1
    return jeu

def make_random_config(n, nbCubes = 0, trace = False):
    """
    retourne une configuration aléatoire pour un jeu
    de dimension n contenant m cubes
    """
    # nombre de cubes dans la configuration, tiré au hasard entre n^3/3 et n^3/2 si non fourni
    if nbCubes == 0:
        nbCubes = rd.randint(n**3//4, 3*n**3//4)
        if trace: print(f"on a {nbCubes} cubes dans la configuration")

    k, f = make_config(n, nbCubes)
    if trace : print(k, f)
    return k

# %% section 2 : Génération d'un énigme

# Deuxième méthode à partir d'un empilement
def randomEnigma2(n, konfig = [], trace = False, easy = 0):
    # l'ensemble des extrémités des arêtes placée dans l'énigme
    node2DSet = set()
    # la liste des arêtes 2D rejetées lors de la première passe
    arRejected = []

    def ar3Dconnected(a):
        """
        retourne (True, False) si une des extrémités 2D de l'arête est dans l'ensemble node2DSet
        """
        
        def onHexEdge(x, y):
            # est-on sur un bord de l'hexagone ?
            return abs(x)==n or 2*n - abs(x) == abs(y)

        org2D = tuple(projection([a[0], a[1], a[2]]))
        if org2D in node2DSet or onHexEdge(*org2D):
            return True

        x, y = org2D
        d = a[3]
        if d=="x":
            dest2D = (x-1, y-1)
        if d=="y":
            dest2D =  (x+1, y-1)
        if d=="z":
            dest2D = (x, y+2)
        
        if dest2D in node2DSet or onHexEdge(*dest2D):
                return True

        node2DSet.add(org2D)
        node2DSet.add(dest2D)
        return False

    # Fabrication de l'empilement aléatoire 3D
    konf = make_random_config(n)
    mat = matrice_jeu(konf)
    enc = encodage(mat)
    encSol3D = encodeSolution3D(enc) 

    if trace : print(f"Empilement de taille {n} terminé")

    # remplissage d'une configuration initialement vide avec les arêtes
    mp = -np.ones((n,n,n), dtype='int')
    lar3D = []
    idx = 0

    # première passe : on ne place que des arêtes isolées 
    # non accrochées sur le bord de l'hexagone
    while len(encSol3D) > 0 and -1 in mp:
        ar = rd.choice(list(encSol3D))
        encSol3D.remove(ar)
        if ar3Dconnected(ar):
            arRejected.append(ar)
            continue
        r, mp2 = placeSommet(*ar, mp)
        if np.any(mp - mp2):    # l'arête modifie la config
            lar3D.append(ar)
            mp = mp2

    if trace : print(f"Première passe : {len(lar3D)} arêtes")

    # s'il reste des cubes indéterminés, c'est qu'on a épuisé
    # la liste des arêtes en rejetant trop d'arêtes connectées.
    # on place donc des arêtes connectées pour lever les 
    # indéterminations.
    while -1 in mp:
        ar = rd.choice(arRejected)
        r, mp2 = placeSommet(*ar, mp)
        if np.any(mp - mp2):    # l'arête modifie la config
            lar3D.append(ar)
            mp = mp2
        arRejected.remove(ar)

    if trace : print(f"Ajout d'arêtes pour lever les indéterminations : {len(lar3D)} arêtes")
    
    # Ajout d'arêtes supplémentaires en fonction de la facilité de la grille
    encSol3D = list(encSol3D) + arRejected
    for _ in range(easy * len(encSol3D) // 10):
        # idx = (idx + 123321) % len(encSol3D)
        ar = rd.choice(list(encSol3D))
        # ar = encSol3D[idx]
        lar3D.append(ar)
        encSol3D.remove(ar)


    if trace : print(f"ajout/facilité : {len(lar3D)} arêtes")


    # plus aucun cube indéterminé. Construction de l'énigme 2D
    enigme = []
    for a in lar3D:
        p = projection([a[0], a[1], a[2]])
        p.append(a[3])
        enigme.append(tuple(p))

    if trace : print(f"énigme construite")

    # Vérification/modification de l'énigme pour que la solution soit unique
    enigme = randomEnigma_fromConstraints(n, True, enigme)
    
    return enigme


# %% Genération version 3 : en ne partant pas d'un empilement, mais créant une grille à partir de contraintes

# L'idée ici est de partir des contraintes (-> les segments de l'énigme) pour générer la grille.
# En partant d'une énigme vide, on effectue une boucle calculant les petits cubes indéterminés (au départ, ils le sont tous !)
# puis en ajoutant une arête au hasard pour lever les indéterminations.
# Une fois tous les cubes déterminés, il se peut qu'il existe plusieurs solutions. On ajoute alors des arêtes
# permettant de sélectionner une seule solution.

# rem : ajout de l'argument par défaut enig pour permettre l'utilisation de cette fonction 
# par la fonction qui suit (randomEnigma_fromConstraints_incremental)
def randomEnigma_fromConstraints(n, trace = False, enig = []):
    start = time.monotonic()

    # la liste enig qui sera retournée est maintenant une arg par défaut.
    # Ceci a été introduit pour la fonction qui suit randomEnigma_fromConstraints_incremental
#    enig = []
    if trace : print(f"Génération d'une énigme de taille {n}")
    if trace : print("élimination des cubes indéterminés")   

    while True:
        rs = doSolve(enig, n) # la liste des Résultats de la réSolution

        rsf = list(filter(lambda m : -1 in m, rs)) # la liste des résultats contenant des cubes indéterminés
        if len(rsf) == 0:
            break       # fin de la première phase
        
        # On prend une config au hasard, avec indétermination
        M = rd.choice(rsf)

        # on calcule l'origine (en projection 2D) de tous les cubes indéterminés
        lci = []
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    if M[x, y, z] == -1:
                        lci.append(tuple(projection((x,y,z))))
        # élimination des doublons
        lci = list(set(lci)) 

        # choix au hasard de l'origine d'un cube indéterminé et de la direction de l'arête
        ci = list(rd.choice(lci))
        cid = rd.choice(["x","y","z"])
        
        # ajout de l'arête à l'énigme
        ci.append(cid)
        enig.append(tuple(ci))
        if trace : print(f"nombre d'arêtes dans l'enigme : {len(enig)}")

    if trace : print(f'durée phase 1 : {time.monotonic()-start} s ({len(rs)} solution(s))')

    # le résultat de la résolution ne contient plus d'indétermination, mais il peut y avoir plusieurs solutions.
    # Idée : si on a plusieurs solutions, on calcule la différence entre les ensembles des arêtes de la deuxième 
    # et de la première solution (arêtes dans la deuxième mais pas dans la première).
    # On en choisit alors une au hasard qu'on ajoute à l'énigme  afin de lever l'ambiguïté.
    # On relance la résolution sur la nouvelle énigme et on recommence tant qu'il existe plusieurs solutions.
    if trace : print("élimination des solutions multiples")    
    while len(rs)>1:
        # calcul de la différence ensembliste des arêtes
        ars = set(encodeSolution(encodage(rs[1]))) - set(encodeSolution(encodage(rs[0])))
        # choix d'une arête au hasard
        ar = rd.choice(list(ars))
        # ajout à l'énigme
        enig.append(ar)
        if trace : print(f"nombre d'arêtes dans l'enigme : {len(enig)}")
        # on relance la résolution
        rs = doSolve(enig, n)

    # fini : on a une solution unique !
    if trace : print(f'durée totale : {time.monotonic()-start} s')

    # pour la justification des lignes suivantes : 
    # un argument nommé ayant une valeur par défaut mutable 
    # retient cette valeur entre les appels de la fonction ...
    # (voir https://stackoverflow.com/questions/16549768/lifetime-of-default-function-arguments-in-python par ex.)
    r = enig.copy()
    # on remet les args par défaut à leurs valeurs correctes
    randomEnigma_fromConstraints.__defaults__ = (False, [])
    return r

# Expérimentalement, pour les grilles de grande dimension (>4), la durée d'exécution de la fonction peut
# devenir assez importante. Dans la fonction précédente, la première phase d'élimination des cubes indéterminés
# est celle qui prend le plus de temps.
# D'où l'idée de réduire les calculs lors de cette phase en limitant le nombre de cubes indéterminés 
# de la façon suivante :
# pour calculer une grille de taille n, on place au centre une grille de taille (n-1) d'énigme (et donc de solution)
# connue. Les seuls cubes indéterminés se retrouveront donc sur la frontière de la grille à calculer.
# En pratique, cela se révèle nettement plus rapide, et fournit des grilles difficiles et denses !
def randomEnigma_fromConstraints_incremental(n, trace = False):
    if n < 5:
        return randomEnigma_fromConstraints(n, trace)
    enigme = randomEnigma_fromConstraints(4, trace)
    for nn in range(n - 4):
        enigme = randomEnigma_fromConstraints(5 + nn, trace, enigme)
    return enigme


