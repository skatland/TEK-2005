import numpy as np
import matplotlib.pyplot as plt

###Variabler###

L = 1000              # bjelkelengde mm
H = 200               # total høyde mm
B = 200               # flensbredde mm

pressure = 300000     # trykk Pa
load_width = 200      # bredden lasten virker over mm
yield_strength = 250  # flytegrense for tilsvarende stål som Fusion, MPa

target_SF = 2.5       # ønsket sikkerhetsfaktor


######################
### Beregning SF #####
######################

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


#############################################
#Parametrisk test av steg- og flenstykkelse#
############################################


steg_values = np.arange(4, 16.25, 0.25)
flens_values = np.arange(4, 26.25, 0.25)

SF_grid = np.zeros((len(flens_values), len(steg_values)))

best_error = 999
best = None

for i, flens_t in enumerate(flens_values):
    for j, steg_t in enumerate(steg_values):

        # Beregner SF for hver kombinasjon
        SF = safety_factor(steg_t, flens_t)
        SF_grid[i, j] = SF

        # Finner kombinasjonen nærmest ønsket SF
        error = abs(SF - target_SF)

        if error < best_error:
            best_error = error
            best = (steg_t, flens_t, SF)


#####################
## Genererer plot ###
#####################

STEG, FLENS = np.meshgrid(steg_values, flens_values)

plt.figure(figsize=(9, 6))

contour = plt.contourf(STEG, FLENS, SF_grid, levels=40)
plt.colorbar(contour, label="Sikkerhetsfaktor")

# Viser målområdet for sikkerhetsfaktor
lines = plt.contour(
    STEG,
    FLENS,
    SF_grid,
    levels=[2, 2.5, 3],
    linewidths=2
)

plt.clabel(lines, inline=True, fontsize=10)


plt.xlabel("Stegtykkelse [mm]")
plt.ylabel("Flenstykkelse [mm]")
plt.title("Parametrisk optimalisering av steg og flens")
plt.grid(True)
plt.legend()
plt.show()
