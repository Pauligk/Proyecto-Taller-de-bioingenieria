def calcular_indice_em(funcion, aplicacion, mantenimiento, cantidad_fallas):
    """
    Calcula el Índice de Criticidad (EM) basado en el modelo de Smith / Alburaiesi.
    El historial de fallas es una variable activa que incrementa el puntaje.
    """
    puntaje_historia = float(cantidad_fallas) * 2.0
    return float(funcion) + float(aplicacion) + float(mantenimiento) + puntaje_historia

def clasificar_prioridad(em):
    """Determina la categoría de triaje clínico y el color visual del badge."""
    if em >= 16.0:
        return "ALTA", "danger"
    elif em >= 12.0:
        return "MEDIA", "warning"
    return "BAJA", "success"

def procesar_triaje_equipos(filas_sql):
    """Procesa la lista de equipos, calcula el EM y los ordena por urgencia."""
    equipos_procesados = []
    
    for fila in filas_sql:
        eq = dict(fila)
        em = calcular_indice_em(
            eq["puntaje_funcion"],
            eq["puntaje_aplicacion"],
            eq["puntaje_mantenimiento"],
            eq["cantidad_fallas"]
        )
        prioridad, color = clasificar_prioridad(em)
        
        eq["indice_em"] = em
        eq["prioridad"] = prioridad
        eq["color_badge"] = color
        equipos_procesados.append(eq)
        
    # Orden descendente: el equipo más crítico queda primero en la lista
    equipos_procesados.sort(key=lambda x: x["indice_em"], reverse=True)
    return equipos_procesados

