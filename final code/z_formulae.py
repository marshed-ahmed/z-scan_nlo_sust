import numpy as np

# defining the curve fitting function as "zscan"
def z_formulae_thin(x,phi):
    
    T = 1 +(((4*x)/(((1 + x**2) * (9 + x**2))))*phi) #closed aparture Z-scan formula
    return T

def z_formulae_thick(x, l, phi):
    numerator = ((x+l/2)**2+1)*((x-l/2)**2+9)
    denominator = ((x-l/2)**2+1)*((x+l/2)**2+9)
    T=1 + 0.25 * np.log(numerator/denominator)*phi

    return T
