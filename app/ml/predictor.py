import random
from datetime import date, timedelta
from typing import Optional

try:
    from sklearn.tree import DecisionTreeRegressor
except Exception:
    # Fallback ligero si scikit-learn no está disponible (solo para evitar crash)
    DecisionTreeRegressor = None


class Predictor:
    def __init__(self):
        self.species_map = {"perro": 0, "gato": 1, "ave": 2, "otro": 3}
        self.treatment_map = {"Vacuna": 0, "Desparasitación": 1, "Control": 2, "Otro": 3}
        self.model = self._train_model()
        self.average_days = 30

    def _train_model(self):
        # Dataset simulado: [edad, species_code, treatment_code, dias_desde_ultima_cita] -> dias_hasta_proxima
        rng = random.Random(42)
        X = []
        y = []
        for _ in range(500):
            edad = rng.randint(1, 15)
            species = rng.choice(list(self.species_map.values()))
            treatment = rng.choice(list(self.treatment_map.values()))
            dias_ultima = rng.randint(0, 180)
            # Regla aproximada: más joven y vacunación -> citas más frecuentes
            base = 45
            base -= 10 if edad <= 2 else 0
            base -= 10 if treatment == self.treatment_map["Vacuna"] else 0
            base += 10 if species == self.species_map["ave"] else 0
            ruido = rng.randint(-7, 7)
            dias_proxima = max(7, base + ruido)
            X.append([edad, species, treatment, dias_ultima])
            y.append(dias_proxima)

        self.average_days = int(sum(y) / len(y))
        if DecisionTreeRegressor is None:
            return None
        model = DecisionTreeRegressor(max_depth=5, random_state=42)
        model.fit(X, y)
        return model

    def _encode_species(self, species: str) -> int:
        key = species.strip().lower()
        return self.species_map.get(key, self.species_map["otro"])

    def _encode_treatment(self, treatment_type: Optional[str]) -> int:
        if not treatment_type:
            return self.treatment_map["Control"]
        key = treatment_type.strip().capitalize()
        return self.treatment_map.get(key, self.treatment_map["Otro"])

    def estimate_next_date(self, pet) -> Optional[date]:
        """Dada una mascota y su historial, estima la próxima cita/vacuna."""
        try:
            last_appt = None
            if pet.appointments:
                last_appt = max((a.date for a in pet.appointments if a.date), default=None)
            last_treatment_type = None
            last_treatment_date = None
            if pet.treatments:
                last_t = max((t.applied_date for t in pet.treatments if t.applied_date), default=None)
                last_treatment_date = last_t
                # Buscar tipo del tratamiento con esa fecha
                for t in pet.treatments:
                    if t.applied_date == last_t:
                        last_treatment_type = t.treatment_type
                        break

            base_date = last_appt or last_treatment_date or date.today()
            dias_ultima = (date.today() - base_date).days if base_date else 0

            features = [
                int(getattr(pet, "age", 1) or 1),
                self._encode_species(getattr(pet, "species", "otro")),
                self._encode_treatment(last_treatment_type),
                dias_ultima,
            ]

            if self.model:
                pred_days = int(self.model.predict([features])[0])
            else:
                pred_days = self.average_days

            pred_days = max(7, pred_days)
            return base_date + timedelta(days=pred_days)
        except Exception:
            return None

    def estimate_next_appointment_date(self, pet) -> Optional[date]:
        """Estimación enfocada en próxima cita general (ignora último tratamiento)."""
        try:
            last_appt = None
            if getattr(pet, "appointments", None):
                last_appt = max((a.date for a in pet.appointments if a.date), default=None)

            base_date = last_appt or date.today()
            dias_ultima = (date.today() - base_date).days if base_date else 0

            features = [
                int(getattr(pet, "age", 1) or 1),
                self._encode_species(getattr(pet, "species", "otro")),
                self.treatment_map["Control"],
                dias_ultima,
            ]

            if self.model:
                pred_days = int(self.model.predict([features])[0])
            else:
                pred_days = self.average_days
            pred_days = max(7, pred_days)
            return base_date + timedelta(days=pred_days)
        except Exception:
            return None

    def estimate_next_vaccine_date(self, pet) -> Optional[date]:
        """Estimación enfocada en próxima vacuna (usa señal de vacuna reciente si existe)."""
        try:
            last_treatment_date = None
            if getattr(pet, "treatments", None):
                last_vac = [t.applied_date for t in pet.treatments if t.treatment_type == "Vacuna" and t.applied_date]
                last_treatment_date = max(last_vac) if last_vac else None

            base_date = last_treatment_date or date.today()
            dias_ultima = (date.today() - base_date).days if base_date else 0

            features = [
                int(getattr(pet, "age", 1) or 1),
                self._encode_species(getattr(pet, "species", "otro")),
                self.treatment_map["Vacuna"],
                dias_ultima,
            ]

            if self.model:
                pred_days = int(self.model.predict([features])[0])
            else:
                pred_days = max(21, self.average_days - 5)
            pred_days = max(14, pred_days)
            return base_date + timedelta(days=pred_days)
        except Exception:
            return None