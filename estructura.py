from dataclasses import dataclass, field
from typing import Annotated
from timefold.solver.domain import (
    planning_entity, planning_solution, PlanningId, PlanningVariable,
    ProblemFactCollectionProperty, PlanningEntityCollectionProperty,
    ValueRangeProvider, PlanningScore
)

from timefold.solver.score import HardMediumSoftScore


@dataclass
class Profes:
    id: str
    nom: str
    area_profe: str
    capacitat_max_profe: int

    # str serà la ID de la sessió
    # int és (0 = no disponible, 1 = disponible)
    disponibilitat: dict[str, int] = field(default_factory=dict)
    # field(default_factory=dict) fa:
    # Cada vegada que creis un professor nou, executa la funció dict() 
    # per crear un diccionari totalment nou i buit només per a ell

    # str serà la ID de l'alumne
    # int és la voluntat del seu treball segons el profe
    voluntats: dict[str, int] = field(default_factory=dict)

    def __hash__(self):
        # Ara Python sap que per identificar aquest tribunal només ha de mirar l'ID
        return hash(self.id)

    def __eq__(self, other):
        # Dos tribunals són el mateix si tenen exactament la mateixa ID
        if isinstance(other, Profes):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.id} {self.nom} (Àrea: {self.area_profe}, Capacitat: {self.capacitat_max_profe})"

@dataclass
class Alumnes:
    id: str
    nom: str
    area_alumne: str
    tutor_id: str 

    # str serà la ID de la sessió
    # int és (0 = no disponible, 1 = disponible)
    disponibilitat_alumne: dict[str, int] = field(default_factory=dict)

    def __hash__(self):
        # Ara Python sap que per identificar aquest tribunal només ha de mirar l'ID
        return hash(self.id)

    def __eq__(self, other):
        # Dos tribunals són el mateix si tenen exactament la mateixa ID
        if isinstance(other, Alumnes):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.id} (Àrea: {self.area_alumne}, Tutor ID: {self.tutor_id})"

@dataclass
class Sessions:
    id: str
    dia: int
    hora: int
    hora_id: str
    max_aules: int

    def __hash__(self):
        # Ara Python sap que per identificar aquest tribunal només ha de mirar l'ID
        return hash(self.id)

    def __eq__(self, other):
        # Dos tribunals són el mateix si tenen exactament la mateixa ID
        if isinstance(other, Sessions):
            return self.id == other.id
        return False

    def __str__(self):
        return f"Sessió {self.id}: Dia {self.dia}, a les {self.hora_id}h ({self.hora}a hora)"
        
@dataclass
class Aules:
    id: str
    ordre: int


    def __hash__(self):
        # Ara Python sap que per identificar aquest tribunal només ha de mirar l'ID
        return hash(self.id)

    def __eq__(self, other):
        # Dos tribunals són el mateix si tenen exactament la mateixa ID
        if isinstance(other, Aules):
            return self.id == other.id
        return False
    
    def __str__(self):
        return self.id


#planning entity significa que aquestes variables son les que ha de trobar el programa

@planning_entity
@dataclass(eq=False) 
class Tribunals:
    id: Annotated[str, PlanningId]
    alumne: Alumnes  
    
    sessio: Annotated[Sessions | None, PlanningVariable] = field(default=None)
    aula: Annotated[Aules | None, PlanningVariable] = field(default=None)
    
    profe1: Annotated[Profes | None, PlanningVariable] = field(default=None)
    profe2: Annotated[Profes | None, PlanningVariable] = field(default=None)
    
    # 2. AFEGIR AQUESTES DUES FUNCIONS AL FINAL
    def __hash__(self):
        # Ara Python sap que per identificar aquest tribunal només ha de mirar l'ID
        return hash(self.id)

    def __eq__(self, other):
        # Dos tribunals són el mateix si tenen exactament la mateixa ID
        if isinstance(other, Tribunals):
            return self.id == other.id
        return False


# planning_solution Defineix aquesta classe com l'estat complet del món.

@planning_solution
@dataclass
class Horari:
    sessions: Annotated[list[Sessions], ProblemFactCollectionProperty, ValueRangeProvider]
    aules: Annotated[list[Aules], ProblemFactCollectionProperty, ValueRangeProvider]
    profes: Annotated[list[Profes], ProblemFactCollectionProperty, ValueRangeProvider]

    alumnes: Annotated[list[Alumnes], ProblemFactCollectionProperty]
    
    tribunals: Annotated[list[Tribunals], PlanningEntityCollectionProperty]
    
    puntuacio: Annotated[HardMediumSoftScore | None, PlanningScore] = field(default=None)
