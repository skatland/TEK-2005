import numpy as np
import matplotlib.pyplot as plt

# Sikkerhetsfaktor fra LCC, ikke fusion
design = {
    "Underdimensjonert": 1.48,
    "Optimalisert": 2.50,
    "Overdimensjonert": 4.47
}

# Strength: flytegrense brukt i optimalisering og Fusion
R = 250  # MPa

# Antatt usikkerhet/spredning.
std_R = 25  # MPa, antatt variasjon i strength
std_S = 20  # MPa, antatt variasjon i stress

# Felles standardavvik for M = R - S fra teori
std_M = np.sqrt(std_R**2 + std_S**2)

#Setter opp x-akse for sikkerhetsmargin
x = np.linspace(-100, 300, 1000)

# Normalfordelingen hentet fra Wikipedia/Normalfordeling:
# https://no.wikipedia.org/wiki/Normalfordeling

def normalfordeling(x, mean, std):
    return (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std)**2)

plt.figure(figsize=(9, 6))

for navn, SF in design.items():
# Formel fra teori:
    S = R / SF

# Limit-state / sikkerhetsmargin:
    M = R - S

    y = normalfordeling(x, M, std_M)

    plt.plot(x, y, label=f"{navn}: M = {M:.1f} MPa")

plt.axvline(0, linestyle="--", color="black", label="Sviktgrense M = 0")

plt.xlabel("Sikkerhetsmargin M = R - S [MPa]")
plt.ylabel("Sannsynlighetstetthet")
plt.title(" Stress–strength-analyse for de 3 bjelkedesignene. (konseptuell)")
plt.legend()
plt.grid(True)
plt.show()