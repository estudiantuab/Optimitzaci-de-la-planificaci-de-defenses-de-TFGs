from estructura import Aules, Sessions, Tribunals

def generar_aules(llista_sessions: list[Sessions]) -> list[Aules]:
    if not llista_sessions:
        return []

    max_aules_necessaries = max(sessio.max_aules for sessio in llista_sessions)
    
    llista_aules = [
        Aules(id=str(100 + i + 1), ordre=i + 1) 
        for i in range(max_aules_necessaries)
    ]
    
    return llista_aules
