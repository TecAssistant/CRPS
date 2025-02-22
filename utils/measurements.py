import numpy as np
from numpy import dot
from numpy.linalg import norm


def distancia_euclidiana(v1, v2):
    """
    Calcula la distancia euclidiana entre dos vectores.

    La distancia euclidiana es la longitud del segmento de línea recta
    que conecta los dos puntos en un espacio n-dimensional.

    Parámetros:
        v1 (array-like): Primer vector de características.
        v2 (array-like): Segundo vector de características.

    Retorna:
        float: La distancia euclidiana entre v1 y v2.
    """
    # Se resta v2 de v1 para obtener la diferencia entre ambos vectores
    diferencia = v1 - v2
    # Se calcula la norma (magnitud) de la diferencia, que representa la distancia
    distancia = np.linalg.norm(diferencia)
    return distancia


def similitud_coseno(v1, v2):
    """
    Calcula la similitud coseno entre dos vectores.

    La similitud coseno es el coseno del ángulo entre dos vectores en un espacio
    n-dimensional. Valores cercanos a 1 indican que los vectores son muy similares,
    mientras que valores cercanos a -1 indican que son opuestos.

    Parámetros:
        v1 (array-like): Primer vector de características.
        v2 (array-like): Segundo vector de características.

    Retorna:
        float: La similitud coseno entre v1 y v2.
    """
    # Se calcula el producto punto de los dos vectores
    producto_punto = dot(v1, v2)
    # Se calcula la norma (magnitud) de cada vector
    norma_v1 = norm(v1)
    norma_v2 = norm(v2)
    # Se calcula la similitud coseno dividiendo el producto punto por el producto de las normas
    similitud = producto_punto / (norma_v1 * norma_v2)
    return similitud
