import pandas as pd
import seaborn as sns
from collections import defaultdict
import argparse

ap = argparse.ArgumentParser()

ap.add_argument('-d', "--smile", required= True, help = "smile code")
ap.add_argument('-f', '--formula', required= True, help = 'complete molecule formula')

df = pd.read_excel('atomic masses.xlsx')

mass_df = df[df.columns[[1, 3]]]

sym_to_mass = {}

for i in range(mass_df.shape[0]):
    sym = mass_df.iloc[i, 0]
    mass = mass_df.iloc[i, 1]
    sym_to_mass[sym] = mass

s = ['C1OC1', 'C1CNC1', 'OO', 'N=[N+]=[N-]', 'N1=CC=CO1', 'C1N(CC1)C']

###############
# To find HEFG
###############

def find_part(data, s):
    """Return a smile part that was found.

    @param1 : data -> input data SMILE
    @param2 : s -> 
    """
    count = 0
    for i in range(len(s)):
        if s[i] in data:
            count += 1
            print(f"\n")
            print(f"{s[i]} found in {data}")
    
    return count

####################
# To find 'C' atoms
####################

def rule_six(data, hefg):
    """Return a integer.

    @param1 : data -> input data SMILE
    @param2 : hefg -> 
    """
    count = 0
    for i in range(len(data)):
        if data[i] == 'C':
            count += 1
    
    x = count / hefg

    if x < 6:
        return 'RED'
    
    return 'GREEN'

#O1N=C(C=C1)C(C1)=CC(=CC=1N=[N+]=[N-])CC

def calculate_formula(smile, mass_df):
    formula = {}
    for i in smile:
        # print(i)
        if i in mass_df['Symbol']:
            print('present')
            print(i)
        break

#################
# To count atoms
#################

def countOfAtoms(formula: str) -> str:
    dt = defaultdict(int)
    stack = [1]
    digits = ""
    lowers = ""
    for element in formula[::-1]:
        if element.isdigit():
            digits = element + digits
        elif element.islower():
            lowers = element + lowers
        elif element == ")":
            stack.append(stack[-1]*int(digits or 1))
            digits = ""
        elif element == "(":
            stack.pop()
        #if element is an uppercase letter
        else:
            element = element + lowers
            dt[element] = dt[element]+stack[-1]*(int(digits or 1))
            digits = ""
            lowers = ""
    result = []
    for key, value in sorted(dt.items()):
        if value == 1:
            value = ""
        result.append(key)
        result.append(str(value))
    
    atoms = []
    for i in result:
        if i == '':
            atoms.append('1')
        else:
            atoms.append(i)
    return atoms

###############################
# To calculate molecule weight
###############################

def molecule_weight(sym_to_mass, atoms):
    mass = 0
    for i in range(len(atoms)):
        if atoms[i] in sym_to_mass:
            m = sym_to_mass[atoms[i]]
            a = int(atoms[i + 1])
            mass =  mass + a*m

    return mass 


####################
# To find oxy params
####################

def oxy_params(atoms):
    for i in range(len(atoms)):
        if atoms[i] == 'C':
            x = int(atoms[i + 1])
        elif atoms[i] == 'H':
            y = int(atoms[i + 1])
        elif atoms[i] == 'O':
            z = int(atoms[i + 1])
    
    return x, y, z

#############################
# To calculate oxygen balance
#############################

def oxygen_balance(sym_to_mass, formula):
    atoms = countOfAtoms(formula)  
    mw = molecule_weight(sym_to_mass, atoms)
    x, y, z = oxy_params(atoms)
    oxy_bal = round(-1600 * (x + y/2 -z) / mw)
    return oxy_bal

def main(smile, s, sym_to_mass, formula):
    hefg = find_part(smile, s)
    r_s = rule_six(smile, hefg)
    oxy = oxygen_balance(sym_to_mass, formula)

    return hefg, r_s, oxy




smile, formula = 'O1N=C(C=C1)C(C1)=CC(=CC=1N=[N+]=[N-])CC' , 'C11H10N4O'
# smile, formula = 'C1N(CC1)CC1=CC(=CC=C1)Br', 'C10H12BrN'
# smile, formula = 'O1C(C1)C1=CC(=CC=C1)C(OO)=O', 'C9H8O4'

if __name__ == "__main__":
    # hefg, r_s, oxy = main(smile, s, sym_to_mass, formula)
    # print(f"\n")
    # print(f"HEFG count: {hefg}")
    # print(f"Rule Six: {r_s}")
    # print(f"Oxygen Balance: {oxy}")
    calculate_formula(smile, mass_df)



# Questions
# 1. what if no hefg found then rule six will give division by 0 error?
# 2. What to do if hefg is found right now i am printing number of hefg is present?
# 3. how to present this calculated info in web interface.