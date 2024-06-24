import random as rd
import numpy as np
from copy import deepcopy
import time
import matplotlib.pyplot as plt

### Constantes

dimPiecei=50.0  #abscisse,i     , on considère d'abord une pièce rectangulaire, et on prend
dimPiecej=40.0  #ordonnée,j       les murs en compte dans la taille

tailleMurs=3  # en mètres

pasFastMarching=1 #pas des matrices correspondantes (à.. aux bords? (division euclidienne..))


# dureeTot=10 # en secondes
# nbEtapes=1000
# pasTemps=dureeTot/nbEtapes
pasTemps=0.08
etape=0


Rind=0.5 #le rayon d'un individu en mètres
#kInd=10000 #en N/m (50 kg --> 500N --> fait bouger de 5cm -->10000N/m)
kInd=300 #en N/m, valeur pour tester
kMurs=7*kInd # 2 fois plus raide (2 fois moins mou..) 
#en vrai + encore vu qu'il y a dans le cas général (pas dans un coin) plus de volume interpenetré que dans l'autre cas pour une meme elongation l nan? (à vérifier, approfondir, ...)
Mind=70 #la masse d'un individu en kg

normeVsouhaitee=0.8 #en m/s (à mieux choisir)
tempsRelaxation=5 #en s (à mieux choisir, et voir ce à quoi ça correspond...)

nombreGensHorsLimite=0 #cf passage()
etapeStationnaire=0 #cf evacuation()


g=9,81 # en m.s^-1

###Fonctions auxiliaires

def discretisationM(i,j,M):
    n,p=M.shape[0],M.shape[1]   
    disi=min(int(i*n/dimPiecei),n-1)  #on calcule les coordonnées associées à (i,j) dans la matrice M
    disj=min(int(j*p/dimPiecej),p-1)
    return(disi,disj)
    
def analogisationM(i,j,M): #"""revoir le nom""" #faire attention à l'utilisation de cette fonction: ne représente
    n,p=M.shape[0],M.shape[1]                                   #pas une case mais juste son centre!
    anai=(i+1/2)*dimPiecei/n
    anaj=(j+1/2)*dimPiecej/p
    return(anai,anaj)
    
def distance(i1,j1,i2,j2):
    return np.sqrt((i1-i2)**2+(j1-j2)**2)

def listeVois(i,j,M):   #la liste des voisins sur la grille d'un point donné (4 voisins)
    p,q=M.shape[0],M.shape[1]
    L=[]
    Lvois=[(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
    for vois in Lvois:
        (k,l)=vois
        if k!=-1 and k!=p and l!=-1 and l!=q:
            L.append(vois)
    return L
    
def listeVoisBis1(i,j,M):   #la liste des voisins dans un carré de côté 3 centré en (i,j)
    p,q=M.shape[0],M.shape[1]
    L=[]
    Lvois=[]
    for k in range(-1,2):
        for l in range(-1,2):
            if k!=0 or l!=0:
                Lvois.append((i+k,j+l))
    for vois in Lvois:
        (k,l)=vois
        if k>-1 and k<p and l>-1 and l<q:
            L.append(vois)
    return L

def listeVoisBis2(i,j,M):   #la liste des voisins dans un carré de côté 5 centré en (i,j)
    p,q=M.shape[0],M.shape[1]
    L=[]
    Lvois=[]
    for k in range(-2,3):
        for l in range(-2,3):
            if k!=0 or l!=0:
                Lvois.append((i+k,j+l))
    for vois in Lvois:
        (k,l)=vois
        if k>-1 and k<p and l>-1 and l<q:
            L.append(vois)
    return L

### Initialisations

def initMenvironnement(dimi,dimj,a): #on initialise une matrice de l'environnement (obstacles et sorties) (carrés de côtés a, entier divisant dimi et dimj)
    di=int(dimi/a)  #(nombre de cases à l'intérieur de la pièce + les murs)
    dj=int(dimj/a)
    M=np.zeros((di,dj), dtype=int)
    for i in range(di):    #on met des murs aux bords de la salle (en fait nan: plus facile pour discretisationM)
        M[i,0]=-1          #et des sorties à l'extérieur
        M[i,1]=1
        M[i,dj-1]=-1
        M[i,dj-2]=1
    for j in range(1,dj-1):
        M[0,j]=-1
        M[1,j]=1
        M[di-1,j]=-1
        M[di-2,j]=1
    return M
    
# a=5
# assert dimPiecei%a==0 and dimPiecej%a==0 #on vérifie que a divise dimi et dimj
Menvironnement=initMenvironnement(dimPiecei,dimPiecej,tailleMurs)

for i in range(1,5):          #exemple de configuration des murs pour tailleMurs=1
    for j in range(4,5):
        Menvironnement[i,j]=1
        
for i in range(3,10):
    for j in range(-5,-4):
        Menvironnement[i,j]=1
        
for i in range(3,10):
    for j in range(-5,-4):
        Menvironnement[i,j]=1
        
for i in range(8,9):
    for j in range(1,9):
        Menvironnement[i,j]=1
        

Menvironnement [3,1]=0 #exemple de configuration de sortie
Menvironnement [-3,1]=0   

    



#Menvironnement[5,1]=0
#Menvironnement[5,0]=-1 

# print(Menvironnement)
        

### Fast Marching: construction du champ des distances geodesiques a la sortie
"""peut-être mettre une fonction pour faire plus propre?"""

def FastMarching(pasGrille=5):
    global dimPiecei
    global dimPiecej
    
    Grille=np.zeros((int(dimPiecei/pasGrille),int(dimPiecej/pasGrille),2)) #(vérifier que la grille couvre bien tout l'espace de 0 à dimPiecei,..)
    p,q=Grille.shape[0],Grille.shape[1]
    dimPiecei=pasGrille*p
    dimPiecej=pasGrille*q
    
    for i in range(p):
        for j in range(q):
            i1,j1=analogisationM(i,j,Grille)
            i2,j2=discretisationM(i1,j1,Menvironnement)
            if Menvironnement[i2,j2]==1:
                Grille[i,j,0]=np.inf  #on met la valeur de la distance et un indice: initialisé à -3 pour les obstacles
                Grille[i,j,1]=-3
            elif Menvironnement[i2,j2]==-1:
                Grille[i,j,0]=0 #indice -2 pour la zone eclairee
                Grille[i,j,1]=-2
            else:
                Grille[i,j,0]=np.inf  #on met un indice -1 pour la zone d'ombre
                Grille[i,j,1]=-1
                
    def calculD(i,j,M): #on calcule la distance géodésique du point (i,j) de sorte que |grad Dij|=1 (calcul à essayer de comprendre + en détail! (voir pourquoi la formule convient par exemple))
        if i==0:
            a=M[i+1,j][0]
        elif i==p-1:
            a=M[i-1,j][0]
        else:
            a=min(M[i-1,j][0],M[i+1,j][0])
        if j==0:
            b=M[i,j+1][0]
        elif j==q-1:
            b=M[i,j-1][0]
        else:
            b=min(M[i,j-1][0],M[i,j+1][0])
        
        if abs(a-b)<pasGrille:      #On remarque que quand on appellera cette fonction, on aura a<inf et b<inf vu que (i,j) est voisin d'un point de la zone eclairee
            return (a+b+np.sqrt(2*pasGrille**2-(a-b)**2))/2
        else:
            return pasGrille+min(a,b)
            
    tas=[0] #le premier indice du tas: nombre d'elements du tas: les indices des elements du tas vont de 1 a n!
    
    
    def redescendre(tas,i):
        n=tas[0]
        while i<=n//2:
            rgFils=2*i
            if rgFils<n and tas[rgFils+1][0]<tas[rgFils][0]:
                rgFils+=1
            if tas[rgFils][0]<tas[i][0]:
                Grille[tas[rgFils][1],tas[rgFils][2]][1],Grille[tas[i][1],tas[i][2]][1]=i,rgFils  #on echange,dans les cases de la matrice Grille, les indices associés au tas
                tas[rgFils],tas[i]=tas[i],tas[rgFils]
                i=rgFils
            else:
                return
        return
    
    def remonter(tas,i):
        while i>1:
            rgPere=i//2
            # print(tas[i][0],tas[rgPere][0],"tas")
            if tas[i][0]<tas[rgPere][0]:
                Grille[tas[rgPere][1],tas[rgPere][2]][1],Grille[tas[i][1],tas[i][2]][1]=i,rgPere #on echange,dans les cases de la matrice Grille, les indices associés au tas
                tas[rgPere],tas[i]=tas[i],tas[rgPere]
                i=rgPere
            else:
                return
        return
    
    def ajouter(tas,elem,i,j): #modifie le tas ET renvoie l'indice de l'element ajoute
        tas.append([elem,i,j])
        tas[0]+=1              #on ajoute un element a la derniere feuille
        Grille[i,j][1]=tas[0] 
        remonter(tas,tas[0])
        return
        
    def extraire(tas):
        n=tas[0]
        elemEtCoord=tas[1]
        tas[1]=tas[n]
        Grille[tas[1][1],tas[1][2]][1]=1
        tas.pop()
        tas[0]+=-1
        redescendre(tas,1)
        return elemEtCoord
    
    
    def tasOk(tas):
        verite=True
        for i in range(1,len(tas)):
            verite= verite and Grille[tas[i][1],tas[i][2]][1]==i
        return verite
        
        
    incr=0
    
    for i in range(p):    #on initialise le tas
        for j in range(q):
            if Grille[i,j,0]==0:
                for voisin in listeVois(i,j,Grille):
                    indice=Grille[voisin][1]
                    if indice==-1:
                        Grille[voisin][0]=calculD(voisin[0],voisin[1],Grille)
                        ajouter(tas,Grille[voisin][0],voisin[0],voisin[1]) #on ajoute une distance au tas et on recupere l'indice associe
                    if tasOk(tas):
                        incr+=1
                        #print("tas_estconforme",incr)
                    else:
                        print("erreur à",incr)
    
    
    def evolueDistanceGeodesique(M,tas):
        [D,i,j]=extraire(tas)
        M[i,j][1]=-2 # on ajoute le point de distance mini de la zone de penombre a la zone eclairee (principe a revoir..)
        for voisin in listeVois(i,j,M):
            indice=M[voisin][1]
            if indice==-1:
                M[voisin][0]=calculD(voisin[0],voisin[1],M)
                ajouter(tas,M[voisin][0],voisin[0],voisin[1])
                #print(tas[0],M[voisin][1])
            elif indice>=1:
                indice=int(indice)
                M[voisin][0]=calculD(voisin[0],voisin[1],M)
                #print(tas[0],indice)
                tas[indice][0]=M[voisin][0]
                redescendre(tas,indice)
                
                
                
        return
        
    while len(tas)!=1:
        evolueDistanceGeodesique(Grille,tas)
            
    N=np.zeros((p,q))
    for i in range(p):
        for j in range(q):
            N[i,j]=Grille[i,j,0]
            
    def calculGradMoins(M,i,j): #calcul du gradient à l'aide du terme en haut/à gauche (voir si cela est pertinent, suffisant,cohérent avec la théorie,..)
        if i==0 or M[i-1,j]==np.inf:
            gradiMoins=0
        else:
            gradiMoins=(M[i,j]-M[i-1,j])/pasGrille
        if j==0 or M[i,j-1]==np.inf:
            gradjMoins=0
        else:
            gradjMoins=(M[i,j]-M[i,j-1])/pasGrille
        
        return (gradiMoins,gradjMoins)
        
    def calculGradPlus(M,i,j): #calcul du gradient à l'aide du terme en bas/à droite
        (p,q)=M.shape
        if i==p-1 or M[i+1,j]==np.inf:
            gradiPlus=0
        else:
            gradiPlus=(M[i+1,j]-M[i,j])/pasGrille
        if j==q-1 or M[i,j+1]==np.inf:
            gradjPlus=0
        else:
            gradjPlus=(M[i,j+1]-M[i,j])/pasGrille
        
        return (gradiPlus,gradjPlus)
        
    
    def calculCoordGrad(M,i,j): # détermination des D..x/y ij Φ (ou 0) qui permettront d'obtenir le gradient égal à 1 selon la formule "|∇Φ| ≈ sqrt(max(D−x ij Φ,−D+x ij Φ,0)**2+ max(D−y ij Φ,−D+y ij Φ,0)**2)" (cf travaux de Mohamed Sylla et Boris Meden (à...))
        (gradiMoins,gradjMoins)=calculGradMoins(M,i,j)
        (gradiPlus,gradjPlus)=calculGradPlus(M,i,j)
        gradi=max(gradiMoins,-gradiPlus,0)
        gradj=max(gradjMoins,-gradjPlus,0)
        if gradi==-gradiPlus:  #rq: dans le cas particulier où gradiMoins=-gradiPlus, on garde arbitrairement gradiPlus (alors qu'on aurait pu choisir au hasard, ou garder gradiMoins par exemple)
            gradi=gradiPlus
        if gradj==-gradjPlus:
            gradj=gradjPlus
        vui=-gradi 
        vuj=-gradj
        return (vui,vuj) #vecteur vitesse unitaire orienté (géodésiquement) vers la sortie
        
        
    MatGradFastMarching=np.zeros((p,q,2))
    for i in range(p):
        for j in range(q):
            if N[i,j]!=np.inf:  #on laisse les vitesses nulles là où il y a des murs
                (k,l)=calculCoordGrad(N,i,j)
                MatGradFastMarching[i,j,0]=k
                MatGradFastMarching[i,j,1]=l
    
    return N,MatGradFastMarching
    
champDGeo,champVsouhaitee=FastMarching(pasFastMarching)

def maxnorme(Mvect):
    p,q=Mvect.shape[0],Mvect.shape[1]
    min=1
    max=0.5
    for i in range(p):
        for j in range(q):
            norme=np.sqrt(Mvect[i,j][0]**2+Mvect[i,j][1]**2)
            if norme>0.1:
                if norme<min:
                    min=norme
                if norme>max:
                    max=norme
    return min,max    

print(maxnorme(champVsouhaitee)) #résultat à ..: les gradients sont-ils bien calculés? ne faut-il pas prendre le max(gradGauche,gradDroite) (ou alors on pourrait normaliser les vecteurs?, mais il faut d'abord vérifier que leur direction est correcte à l'aide d'une représentation graphique, ou de calculs,..)?

# p,q=champDGeo.shape
# for i in range(p):
#     for j in range(q):
#         nb=champDGeo[i,j]
#         if nb==np.inf:
#             champDGeo[i,j]=-1
#         else:
#             champDGeo[i,j]=int(nb)
# print(champDGeo)

### Calcul des forces exercées et du PFD (ou du moins de ce qui détermine le mouvement de l'individu)

def creerListeGens(n): #à perfectionner car les gens peuvent apparaître à moitié dans un mur
    listeG=[]
    for k in range(n):
        verite=True
        while verite:
            i=rd.uniform(0,dimPiecei)
            j=rd.uniform(0,dimPiecej)
            ibis,jbis=discretisationM(i,j,Menvironnement)
            verite=Menvironnement[ibis,jbis]==1 or Menvironnement[ibis,jbis]==-1
            
        listeG.append([(i,j),(0,0),(0,0)])  #une personne: [position,vitesse,force s'appliquant sur elle] (à l'instant t)
    return listeG
    
listeGens=creerListeGens(500)
#listeGens=[[(4,36),(0,0),(0,0)]]

def R(natureObjet): #le rayon de l'objet selon sa nature
    if natureObjet==1:
        return Rind
    elif natureObjet==2:
        return tailleMurs/2
        
def kElast(natureObjet):
    if natureObjet==1:
        return kInd
    elif natureObjet==2:
        return kMurs
    
    
def forceElastique(i1,j1,i2,j2,n2): # 1 est l'individu considéré, n2 est la nature de l'autre objet
    d=distance(i1,j1,i2,j2)
    vfi,vfj=(i1-i2)/d,(j1-j2)/d
    normeF=(Rind+R(n2)-d)*kElast(n2)
    return (vfi*normeF,vfj*normeF)
    
def contact(i1,j1,i2,j2,n2): #un booléen qui dit si il y a contact
    return distance(i1,j1,i2,j2)<=Rind+R(n2)
    

def initMgens():
    Mgens=np.empty((int(dimPiecei/Rind),int(dimPiecej/Rind)),list)
    (n,p)=Mgens.shape
    for i in range(n):
        for j in range(p):
            Mgens[i,j]=[]
    
    for individu in listeGens:  #parties de programme à vérifier! avec des affichages par exemple
        i,j=individu[0]
        (disi,disj)=discretisationM(i,j,Mgens)
        Mgens[disi,disj].append((i,j))  #la liste des gens correspondant à la position (dis,disj) dans Mgens
    return Mgens
    
Mgens=initMgens()
    
def forceElastMurs(dmax,imax,murprochemax):
    if dmax>=Rind+tailleMurs/2:
        return 0
    else:
        signe=(imax-murprochemax)/dmax
        return signe*(Rind+tailleMurs/2-dmax)*kMurs

def calculForcesElastiques():
    for individu in listeGens:
        (i,j)=individu[0]
        (disi,disj)=discretisationM(i,j,Mgens)
        for coordVois in listeVoisBis2(disi,disj,Mgens):
            (k,l)=coordVois
            for indProche in Mgens[k,l]: #calcul de la force élastique inter-individuelle (pour 1 des deux individus ici)
                (p,q)=indProche
                if (p,q)!=(i,j) and contact(i,j,p,q,1): #force elastique seulement si il y a contact
                    (fi,fj)=forceElastique(i,j,p,q,1)
                    individu[2]=(fi+individu[2][0],fj+individu[2][1]) #somme des forces subies (A AMELIORER PEUT ETRE AVEC DES TABLEAUX AU LIEU DE REMPLACER LA FORCE SUBIE A CHAQUE FOIS)
                    # if etape%10==0:
                    #     print(fi,fj,"forces individu")
                    #     print(individu[2],"forces totales")
        (disi,disj)=discretisationM(i,j,Menvironnement)
        L=listeVoisBis1(disi,disj,Menvironnement)
        L.append((disi,disj)) #on inclut la case où il y a l'individu
        (murprochei,murprochej)=(-1,-1) #on détermine le mur le plus proche
        dmin=np.inf
        for coordVois in L:
            (k,l)=coordVois
            if Menvironnement[k,l]==1:
                (x,y)=analogisationM(k,l,Menvironnement)
                d=distance(i,j,x,y)
                if d<dmin:
                    dmin=d
                    (murprochei,murprochej)=(x,y)
        if murprochei!=-1 and d<=Rind+tailleMurs/np.sqrt(2):   #(tailleMurs/2)*sqrt(2)
            di=abs(i-murprochei)
            dj=abs(j-murprochej)
            if di>dj:  #on considère que l'individu est repoussé dans la direction k correspondant au plus grand dk (voir sur un dessin). Il y a donc une approximation forte au niveau des coins. De plus, on considère que le cas particulier où il n'y a pas contact avec le murproche choisi alors qu'il existe un autre mur avec lequel il y a contact n'est jamais vérifié (voir dessin: il faudrait que tailleMurs<Rind et/ou que le mur avec lequel il y ait contact soit un coin (à vérifier/préciser peut-être ..))
                
                fi=forceElastMurs(di,i,murprochei)
                individu[2]=(fi+individu[2][0],individu[2][1])
                # if etape%10==0:
                #     print(fi,"force murs fi")
            else:
                fj=forceElastMurs(dj,j,murprochej)
                individu[2]=(individu[2][0],fj+individu[2][1])
                # if etape%10==0:
                #     print(fj,"force murs fj")
                

def calculForcesSociales():
    for individu in listeGens:
        (i,j)=individu[0]            
        (disi,disj)=discretisationM(i,j,champVsouhaitee)
        (vi,vj)=champVsouhaitee[disi,disj]
        fi=Mind*(normeVsouhaitee*vi-individu[1][0])/tempsRelaxation
        fj=Mind*(normeVsouhaitee*vj-individu[1][1])/tempsRelaxation
        # if etape%10==0:
        #     print(fi,fj,"forces sociales")
        individu[2]=(fi+individu[2][0],fj+individu[2][1])
        

def passage():
    global nombreGensHorsLimite
    for individu in listeGens:
        individu[2]=(0,0)
    
    calculForcesSociales()
    calculForcesElastiques() #fonctions In place
    
    
    for individu in listeGens:
        (i,j)=individu[0]
        (disGensi,disGensj)=discretisationM(i,j,Mgens)   #On commence à modifier Mgens
        Mgens[disGensi,disGensj].remove((i,j))
        
        ai=individu[2][0]/Mind
        aj=individu[2][1]/Mind
        
        vi=individu[1][0]+ai*pasTemps #calcul de la vitesse avec un DL à l'ordre 1
        vj=individu[1][1]+aj*pasTemps
        
        i+=vi*pasTemps+(ai/2)*pasTemps**2 #DL à l'ordre 2 ici (ordre 1 peut-être peut-être suffisant?)
        j+=vj*pasTemps+(aj/2)*pasTemps**2
        individu[1]=(vi,vj)
        individu[0]=(i,j)
        # if etape%10==0:
        #     print(vi,vj,"vitesse")
        #     print(np.sqrt(vi**2+vj**2),"norme vitesse")
        #     print(individu,"(individu)")
        #     print(ai,aj,"acceleration")
        #     print(i,j,"position")
        
        (disi,disj)=discretisationM(i,j,Menvironnement)
        if estHorsLimites(i,j):
            listeGens.remove(individu)
            nombreGensHorsLimite+=1
        elif Menvironnement[disi,disj]==-1:
            listeGens.remove(individu)
        else:
            (disGensi,disGensj)=discretisationM(i,j,Mgens)   #On finit de modifier Mgens
            Mgens[disGensi,disGensj].append((i,j))
            
def estHorsLimites(i,j):
    return i<0 or i>dimPiecei or j<0 or j>dimPiecej
        

def afficheTemporaire():
    N=deepcopy(Menvironnement)
    for individu in listeGens:
        (i,j)=individu[0]
        (disi,disj)=discretisationM(i,j,Menvironnement)
        N[disi,disj]+=1
    print(N)
            
# while len(listeGens)!=0:
#     passage()
#     afficheTemporaire()
#     time.sleep(0.2)
    

### affichage

def afficheDgeo():
    plt.clf()
    M=deepcopy(champDGeo)
    p,q=M.shape
    print(p,q)
    for i in range(p):
        for j in range(q):
            nb=M[i,j]
            if nb==np.inf:
                M[i,j]=-1
    # Y=np.arange(0,dimPiecei,pasFastMarching)
    # X=np.arange(0,dimPiecej,pasFastMarching)
    Y=np.linspace(0,dimPiecei,p)  #pourquoi cet ordre?
    X=np.linspace(0,dimPiecej,q)
    XX, YY = np.meshgrid(X, Y)
    plt.title(u"Equidistances geodesiques") #pourquoi "u", "equal",..?
    plt.axis('equal')   
    plt.xlim(0, dimPiecei) 
    plt.ylim(0, dimPiecej)
    C=plt.contourf(YY, XX, M, cmap='bone')
    plt.colorbar(C)
    plt.show()
    

def afficheVsouhaitee():
    plt.clf()
    (p,q,deux)=champVsouhaitee.shape
    Mvi=np.zeros((p,q))
    Mvj=np.zeros((p,q))
    for i in range(p):
        for j in range(q):
            Mvi[i,j]=champVsouhaitee[i,j,0]
            Mvj[i,j]=champVsouhaitee[i,j,1]
            
    Y=np.linspace(0,dimPiecei,p)  #pourquoi cet ordre?
    X=np.linspace(0,dimPiecej,q)
    XX, YY = np.meshgrid(X, Y)
    
    plt.title(u"Vecteurs Vitesse souhaitée unitaires")
    plt.axis('equal')   
    plt.ylim(0, dimPiecei) 
    plt.xlim(0, dimPiecej)
    step=2
    plt.quiver(YY[::step, ::step], XX[::step, ::step], Mvi[::step, ::step], Mvj[::step, ::step]) # Bon sens?
    plt.show()
    
    
### animation

def evacuation():
    global etape
    global nombreGensHorsLimite
    global etapeStationnaire
    
    nombreGensHorsLimite=0
    etapeStationnaire=0
    
    plt.clf()
    x=[] 
    y=[]
    v=[]
    w=[]
    n,p=Menvironnement.shape
    for i in range(n):
        for j in range(p):
            if Menvironnement[i,j]==1: #affichage des murs
                (anai,anaj)=analogisationM(i,j,Menvironnement)
                x.append(anai)
                y.append(anaj)
            elif Menvironnement[i,j]==-1: #affichage des sorties
                (anai,anaj)=analogisationM(i,j,Menvironnement)
                v.append(anai)
                w.append(anaj)
    plt.scatter(x, y, s=(20*tailleMurs**2), c="blue", marker="s", edgecolors="black")
    plt.scatter(v, w, s=(20*tailleMurs**2), c="grey", marker="s")
    n=len(listeGens)
    x=np.zeros((n))
    y=np.zeros((n))
    for i in range(n):
        x[i]=listeGens[i][0][0]
        y[i]=listeGens[i][0][1]
    scat = plt.scatter(x,y,s=20, c="red", edgecolors="black")
    while len(listeGens)!=0:
        nbGens=len(listeGens)
        etape+=1
        passage()
        
        if nbGens==len(listeGens):
            etapeStationnaire+=1
        else:
            etapeStationnaire=0
        if etapeStationnaire> (1/pasTemps)*90: # (nbEtapes/seconde)*secondes: on considère que les individus sont bloqués si personne ne sort pendant 3 minutes
            print(len(listeGens),"individus sont restés bloqués (personne n'est sorti pendant 90/60= 1 minute 30s)")
            for i in range(len(listeGens)):
                listeGens.pop()
            
            
        n=len(listeGens)
        tableau=np.zeros((n,2))
        for i in range(n):
            tableau[i,0]=listeGens[i][0][0]
            tableau[i,1]=listeGens[i][0][1]
        scat.set_offsets(tableau)
        plt.pause(0.01)
       
    plt.axis('equal')
    dim=max(dimPiecei,dimPiecej)
    plt.xlim(0, dim) 
    plt.ylim(0, dim)
    plt.show()
    
    print(nombreGensHorsLimite," personne(s) est/sont sortie(s) de la pièce en traversant un ou plusieurs murs")
    if nombreGensHorsLimite>3:
        print("penser à augmenter la taille des murs ou changer les constantes de raideur pour que moins de gens traversent les murs (ou changer la façon dont sont calculées les forces élastiques exercées par les murs sur les individus)")




























    