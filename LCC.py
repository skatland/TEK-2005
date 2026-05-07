import numpy as np
import matplotlib.pyplot as plt

#### Variabler ####

L = 1000              # bjelkelengde [mm]
H = 200               # total høyde [mm]
B = 200               # flensbredde [mm]

pressure = 300000     # trykk [Pa]
load_width = 200      # belastet bredde [mm]

yield_strength = 250  # flytegrense, tilsvarende optimaliseringsmodell og fusion
target_SF = 2.5       # ønsket sikkerhetsfaktor


#############################################################
## Gjennbruk av sefatey_factor fra optimaliseringsmodellen ##
#############################################################

def safety_factor(steg_t, flens_t):

    # Trykk omregnes fra Pa til N/mm^2 (F = p * A)
    pressure_N_mm2 = pressure / 1_000_000

    # Total last på toppflaten
    F = pressure_N_mm2 * load_width * L

    # Formel 4: M_max = w * L^2 / 2
    w = F / L
    M = w * L**2 / 2

    # Steg høyde = total høyde - øver+nedre flens
    steg_height = H - 2 * flens_t

    # Eliminerer steg høyde som er 0 eller mindre
    if steg_height <= 0:
        return np.nan

    # Formel 2: I = b * h^3 / 12
    # Arealmoment for steget
    I_steg = steg_t * steg_height**3 / 12

    # Formel 2 + parallellakseteoremet:
    # I = I_lokal + A * d^2
    A_flens = B * flens_t
    y_flens = H / 2 - flens_t / 2
    I_flens_local = B * flens_t**3 / 12

    I_flenser = 2 * (
        I_flens_local + A_flens * y_flens**2
    )

    # Totalt arealmoment for hele I-profilet
    I_total = I_steg + I_flenser


    # Formel 1 / Formel 3:
    # sigma = M * y / I
    sigma = M * (H / 2) / I_total

    # Formel 6:
    # SF = sigma_y / sigma
    # Forholdet mellom flytegrensen til stålet
    #og beregnet bøyespenning
    SF = yield_strength / sigma

    return SF

#### LCC-antakelser ####

steel_density = 7850        # kg/m3
steel_price = 25            # kr/kg, antatt pris for konstruksjonsstål
analysis_years = 50         # år, antatt analyseperiode
inspection_cost_year = 100  # kr/år, enkel inspeksjon/vedlikehold
failure_cost = 25000        # kr, antatt kostnad ved svikt/utskiftning


###############################
#### Tverrsnitt, volum, masse ###
################################

def beam_area_mm2(steg_t, flens_t):
    steg_height = H - 2 * flens_t
    if steg_height <= 0:
        return np.nan
    A_steg = steg_t * steg_height
    A_flenser = 2 * B * flens_t
    return A_steg + A_flenser


def beam_mass_kg(steg_t, flens_t):
    A_mm2 = beam_area_mm2(steg_t, flens_t)
    if np.isnan(A_mm2):
        return np.nan
    volume_mm3 = A_mm2 * L
    volume_m3 = volume_mm3 * 1e-9
    return volume_m3 * steel_density


################################
### Sviktsannsynlighet ########
###############################

def failure_probability(SF):

    # Forenklet antatt sannsynlighet for svikt basert på sikkerhetsfaktor.
    # Brukes kun som numerisk demonstrasjon i LCC.

    if SF < 2.0:
        return 0.30
    elif SF < 2.5:
        return 0.15
    elif SF < 3.0:
        return 0.03
    else:
        return 0.01


####################
### LCC-beregning ###
#####################

def calculate_lcc(steg_t, flens_t):
    SF = safety_factor(steg_t, flens_t)
    mass = beam_mass_kg(steg_t, flens_t)

    if np.isnan(SF) or np.isnan(mass):
        return None

    C_material = mass * steel_price
    C_maintenance = inspection_cost_year * analysis_years
    C_failure = failure_probability(SF) * failure_cost

    total_LCC = C_material + C_maintenance + C_failure

    return {
        "steg_t": steg_t,
        "flens_t": flens_t,
        "SF": SF,
        "mass": mass,
        "C_material": C_material,
        "C_maintenance": C_maintenance,
        "C_failure": C_failure,
        "total_LCC": total_LCC,
        "Pf": failure_probability(SF)
    }


###############################
### Tre design-alternativer ###
###############################

alternatives = {
    "Underdimensjonert": (4.0, 4.0),
    "Optimalisert":      (5.75, 7.25),
    "Overdimensjonert":  (12.0, 14.0)
}

results = {}

print("\n=== LCC-SAMMENLIGNING AV BJELKEDESIGN ===\n")

for name, (steg_t, flens_t) in alternatives.items():
    result = calculate_lcc(steg_t, flens_t)
    results[name] = result

    print(name)
    print(f"Stegtykkelse:            {result['steg_t']:.2f} mm")
    print(f"Flenstykkelse:           {result['flens_t']:.2f} mm")
    print(f"Sikkerhetsfaktor:        {result['SF']:.2f}")
    print(f"Sviktsannsynlighet:      {result['Pf']*100:.1f} %")
    print(f"Masse:                   {result['mass']:.2f} kg")
    print(f"Materialkostnad:         {result['C_material']:.0f} kr")
    print(f"Vedlikehold/inspeksjon:  {result['C_maintenance']:.0f} kr")
    print(f"Forventet sviktkostnad:  {result['C_failure']:.0f} kr")
    print(f"Total LCC:               {result['total_LCC']:.0f} kr")
    print("-" * 45)


###################################
### Finn laveste LCC med SF >= 2.5
###################################

steg_values  = np.arange(4, 16.25, 0.25)
flens_values = np.arange(4, 26.25, 0.25)

best_lcc = float("inf")
best_design = None

LCC_grid = np.zeros((len(flens_values), len(steg_values)))
SF_grid  = np.zeros((len(flens_values), len(steg_values)))

for i, flens_t in enumerate(flens_values):
    for j, steg_t in enumerate(steg_values):
        result = calculate_lcc(steg_t, flens_t)

        if result is None:
            LCC_grid[i, j] = np.nan
            SF_grid[i, j]  = np.nan
            continue

        LCC_grid[i, j] = result["total_LCC"]
        SF_grid[i, j]  = result["SF"]

        if result["SF"] >= target_SF and result["total_LCC"] < best_lcc:
            best_lcc = result["total_LCC"]
            best_design = result

print("\n=== LAVEST LCC MED KRAV SF >= 2.5 ===\n")
print(f"Stegtykkelse:   {best_design['steg_t']:.2f} mm")
print(f"Flenstykkelse:  {best_design['flens_t']:.2f} mm")
print(f"Sikkerhetsfaktor: {best_design['SF']:.2f}")
print(f"Masse:          {best_design['mass']:.2f} kg")
print(f"Total LCC:      {best_design['total_LCC']:.0f} kr")


#########################################
#### Plot LCC for alle tre designene ###
#############################################

names      = list(results.keys())
lcc_values = [results[name]["total_LCC"] for name in names]

plt.figure(figsize=(8, 5))
plt.bar(names, lcc_values)
plt.ylabel("Total LCC [kr]")
plt.title("Livsløpskostnad for tre bjelkedesign")
plt.grid(axis="y")
plt.tight_layout()
plt.show()


