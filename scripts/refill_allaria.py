# recargar_allaria.py
"""
Script AUTOMÁTICO para la recarga mensual de la tarjeta Allaria.
- Reinicia el saldo existente (lo pasa a una cuenta de gastos de ajuste).
- Pide únicamente el nuevo monto a cargar.
- Fija la fecha al día 12 del mes actual.
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from datetime import datetime
from decimal import Decimal
import gnucash
from gnucash.gnucash_core import gnc_numeric_from_string, SessionOpenMode

import config
from gnucash_utils import parse_decimal, find_account_by_path

# --- CONFIGURACIÓN DE CUENTAS ---
# Rutas de las cuentas que usará el script. ¡No necesitas escribirlas cada vez!
CUENTA_ACTIVO_ALLARIA = "Activos.Activo Corriente.Cuenta Corriente.Tarjeta Allaria"
CUENTA_INGRESO_ALLARIA = "Ingresos.Adicionales.Allaria.Tarjeta Corporativa"
CUENTA_AJUSTE_GASTO = "Gastos.Ajustes.Tarjeta Allaria+"


def main():
    session = None
    try:
        # --- 1. Conexión con GnuCash ---
        session = gnucash.Session(
            config.FILE_URI, mode=SessionOpenMode.SESSION_NORMAL_OPEN
        )
        book = session.get_book()
        root = book.get_root_account()
        currency = book.get_table().lookup("ISO4217", config.MONEDA_PRINCIPAL)

        # --- 2. Buscar las cuentas necesarias ---
        cta_activo_allaria = find_account_by_path(root, CUENTA_ACTIVO_ALLARIA)
        cta_ingreso_allaria = find_account_by_path(root, CUENTA_INGRESO_ALLARIA)
        cta_ajuste_gasto = find_account_by_path(root, CUENTA_AJUSTE_GASTO)

        if not all([cta_activo_allaria, cta_ingreso_allaria, cta_ajuste_gasto]):
            print(
                "\033[91mERROR: Una o más cuentas no fueron encontradas. Verifica las rutas en el script.\033[0m"
            )
            return

        # --- 3. Ajuste del saldo remanente (la magia de "pisar" el dinero) ---
        saldo_actual_gnc = cta_activo_allaria.GetBalance()
        saldo_actual = Decimal(saldo_actual_gnc.to_string()) / Decimal(
            "100.0"
        )  # GnuCash guarda valores como enteros

        fecha_recarga = datetime.now().replace(day=12)

        if saldo_actual > 0:
            print(f"Detectado un saldo remanente de ${saldo_actual:,.2f}.")
            print("Creando transacción de ajuste para poner el saldo en cero...")

            tx_ajuste = gnucash.Transaction(book)
            tx_ajuste.BeginEdit()
            tx_ajuste.SetCurrency(currency)
            tx_ajuste.SetDate(
                fecha_recarga.day, fecha_recarga.month, fecha_recarga.year
            )
            tx_ajuste.SetDescription(
                "Ajuste por saldo no acumulable de beneficio corporativo"
            )

            # Origen: Sale dinero del activo (crédito)
            split1 = gnucash.Split(book)
            split1.SetParent(tx_ajuste)
            split1.SetAccount(cta_activo_allaria)
            split1.SetValue(saldo_actual_gnc.neg())  # Negativo

            # Destino: Se registra como un gasto (débito)
            split2 = gnucash.Split(book)
            split2.SetParent(tx_ajuste)
            split2.SetAccount(cta_ajuste_gasto)
            split2.SetValue(saldo_actual_gnc)  # Positivo

            tx_ajuste.CommitEdit()
            print("\033[92m¡Ajuste completado!\033[0m")

        # --- 4. Pedir el nuevo monto y crear la transacción de recarga ---
        print("\n--- RECARGA MENSUAL ALLARIA ---")
        monto_str = input(
            f"Introduce el NUEVO MONTO para la recarga del {fecha_recarga.strftime('%d/%m/%Y')}: "
        )
        monto_recarga = parse_decimal(monto_str)
        monto_recarga_gnc = gnc_numeric_from_string(str(monto_recarga))

        tx_recarga = gnucash.Transaction(book)
        tx_recarga.BeginEdit()
        tx_recarga.SetCurrency(currency)
        tx_recarga.SetDate(fecha_recarga.day, fecha_recarga.month, fecha_recarga.year)
        tx_recarga.SetDescription("Recarga mensual de beneficios corporativos")

        # Origen: El ingreso (crédito)
        split1_recarga = gnucash.Split(book)
        split1_recarga.SetParent(tx_recarga)
        split1_recarga.SetAccount(cta_ingreso_allaria)
        split1_recarga.SetValue(monto_recarga_gnc.neg())  # Negativo

        # Destino: El dinero va al activo (débito)
        split2_recarga = gnucash.Split(book)
        split2_recarga.SetParent(tx_recarga)
        split2_recarga.SetAccount(cta_activo_allaria)
        split2_recarga.SetValue(monto_recarga_gnc)  # Positivo

        tx_recarga.CommitEdit()

        print("\n\033[92m¡ÉXITO! Recarga registrada correctamente.\033[0m")
        print(
            f"El nuevo saldo de la '{CUENTA_ACTIVO_ALLARIA}' es de ${monto_recarga:,.2f}."
        )

    except Exception as e:
        print(f"\n\033[91mERROR INESPERADO: {e}\033[0m")
    finally:
        if session:
            session.save()
            session.end()
            print("\nLibro guardado y sesión cerrada.")


if __name__ == "__main__":
    main()
