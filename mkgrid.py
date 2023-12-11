# %%
import time
from gen_calisson import randomEnigma2
from html_calisson import make_url
import pyscript

@pyscript.when("click","#mkgrid")
def mkGrid(event):

    elem_n = pyscript.document.querySelector("#taille")
    n = int(elem_n.value)
    elem_easy = pyscript.document.querySelector("#facilite")
    n = int(elem_n.value)
    eas = int(elem_easy.value)

    elem_info = pyscript.document.querySelector("#info")
    elem_info.innerText = "Calcul de la grille en cours ..."

    deb = time.monotonic()
    enigme = randomEnigma2(n, [], trace = True, easy = eas)
    elem_info.innerText = f"Grille calculée en {time.monotonic()-deb:.2f} s"
    
    url = make_url(enigme, n)
    tab = url.split("=")[-1]
    element = pyscript.document.querySelector("#game")
    element.src = "./calisson.html?tab=" + tab
    

# mkGrid(4)