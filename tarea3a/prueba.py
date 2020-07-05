import numpy as np
import matplotlib.pyplot as plt
h=0.2
Width=3
Lenght=6
Height = 4
a=np.load('solution.npy')
X, Y, Z=np.mgrid[h:Width:h,h:Lenght:h,h:Height:h]

fig= plt.figure(figsize=(35,20))
ax=fig.gca(projection='3d')
scat= ax.scatter(X,Y,Z, c=a, alpha=1, s=100, marker='s')

fig.colorbar(scat, shrink=0.5, aspect=5)

ax.set_title('temperatura en acuario')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.legend()

plt.show()
from matplotlib import cm

fig, ax=plt.subplots()

XX,YY= np.mgrid[h:Width:h,h:Lenght:h]

pcm=ax.pcolor(XX,YY,a[:,:,0],cmap='viridis')

fig.colorbar(pcm, shrink=0.5, aspect=5, label='temperatura')

ax.set_title('temperatura en acuario z=0')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()

plt.show()