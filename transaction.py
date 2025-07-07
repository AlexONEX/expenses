# transaction.py

"""
Script INTERACTIVO para registrar transacciones.
Al ejecutarlo, muestra una lista de cuentas y luego pide los datos,
incluyendo una fecha opcional.
"""

from datetime import datetime
import gnucash
from gnucash.gnucash_core import gnc_numeric_from_string, SessionOpenMode

# --- Importaciones del sistema propio ---
import config
from gnucash_utils import parse_decimal, find_account_by_path


def listar_cuentas(root_account):
    """Imprime una lista legible de todas las cuentas para el usuario."""
    print("\n\033[94m--- LISTA DE CUENTAS DISPONIBLES ---\033[0m")
    print("Copia y pega la ruta completa de la cuenta que necesites.\n")

    cuentas_list = []

    def collect_accounts(account):
        # Recolecta recursivamente los nombres completos de las cuentas
        if not account.is_root():
            cuentas_list.append(account.get_full_name())
        for child in account.get_children():
            collect_accounts(child)

    collect_accounts(root_account)
    cuentas_list.sort()  # Ordenar alfabéticamente para fácil búsqueda
    for nombre_completo in cuentas_list:
        print(f"  {nombre_completo}")

    print("\n\033[94m-------------------------------------\033[0m\n")


def main():
    session = None
    tx = None
    try:
        session = gnucash.Session(
            config.FILE_URI, mode=SessionOpenMode.SESSION_NORMAL_OPEN
        )
        book = session.get_book()
        root = book.get_root_account()

        # 1. Mostrar la lista de cuentas al usuario
        listar_cuentas(root)

        # 2. Pedir los datos de forma interactiva
        print("--- NUEVA TRANSACCIÓN ---")

        # --- NUEVO: Pedir la fecha ---
        fecha_str = input("Introduce la FECHA (DD/MM/AAAA) o deja en blanco para hoy: ")

        monto_str = input("Introduce el MONTO: ")
        ruta_origen = input(
            "Introduce la ruta COMPLETA de la cuenta de ORIGEN (de donde sale el dinero): "
        )
        ruta_destino = input(
            "Introduce la ruta COMPLETA de la cuenta de DESTINO (a donde va el dinero): "
        )
        descripcion = input("Introduce una DESCRIPCIÓN para la transacción: ")

        monto = parse_decimal(monto_str)

        # --- NUEVO: Procesar la fecha ---
        if fecha_str.strip():  # Si el usuario introdujo una fecha
            try:
                fecha_transaccion = datetime.strptime(fecha_str, "%d/%m/%Y")
            except ValueError:
                raise ValueError(
                    f"El formato de fecha '{fecha_str}' no es válido. Usa DD/MM/AAAA."
                )
        else:  # Si el usuario dejó el campo en blanco
            fecha_transaccion = datetime.now()

        # 3. Búsqueda y validación de cuentas
        cta_origen = find_account_by_path(root, ruta_origen)
        if not cta_origen:
            raise Exception(
                f"La cuenta de origen con ruta '{ruta_origen}' no fue encontrada."
            )

        cta_destino = find_account_by_path(root, ruta_destino)
        if not cta_destino:
            raise Exception(
                f"La cuenta de destino con ruta '{ruta_destino}' no fue encontrada."
            )

        # 4. Creación de la transacción
        tx = gnucash.Transaction(book)
        tx.BeginEdit()

        currency = book.get_table().lookup("ISO4217", config.MONEDA_PRINCIPAL)
        tx.SetCurrency(currency)

        # Usamos la fecha procesada
        tx.SetDate(
            fecha_transaccion.day, fecha_transaccion.month, fecha_transaccion.year
        )
        tx.SetDescription(descripcion)

        # Split 1: Origen (Crédito, negativo)
        split_origen = gnucash.Split(book)
        split_origen.SetParent(tx)
        split_origen.SetAccount(cta_origen)
        split_origen.SetValue(gnc_numeric_from_string(str(-monto)))

        # Split 2: Destino (Débito, positivo)
        split_destino = gnucash.Split(book)
        split_destino.SetParent(tx)
        split_destino.SetAccount(cta_destino)
        split_destino.SetValue(gnc_numeric_from_string(str(monto)))

        tx.CommitEdit()
        print("\n\033[92m¡ÉXITO! Transacción registrada correctamente.\033[0m")
        print(f"  - Fecha: {fecha_transaccion.strftime('%d/%m/%Y')}")
        print(f"  - Descripción: {descripcion}")
        print(f"  - Monto: ${monto:,.2f}")
        print(f"  - Origen: {ruta_origen}")
        print(f"  - Destino: {ruta_destino}")

    except Exception as e:
        print(f"\n\033[91mERROR: {e}\033[0m")
        if tx and tx.IsInEdit():
            tx.RollbackEdit()
            print("Se revirtieron los cambios en la transacción.")
    finally:
        if session:
            session.save()
            session.end()
            print("\nLibro guardado y sesión cerrada.")


if __name__ == "__main__":
    main()
