def calculo_de_importe(hE, fE, hS, fS, pension, t_tolerancia):
    #Convertir las fechas en listas iterables
    hEntrada = list(hE.split(':'))
    fEntrada = list(fE.split('-'))
    hSalida = list(hS.split(':'))
    fSalida = list(fS.split('-')) #Al final cambiar a "-"

    #Identificador de tipo de pension
    tipos_de_pension = {"Ninguna":1, "Día":2, "Semana":3, "Mes":4}
    for i in tipos_de_pension:
        if pension == i:
            pension_actual = tipos_de_pension[i]

    #Cálculo de los días
    dias_mes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    mes = int(fEntrada[-2])#4
    cont_mes=0
    if mes < int(fSalida[-2]):
        while mes < int(fSalida[-2]):
            cont_mes = cont_mes + dias_mes[mes]
            mes = mes + 1
        dias_totales =  int(fSalida[-1]) + (cont_mes - (int(fEntrada[-1])-1))
    elif mes == int(fSalida[-2]):
        if pension_actual == 1:
            if int(fSalida[-1]) == int(fEntrada[-1]) or ((int(fEntrada[-1]))+1) == int(fSalida[-1]):
                dias_totales = 0
            else:
                dias_totales = (int(fSalida[-1]) - (int(fEntrada[-1])))
        else:
            if int(fSalida[-1]) == int(fEntrada[-1]):
                dias_totales = 0
            else:
                dias_totales = (int(fSalida[-1]) - (int(fEntrada[-1])))
    print("Dias totales:",dias_totales)
    #Calculo de horas
    if fEntrada[-2] != fSalida[-2]:
        minutos_totales = (1440 - ((int(hEntrada[0])*60)+int(hEntrada[1]))) + ((int(hSalida[0])*60)+int(hSalida[1]))
    else:
        if int(hEntrada[0]) <= int(hSalida[0]):
            minutos_totales = ((int(hSalida[0])*60)+int(hSalida[1])) - ((int(hEntrada[0])*60)+int(hEntrada[1]))
        elif int(hEntrada[0]) > int(hSalida[0]):
            minutos_totales = 1440 - (((int(hEntrada[0])*60)+int(hEntrada[1])) - ((int(hSalida[0])*60)+int(hSalida[1])))
    #Calculo de importe
    #sin pension
    if pension_actual == 1:
        calculo_tiempo_total = ((dias_totales*24)*60) + minutos_totales
        print("Total de minutos:",calculo_tiempo_total)
        if calculo_tiempo_total <= t_tolerancia:
            importe_final = 0
        elif calculo_tiempo_total <= 120 and calculo_tiempo_total > t_tolerancia:
            importe_final = 20
        else:
            importe_final = ((round((calculo_tiempo_total-120)/60))*20)+20
    #pension de dia
    elif pension_actual == 2:
        calculo_tiempo_total = ((dias_totales*24)*60) + minutos_totales#dias_totales + (int((minutos_totales/60)/24))
        importe_final = (int((calculo_tiempo_total/60)/24)) * 200
    #pension de semana
    elif pension_actual == 3:
        calculo_tiempo_total = round((dias_totales)/7)
        importe_final = int(calculo_tiempo_total * 1000)
    #pension de mes
    elif pension_actual == 4:
        calculo_tiempo_total = round(dias_totales/30)
        importe_final = calculo_tiempo_total * 4000
    #return print("Días totales:",dias_totales,", código de pensión:",pension_actual,", minutos totales:", minutos_totales, ", importe final: ${} MXN " .format(importe_final))
    return importe_final