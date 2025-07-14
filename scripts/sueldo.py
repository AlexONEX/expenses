# sueldo.py

"""
Script inteligente para registrar el sueldo.
- Modo Automático: Procesa los datos pasados como argumentos.
- Modo Interactivo: Guía al usuario si no se pasan argumentos.
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from datetime import datetime
import gnucash
from gnucash.gnucash_core import gnc_numeric_from_string, SessionOpenMode
from decimal import Decimal, ROUND_HALF_UP

import config
from gnucash_utils import parse_decimal, find_account_by_path

# Constante para el redondeo a 2 decimales
DOS_DECIMALES = Decimal("0.01")


def get_respuesta_si_no(pregunta):
    while True:
        respuesta = input(pregunta).lower().strip()
        if respuesta in ["s", "n"]:
            return respuesta
        print("Respuesta no válida. Por favor, introduce 's' o 'n'.")


def get_monto_usuario(pregunta):
    while True:
        try:
            monto_str = input(pregunta)
            return parse_decimal(monto_str)
        except ValueError as e:
            print(f"Error: {e}. Inténtalo de nuevo.")


def run_transaction_logic(sueldo_bruto, aguinaldo_bruto):
    session = None
    tx = None
    try:
        session = gnucash.Session(
            config.FILE_URI, mode=SessionOpenMode.SESSION_NORMAL_OPEN
        )
        book = session.get_book()
        root = book.get_root_account()
        cuentas = {
            key: find_account_by_path(root, path)
            for key, path in config.CUENTAS.items()
        }
        for key, cta in cuentas.items():
            if not cta:
                raise Exception(
                    f"FATAL: La cuenta '{key}' con ruta '{config.CUENTAS[key]}' no fue encontrada."
                )

        bruto_total = sueldo_bruto + aguinaldo_bruto

        tx = gnucash.Transaction(book)
        tx.BeginEdit()

        # --- CORRECCIÓN 2: Asignar la moneda a la transacción ---
        currency = book.get_table().lookup("ISO4217", config.MONEDA_PRINCIPAL)
        tx.SetCurrency(currency)

        tx.SetDate(datetime.now().day, datetime.now().month, datetime.now().year)
        tx.SetDescription(
            f"Sueldo {datetime.now().strftime('%B %Y')}{' con Aguinaldo' if aguinaldo_bruto > 0 else ''}"
        )

        # Splits de Ingresos (Créditos)
        split_ing_sueldo = gnucash.Split(book)
        split_ing_sueldo.SetParent(tx)
        split_ing_sueldo.SetAccount(cuentas["ingreso_sueldo"])
        split_ing_sueldo.SetValue(gnc_numeric_from_string(str(-sueldo_bruto)))

        if aguinaldo_bruto > 0:
            split_ing_agui = gnucash.Split(book)
            split_ing_agui.SetParent(tx)
            split_ing_agui.SetAccount(cuentas["ingreso_aguinaldo"])
            split_ing_agui.SetValue(gnc_numeric_from_string(str(-aguinaldo_bruto)))

        # Splits de Deducciones y Neto (Débitos)
        neto_calculado = bruto_total
        for d in config.DEDUCCIONES:
            monto_deduccion = Decimal("0")
            if d["tipo"] == "fijo":
                monto_deduccion = Decimal(str(d["valor"]))
            elif d["tipo"] == "porcentaje":
                # --- CORRECCIÓN 1: Redondear el cálculo ---
                monto_deduccion = (
                    bruto_total * (Decimal(str(d["valor"])) / Decimal("100"))
                ).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)

            split_deduccion = gnucash.Split(book)
            split_deduccion.SetParent(tx)
            split_deduccion.SetAccount(cuentas[d["cuenta_destino"]])
            split_deduccion.SetValue(gnc_numeric_from_string(str(monto_deduccion)))
            neto_calculado -= monto_deduccion

        # --- CORRECCIÓN 1: Redondear el neto final ---
        neto_calculado = neto_calculado.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)

        split_neto_banco = gnucash.Split(book)
        split_neto_banco.SetParent(tx)
        split_neto_banco.SetAccount(cuentas["banco_sueldo"])
        split_neto_banco.SetValue(gnc_numeric_from_string(str(neto_calculado)))

        tx.CommitEdit()
        print("\n\033[92m¡ÉXITO! Recibo de sueldo registrado correctamente.\033[0m")
        print(f"  - Sueldo Bruto: ${sueldo_bruto:,.2f}")
        if aguinaldo_bruto > 0:
            print(f"  - Aguinaldo Bruto: ${aguinaldo_bruto:,.2f}")
        print(f"  - Neto a Banco (Calculado): ${neto_calculado:,.2f}")

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


def main():
    num_args = len(sys.argv)
    if num_args > 1:
        try:
            if num_args == 2:
                print("--- Modo Automático: Sueldo Normal ---")
                sueldo_bruto = parse_decimal(sys.argv[1])
                aguinaldo_bruto = Decimal("0")
                run_transaction_logic(sueldo_bruto, aguinaldo_bruto)
            elif num_args == 3:
                print("--- Modo Automático: Sueldo + Aguinaldo ---")
                neto_recibido = parse_decimal(sys.argv[1])
                base_aguinaldo = parse_decimal(sys.argv[2])
                deducciones_fijas = sum(
                    Decimal(str(d["valor"]))
                    for d in config.DEDUCCIONES
                    if d["tipo"] == "fijo"
                )
                porcentaje_deducciones = sum(
                    Decimal(str(d["valor"]))
                    for d in config.DEDUCCIONES
                    if d["tipo"] == "porcentaje"
                ) / Decimal("100")
                bruto_total = (neto_recibido + deducciones_fijas) / (
                    Decimal("1") - porcentaje_deducciones
                )

                # --- CORRECCIÓN 1: Redondear todos los cálculos iniciales ---
                aguinaldo_bruto = (
                    base_aguinaldo
                    * (Decimal(str(config.PORCENTAJE_AGUINALDO)) / Decimal("100"))
                ).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
                sueldo_bruto = (bruto_total - aguinaldo_bruto).quantize(
                    DOS_DECIMALES, rounding=ROUND_HALF_UP
                )

                run_transaction_logic(sueldo_bruto, aguinaldo_bruto)
            else:
                print("Error: Número incorrecto de argumentos.")
                sys.exit(1)
        except (ValueError, IndexError) as e:
            print(f"Error en los argumentos: {e}")
            sys.exit(1)
    else:
        # El modo interactivo sigue la misma lógica de redondeo
        mes_actual = datetime.now().month
        es_mes_aguinaldo = mes_actual in [6, 7, 12]
        registrar_con_aguinaldo = False
        if es_mes_aguinaldo:
            respuesta = get_respuesta_si_no(
                "¿El sueldo a registrar incluye aguinaldo? (s/n): "
            )
            registrar_con_aguinaldo = respuesta == "s"
        if registrar_con_aguinaldo:
            neto_recibido = get_monto_usuario(
                "Introduce el MONTO NETO TOTAL que recibiste: "
            )
            base_aguinaldo = get_monto_usuario(
                "Introduce el MEJOR SUELDO BRUTO del semestre: "
            )
            deducciones_fijas = sum(
                Decimal(str(d["valor"]))
                for d in config.DEDUCCIONES
                if d["tipo"] == "fijo"
            )
            porcentaje_deducciones = sum(
                Decimal(str(d["valor"]))
                for d in config.DEDUCCIONES
                if d["tipo"] == "porcentaje"
            ) / Decimal("100")
            bruto_total = (neto_recibido + deducciones_fijas) / (
                Decimal("1") - porcentaje_deducciones
            )
            aguinaldo_bruto = (
                base_aguinaldo
                * (Decimal(str(config.PORCENTAJE_AGUINALDO)) / Decimal("100"))
            ).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
            sueldo_bruto = (bruto_total - aguinaldo_bruto).quantize(
                DOS_DECIMALES, rounding=ROUND_HALF_UP
            )
            run_transaction_logic(sueldo_bruto, aguinaldo_bruto)
        else:
            sueldo_bruto = get_monto_usuario("Introduce el MONTO BRUTO de tu sueldo: ")
            aguinaldo_bruto = Decimal("0")
            run_transaction_logic(sueldo_bruto, aguinaldo_bruto)


if __name__ == "__main__":
    main()
