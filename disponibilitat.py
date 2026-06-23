from estructura import Tribunals, Horari, Profes, Alumnes, Aules, Sessions
import pandas as pd
import re

def omplir_i_exportar_disponibilitat(ruta_arxiu_origen: str, llista_profes: list[Profes], llista_sessions: list, configuracio_dies: list) -> list[Profes]:
    df = pd.read_excel(ruta_arxiu_origen)
    
    mapa_disponibilitat = {
        "no disponible": 0,
        "disponible": 1,
        "preferible": 1
    }
    
    dicc_profes = {p.nom: p for p in llista_profes}
    patro = r'(\d{1,2}:\d{2}-\d{1,2}:\d{2})'

    MAPA_DIES_SETEMBRE = {
        21: "Dimarts 1",
        22: "Dimecres 2",
        23: "Dijous 3 ",
        24: "Divendres 4"
    }
    DIES_SETEMBRE = set(MAPA_DIES_SETEMBRE.keys())

    sessions_regulars = [s for s in llista_sessions if s.dia not in DIES_SETEMBRE]
    sessions_setembre = [s for s in llista_sessions if s.dia in DIES_SETEMBRE]

    noms_totes_columnes = df.columns.tolist()
    columnes_sessions = []
    
    for config in configuracio_dies:
        inici = config['col_inici']
        fi = config['col_fi']
        for i in range(inici, fi + 1):
            if i < len(noms_totes_columnes):
                nom_col = str(noms_totes_columnes[i])
                if re.search(patro, nom_col):
                    columnes_sessions.append(nom_col)
                    
    # Ara len(columnes_sessions) és idèntic a len(llista_sessions)

    # Confirmem que les columnes trobades coincideixen exactament amb les sessions creades
    assert len(columnes_sessions) == len(sessions_regulars), (
        f"Desajust: {len(columnes_sessions)} columnes trobades vs {len(sessions_regulars)} sessions esperades"
    )
    
    for index, fila in df.iterrows():
        nom_profe = str(fila['Nom']).strip()
        
        if nom_profe in dicc_profes:
            profe = dicc_profes[nom_profe]
            
            profe.disponibilitat = {}
            
            # Iterem utilitzant zip per emparellar exactament la columna correcta amb la sessió correcta
            for nom_columna, sessio in zip(columnes_sessions, sessions_regulars):
                # Netegem espais i passem a minúscules per assegurar que el mapa funciona
                valor_excel = str(fila[nom_columna]).strip().lower()
                
                profe.disponibilitat[sessio.id] = mapa_disponibilitat.get(valor_excel, 0)

            for sessio in sessions_setembre:
                nom_columna_dia = MAPA_DIES_SETEMBRE[sessio.dia]
                valor_excel = str(fila[nom_columna_dia]).strip().lower()
                profe.disponibilitat[sessio.id] = mapa_disponibilitat.get(valor_excel, 0)


    
    return llista_profes


from estructura import Alumnes, Sessions

def omplir_disponibilitat_alumnes(llista_alumnes: list[Alumnes], 
                                  llista_sessions: list[Sessions], 
                                  restriccions: dict, 
                                  alumnes_setembre: list[str]) -> list[Alumnes]:
    if restriccions is None:
        restriccions = {}

    restriccions_netes = {str(k).strip().replace(" ", "_").lower(): v for k, v in restriccions.items()}

    ids_sessions = [sessio.id for sessio in llista_sessions]

    DIES_SETEMBRE = {21, 22, 23, 24}
    ids_sessions_setembre = {sessio.id for sessio in llista_sessions if sessio.dia in DIES_SETEMBRE}

    dispo_total_0 = {sessio: 0 for sessio in ids_sessions}
    dispo_no_setembre = {
        sessio: (0 if sessio in ids_sessions_setembre else 1)
        for sessio in ids_sessions
    }

    alumnes_setembre_nets = {a.strip().replace(" ", "_").lower() for a in alumnes_setembre} if alumnes_setembre else set()

    for alumne in llista_alumnes:
        id_net = alumne.id.strip().replace(" ", "_").lower()

        if id_net in alumnes_setembre_nets:
            # 0 a tot, 1 només a les sessions de setembre (dies 21-24)
            alumne.disponibilitat_alumne = dispo_total_0.copy()
            for id_sessio in ids_sessions_setembre:
                alumne.disponibilitat_alumne[id_sessio] = 1

        elif id_net in restriccions_netes:
            # 0 a tot (incloses les sessions de setembre) i 1 només a les permeses no-setembre
            alumne.disponibilitat_alumne = dispo_total_0.copy()
            sessions_permeses = restriccions_netes[id_net]
            for sessio in sessions_permeses:
                if sessio in alumne.disponibilitat_alumne and sessio not in ids_sessions_setembre:
                    alumne.disponibilitat_alumne[sessio] = 1

        else:
            # 1 a totes les sessions excepte les de setembre
            alumne.disponibilitat_alumne = dispo_no_setembre.copy()

    return llista_alumnes