def color_picker(oxy = -80):
    color = None
    text = ''
    if oxy > 160 or oxy < -240:
        print('Green')
        color = '#C2D69B'
        text = 'Low'
    elif 80 < oxy < 160 or -120 > oxy > -240:
        print('Yellow')
        color = '#FFC000'
        text = 'Medium'
    elif 80 > oxy > -120:
        print('Red')
        color = '#FF0000'
        text = 'High'

    return color, text



color, text = color_picker()

print(color)
print(text)