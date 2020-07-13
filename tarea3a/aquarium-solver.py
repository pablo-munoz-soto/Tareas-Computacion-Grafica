import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
import json
import sys
a= open(str(sys.argv[1]))
data=json.load(a)
a.close()


# Problem setup
#eje x , Right
Width=data['width']
#eje y, front
Lenght=data['lenght']
#eje z, up
Height=data['height']


F=data['window_loss']
regulador_A=data['heater_a']
regulador_B=data['heater_b']
T=data['ambient_temperature']
h=0.25

nx = int(Width / h) - 1
ny = int(Lenght / h) - 1
nz = int(Height / h) - 1

N = nx * ny * nz

# We define a function to convert the indices from i,j to k and viceversa
# i,j,k indexes the discrete domain in 3D.
# n parametrize those i,j,k this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getn(i, j, k):
    return k*nx*ny+j * nx + i

def getIJK(n):
    global nx, ny, nz
    k = n//(ny*nx)
    j = (n%(ny*nx))//nx
    i = (n%(ny*nx))%nx
    return (i,j,k)


# In this matrix we will write all the coefficients of the unknowns
A = csc_matrix((N, N))

# In this vector we will write all the right side of the equations
b = np.zeros((N,))

# We iterate over each point inside the domain
# Each point has an equation associated
# The equation is different depending on the point location inside the domain
for k in range(0,nz):
    for j in range(0,ny):
        for i in range(0,nx):

         # We will write the equation associated with row n
         n = getn(i, j, k)

         # We obtain indices of the other coefficients
         n_up = getn(i, j , k+1)
         n_down = getn(i, j , k-1)
         n_left = getn(i - 1, j, k)
         n_right = getn(i + 1, j, k)
         n_front = getn(i, j+1, k)
         n_back = getn(i, j-1, k)

         # Depending on the location of the point, the equation is different
         #regulador termico a
         if Width/3<=(i+1)*h<=2*Width/3 and 3*Lenght/5<=(j+1)*h<=4*Lenght/5 and k==0:
             A[n, n_up] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 1
             A[n, n_right] = 1
             A[n, n] = -6
             b[n] = -regulador_A

         #regulador termico b
         elif Width/3<=(i+1)*h<=2*Width/3 and Lenght/5<=(j+1)*h<=2*Lenght/5 and k==0:
             A[n, n_up] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 1
             A[n, n_right] = 1
             A[n, n] = -6
             b[n] = -regulador_B

         # Interior
         elif 1 <= i <= nx - 2 and 1 <= j<= ny - 2 and 1<=k<=nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 1
             A[n, n_right] = 1
             A[n, n] = -6
             b[n] = 0

         #when touching 1 side

         # left side
         elif i == 0 and 1 <= j  <= ny - 2 and 1<=k<=nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -2*h*F

         # right side
         elif i == nx - 1 and 1 <= j <= ny - 2 and 1<=k<=nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -2 * h * F

         # back side
         elif 1<= i <= nx-2 and j==0 and 1 <= k<= nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = -2 * h * F

         # front side
         elif 1<= i <= nx-2 and j==ny - 1  and 1 <= k<= nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = -2 * h * F

         # bottom side
         elif 1 <= i <= nx - 2 and 1 <= j <= ny - 2 and k==0:
             A[n, n_up] = 2
             A[n, n_back] = 1
             A[n, n_front] = 1
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = 0

         # top side
         elif 1 <= i <= nx - 2 and 1 <= j <= ny - 2 and k == nz -1:
             A[n, n_down] = 1
             A[n, n_back] = 1
             A[n, n_front] = 1
             A[n, n_left] = 1
             A[n, n_right] = 1
             A[n, n] = -6
             b[n] = -T

         #when touching 2 sides

         #left and bottom side
         elif i==0 and 1 <= j <= ny - 2 and k==0:
             A[n, n_up] = 2
             A[n, n_back] = 1
             A[n, n_front] = 1
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -2*h*F

         #left and top side
         elif i == 0 and 1 <= j <= ny - 2 and k == nz - 1:
             A[n, n_down] = 1
             A[n, n_back] = 1
             A[n, n_front] = 1
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -T-2 * h * F

         #left and back side
         elif i == 0 and j==0 and 1 <= k<= nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -4 * h * F

         #left and front side
         elif i == 0 and j==ny-1 and 1 <= k<= nz-2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -4 * h * F

         # right and bottom side
         elif i == nx - 1 and 1 <= j <= ny - 2 and k == 0:
             A[n, n_up] = 2
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -2 * h * F

         # right and top side
         elif i == nx - 1 and 1 <= j <= ny - 2 and k == nz - 1:
             A[n, n_down] = 1
             A[n, n_front] = 1
             A[n, n_back] = 1
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -T-2 * h * F

         # right and back side
         elif i == nx - 1 and j == 0 and 1 <= k <= nz - 2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -4 * h * F

         # right and front side
         elif i == nx - 1 and j == ny - 1 and 1 <= k <= nz - 2:
             A[n, n_up] = 1
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -4 * h * F

         #back and bottom side
         elif 1<= i <= nx - 2 and j == 0 and k == 0:
             A[n, n_up] = 2
             A[n, n_front] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = -2 * h * F

         #back and top side
         elif 1<= i <= nx - 2 and j == 0 and k == nz-1:
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = -T-2 * h * F

         #front and bottom side
         elif 1<= i <= nx - 2 and j == ny-1 and k == 0:
             A[n, n_up] = 2
             A[n, n_back] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = - 2 * h * F

         #front and top side
         elif 1<= i <= nx - 2 and j == ny-1 and k == nz-1:
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_right] = 1
             A[n, n_left] = 1
             A[n, n] = -6
             b[n] = -T - 2 * h * F

         #when touching 3 sides

         #left, back, bottom corner
         elif i== 0 and j == 0 and k == 0:
             A[n, n_up] = 2
             A[n, n_front] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = - 4 * h * F

         #right, back, bottom corner
         elif i== nx-1 and j == 0 and k == 0:
             A[n, n_up] = 2
             A[n, n_front] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = - 4 * h * F

         #left, back, top corner
         elif i== 0 and j == 0 and k == nz-1:
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -T - 4 * h * F

         #right, back, top corner
         elif i== nx-1 and j == 0 and k == nz-1:
             A[n, n_down] = 1
             A[n, n_front] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -T - 4 * h * F

         # left, front, bottom corner
         elif i == 0 and j == ny-1 and k == 0:
             A[n, n_up] = 2
             A[n, n_back] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] =- 4 * h * F

         # right, front, bottom corner
         elif i == nx - 1 and j == ny-1 and k == 0:
             A[n, n_up] = 2
             A[n, n_back] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = - 4 * h * F

         # left, front, top corner
         elif i == 0 and j == ny-1 and k == nz - 1:
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_right] = 2
             A[n, n] = -6
             b[n] = -T- 4 * h * F

         # right, front, top corner
         elif i == nx - 1 and j == ny-1 and k == nz - 1:
             A[n, n_down] = 1
             A[n, n_back] = 2
             A[n, n_left] = 2
             A[n, n] = -6
             b[n] = -T- 4 * h * F

         else:
            print("Point (" + str(i) + ", " + str(j) + ") missed!")
            print("Associated point index is " + str(k))
            raise Exception()

# Solving our system
x=spsolve(A,b)
solucion=np.zeros((nx,ny,nz))
for n in range(len(x)):
    i,j,k=getIJK(n)
    solucion[i,j,k]= x[n]
#guardando la matriz
np.save(data['filename'],solucion,allow_pickle=True)




