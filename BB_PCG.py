import numpy as np
import time
import networkx as nx
import matplotlib.pyplot as plt

class Graph: 

    matrice = [] #Contient la matrice d'adjacence

    SUBPLOT_NUM = 211
    TYPE_COMMENT = "c"
    TYPE_PROBLEM_LINE = "p"
    TYPE_EDGE_DESCRIPTOR = "e"

    def __init__(self, file_name): #constructeur
        self.from_file(file_name)

    def nbNoeuds(self) :
        return len(self.matrice[0])

    def get_Matrice(self) :
        return self.matrice

    def get_Voisins(self, noeud): #renvoie la liste des voisins
        return [ v for v,i in enumerate(self.matrice[noeud]) if i != 0 ]

    def displayGraph(self,color) : #Affiche le graph et colorie les noeuds
        network = nx.from_numpy_matrix(np.array(self.matrice))
        plt.subplot(Graph.SUBPLOT_NUM, title=None)
        Graph.SUBPLOT_NUM += 1
        nx.draw_circular(network, font_weight="bold", node_color = color, with_labels=True, vmin=0, vmax=max(color))
        plt.show()  

    @staticmethod
    def parse_line(line): 
        if line.startswith(Graph.TYPE_COMMENT):
            return Graph.TYPE_COMMENT, None
        elif line.startswith(Graph.TYPE_PROBLEM_LINE):
            _, _, num_nodes, num_edges = line.split(' ')
            return Graph.TYPE_PROBLEM_LINE, (int(num_nodes), int(num_edges))
        elif line.startswith(Graph.TYPE_EDGE_DESCRIPTOR):
            _, node1, node2 = line.split(' ')
            return Graph.TYPE_EDGE_DESCRIPTOR, (int(node1), int(node2))
        else:
            raise ValueError(f"Unable to parse '{line}'")

    def from_file(self, filename): #Contruit la matrice d'adjacence à partir des fichiers fournis
        self.matrice = None
        with open(filename) as f:
            problem_set = False
            for line in f.readlines():
                line_type, val = Graph.parse_line(line.strip())
                if line_type == Graph.TYPE_COMMENT:
                    continue
                elif line_type == Graph.TYPE_PROBLEM_LINE and not problem_set:
                    num_nodes, num_edges = val
                    self.matrice = [ [0 for _ in range(num_nodes)] for _ in range(num_nodes) ]
                    problem_set = True
                elif line_type == Graph.TYPE_EDGE_DESCRIPTOR:
                    if not problem_set:
                        raise RuntimeError("Edge descriptor found before problem line")
                    node1, node2 = val
                    self.matrice[node1-1][node2-1] = 1
                    self.matrice[node2-1][node1-1] = 1
        return self.matrice

def GraphColoring(graph) :
    """
    La fonction chargée du traitement global
    la coloration finale se trouvera dans Solution
    Le parcours de l'arbre se fait en empilant les contexte
    """
    nbNoeuds = graph.nbNoeuds()
    colors = [0]*nbNoeuds #Liste des couleurs, 0 signifie la non coloration d'un noeuf
    pile = [] #pile de parcours
    max_color = greedy_Heurisic(graph,nbNoeuds,0)
    solution = colors.copy(),max_color+1 #Contient la meilleur solution réalisable : la plus optimale
    print("Nombre de couleurs avec Heurisitque = ", max_color)
    colors[0] = 1 #initaliser le premier noeud
    pile.append([colors.copy(),0,1]) #Empiler le contexte initial
    while (pile): #tant que la pile n'est pas vide
        colors, indice, nbcouleur = pile.pop() #On dépile
        if (indice != nbNoeuds -1 ) : #Nous n'avons pas atteint un noeud feuille
            indice += 1 #Passer au noeud suivant
            for color in generate_validColors(indice,graph,colors,max_color) :
                #Générer les couleurs possibles = solutions réalisables
                if color not in colors : 
                    nbcouleur = nbcouleur + 1 #Si la couleur n'a jamais été utilisée auparavent
                    if nbcouleur >= solution[1] :
                        break
                colors[indice] = color #Colorer le noeud
                if (Eval(indice,graph, colors, nbcouleur,nbNoeuds) < solution[1] ) : #Tester la condition de non élagage
                    pile.append([colors.copy(), indice, nbcouleur]) #Empiler le contexte
        else : #Le noeud feuille a passé le test d'évaluation avant empilation, il est donc optimal
            solution = colors.copy(), nbcouleur #Remplacer la solution optimale
    end = time.time()
    print("Temps d'execution = ", end-start," seconds")
    print("Le nombre de couleurs optimal = ", solution[1])
    #Une fois la pile vide, la solution finale est contenue dans la variable solution
    graph.displayGraph(solution[0].copy())

def generate_validColors(v,graph,colors,max_color) :
    """
    Génère les couleur valides d'un noeuds
    le noeud v étant le dernier noeud à colorer, nous parcourant les noeuds d'indice inférieur à lui
    Et ce en retirant les couleurs de ses voisins à l'ensemble des couleurs disponibles
    """
    Restricted_Colors = [colors[i] for i in [j for j in graph.get_Voisins(v) if j<v]]
    return [i for i in range(1,max_color+1) if i not in Restricted_Colors]


def greedy_Heurisic(graph,nbNoeuds,nb_colors): #Heuristique Gloutonne de Welsh et Powell pour l'initalisation
    welshEtpowell = [0]*nbNoeuds
    cpt = nb_colors
    for i in range(nbNoeuds) :
                couleur = generate_validColors(i,graph,welshEtpowell,nbNoeuds-1)[0] #ICi ça me dit index out of range, ça veut dire qu'il y a aucune couleur possible, et ça c'est bizarre
                if (couleur not in welshEtpowell) : cpt = cpt + 1 #Nouvelle couleur utilisée
                welshEtpowell[i] = couleur
    return cpt

def Eval(niveau, graph, colors, nb_colors, nb_noeuds):
    """
    Calcul l'évaluation du noeud courant
    """
    increment = False
    for v in range(niveau +1, nb_noeuds) :
        voisins = graph.get_Voisins(v)
        if (len(set([colors[i] for i in voisins])) >= nb_colors) :
        #toutes les couleurs avoisinent v : on retourne au moins nb_colors +1
            increment = True
            for j in range(v + 1,nb_noeuds) :
                if (j in voisins) and (len(set([colors[i] for i in graph.get_Voisins(j)])) >= nb_colors) :
        #Si un voisin non coloré de ce noeud est aussi voisin de toutes les couelurs : on retourne nb_colors +2
                    return nb_colors + 2
    return (nb_colors + 1) if increment else nb_colors

dataset = input("Entrer le nom du dataset: ")
monGraph = Graph(dataset)
start = time.time()
end = 0.0
GraphColoring(monGraph)
