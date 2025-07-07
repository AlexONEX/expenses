"""
Script de procesamiento por lotes para registrar resúmenes completos
de tarjetas de crédito en GnuCash, con soporte para múltiples monedas.
"""

from datetime import datetime
import gnucash
from gnucash.gnucash_core import gnc_numeric_from_string, SessionOpenMode

import config
from gnucash_utils import parse_decimal, find_account_by_path

DATOS_VISA_GALICIA = [
    {
        "fecha": "20/05/2025",
        "desc": "MERPAGO*4PRODUCTOS",
        "monto": "19865.60",
        "destino": "Gastos.Bienes y servicios varios",
    },
    {
        "fecha": "01/06/2025",
        "desc": "PAYU*AR*UBER",
        "monto": "18540.00",
        "destino": "Gastos.Transporte.Uber",
    },
    {
        "fecha": "02/06/2025",
        "desc": "WWW.COTODIGITAL.COM.AR/SU",
        "monto": "130555.73",
        "destino": "Gastos.Alimentos y bebidas no alcohólicas",
    },
    {
        "fecha": "02/06/2025",
        "desc": "SUBSCRIBESTAR USD",
        "monto": "5.73",
        "destino": "Gastos.Bienes y servicios varios.Subscripciones",
        "moneda": "USD",
    },
    {
        "fecha": "05/06/2025",
        "desc": "Q GOOGLE *YouTubeP",
        "monto": "6799.00",
        "destino": "Gastos.Bienes y servicios varios.Subscripciones.Youtube",
    },
    {
        "fecha": "07/06/2025",
        "desc": "MERPAGO*CARREFOUR",
        "monto": "96299.00",
        "destino": "Gastos.Alimentos y bebidas no alcohólicas",
    },
    {
        "fecha": "08/06/2025",
        "desc": "PEDIDOSYA RESTAURANTE",
        "monto": "22494.00",
        "destino": "Gastos.Restaurantes y Hoteles.Restaurantes",
    },
    {
        "fecha": "08/06/2025",
        "desc": "PEDIDOSYA PROPINAS",
        "monto": "550.00",
        "destino": "Gastos.Restaurantes y Hoteles.Restaurantes",
    },
    {
        "fecha": "12/06/2025",
        "desc": "MERPAGO*3PRODUCTOS",
        "monto": "14517.90",
        "destino": "Gastos.Bienes y servicios varios",
    },
    {
        "fecha": "12/06/2025",
        "desc": "MERPAGO*3PRODUCTOS",
        "monto": "41507.29",
        "destino": "Gastos.Bienes y servicios varios",
    },
    {
        "fecha": "17/06/2025",
        "desc": "PAYU*AR*UBER",
        "monto": "13484.00",
        "destino": "Gastos.Transporte.Uber",
    },
    {
        "fecha": "18/06/2025",
        "desc": "DLO*Riot Games",
        "monto": "12786.58",
        "destino": "Gastos.Recreación y cultura",
    },
    {
        "fecha": "20/06/2025",
        "desc": "GRIDO-GRIDO MONROE",
        "monto": "8400.00",
        "destino": "Gastos.Alimentos y bebidas no alcohólicas",
    },
    {
        "fecha": "21/06/2025",
        "desc": "MERPAGO*LAFAROLADEURQUIZA",
        "monto": "84100.00",
        "destino": "Gastos.Restaurantes y Hoteles.Restaurantes",
    },
    {
        "fecha": "26/06/2025",
        "desc": "IIBB PERCEP-CABA 2,00%",
        "monto": "135.98",
        "destino": "Gastos.Impuestos.Impuestos Provinciales.IIGG CABA",
    },
    {
        "fecha": "26/06/2025",
        "desc": "IVA RG 4240 21%",
        "monto": "1427.79",
        "destino": "Gastos.Impuestos.IVA",
    },
    {
        "fecha": "26/06/2025",
        "desc": "DB.RG 5617 30%",
        "monto": "4087.88",
        "destino": "Gastos.Impuestos",
    },
]

DATOS_MASTERCARD_GALICIA = [
    {
        "fecha": "08/06/2025",
        "desc": "TUENTI RECARGAS DCP",
        "monto": "4650.00",
        "destino": "Gastos.Comunicacion.Tuenti",
    },
    {
        "fecha": "26/06/2025",
        "desc": "TUENTI RECARGAS DCP",
        "monto": "10300.00",
        "destino": "Gastos.Comunicacion.Tuenti",
    },
    {
        "fecha": "26/06/2025",
        "desc": "INTERESES DE FINANCIACION",
        "monto": "601.55",
        "destino": "Gastos.Comisiones",
    },
    {
        "fecha": "26/06/2025",
        "desc": "INTERESES COMPENSATORIOS",
        "monto": "0.02",
        "destino": "Gastos.Comisiones",
    },
    {
        "fecha": "26/06/2025",
        "desc": "IMPUESTO DE SELLOS",
        "monto": "8.49",
        "destino": "Gastos.Impuestos.Sellos",
    },
    {
        "fecha": "26/06/2025",
        "desc": "I.V.A. 21,0%",
        "monto": "126.33",
        "destino": "Gastos.Impuestos.IVA",
    },
]

# ==============================================================================


def registrar_lote(book, lote_de_datos, cuentas_origen):
    """Procesa una lista de transacciones para una tarjeta, manejando múltiples monedas."""
    print(
        f"\n\033[94m--- Procesando lote para: {list(cuentas_origen.values())[0].split('.')[-2]} ---\033[0m"
    )

    for item in lote_de_datos:
        tx = None  # Resetear tx para cada item
        try:
            monto = parse_decimal(item["monto"])
            fecha = datetime.strptime(item["fecha"], "%d/%m/%Y")
            ruta_destino = item["destino"]
            descripcion = item["desc"]
            moneda_str = item.get("moneda", "ARS")  # Asume ARS si no se especifica

            # --- Lógica Multi-moneda ---
            if moneda_str == "ARS":
                ruta_origen = cuentas_origen["ARS"]
            elif moneda_str == "USD":
                ruta_origen = cuentas_origen["USD"]
            else:
                raise Exception(f"Moneda '{moneda_str}' no soportada.")

            cta_origen = find_account_by_path(book.get_root_account(), ruta_origen)
            if not cta_origen:
                raise Exception(
                    f"La cuenta de pasivo '{ruta_origen}' no fue encontrada."
                )

            cta_destino = find_account_by_path(book.get_root_account(), ruta_destino)
            if not cta_destino:
                raise Exception(
                    f"La cuenta de gasto '{ruta_destino}' no fue encontrada."
                )

            tx = gnucash.Transaction(book)
            tx.BeginEdit()

            currency = book.get_table().lookup("ISO4217", moneda_str)
            tx.SetCurrency(currency)

            tx.SetDate(fecha.day, fecha.month, fecha.year)
            tx.SetDescription(descripcion)

            split_origen = gnucash.Split(book)
            split_origen.SetParent(tx)
            split_origen.SetAccount(cta_origen)
            split_origen.SetValue(gnc_numeric_from_string(str(-monto)))

            split_destino = gnucash.Split(book)
            split_destino.SetParent(tx)
            split_destino.SetAccount(cta_destino)
            split_destino.SetValue(gnc_numeric_from_string(str(monto)))

            tx.CommitEdit()
            print(
                f"  \033[92m[OK]\033[0m {fecha.strftime('%d/%m/%Y')}: {descripcion} - {moneda_str} ${monto:,.2f}"
            )

        except Exception as e:
            print(f"  \033[91m[ERROR]\033[0m Procesando '{item.get('desc')}': {e}")
            if tx and tx.IsInEdit():
                tx.RollbackEdit()


def main():
    session = None
    try:
        session = gnucash.Session(
            config.FILE_URI, mode=SessionOpenMode.SESSION_NORMAL_OPEN
        )
        book = session.get_book()

        # Definir las cuentas de pasivo para cada tarjeta
        cuentas_visa = {
            "ARS": "Pasivo.Tarjeta de Crédito.Galicia Visa.Visa Credito (ARS)",
            "USD": "Pasivo.Tarjeta de Crédito.Galicia Visa.Visa Credito (USD)",
        }
        cuentas_master = {
            "ARS": "Pasivo.Tarjeta de Crédito.Galicia Mastercard.Mastercard Credito (ARS)",
            "USD": "Pasivo.Tarjeta de Crédito.Galicia Mastercard.Mastercard Credito (USD)",
        }

        # Procesar cada resumen
        registrar_lote(book, DATOS_VISA_GALICIA, cuentas_visa)
        registrar_lote(book, DATOS_MASTERCARD_GALICIA, cuentas_master)

        print("\n\033[92mProceso de registro de resúmenes finalizado.\033[0m")

    except Exception as e:
        print(f"\n\033[91mERROR CRÍTICO: {e}\033[0m")
    finally:
        if session:
            session.save()
            session.end()
            print("\nLibro guardado y sesión cerrada.")


if __name__ == "__main__":
    main()
