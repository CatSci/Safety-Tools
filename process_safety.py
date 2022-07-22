import streamlit as st
import pandas as pd
from collections import defaultdict

st.markdown('**Note - Please do not post target or intermediate structure information externally**.')
st.title('Process Safety')

smile = st.text_input('Enter Smile Code', value= 'O1N=C(C=C1)C(C1)=CC(=CC=1N=[N+]=[N-])CC')
formula = st.text_input('Enter Molecule Formula', 'C11H10N4O')


df = pd.read_excel('atomic masses.xlsx')

mass_df = df[df.columns[[1, 3]]]

sym_to_mass = {}

for i in range(mass_df.shape[0]):
    sym = mass_df.iloc[i, 0]
    mass = mass_df.iloc[i, 1]
    sym_to_mass[sym] = mass

hefg_list = ['C1OC1', 'O1C(C1)C', 
    'C1CNC1', 'C1CN(C1)C',
    'OO',
    'N=[N+]=[N-]',
    'N1=CC=CO1', 'C1C=C(ON=1)C', 'O1N=C(C=C1)C', 'N1=CC(=CO1)C',
    'C#C',
    'N#C', 'C#N',
    'N(=O)=O', '[N+]([O-])=O',
    'O=NO', 
    'N+]#N', 'N=N', 
    '[O-]Cl', '[O-]Br',
    'O=Cl(=O)[O-]', 'O=Cl(=O)(=O)[O-]',
    'I=O', '(OI2(O)=O)=O', 
    '[Li]', '[Mg]',
    'NN',
    '[O-][N+](=O)[O-]',
    'NO',
    '[N+]', '[O-]',
    'C1N(CC1)']
###############
# To find HEFG
###############

def find_part(data, hefg_list):
    """Return a smile part that was found.

    @param1 : data -> input data SMILE
    @param2 : s -> 
    """
    count = 0
    group = []
    for i in range(len(hefg_list)):
        if hefg_list[i] in data:
            count += 1
            group.append(hefg_list[i])
    return count, group

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
    if hefg > 0:
        x = count / hefg
    
        if x < 6:
            return x
    
    return x


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
        if 'C' not in atoms:
            x = 0
        if 'H' not in atoms:
            y = 0
        if 'O' not in atoms:
            z = 0

        if atoms[i] == 'C':
            x = int(atoms[i + 1])
        if atoms[i] == 'H':
            y = int(atoms[i + 1])
        if atoms[i] == 'O':
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

def main(smile, hefg_list, sym_to_mass, formula):
    if smile is not None and formula is not None:
        hefg, group = find_part(smile, hefg_list)
        r_v = rule_six(smile, hefg)
        oxy = oxygen_balance(sym_to_mass, formula)

    return hefg, r_v, oxy, group
 

def color_picker(oxy):
    color = ''
    text = ''
    if oxy > 160 or oxy < -240:
        color = '#C2D69B'
        text = 'Low'
    elif 80 < oxy < 160 or -120 > oxy > -240:
        color = '#FFC000'
        text = 'Medium'
    elif 80 > oxy > -120:
        color = '#FF0000'
        text = 'High'

    return color, text


def summary(group, r_v, oxy, text):
    st.markdown('<p class="big-font">{} High Energy Fucntion groups found.</p>'.format(len(group)), unsafe_allow_html=True)
    if r_v < 6 or r_v != 0:
        st.markdown('<p class="big-font">Failed Rule Six Because its less than 6.</p>'.format(r_v), unsafe_allow_html=True)
    else:
        st.markdown('<p class="big-font">Passed Rule Six Because its greater than 6.</p>'.format(r_v), unsafe_allow_html=True)
    st.markdown('<p class="big-font">Hazard rank is {} because Oxygen Balance is {}.</p>'.format(text, oxy), unsafe_allow_html=True)



def create_dataframe(hefg, rule_six, oxy, hazard):
    df = pd.DataFrame({'HEFG': hefg, 'Rule Six': rule_six, 'Oxygen Balance': oxy, 'Hazard Rank': hazard})
    return df.to_csv().encode('utf-8')


st.markdown("""
    <style>
    .big-font {
        font-size:19px !important;
        font-family: serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0C1B2A;
    color:#ffffff;
    border:None;
}
div.stButton > button:first-child:focus {
    background-color: #0C1B2A;
    color:#ffffff;
    border:None;
}
</style>""", unsafe_allow_html=True)




if st.button('Calculate'):
    hefg, r_v, oxy, group = main(smile, hefg_list, sym_to_mass, formula)
    color, text = color_picker(oxy)
    df = create_dataframe(group, r_v, oxy, text)
    st.download_button(
        label= 'Download Data',
        data = df,
        file_name = 'project_safety.csv',
        mime= 'text/csv'
    )
    col1, col2, col3, col4 = st.columns((1.3, 1, 1, 1))
    with col1:
        st.text('HEFG')
        for i in range(len(group)):
            if i + 1 < len(group):
                st.subheader(str(group[i] + ','))
            else:
                st.subheader(str(group[i]))
    
    with col2:
        st.text('Rule Six')
        st.subheader(round(r_v, 2))
    with col3:
        st.text('Oxygen Balance')
        st.subheader(oxy)
    with col4:
        st.text('Hazard Rank')
        st.subheader(text)
    
    st.text('')
    st.text('Summary')
    summary(group, r_v, oxy, text) 


# s = ['C1OC1', 'C1CNC1', 'OO', 'N=[N+]=[N-]', 'N1=CC=CO1']
# # smile, formula = 'O1N=C(C=C1)C(C1)=CC(=CC=1N=[N+]=[N-])CC' , 'C11H10N4O'
# # smile, formula = 'C1N(CC1)CC1=CC(=CC=C1)Br', 'C10H12BrN'
# smile, formula = 'O1C(C1)C1=CC(=CC=C1)C(OO)=O', 'C9H8O4'




# add summary below to display why hazard rank is high or low
