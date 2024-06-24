import matplotlib.pyplot as plt
import numpy as np
import random as rd
from math import *
from copy import deepcopy

##         Le coin des variables globales modifiées dans des fonctions (dangeureux..)

Listetrous=[]   #cf evpour,evpour2
ListeSorties=[]  #cf evpour,evpour2
Listeobstacles=[] #cf evpour,evpour2
listeGens=[] #cf evpour,evpour2,passage:2eme ligne: attention au sens de parcourt de listeGens! à modifier si probleme (a cause d'une evolution du programme) car un peu dangeureux!
tableauDistancesSorties=[]
tableauDistancesObstacles=[]

isortie=[0,1,2] #cf ListeSorties,tableauDistancesSorties,evpour,evpour2,moyennesimu(1 et 2),sortie_mouvante

nombreGensPaniqueBefore=0
nombreGensPaniqueAfter=0
nombreGensRestants=0 #definitions à revoir?
nombreGensDebut=0

cstPaniqueGens=1 #DOIT ETRE ASSEZ GRANDE (mais pas trop--> proba) (liée au nombre de gens (et à la taille de L))
cstPaniqueSituation=0.05 #la même tout au long de l'évacuation: car elle dépend de la situation(+ ou - dangeureuse)

tempsfonction=0
t3=0


# def f(x):            #exemple
#     global y
#     y = y+x
#     return x+1

##                                     Programmation évacuation 


def jsortie(L):
    return len(L)-1

def somme(L):
    s=0
    for i in range(len(L)):
        for k in range(len(L[i])):
            s+=L[i][k]
    return s 

def appartient(l,e):                    #verifier si un élément est dans une liste: utilisée pour la fonction "bouger"
    m=False
    for k in l:
        if k==e:
            m=True
    return m


def panique(L):
    global nombreGensPaniqueAfter                     #DANGER
    NiveauPanique=cstPaniqueSituation+nombreGensRestants+nombreGensPaniqueBefore
    
    proba_a_atteindre=cstPaniqueSituation+cstPaniqueGens*(nombreGensRestants+15*nombreGensPaniqueBefore)/(16*nombreGensDebut)
    #la constante "15" choisie correspond à L'INFLUENCE DE LA PANIQUE!
    #print(proba_a_atteindre)
    if rd.random()<=proba_a_atteindre:
        nombreGensPaniqueAfter+=1
        return True
    else:
        return False
    
    
    

def listeVoi(M,i,k):
    if 0<i<len(M)-1 and 0<k<len(M)-1:   #la liste des voisins sur la grille d'un point donné
        return [(i+1,k),(i-1,k),(i,k-1),(i,k+1)]
    if i==0 and k!=0 and k!=len(M)-1:
        return [(i+1,k),(i,k-1),(i,k+1)]
    if i==len(M)-1 and k!=0 and k!=len(M)-1:
        return [(i-1,k),(i,k-1),(i,k+1)]
    if k==0 and i!=len(M)-1 and i!=0:
        return [(i+1,k),(i-1,k),(i,k+1)]
    if k==len(M)-1 and i!=len(M)-1 and i!=0:
        return [(i+1,k),(i-1,k),(i,k-1)]
    if (i,k)==(0,0):
        return [(i+1,k),(i,k+1)]
    if (i,k)==(len(M)-1,0):
        return [(i-1,k),(i,k+1)]
    if (i,k)==(0,len(M)-1):
        return [(i+1,k),(i,k-1)]
    if (i,k)==(len(M)-1,len(M)-1):
        return [(i-1,k),(i,k-1)]

def sommevoisin(L,i,j):
    s=0
    V=listeVoi(L,i,j)
    for v in V:
        s+=L[v[0]][v[1]]
    return s
        

def choix(L,i,j):
    if il_y_a_un_obstacle_devant(L,i,j):        #deux situations possibles: soit il y a un obstacle devant alors -> fn goobstacle
        return goobstacle(L,i,j)                # soit il n'y en a pas alors -> fn gosortie
    else:
        return gosortie(L,i,j)

def choixestpossible(L,id,jd):
    if L[id][jd]==1:
        return False
    if appartient(Listeobstacles,(id,jd)):                 #si c'est un obstacle ou si il y a deja quelqu'un alors on peut pas y aller
        return False
    return True

def il_y_a_un_obstacle_devant(L,i,j):
    A=Listeobstacles                             #renvoie si oui ou non il y a une ligne d'obstacle entre nous et la sortie
    if A==[]:
        return False
    elif j<A[0][1]:
        return True
    return False
    
def gosortie(L,i,j):
    Voi=listeVoi(L,i,j)
    D=[]
    V=[]
    for k in range(len(Voi)):                   #on créé la liste des voisins ou ya pas deja quelqu'un
        (a,b)=(Voi[k][0],Voi[k][1])
        if choixestpossible(L,a,b):
            V.append((a,b))
    
    if V!=[]:       #si au moins un des voisins est libre...
        for k in range(len(V)):                            
            D.append(tableauDistancesSorties[V[k][0],V[k][1]]) #on créé la liste correspondante avec les distance sa la sortie des voisins
        Dmin=min(D)
        for k in range(len(V)):
            if D[k]==Dmin:
                return V[k]    #on renvoie comme choix de direction celui le plus proche d'une sortie quelconque
    else:
        return (i,j) #si on est bloqué on reste sur place

def distance(a,b):
    return (a[0]-b[0])**2+(a[1]-b[1])**2
        
def goobstacle(L,i,j):
    Voi=listeVoi(L,i,j)
    D=[]
    V=[]
    for k in range(len(Voi)):                   #on créé la liste des voisins ou ya pas deja quelqu'un et qui est pas un obstacle
        (a,b)=(Voi[k][0],Voi[k][1])
        if choixestpossible(L,a,b):
            V.append((a,b))
    if V!=[]:       #si au moins un des voisins est libre...
        for k in range(len(V)):                             
            D.append(tableauDistancesObstacles[V[k][0],V[k][1]]) #on créé la liste correspondante avec les distance sa la sortie des voisins
        Dmin=min(D)
        for k in range(len(V)):
            if D[k]==Dmin:
                return V[k]   #on renvoie comme choix de direction celui le plus proche d'une sortie quelconque
    else:
        return (i,j) #si on est bloqué on reste sur place
    
# def obstaclevise(L,i,j):   #Avec la programmation actuelle, les obstacles doivent être placés sur une seule colonne...
#     colonne=Listeobstacles[0][1]
#     coordopti=(0,colonne)                   #On cherche le trou le plus proche
#     Distmin=len(L)**2
#     for coordtrou in Listetrous:
#         D=distance(coordtrou,(i,j))
#         if D<Distmin:
#             Distmin=D
#             coordopti=coordtrou
#     return coordopti
    
def bouger(L,i,j,k,p1):
    if rd.random()>=p1:  #un facteur aléatoire qui peut faire que la personne n'avance pas
        if appartient(ListeSorties,(i,j)):       #si le 1 est sur une des sorties il part
            L[i][j]=0
            listeGens.pop(k)
        else:
            (id,jd)=choix(L,i,j)                    #sinon il va là où la fonction "choix" le dirige
            L[i][j]=0
            L[id][jd]=1
            listeGens[k]=(id,jd)
        
def passage(L,p1):
    rd.shuffle(listeGens)
    for k in range(len(listeGens)-1,-1,-1):             #on fait bouger chaque personne chacun son tour
    #MODIFICATION: on parcourt dans le sens indirect! et cela influe sur la façon dont les éléments sont gérés! attention!
        (i,j)=(listeGens[k][0],listeGens[k][1])
        # if sommevoisin(L,i,j)<=3 and not panique(L):       # ajout de différentes perturbations: panique + si il y a trop de voisins je fait un malaise a 50% de chances           
        #     bouger(L,i,j,k,p1)
        # else:
        #     if rd.random()>0.5:
        #         bouger(L,i,j,k,p1)
        bouger(L,i,j,k,p1) #sans ajout de perturbations
        

def evolution(L,p1):                #p1 la prob qu'une personne n'avance pas a son tour
    global nombreGensRestants                     #DANGER
    global nombreGensPaniqueBefore                     #DANGER
    global nombreGensPaniqueAfter                      #DANGER
    global nombreGensDebut                             #DANGER
    
    étape=0
    nombreGensPaniqueBefore=0
    nombreGensRestants=len(listeGens)
    nombreGensDebut=nombreGensRestants
    listeEtape=[]                                   #pour le tracé
    listeGensSortis=[]
    nombreGensAvant=nombreGensRestants
    while nombreGensRestants!=0:
        nombreGensPaniqueBefore=nombreGensPaniqueAfter
        nombreGensPaniqueAfter=0
        
        passage(L,p1)
        étape+=1
        M=np.ones((len(L),len(L[0]),3),dtype=float)
        for a in Listeobstacles:                               #test pour afficher les obstacles
            M[a[0]][a[1]]=np.array((0,0,1))
        for a in ListeSorties:
            if L[a[0]][a[1]]!=1:
                M[a[0]][a[1]]=np.array((0.5,0.5,0.5))
        for a in listeGens:
            M[a[0]][a[1]]=np.array((1,0,0))
        plt.imshow(M,interpolation="none")
        #plt.imshow(L,cmap="binary",interpolation="none")
        
        axes = plt.gca()    #pour afficher la grille
        s=len(L)
        axes.set_xlim(0.5, s-0.5)
        axes.set_ylim(0.5, s-0.5)
        axes.xaxis.set_ticks([0.5+k for k in range(s)])
        axes.yaxis.set_ticks([0.5+k for k in range(s)])
        axes.xaxis.set_ticklabels([])
        axes.yaxis.set_ticklabels([])
        axes.grid(True,linewidth = 0.25)
        
        plt.show()
        plt.pause(0.5)
        # print("étape numéro: "+str(étape)+" il en reste "+str(somme(L)))
        # print("-"*3*(len(L)-1))
        
        nombreGensRestants=len(listeGens)
        
        listeEtape.append(étape)                                     #pour le tracé
        listeGensSortis.append(nombreGensAvant-nombreGensRestants)
        nombreGensAvant=nombreGensRestants
        
        # print(nombreGensPaniqueAfter)
        # print(nombreGensRestants)
        # print("ok")
        
    # plt.clf()
    # plt.plot(listeEtape,listeGensSortis)
    # #plt.plot(listeEtape,lineariseBof(listeGensSortis))
    # plt.plot(listeEtape,lineariseBofBis(listeGensSortis,6))
    # plt.legend()
    # plt.xlabel("étape")
    # plt.ylabel("nombre d'individus qui évacuent")
    # plt.show()
        
    return étape
        
##                                 Fonctions de tracés 

def evpour(p,s,p1):
    global Listetrous                        #DANGER
    global isortie                           #DANGER
    global ListeSorties                      #DANGER
    global Listeobstacles                    #DANGER
    global listeGens                         #DANGER
    global tableauDistancesSorties           #DANGER
    global tableauDistancesObstacles         #DANGER
    
    n=int(s**2*p/100)
    L=[[0 for k in range(s)] for k in range(s)]
    L[4][6]=1
    L[3][6]=1
    L[5][6]=1
    L[4][5]=1
    L[4][7]=1
    # M=[0 for k in range(s**2)]
    # for k in range(n):
    #     M[k]=1
    # rd.shuffle(M)
    # for k in range(len(M)):
    #     L[k//s][k%s]=M[k]
    # n=int(s**2*p/100)
    
    
    
    
    
    
    #Listeobstacles=[]                              #sans obstacles
    #Listeobstacles=[(int(len(L)/2)+k,len(L)-6) for k in range(-4,4)]        #(modifiable a volonté)
    Listeobstacles=[(int(len(L)/2)+2*k,len(L)-2) for k in range(-6,7)]      #filtre
    liste=[]
    taillemurets=5
    tailletrous=2
    decalage=-2
    for k in range(-1,2):
        for l in range(taillemurets):
            liste.append((int(len(L)/2)+k*(taillemurets+tailletrous)+l+decalage,len(L)-6))
    Listeobstacles=liste
        
    
    
    #isortie=[int(len(L)/2)]
    isortie=[int(len(L)/2)+k for k in range(-2,3)]
    #isortie=[2+l for l in range(-2,1)]
    
    ListeSorties=[]
    for a in range(len(isortie)):
        ListeSorties.append((isortie[a],jsortie(L)))                    #la liste des coordonnées des sorties: la ou les 1 doivent devenir des 0
    
    

    if len(Listeobstacles)==0:
         Listetrous=[(i,len(L)-3) for i in range (len(L))]
    else:
        
        Listetrous=[]
        colonne=Listeobstacles[0][1]
        incrL=0                                      #l'indice de la ligne qu'on va incrémenter
        for k in range(len(Listeobstacles)):  #... et doivent être rangés par indice de ligne croissant
            while incrL!=Listeobstacles[k][0]:
                Listetrous.append((incrL,colonne))  #On ne garde que les cases sans obstacle
                incrL+=1
            incrL+=1
        for l in range(incrL,len(L)):           #On complète la liste jusqu'à la fin de la colonne
            Listetrous.append((l,colonne))
            
    
    
    listeGens=[]
    for i in range(len(L)):
        for j in range(len(L[i])):                  #la liste des gens dans la liste a une étape en particulier
            if L[i][j]==1:
                listeGens.append((i,j))
            
    
    if Listeobstacles!=[]:
        tableauDistancesObstacles=np.zeros((len(L),Listeobstacles[0][1]+1))
        for i in range(len(L)):
            for j in range(Listeobstacles[0][1]+1):
                A=[]
                for trou in Listetrous:
                    A.append(np.sqrt((i-trou[0])**2+(j-trou[1])**2))   #renvoie la distance minimale a n'importe quelle sortie pour un couple donné
                tableauDistancesObstacles[i,j]=min(A)
            
    
    tableauDistancesSorties=np.zeros((len(L),len(L[0])))
    for i in range(len(L)):
        for j in range(len(L[0])):
            A=[]
            for a in range(len(isortie)):
                A.append(np.sqrt((i-isortie[a])**2+(j-jsortie(L))**2))   #renvoie la distance minimale a n'importe quelle sortie pour un couple donné
            tableauDistancesSorties[i,j]=min(A)
    
    
    return evolution(L,p1)
                
def evpour2(li,lj,p,s,p1):    #li et lj sont des couples (liinf,lisup) et (ljinf,ljsup)
    global Listetrous                        #DANGER
    global isortie                           #DANGER
    global ListeSorties                      #DANGER
    global Listeobstacles                    #DANGER
    global listeGens                         #DANGER
    global tableauDistancesSorties           #DANGER
    global tableauDistancesObstacles         #DANGER
    
    nb_lignes=li[1]-li[0]+1
    nb_colonnes=lj[1]-lj[0]+1
    taillematrice_de_repartition=nb_lignes*nb_colonnes      
    n=int(taillematrice_de_repartition*p/100)     #attention, ici le p ne correspond pas à la matrice de taille s**2 mais à celle 
    L=[[0 for k in range(s)] for k in range(s)]   #formée avec li et lj! (veiller à bien adapter p en conséquence)
    M=[0 for k in range(taillematrice_de_repartition)]
    for k in range(n):
        M[k]=1
    rd.shuffle(M)
    for k in range(len(M)):
        L[(k//nb_colonnes)+li[0]][(k%nb_colonnes)+lj[0]]=M[k]
        
        
    #Listeobstacles=[]                              #sans obstacles
    #Listeobstacles=[(int(len(L)/2)+k,len(L)-6) for k in range(-4,4)]        #(modifiable a volonté)
    Listeobstacles=[(int(len(L)/2)+2*k,len(L)-2) for k in range(-6,7)]      #filtre
    liste=[]
    taillemurets=5
    tailletrous=2
    decalage=-2
    for k in range(-1,2):
        for l in range(taillemurets):
            liste.append((int(len(L)/2)+k*(taillemurets+tailletrous)+l+decalage,len(L)-6))
    Listeobstacles=liste
            
        
        
    #isortie=[int(len(L)/2)+k for k in range(-2,2)]
    isortie=[int(len(L)/2)+k for k in range(-2,3)]
    #isortie=[5+l for l in range(-2,1)]
    
    ListeSorties=[]
    for a in range(len(isortie)):
        ListeSorties.append((isortie[a],jsortie(L)))                    #la liste des coordonnées des sorties: la ou les 1 doivent devenir des 0



    if len(Listeobstacles)==0:
         Listetrous=[(i,len(L)-3) for i in range (len(L))]
    else:
        Listetrous=[]
        colonne=Listeobstacles[0][1]
        incrL=0                                      #l'indice de la ligne qu'on va incrémenter
        for k in range(len(Listeobstacles)):  #... et doivent être rangés par indice de ligne croissant
            while incrL!=Listeobstacles[k][0]:
                Listetrous.append((incrL,colonne))  #On ne garde que les cases sans obstacle
                incrL+=1
            incrL+=1
        for l in range(incrL,len(L)):           #On complète la liste jusqu'à la fin de la colonne
            Listetrous.append((l,colonne))
        
        
    
    listeGens=[]
    for i in range(len(L)):
        for j in range(len(L[i])):                  #la liste des gens dans la liste a une étape en particulier
            if L[i][j]==1:
                listeGens.append((i,j))
                
    if Listeobstacles!=[]:
        tableauDistancesObstacles=np.zeros((len(L),Listeobstacles[0][1]+1))
        for i in range(len(L)):
            for j in range(Listeobstacles[0][1]+1):
                A=[]
                for trou in Listetrous:
                    A.append(np.sqrt((i-trou[0])**2+(j-trou[1])**2))   #renvoie la distance minimale a n'importe quelle sortie pour un couple donné
                tableauDistancesObstacles[i,j]=min(A)
            
    
    tableauDistancesSorties=np.zeros((len(L),len(L[0])))
    for i in range(len(L)):
        for j in range(len(L[0])):
            A=[]
            for a in range(len(isortie)):
                A.append(np.sqrt((i-isortie[a])**2+(j-jsortie(L))**2))   #renvoie la distance minimale a n'importe quelle sortie pour un couple donné
            tableauDistancesSorties[i,j]=min(A)
    
    return evolution(L,p1)

def unesimu(s,p1):             #simule des évacuations avec p variant et renvoie la liste du
    Y=[]                            #temps d'évacuation en fonction de p
    for p in np.linspace(1,40,20):
        Y.append(evpour(p,s,p1))
    return Y

def unesimu2(li,lj,s,p1):             #simule des évacuations avec p variant et renvoie la liste du
    Y=[]                            #temps d'évacuation en fonction de p
    for p in np.linspace(10,70,8):
        Y.append(evpour2(li,lj,p,s,p1))
    return Y    

def moyennesimu(n,s,p1):    
    
    X=[p for p in np.linspace(1,40,20)]           #calcule la moyenne de n simulations et la plot
    Y=[0 for p in range(20)]
    for k in range(n):
        Z=unesimu(s,p1)
        for i in range(len(Z)):
            Y[i]+=Z[i]
        print(n-k)
    for i in range(len(Y)):
        Y[i]/=n
    plt.clf()
    plt.plot(X,Y,label="p1="+str(p1))
    #plt.plot(X,Y,".",label="isortie="+str(isortie[0]+1))
    plt.legend()
    plt.xlabel("pourcentage de gens")
    plt.ylabel("temps d'évacuation")
    #plt.title("moyenne à taille fixée s="+str(s))
    plt.show()
    #print("isortie=",isortie[0]+1)
    
def moyennesimu2(li,lj,n,s,p1):
    X=[p for p in np.linspace(10,70,8)]           #calcule la moyenne de n simulations et la plot
    Y=[0 for p in range(8)]
    for k in range(n):
        Z=unesimu2(li,lj,s,p1)
        for i in range(len(Z)):
            Y[i]+=Z[i]
        print(n-k)
    for i in range(len(Y)):
        Y[i]/=n
    #plt.clf()
    #plt.plot(X,Y)
    plt.plot(X,Y,".",label="isortie="+str(isortie[0]+1))
    plt.legend()
    plt.xlabel("pourcentage de gens")
    plt.ylabel("temps d'évacuation")
    #plt.title("moyenne à taille fixée s="+str(s))
    #plt.show()
    print("isortie=",isortie[0]+1)

def ungraphep1(p,s):
    X=[p1 for p1 in np.linspace(0,0.999,100)]
    Y=[]
    for p1 in X:
        Y.append(evpour(p,s,p1))
    return Y
    
def moyennegraphep1(n,p,s):
    X=[p1 for p1 in np.linspace(0,0.999,100)]           #pour tracer temps d'évac en fn de p1 la pro de tomber 
    Y=[0 for p1 in X]
    for k in range(n):
        L=ungraphep1(p,s)
        for i in range(len(L)):
            Y[i]+=L[i]
        print(n-k)
    for i in range(len(Y)):
        Y[i]/=n
    plt.plot(X,Y,label="p=5")
    plt.legend()
    plt.show()
        
def moyennetempsevac(p,s,p1,n):
    m=0
    for k in range(n):
        
        m+=evpour(p,s,p1)  
        print(n-k)      
    return m/n    

def moyennetempsevac2(li,lj,p,s,p1,n):
    m=0
    for k in range(n):
        m+=evpour2(li,li,p,s,p1)  
    return m/n

def sortie_mouvante(li,lj,n,p1,taillesortie,s=19): #ATTENTION à l'ordre inhabituel des arguments
    global isortie              #DANGER (pour le global) + ne pas oublier de ctrl r la ligne avec isortie dans evpour()
    iinf=int(-taillesortie//2)
    isup=int(taillesortie//2)
    if isup-iinf==taillesortie:  #normalement cette condition est toujours vérifiée pour taillesortie de type int
        for k in range(-iinf,-iinf+int(s/2)+2):  #ne pas prendre des matrices trop petites (relativement par rapport à taillesortie)
            isortie=[k+l for l in range(iinf,isup)]
            moyennesimu2(li,lj,n,s,p1) #ne pas oublier de faire les modifs adaptées dans moyennesimu()
    plt.show()

def sortie_mouvante_pfixe(li,lj,n,p1,taillesortie,p,s=19): #ATTENTION à l'ordre inhabituel des arguments
    global isortie              #DANGER (pour le global) + ne pas oublier de ctrl r la ligne avec isortie dans evpour()
    X=[]
    Y=[]
    iinf=int(-taillesortie//2)
    isup=int(taillesortie//2)
    if isup-iinf==taillesortie:  #normalement cette condition est toujours vérifiée pour taillesortie de type int
        for k in range(-iinf,-iinf+int(s/2)+2):  #ne pas prendre des matrices trop petites (relativement par rapport à taillesortie)
            isortie=[k+l for l in range(iinf,isup)]
            indicesortie=isortie[0]+1   #à modifier: milieu de la sortie (dépend de taillesortie)
            distance_trou1=sqrt(distance((5.5,13),(indicesortie,18)))
            distance_trou2=sqrt(distance((12.5,13),(indicesortie,18)))
            d=distance_trou1+distance_trou2
            X.append(d)   
            Y.append(0)
            for q in range(n):
                Y[k]+=evpour2(li,lj,p,s,p1)
            Y[k]/=n
        plt.clf()
        plt.plot(X,Y,".")
        plt.legend()
        plt.xlabel("somme des distances du milieu de la sortie aux fentes")
        plt.ylabel("temps d'évacuation")
        #plt.title("moyenne à taille fixée s="+str(s))
        plt.show()
        
def lineariseBof(liste,pas=3):  #-pas et +pas donc le pas va donner un pas double ici! attention..
    longueur=len(liste)
    ListeLinearise=[]
    for k in range(longueur):
        somme=0
        if k<pas:
            for i in range(k+pas+1):
                somme+=liste[i]
            ListeLinearise.append(somme/(k+pas+1))
        elif k>(longueur-pas-1):
            for i in range(k-pas,longueur):
                somme+=liste[i]
            ListeLinearise.append(somme/(longueur-k+pas))
        else:
            for i in range(k-pas,k+pas+1):
                somme+=liste[i]
            ListeLinearise.append(somme/(2*pas+1))
    return ListeLinearise

def lineariseBofBis(liste,pas=3):   #avec moins de valeurs  #le pas est le vrai pas ici
    longueur=len(liste)
    ListeLinearise=[]
    compteur=0
    somme=0
    for k in range(longueur):
            somme+=liste[k]
            compteur+=1
            if compteur==pas:
                for i in range(pas):
                    ListeLinearise.append(somme/pas)
                somme=0
                compteur=0
    for i in range(compteur):
        ListeLinearise.append(somme/compteur)
    
    return ListeLinearise
        
        

























