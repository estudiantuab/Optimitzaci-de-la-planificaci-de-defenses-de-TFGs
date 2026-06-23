import pandas as pd
from estructura import Profes, Alumnes

def omplir_voluntats_profes(ruta_arxiu_origen: str, llista_profes: list[Profes], llista_alumnes: list[Alumnes]) -> list[Profes]:
    df = pd.read_excel(ruta_arxiu_origen)
    
    mapa_voluntats = {
        "gens": 0,
        "indiferent": 5,
        "bastant": 15,
        "molt": 20,
        "tutor/a": 0
    }
    
    dicc_profes = {p.nom.strip(): p for p in llista_profes}
    
    for index, fila in df.iterrows():
        nom_profe = str(fila.get('Nom', fila.iloc[0])).strip() 
        
        if nom_profe in dicc_profes:
            profe = dicc_profes[nom_profe]
            profe.voluntats = {}
            
            for alumne in llista_alumnes:
                nom_alumne = alumne.nom.strip()
                
                if nom_alumne in df.columns:
                    valor_cru = fila[nom_alumne]
                    
                    if pd.isna(valor_cru) or str(valor_cru).strip() == "":
                        valor_numeric = 5
                    else:
                        valor_cella = str(valor_cru).strip().lower()
                        valor_numeric = mapa_voluntats.get(valor_cella, 5)
                        
                    profe.voluntats[alumne.id] = valor_numeric
                else:
                    profe.voluntats[alumne.id] = 0
                    
    return llista_profes