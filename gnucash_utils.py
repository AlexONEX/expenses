from decimal import Decimal, InvalidOperation


def parse_decimal(numero_str: str) -> Decimal:
    """
    Convierte una cadena de texto con formato numérico a un objeto Decimal.
    Maneja ',' y '.' como separadores de miles y decimales.
    """
    try:
        clean_str = numero_str.replace(".", "").replace(",", ".")
        if "," in numero_str:
            clean_str = numero_str.replace(".", "").replace(",", ".")
        else:  # Si no había comas, los puntos podrían ser miles o un decimal.
            clean_str = numero_str.replace(",", ".")

        # Un apaño final para el caso "1.234,56" vs "1,234.56"
        if clean_str.count(".") > 1:
            parts = clean_str.split(".")
            clean_str = "".join(parts[:-1]) + "." + parts[-1]

        return Decimal(clean_str)
    except InvalidOperation:
        raise ValueError(f"El formato del número '{numero_str}' no es válido.")


def find_account_by_path(root_account, path: str):
    """
    Busca una cuenta navegando manualmente a través del árbol de cuentas.
    'path' debe ser una cadena con nombres separados por puntos.
    """
    current_account = root_account
    for part in path.split("."):
        found_child = None
        for child in current_account.get_children():
            if child.GetName() == part:
                found_child = child
                break
        if found_child:
            current_account = found_child
        else:
            return None
    return current_account
