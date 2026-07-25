from machine import Pin
import time

pino_dados = Pin(4, Pin.IN, Pin.PULL_DOWN)
pino_clock = Pin(5, Pin.OUT)

# Etapa 1
def ler_sensor_bruto():
    while pino_dados.value() == 1:
        pass
    valor = 0
    for _ in range(24):
        pino_clock.value(1)
        time.sleep_us(1)
        bit = pino_dados.value()
        valor = (valor<<1) | bit
        pino_clock.value(0)
        time.sleep_us(2)

    pino_clock.value(1)
    time.sleep_us(1)
    pino_clock.value(0)
    time.sleep_us(1)

    if valor & 0x800000:
        valor -= 0x1000000

    return valor

# Etapa 2
def ler_peso_gramas():
    for _ in range(15):
        leitura1 = ler_sensor_bruto()
        leitura2 = ler_sensor_bruto()
        if abs(leitura1 - leitura2) < 30:
            bruto = leitura2
            break
    else:
        bruto = leitura2

    gramas = (bruto / 2100) * 5000
    return gramas

# 2.1
limite_vazio = 200
limite_cheio = 4500

estado_atual = "regular"

print("Sistema Kanban Inicializado")

# Etapa 3 - Loop Principal
while True:
    peso = ler_peso_gramas()

    if peso <= 50:
        estado_novo = "anomalia"

    elif peso < limite_vazio:
        estado_novo = "vazio"

    elif peso > limite_cheio:
        estado_novo = "cheio"

    else:
        estado_novo = "regular"

    time.sleep(0.1)

    if estado_novo != estado_atual:
        if estado_novo == "anomalia":
            print("ALERTA: Caixa ausente ou erro de calibração no sensor HX711!")
        elif estado_novo == "vazio":
            print("Evento de reposição disparado! Caixa vazia detectada.")
        elif estado_novo == "cheio":
            print("Abastecimento concluído. Caixa cheia.")
        else:
            print(f"Status: Estoque Regular ({int(peso)}g)")

        estado_atual = estado_novo
