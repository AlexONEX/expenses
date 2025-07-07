import sys
from datetime import datetime
import gnucash
from gnucash.gnucash_core import gnc_numeric_from_string, SessionOpenMode
from decimal import Decimal, ROUND_HALF_UP

import config
from gnucash_utils import parse_decimal, find_account_by_path


def main():
    if len(sys.argv) not in [2, 3]:
        print(
            f"Uso: python3 {sys.argv[0]} <monto_neto_recibido> [sueldo_bruto_base_para_aguinaldo]"
        )
        print(f'Ejemplo: python3 {sys.argv[0]} "2265985.00" "1834099.20"')
        sys.exit(1)

    # --- Parseo de Argumentos ---
    try:
        neto_recibido = parse_decimal(sys.argv[1])
        base_aguinaldo = parse_decimal(sys.argv[2]) if len(sys.argv) == 3 else None
    except ValueError as e:
        print(f"Error de formato: {e}")
        sys.exit(1)

    # --- Estimación de Brutos ---
    deducciones_fijas = sum(
        Decimal(str(d["valor"])) for d in config.DEDUCCIONES if d["tipo"] == "fijo"
    )
    porcentaje_deducciones = sum(
        Decimal(str(d["valor"]))
        for d in config.DEDUCCIONES
        if d["tipo"] == "porcentaje"
    ) / Decimal("100")

    bruto_total_estimado = (neto_recibido + deducciones_fijas) / (
        Decimal("1") - porcentaje_deducciones
    )

    if base_aguinaldo:
        aguinaldo_bruto_estimado = (base_aguinaldo / Decimal("2")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        sueldo_bruto_estimado = bruto_total_estimado - aguinaldo_bruto_estimado
    else:
        # Si no se provee base, se asume que 1/3 del bruto es aguinaldo (aproximación)
        aguinaldo_bruto_estimado = (bruto_total_estimado / Decimal("3")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        sueldo_bruto_estimado = bruto_total_estimado - aguinaldo_bruto_estimado

    # --- Interacción con GnuCash ---
    session = None
    try:
        session = gnucash.Session(
            config.FILE_URI, mode=SessionOpenMode.SESSION_NORMAL_OPEN
        )
        book = session.get_book()
        root = book.get_root_account()

        cuentas_gnucash = {
            key: find_account_by_path(root, path)
            for key, path in config.CUENTAS.items()
        }
        for key, cta in cuentas_gnucash.items():
            if not cta:
                raise Exception(f"FATAL: La cuenta para '{key}' no fue encontrada.")

        tx = gnucash.Transaction(book)
        tx.BeginEdit()
        tx.SetDate(datetime.now().day, datetime.now().month, datetime.now().year)
        tx.SetDescription(f"Sueldo y Aguinaldo {datetime.now().strftime('%B %Y')}")

        # --- Splits de Ingresos (Créditos, negativos) ---
        tx.CreateSplit(
            cuentas_gnucash["ingreso_sueldo"],
            gnc_numeric_from_string(str(-sueldo_bruto_estimado)),
        )
        tx.CreateSplit(
            cuentas_gnucash["ingreso_aguinaldo"],
            gnc_numeric_from_string(str(-aguinaldo_bruto_estimado)),
        )

        # --- Splits de Débitos (Positivos) ---
        tx.CreateSplit(
            cuentas_gnucash["banco_sueldo"], gnc_numeric_from_string(str(neto_recibido))
        )

        for d in config.DEDUCCIONES:
            if d["tipo"] == "fijo":
                monto = Decimal(str(d["valor"]))
            else:  # porcentaje
                monto = bruto_total_estimado * (
                    Decimal(str(d["valor"])) / Decimal("100")
                )

            tx.CreateSplit(
                cuentas_gnucash[d["cuenta_destino"]],
                gnc_numeric_from_string(str(monto)),
            )

        tx.CommitEdit()
        print("\n¡ÉXITO! Sueldo y aguinaldo registrados correctamente.")
        print(f"  - Sueldo Bruto (Estimado): ${sueldo_bruto_estimado:,.2f}")
        print(f"  - Aguinaldo Bruto (Estimado): ${aguinaldo_bruto_estimado:,.2f}")
        print(f"  - Neto Recibido en Banco: ${neto_recibido:,.2f}")

    except Exception as e:
        print(f"\nERROR: {e}")
        if "tx" in locals() and tx.is_in_edit():
            tx.RollbackEdit()
    finally:
        if session:
            session.save()
            session.end()
            print("\nLibro guardado y sesión cerrada.")


if __name__ == "__main__":
    main()
