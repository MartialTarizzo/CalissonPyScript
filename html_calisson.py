# html_calisson.py : fonctions d'interfaçage avec le site web de calisson
#
# ============================================================================
# Auteur : Martial Tarizzo
#
# Licence : CC BY-NC-SA 4.0 DEED
# https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr
# ============================================================================
from calisson import projection, doSolve, encodeAxes
from gen_calisson import encodage, encodeSolution

def make_tab_segments(taille=3):
    """
    retourne la liste de tous les segments traçables avec la syntaxe utilisée pour l'encodage
    des énigmes.

    Le code de cette fonction reprend du code contenu dans le fichier javascript
    traçant les différents segments de la figure.
    (voir la fonction  miseajourpointencours de javascript.js par exemple)

    La liste est dans l'ordre du tracé des segments dans le code JS : ceci est important
    car le programme web se sert de la position dans une chaîne pour connaître le status
    d'une arête
    """
    # Les coordonnées javascript sont avec origine en haut et axe y vers le bas.
    # le codage des coordonnées pour mes fonctions est avec origine au centre et axe y vers le haut
    # cette fonction effectue la transformation js -> python
    def transf_coord(tab):
        for p in tab:
            p[0][1] = 2*taille - p[0][1]
            p[1][1] = 2*taille - p[1][1]

    tabsegment = []

    # tout ce qui suit n'est qu'une reprise du code JS avec simplifications
    # car des variables sont inutiles (constamment nulles ...),
    # et mes coordonnées sont entières

    # partie gauche
    for j in range(2*taille):
        for i in range(min(taille+1, 2*taille-j)):
            if j>0 and i<taille:
                tabsegment.append([[-i, i + 2*j],
                            [-(i + 1), (i + 1) + 2*j]])
            if i<taille:
                tabsegment.append([[-i,  i  + 2*j],
                            [ -i, i + 2*(j+1)]])
            if i>0:
                tabsegment.append([[-i, i  + 2*j],
                            [-i + 1, i + 2*j + 1]])
    # partie droite sans la ligne verticale x==0
    for j in range(2 * taille):
            for k in range(min(taille + 1, 2 * taille - j)):
                if ((j > 0) and (k < taille)):
                    tabsegment.append([[ -i + k,2*j + k],
                        [(k + 1),  2*j + (k + 1)]])
                if ((k < taille) and (k > 0)):
                    tabsegment.append([[k,  2*j + k],
                        [ k,  2*(j + 1) + k]])
                if (k > 0):
                    tabsegment.append([[ k, 2*j + k],
                        [-1 + k, 1 + 2*j + k]])

    # tabsegment est maintenant une liste de segments, chaque segment est de la
    # forme [A,B], A et B étant des points, donc des listes de la forme [x, y]
    # dans le système de coordonnées JS.

    # on passe en coordonnées Python en modifiant tabsegment
    transf_coord(tabsegment)

    # on va maintenant transformer chaque segment pour passer dans la même syntaxe
    # que celle utilisée pour l'encodage Python des énigmes (X, Y, direction)

    l = [] # la liste résultat qui sera rendue par la fonction
    for cp in tabsegment: # pour chaque segment <-> couple de points
        A, B = cp[0], cp[1]
        if A[0]==B[0]: # segment selon z, l'origine est le point le plus bas
            if A[1]>B[1]:
                l.append(tuple(B + ["z"]))
            else:
                l.append(tuple(A + [ "z"]))

        elif (A[0]-B[0])*(A[1]-B[1]) > 0: # segment selon x, origine la plus à droite
            if A[0]<B[0]:
                l.append(tuple(B + ["x"]))
            else:
                l.append(tuple(A + ["x"]))
        else: # segment selon y, origine la plus à gauche
            if A[0]<B[0]:
                l.append(tuple(A + ["y"]))
            else:
                l.append(tuple(B + ["y"]))
    # C'est fini
    return l


# la chaîne argument de la page web est de la forme suivante (pour une grille de taille 3):
# "fffssfsffsfsftssfsssfsfffttfsffsssftfsftsffffsfssffsftssfsffftfsffssfsfs33301"
# t -> arête fixée non modifiable  <=> arête de l'énigme toujours affichée dans la page web
# s -> arête de la solution, non affichée (ça serait trop facile !)
# f -> arête ne faisant pas partie de la solution
# les chiffres à la fin ne sont qu'une référence vers le numéro de l'énigme : ils
# ne servent à rien ici.


# fonction qui transforme une énigme python en une chaîne d'url ayant le bon format
# pour le script JS de la page de mathix.org
# il suffit alors, sous python, d'invoquer qque chose du genre :
#   url = make_url(enigme, 5)
#   webbrowser.open(url)
# pour avoir la page de résolution de l'énigme qui s'ouvre dans son navigateur
def make_url(enigme, dim):
    """
    enigme : l'énigme à résoudre. Il est souhaitable (nécessaire !) qu'elle ne
    donne qu'une seule solution.
    dim : la taille de la zone de rangement des cubes

    retourne l'url permettant de tenter la résolution sur mathix.org
    """
    tabseg = make_tab_segments(dim)
    lsol = doSolve(enigme, dim)
    jeu = lsol[0]
    encsol = encodeSolution(encodage(jeu))
    encsol.extend(encodeAxes(jeu))

    # for i in range(dim):
    #     if not jeu[i, 0, 0]:
    #         X,Y = projection((i, 0, 0))
    #         encsol.append((X, Y, 'x'))
    #     if not jeu[0, i, 0]:
    #         X,Y = projection((0, i, 0))
    #         encsol.append((X, Y, 'y'))
    #     if not jeu[0, 0, i]:
    #         X,Y = projection((0, 0, i))
    #         encsol.append((X, Y, 'z'))

    # construction du paramètre de l'url
    str = ""
    for seg in tabseg:
        if seg in enigme:
            str += 't'
        elif seg in encsol:
            str += 's'
        else:
            str += 'f'

    # fini ...

    return 'https://mathix.org/calisson/index.html?tab=' + str

# remarque :
# si on tente d'ouvrir une adresse locale du genre :
# command = 'file://' + os.getcwd() + "/calisson_js/calisson.html?tab=" + str
# avec l'instruction suivante :
# webbrowser.open(command)
#
# Sur mon vieux mac (10.13), ça marche pas, le paramètre est effacé pour le
# navigateur par défaut (chrome). (référence au bug connue et référencée sur le web)
# Si je lance avec safari, ça marche :
# webbrowser.get('Safari').open(command)
#
# Par contre, pas de problème pour une adresse web réelle.
# C'est la raison pour laquelle "https://mathix.org/calisson/index.html?tab="
# est utilisée dans la fonction précédente
