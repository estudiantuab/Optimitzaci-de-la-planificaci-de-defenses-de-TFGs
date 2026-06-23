from timefold.solver.score import ConstraintCollectors
from timefold.solver.score import HardMediumSoftScore
from timefold.solver.score import (ConstraintFactory, Joiners, Constraint)

from estructura import Tribunals, Profes, Alumnes, Aules, Sessions


def c0(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: Totes les variables han d'estar assignades
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: 
                    t.sessio is None or 
                    t.aula is None or 
                    t.profe1 is None or 
                    t.profe2 is None)
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Totes les variables han d'estar assignades"))

def c1(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: Dos tribunals no poden coincidir en dia+hora i aula
    return (constraint_factory
            .for_each_unique_pair(Tribunals,
                Joiners.equal(lambda t: t.sessio.dia if t.sessio is not None else None),
                Joiners.equal(lambda t: t.sessio.hora if t.sessio is not None else None),
                Joiners.equal(lambda t: t.aula.id if t.aula is not None else None)
            )
            .filter(lambda t1, t2: t1.sessio is not None and t1.aula is not None and
                        t2.sessio is not None and t2.aula is not None)
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Conflicte d'aula: Mateixa sessió i aula"))

def c2(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: Els dos professors han de ser diferents
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: t.profe1 is not None and t.profe2 is not None and t.profe1.id == t.profe2.id)
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Els dos professors han de ser diferents"))

def c2_bis(constraint_factory: ConstraintFactory) -> Constraint:
    # Evitar simetries 
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: t.profe1 is not None and t.profe2 is not None and t.profe1.id > t.profe2.id)
            .penalize(HardMediumSoftScore.ONE_SOFT) # Això pot ser SOFT per no bloquejar el solver
            .as_constraint("Ordre alfabètic profes"))


def c3(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: El tutor o tutors de l'alumne no poden formar part del seu tribunal.
    return (constraint_factory
            .for_each(Tribunals)
            # Transformem "profe_1, profe_28" en la llista ['profe_1', 'profe_28'] 
            # i comprovem si l'ID exacta del professor hi és a dins.
            .filter(lambda t: 
                    (t.profe1 is not None and t.profe1.id in [tutor.strip() for tutor in t.alumne.tutor_id.split(',')]) or 
                    (t.profe2 is not None and t.profe2.id in [tutor.strip() for tutor in t.alumne.tutor_id.split(',')]))
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("El tutor no pot estar al tribunal del seu alumne"))

def c4(constraint_factory: ConstraintFactory) -> Constraint:
    # L'alumne ha d'estar disponible a la sessió assignada.
    return (constraint_factory
            .for_each(Tribunals)
            # Filtrem si hi ha sessió assignada i l'alumne hi té un 0 (no disponible)
            .filter(lambda t: 
                    t.sessio is not None and 
                    t.alumne.disponibilitat_alumne.get(t.sessio.id, 0) == 0)
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("L'alumne no està disponible a la sessió assignada"))

def c5(constraint_factory: ConstraintFactory) -> Constraint:
    # Els dos professors han d'estar disponibles a la sessió assignada.
    return (constraint_factory
            .for_each(Tribunals)
            # Filtrem si hi ha sessió assignada i algun dels dos professors hi té un 0
            .filter(lambda t: 
                    t.sessio is not None and 
                    ((t.profe1 is not None and t.profe1.disponibilitat.get(t.sessio.id, 0) == 0) or
                    (t.profe2 is not None and t.profe2.disponibilitat.get(t.sessio.id, 0) == 0)))
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Un o els dos professors no estan disponibles a la sessió assignada"))

def c6(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: Un professor no pot estar a dos llocs alhora
    return (constraint_factory
            .for_each_unique_pair(Tribunals,
                Joiners.equal(lambda t: t.sessio.dia if t.sessio is not None else None),
                Joiners.equal(lambda t: t.sessio.hora if t.sessio is not None else None)
            )
            .filter(lambda t1, t2: t1.sessio is not None and t2.sessio is not None)
            .filter(lambda t1, t2:
                    (t1.profe1 is not None and (t1.profe1 == t2.profe1 or t1.profe1 == t2.profe2)) or
                    (t1.profe2 is not None and (t1.profe2 == t2.profe1 or t1.profe2 == t2.profe2)))
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Conflicte de professor: Dues sessions alhora"))

def c7(constraint_factory: ConstraintFactory) -> Constraint:
    # Una sessió només pot utilitzar les primeres 'max_aules' aules.
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: t.sessio is not None and t.aula is not None)
            .filter(lambda t: t.aula.ordre > t.sessio.max_aules)
            .penalize(HardMediumSoftScore.ONE_MEDIUM, 
                    lambda t: t.aula.ordre - t.sessio.max_aules)
            .as_constraint("Aula fora de l'índex permès per a la sessió"))

def c8(constraint_factory: ConstraintFactory) -> Constraint:
    # HARD: Temps de trasllat. Un professor només pot fer dues sessions 
    # consecutives si són a la mateixa aula. Si canvia d'aula, cal 1h lliure.
    return (constraint_factory
            .for_each_unique_pair(Tribunals)
            .filter(lambda t1, t2: 
                    t1.sessio is not None and t2.sessio is not None and
                    t1.aula is not None and t2.aula is not None)
            
            .filter(lambda t1, t2: t1.sessio.dia == t2.sessio.dia)
            
            .filter(lambda t1, t2: abs(t1.sessio.hora - t2.sessio.hora) == 1)
            
            .filter(lambda t1, t2: t1.aula.id != t2.aula.id)
            
            .filter(lambda t1, t2: 
                    (t1.profe1 is not None and (t1.profe1 == t2.profe1 or t1.profe1 == t2.profe2)) or
                    (t1.profe2 is not None and (t1.profe2 == t2.profe1 or t1.profe2 == t2.profe2))
            )
            .penalize(HardMediumSoftScore.ONE_HARD)
            .as_constraint("Temps de trasllat: Canvi d'aula sense hora lliure"))

def c9(constraint_factory: ConstraintFactory, profes_comodi) -> Constraint:

    return (constraint_factory
            .for_each(Profes)
            .join(Tribunals,
                Joiners.filtering(lambda profe, t: 
                                    (t.profe1 is not None and t.profe1.id == profe.id) or 
                                    (t.profe2 is not None and t.profe2.id == profe.id)))
            .group_by(lambda profe, t: profe, ConstraintCollectors.sum(lambda profe, t: 1))
            .filter(lambda profe, recompte: recompte > profe.capacitat_max_profe)
            # Apliquem el nivell MEDIUM per donar-li flexibilitat.
            # Si el profe és a la llista 'comodi', la penalització es multiplica per 1.
            # Si no hi és, es multiplica per 100
            .penalize(HardMediumSoftScore.ONE_MEDIUM, 
                      lambda profe, recompte: (recompte - profe.capacitat_max_profe) * (1 if profe.id in profes_comodi else 100))
            .as_constraint("Capacitat maxima superada (amb prioritat de comodins)"))