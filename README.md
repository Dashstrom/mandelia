# Mandelbrot

Ancien projet fait en Cython/Python avec Tkinter pour afficher la fractale de Mandelbrot.

# Usage
Lancer l'application avec `main.py`.
Pour les fonctionnalitées principales vous pouvez selectionner une zone pour zoomer
et double clicker pour faire un gif plongeant

# Exemmple

# About
En mathématiques, l'ensemble de Mandelbrot est une fractale définie
comme l'ensemble des points c du plan complexe pour lesquels la suite
de nombres complexes définie par récurrence par :
z₀=0
zₙ₊₁=zₙ²+c
est bornée.

L'ensemble de Mandelbrot a été découvert par Gaston Julia
et Pierre Fatou1 avant la Première Guerre mondiale. Sa définition et
son nom actuel sont dus à Adrien Douady, en hommage aux représentations
qu'en a réalisées Benoît Mandelbrot dans les années 1980. Cet
ensemble permet d'indicer les ensembles de Julia : à chaque point
du plan complexe correspond un ensemble de Julia différent. Les
points de l'ensemble de Mandelbrot correspondent précisément aux
ensembles de Julia connexes, et ceux en dehors correspondent aux
ensembles de Julia non connexes. Cet ensemble est donc intimement
lié aux ensembles de Julia, ils produisent d'ailleurs des formes
similairement complexes.

Les images de l'ensemble de Mandelbrot sont réalisées en parcourant
les nombres complexes sur une région carrée du plan complexe et
en déterminant pour chacun d'eux si le résultat tend vers l'infini
ou pas lorsqu'on y itère une opération mathématique. On considère
la partie réelle et imaginaire de chaque nombre complexe comme des
coordonnées et chaque pixel est coloré selon la rapidité de
divergence, ou si elle ne diverge pas.

Les images de l'ensemble de Mandelbrot exposent une limite
élaborée qui révèle progressivement des détails récursifs
toujours plus fins en augmentant le grossissement. La limite
de l'ensemble est constituée de plus petites versions de la
forme principale,donc la propriété fractale de l'autosimilarité
s'applique à l'ensemble tout entier (et pas simplement à
certaines parties).

L'ensemble de Mandelbrot est devenu populaire hors des
mathématiques, comme inspiration artistique et comme
exemple de structure complexe venant de l'application
de règles simples. C'est l'un des exemples les plus
connus de visualisation mathématique.

Source: https://fr.wikipedia.org/wiki/Ensemble_de_Mandelbrot
