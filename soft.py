from timefold.solver.score import ConstraintCollectors
from timefold.solver.score import HardMediumSoftScore
from timefold.solver.score import (ConstraintFactory, Joiners, Constraint)

from estructura import Tribunals, Profes, Alumnes, Aules, Sessions


def r1(constraint_factory: ConstraintFactory) -> Constraint:
    # Maximitzar la voluntat dels professors
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: t.profe1 is not None or t.profe2 is not None)
            .reward(HardMediumSoftScore.ONE_SOFT,
                    lambda t: (t.profe1.voluntats.get(t.alumne.id, 0) if t.profe1 is not None else 0) +
                            (t.profe2.voluntats.get(t.alumne.id, 0) if t.profe2 is not None else 0))
            .as_constraint("Maximitzar voluntats dels professors"))


def r2(constraint_factory: ConstraintFactory, w2) -> Constraint:
    return (constraint_factory
            .for_each(Tribunals)
            .filter(lambda t: t.profe1 is not None and t.profe2 is not None)
            .penalize(HardMediumSoftScore.ONE_SOFT,
                    lambda t: w2 * ((1 if t.profe1.area_profe != t.alumne.area_alumne else 0) +
                                   (1 if t.profe2.area_profe != t.alumne.area_alumne else 0)))
            .as_constraint("Penalitzar discordança d'àrees"))

def r3(constraint_factory: ConstraintFactory, w3) -> Constraint:
    return (constraint_factory
            .for_each_unique_pair(Tribunals)
            .filter(lambda t1, t2: 
                    t1.sessio is not None and t2.sessio is not None and
                    t1.aula is not None and t2.aula is not None and
                    t1.sessio.dia == t2.sessio.dia and
                    t1.aula.id != t2.aula.id)
            .filter(lambda t1, t2:
                    (t1.profe1 is not None and (t1.profe1 == t2.profe1 or t1.profe1 == t2.profe2)) or
                    (t1.profe2 is not None and (t1.profe2 == t2.profe1 or t1.profe2 == t2.profe2)))
            .penalize(HardMediumSoftScore.ONE_SOFT, lambda t1, t2: w3)
            .as_constraint("Evitar canvis d'aula durant el dia"))



def r4(constraint_factory: ConstraintFactory) -> Constraint:
    # minimitzar els dies que ve un professor
    return (constraint_factory
            .for_each(Profes)
            # Unim amb els tribunals on aquest professor participa
            .join(Tribunals,
                Joiners.filtering(lambda profe, t: 
                                    (t.profe1 is not None and t.profe1.id == profe.id) or 
                                    (t.profe2 is not None and t.profe2.id == profe.id)))
            # Agrupem per Professor i Dia
            .filter(lambda profe, t: t.sessio is not None)
            .group_by(lambda profe, t: (profe.id, t.sessio.dia))

            # Per cada dia que el professor hagi de venir, apliquem una penalització forta (SOFT)
            .penalize(HardMediumSoftScore.ONE_SOFT)
            .as_constraint("Minimitzar dies de desplaçament"))

def r5(constraint_factory: ConstraintFactory) -> Constraint:
    #minimitzar hores mortes
    return (constraint_factory
            .for_each_unique_pair(Tribunals,
                # Mateix dia
                Joiners.equal(lambda t: t.sessio.dia if t.sessio is not None else None),
                # Han de compartir algun professor (en qualsevol combinació de profe1/profe2)
                Joiners.filtering(lambda t1, t2: 
                    (t1.profe1 is not None and (t1.profe1 == t2.profe1 or t1.profe1 == t2.profe2)) or
                    (t1.profe2 is not None and (t1.profe2 == t2.profe1 or t1.profe2 == t2.profe2))
                )
            )
            # Penalitzem la distància temporal
            # Si hora1=9 i hora2=10, abs(9-10)-1 = 0 (perfecte)
            # Si hora1=9 i hora2=12, abs(9-12)-1 = 2 (dues hores mortes)
            .filter(lambda t1, t2: t1.sessio is not None and t2.sessio is not None)  # filter separat
            .penalize(HardMediumSoftScore.ONE_SOFT,
                    lambda t1, t2: max(0, abs(t1.sessio.hora - t2.sessio.hora) - 1))  # sense if
            .as_constraint("Minimitzar hores mortes"))

