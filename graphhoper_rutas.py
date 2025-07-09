#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse
import re

API_KEY = "8bc67068-d89a-4e21-ab2c-3abc59f3050b"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"

TRANSPORTES = {
    "1": ("car", "Auto"),
    "2": ("bike", "Bicicleta"),
    "3": ("foot", "Caminando")
}

def geocodificar(ubicacion):
    if not ubicacion:
        return None, None, ubicacion

    params = {"q": ubicacion, "limit": 1, "key": API_KEY}
    try:
        r = requests.get(GEOCODE_URL + urllib.parse.urlencode(params))
        r.raise_for_status()
        data = r.json()
        if not data["hits"]:
            print(f"No se encontró: {ubicacion}")
            return None, None, ubicacion

        h = data["hits"][0]
        lat, lng = h["point"]["lat"], h["point"]["lng"]
        nombre = h.get("name", ubicacion)
        estado = h.get("state", "")
        pais = h.get("country", "")
        if estado and pais:
            nombre = f"{nombre}, {estado}, {pais}"
        elif pais:
            nombre = f"{nombre}, {pais}"

        return lat, lng, nombre

    except requests.RequestException as e:
        print("Error geocodificando:", e)
        return None, None, ubicacion

def calcular_ruta(origen, destino, perfil):
    params = {
        "key": API_KEY,
        "vehicle": perfil,
        "point": [f"{origen[0]},{origen[1]}", f"{destino[0]},{destino[1]}"],
        "instructions": "true",
        "locale": "es"
    }
    try:
        url = ROUTE_URL + urllib.parse.urlencode(params, doseq=True)
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print("Error calculando ruta:", e)
        return None

def traducir_indicacion(texto):
    # Traducciones comunes
    texto = re.sub(r"\band take (\d+) toward ([\w\s]+)", r"y toma la ruta \1 hacia \2", texto)
    texto = re.sub(r"\btake (\d+) toward ([\w\s]+)", r"toma la ruta \1 hacia \2", texto)
    texto = re.sub(r"\btoward ([\w\s]+)", r"hacia \1", texto)
    texto = re.sub(r"\bSlight right\b", "Gira levemente a la derecha", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bSlight left\b", "Gira levemente a la izquierda", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bKeep right\b", "Mantente a la derecha", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bKeep left\b", "Mantente a la izquierda", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bTurn right\b", "Gira a la derecha", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bTurn left\b", "Gira a la izquierda", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bAt roundabout, take exit (\d+)", r"En la rotonda, toma la salida \1", texto, flags=re.IGNORECASE)
    return texto

def seleccionar_transporte():
    while True:
        print("\nSeleccione tipo de transporte (o 's' para salir):")
        print("  1 - Auto")
        print("  2 - Bicicleta")
        print("  3 - Caminando")
        opcion = input("Opción: ").strip().lower()
        if opcion == "s":
            return None
        if opcion in TRANSPORTES:
            return TRANSPORTES[opcion]
        print("Opción inválida, intente de nuevo.")

def main():
    print("=== Calculadora de Rutas GraphHopper ===")
    while True:
        sel = seleccionar_transporte()
        if sel is None:
            break
        perfil_api, perfil_txt = sel

        origen = input("Ciudad de Origen (p.ej., Santiago, Chile) o 's' para salir: ").strip()
        if origen.lower() == "s":
            break
        lat_o, lng_o, nom_o = geocodificar(origen)
        if lat_o is None:
            continue

        destino = input("Ciudad de Destino (p.ej., Buenos Aires, Argentina) o 's' para salir: ").strip()
        if destino.lower() == "s":
            break
        lat_d, lng_d, nom_d = geocodificar(destino)
        if lat_d is None:
            continue

        resultado = calcular_ruta((lat_o, lng_o), (lat_d, lng_d), perfil_api)
        if not resultado or "paths" not in resultado:
            print("No se pudo obtener la ruta.")
            continue

        p = resultado["paths"][0]
        km = p["distance"] / 1000
        millas = km / 1.60934
        t_ms = p["time"]
        h = int(t_ms // (1000*60*60))
        m = int((t_ms // (1000*60)) % 60)
        s = int((t_ms // 1000) % 60)

        print("\n====== Resultado de la Ruta ======")
        print(f"Origen:     {nom_o}")
        print(f"Destino:    {nom_d}")
        print(f"Transporte: {perfil_txt}")
        print(f"Distancia:  {millas:.1f} millas / {km:.1f} km")
        print(f"Duración:   {h:02d}h:{m:02d}m:{s:02d}s")
        print("Indicaciones:")
        for instr in p["instructions"]:
            texto = traducir_indicacion(instr["text"])
            dkm = instr["distance"] / 1000
            print(f" • {texto} ({dkm:.1f} km)")
        print("==================================\n")

if __name__ == "__main__":
    main()