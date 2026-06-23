import pandas as pd
import re

from estructura import Tribunals, Profes, Alumnes, Aules, Sessions



def generar_profes(ruta_arxiu: str) -> list[Profes]:
    df = pd.read_excel(ruta_arxiu)
    llista_professors = []
    dades_per_excel = []
    for index, fila in df.iterrows():
        id_profe = f"profe_{index + 1}"
        
        nom = str(fila['professor']).strip()
        area = str(fila['area_profe']).strip() if pd.notna(fila['area_profe']) else "Sense Àrea"
        
        capacitat = int(fila['capacitat_max_profe']) if pd.notna(fila['capacitat_max_profe']) else 0
        
        profe = Profes(
            id=id_profe,
            nom=nom,
            area_profe=area,
            capacitat_max_profe=capacitat
        )

        
        dades_per_excel.append({
            'ID_Profe': profe.id,
            'Nom_Profe': profe.nom,
            'Area': profe.area_profe,
            'Capacitat_Max': profe.capacitat_max_profe
        })

        llista_professors.append(profe)
        
    df_resultat = pd.DataFrame(dades_per_excel)
    
    #df_resultat.to_excel("llistat_professors.xlsx", index=False)
        
        
    return llista_professors
    

def analitzar_tutors_alumnes(ruta_excel: str):
    df_complet = pd.read_excel(ruta_excel, index_col=4)
    df_matriu = df_complet.loc[:, "Introducció als sistemes dinàmics en dimensió infinita a partir de models de poblacions amb estructura per l'edat":]
    
    tots_els_alumnes = df_matriu.columns.tolist()
    
    df_llarg = df_matriu.stack().reset_index()
    df_llarg.columns = ['Tutor', 'Alumne', 'Valor_Cella']
    
    condicio = df_llarg['Valor_Cella'].astype(str).str.strip().str.lower() == 'tutor/a'
    df_tutors = df_llarg[condicio][['Alumne', 'Tutor']].copy()
    
    df_tutors = df_tutors.groupby('Alumne')['Tutor'].apply(lambda x: ', '.join(x.astype(str).str.strip())).reset_index()
    
    df_tots_alumnes = pd.DataFrame({'Alumne': tots_els_alumnes})
    df_final = pd.merge(df_tots_alumnes, df_tutors, on='Alumne', how='left')
    
    df_final = df_final.sort_values(by='Alumne').reset_index(drop=True)
    df_final['Tutor'] = df_final['Tutor'].fillna('Sense tutor assignat')
    df_final = df_final[['Alumne', 'Tutor']]
    
    return df_final


def crear_alumnes_i_excel(df_alumnes_tutors: pd.DataFrame, df_excepcions: pd.DataFrame, llista_profes: list, ruta_sortida_excel: str) -> list:

    dicc_profes = {profe.nom.strip(): profe for profe in llista_profes}
    
    dicc_excepcions = {}
    if not df_excepcions.empty:
        for _, fila in df_excepcions.iterrows():
            nom_exc = str(fila['Alumne']).strip()
            area_exc = str(fila['Area']).strip()
            dicc_excepcions[nom_exc] = area_exc
            
    llista_objectes_alumnes = []
    dades_per_excel = [] 
    for index, fila in df_alumnes_tutors.iterrows():
        id_alumne = f"alumne_{index + 1}"
        
        nom_alumne = str(fila['Alumne']).strip()
        nom_tutor = str(fila['Tutor']).strip()
        
        if nom_tutor in dicc_profes:
            profe_assignat = dicc_profes[nom_tutor]
            tutor_id = profe_assignat.id
            area = profe_assignat.area_profe
        else:
            tutor_id = "Sense Tutor"
            area = "Sense Àrea"
            
        if nom_alumne in dicc_excepcions:
            area = dicc_excepcions[nom_alumne]
            
        alumne = Alumnes(
            id=id_alumne,
            nom=nom_alumne,
            area_alumne=area,
            tutor_id=tutor_id
        )
        llista_objectes_alumnes.append(alumne)
        
        dades_per_excel.append({
            'ID_Alumne': alumne.id,
            'Nom_Alumne': alumne.nom,
            'Area': alumne.area_alumne,
            'ID_Tutor': alumne.tutor_id,
            'Nom_Tutor': nom_tutor
        })
        
    df_resultat = pd.DataFrame(dades_per_excel)
    
    #df_resultat.to_excel(ruta_sortida_excel, index=False)
    
    return llista_objectes_alumnes


def extreure_i_crear_sessions(ruta_arxiu_origen: str, 
                              configuracio_dies: list[dict], 
                              ruta_arxiu_desti: str, 
                              alumnes_setembre: list[str]) -> list[Sessions]:
    df_origen = pd.read_excel(ruta_arxiu_origen, nrows=0)
    noms_columnes = df_origen.columns.tolist()
    
    llista_sessions = []
    dades_per_excel = []
    
    patro = r'(\d{1,2}:\d{2}-\d{1,2}:\d{2})'
    comptador_id = 1
    
    for config in configuracio_dies:
        dia_actual = config['dia']
        inici = config['col_inici']
        fi = config['col_fi']
        aules_maximes = config['max_aules']
        
        # Inicialitzem el comptador d'hores en 1 per a cada nou dia
        comptador_hora = 1 
        
        for i in range(inici, fi + 1):
            if i < len(noms_columnes):
                nom_original = str(noms_columnes[i])
                coincidencia = re.search(patro, nom_original)
                
                if coincidencia:
                    hora_neta = coincidencia.group(1)
                    
                    sessio = Sessions(
                        id=f"sessio_{comptador_id}",
                        dia=dia_actual,
                        hora=comptador_hora,
                        hora_id=hora_neta,
                        max_aules=aules_maximes
                    )
                    
                    llista_sessions.append(sessio)
                    
                    dades_per_excel.append({
                        'ID': sessio.id,
                        'Dia': sessio.dia,
                        'Hora': sessio.hora,
                        'Hora_ID': sessio.hora_id,
                        'Max_Aules': sessio.max_aules
                    })
                    
                    # Incrementem els comptadors
                    comptador_id += 1
                    comptador_hora += 1

    if alumnes_setembre:
        num_alumnes = len(alumnes_setembre)
        DIES_SETEMBRE = [21, 22, 23, 24]

        for dia in DIES_SETEMBRE:
            for comptador_hora in range(1, num_alumnes + 1):
                sessio = Sessions(
                    id=f"sessio_{comptador_id}",
                    dia=dia,
                    hora=comptador_hora,
                    hora_id=f"setembre_dia{dia}_{comptador_hora:02d}",
                    max_aules=1
                )
                llista_sessions.append(sessio)
                dades_per_excel.append({
                    'ID': sessio.id,
                    'Dia': sessio.dia,
                    'Hora': sessio.hora,
                    'Hora_ID': sessio.hora_id,
                    'Max_Aules': sessio.max_aules
                })
                comptador_id += 1

    # Creem i guardem l'Excel amb les noves columnes
    df_resultat = pd.DataFrame(dades_per_excel)
    #df_resultat.to_excel(ruta_arxiu_desti, index=False)
    
    return llista_sessions

