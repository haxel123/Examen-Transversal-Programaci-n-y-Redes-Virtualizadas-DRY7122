'''Script para solicitar número de vlan al usuario, indicando en pantalla 
si corresponde a la VLAN de rango normal o de rango extendido 
 '''
print('---------------------------------------')


while True:
    #Solicitar al usuario el numero de VLAN al usuario
    entrada = input('\n Ingresar número de VLAN (o "s" para salir): ')

    #Verificar si el usuario quiere salir
    if entrada.lower() == 's':
        print ('Saliendo del programa....')
        break

    try:
        #Convertir a entero y validar VLAN
        vlan = int(entrada)

        if 1 <= vlan <= 1005:
            print(f'VLAN {vlan} es de rango normal')
        elif 1006 <= vlan <= 4094:
            print(f'VLAN {vlan} es de rango extendido')
        else:
            print(f'VLAN {vlan} invalida -Rango válido: 1-4094')

    except ValueError:
        print('Error: Debe ingresar un numero entero valido')
    
