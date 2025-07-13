import requests
import json

# --- INGRESO DE DATOS ---

# 1. Pide la cadena de texto completa de las cookies.
COOKIE_STRING = input(
    "🍪 Pega aquí el valor completo de la cabecera 'Cookie' y presiona Enter:\n"
)

# 2. Pide el token CSRF.
CSRF_TOKEN = input(
    "🛡️  Pega aquí el valor de la cabecera 'x-csrf-token' y presiona Enter:\n"
)

if not COOKIE_STRING.strip() or not CSRF_TOKEN.strip():
    print("❌ Error: Debes ingresar ambos valores. El script se detendrá.")
else:
    base_url = "https://www.mercadopago.com.ar/activities/api/activities/list"

    # Cabeceras que simulan la solicitud del navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "application/json, text/plain, */*",
        "x-csrf-token": CSRF_TOKEN,
        "Cookie": COOKIE_STRING,
        "Referer": "https://www.mercadopago.com.ar/activities",
    }

    all_activities = []
    current_page = 1  # La paginación de Mercado Pago empieza en 1

    print("\n🔄 Iniciando la descarga de actividades de Mercado Pago...")

    try:
        while True:
            params = {
                "period": "last_week",  # Puedes cambiarlo a 'last_month', 'last_three_months', etc.
                "page": current_page,
                "listing": "activities",
                "useEmbeddings": "true",
            }

            print(f"    📄 Obteniendo página {current_page}...")

            response = requests.get(
                base_url, headers=headers, params=params, timeout=20
            )

            # Si el servidor responde con 401 o 403, las credenciales expiraron.
            if response.status_code in [401, 403]:
                print(
                    "\n🚨 ¡Error de autorización! Tus credenciales (cookie/token) han expirado."
                )
                print(
                    "Por favor, obtén valores nuevos desde Firefox y vuelve a ejecutar el script."
                )
                break

            response.raise_for_status()

            data = response.json()
            page_activities = data.get("results", [])

            # Si la página no devuelve resultados, hemos llegado al final.
            if not page_activities:
                print("    ✅ No se encontraron más actividades. Proceso finalizado.")
                break

            all_activities.extend(page_activities)
            current_page += 1

        if all_activities:
            file_name = "mercadopago_activities.json"
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(all_activities, f, ensure_ascii=False, indent=4)
            print(
                f"\n🎉 ¡Éxito! Se guardaron {len(all_activities)} actividades en el archivo '{file_name}'."
            )

    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")
