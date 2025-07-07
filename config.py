# --- CONFIGURACIÓN GENERAL ---
FILE_URI = "file:///home/mars/OneDrive/Backups/GnuCash/tracking/patrimonio.gnucash"
MONEDA_PRINCIPAL = "ARS"


# --- PARÁMETROS DE CÁLCULO (Para el script de sueldo) ---
PORCENTAJE_AGUINALDO = 50.0  # 50%


# --- PLAN DE CUENTAS COMPLETO ---
# Mapeo de una clave corta y memorable a la ruta completa de la cuenta en GnuCash.
# Usa el punto '.' como separador.
CUENTAS = {
    # ==================================================================
    # --- ACTIVOS ---
    # ==================================================================
    # Activo Corriente
    "activo_banco_bbva": "Activos.Activo Corriente.Caja de Ahorro.BBVA",
    "activo_banco_gali_ars": "Activos.Activo Corriente.Caja de Ahorro.Galicia (ARS)",
    "activo_banco_gali_usd": "Activos.Activo Corriente.Caja de Ahorro.Galicia (USD)",
    "activo_efectivo_ars": "Activos.Activo Corriente.Caja.Efectivo (ARS)",
    "activo_efectivo_usd": "Activos.Activo Corriente.Caja.Efecitvo (USD)",  # Ojo: "Efecitvo" como en tu libro
    "activo_mp": "Activos.Activo Corriente.Money Market.MP",
    "activo_tarjeta_allaria": "Activos.Activo Corriente.Cuenta Corriente.Tarjeta Allaria",
    # Activos de Inversión
    "activo_inv_wallet_ars": "Activos.Inversiones.Brokerage Accounts.Electronic Wallet App (AR)",
    "activo_inv_wallet_usd": "Activos.Inversiones.Brokerage Accounts.Electronic Wallet App (US)",
    "activo_inv_ieb_ars": "Activos.Inversiones.Brokerage Accounts.IEB (ARS)",
    "activo_inv_ieb_usd": "Activos.Inversiones.Brokerage Accounts.IEB (USD)",
    # Activos - Cuentas por Cobrar
    "activo_cobrar_amigos": "Activos.Cuentas por Cobrar.Amigos",
    # ==================================================================
    # --- PASIVOS (Deudas y Tarjetas de Crédito) ---
    # ==================================================================
    "pasivo_tc_gali_master_ars": "Pasivo.Tarjeta de Crédito.Galicia Mastercard.Mastercard Credito (ARS)",
    "pasivo_tc_gali_master_usd": "Pasivo.Tarjeta de Crédito.Galicia Mastercard.Mastercard Credito (USD)",
    "pasivo_tc_gali_visa_ars": "Pasivo.Tarjeta de Crédito.Galicia Visa.Visa Credito (ARS)",
    "pasivo_tc_gali_visa_usd": "Pasivo.Tarjeta de Crédito.Galicia Visa.Visa Credito (USD)",
    "pasivo_prestamo_allaria": "Pasivo.Prestamos.Allaria",
    # ==================================================================
    # --- PATRIMONIO ---
    # ==================================================================
    "patrimonio_apertura_ars": "Patrimonio.Opening Balance (ARS)",
    "patrimonio_apertura_usd": "Patrimonio.Opening Balance (USD)",
    # ==================================================================
    # --- INGRESOS ---
    # ==================================================================
    "ing_sueldo": "Ingresos.Sueldo.Allaria",
    "ing_aguinaldo": "Ingresos.Sueldo.Allaria",
    "ing_adicionales": "Ingresos.Adicionales",
    "ing_dividendos": "Ingresos.Ingresos por dividendos",
    "ing_intereses": "Ingresos.Ingresos por intereses",
    "ing_intereses_ganados": "Ingresos.Intereses Ganados",
    "ing_otros_ars": "Ingresos.Otros Ingresos (ARS)",
    "ing_otros_usd": "Ingresos.Otros Ingresos (USD)",
    "ing_regalos": "Ingresos.Regalos",
    # ==================================================================
    # --- GASTOS ---
    # ==================================================================
    "gasto_ajustes": "Gastos.Ajustes",
    "gasto_alimentos": "Gastos.Alimentos y bebidas no alcohólicas",
    "gasto_alcohol_tabaco": "Gastos.Bebidas alcohólicas y tabaco",
    "gasto_bienes_servicios": "Gastos.Bienes y servicios varios",
    "gasto_comisiones": "Gastos.Comisiones",
    "gasto_comunicacion": "Gastos.Comunicacion",
    "gasto_deudas_incobrables": "Gastos.Deudas Incobrables",
    "gasto_educacion": "Gastos.Educación",
    "gasto_hogar": "Gastos.Equipamiento y mantenimiento del hogar",
    "gasto_inversiones": "Gastos.Inversiones",
    "gasto_ropa_calzado": "Gastos.Prendas de Vestir y Calzado",
    "gasto_prestamos": "Gastos.Prestamos",
    "gasto_recreacion": "Gastos.Recreación y cultura",
    "gasto_regalos": "Gastos.Regalos",
    "gasto_restaurantes_hoteles": "Gastos.Restaurantes y Hoteles",
    "gasto_rodados": "Gastos.Rodados",
    "gasto_seguros": "Gastos.Seguros",
    "gasto_transporte": "Gastos.Transporte",
    "gasto_vivienda_servicios": "Gastos.Vivienda, agua, electricidad, gas y otros combustibles",
    # Gastos de Impuestos (incluye deducciones de sueldo)
    "gasto_impuestos": "Gastos.Impuestos",
    "gasto_imp_jubilacion": "Gastos.Impuestos.Jubilacion",
    "gasto_imp_ley19032": "Gastos.Impuestos.Ley 19032",
    "gasto_imp_obrasocial": "Gastos.Salud.Obra Social",  # Nota: Lo moví a Salud en el config anterior, pero lo dejo aquí también si lo usas en Impuestos
    "gasto_redondeo": "Gastos.Redondeo",
}


# --- REGLAS DE DEDUCCIONES DEL SUELDO (Usa las claves de arriba) ---
DEDUCCIONES = [
    {
        "nombre": "Jubilacion",
        "tipo": "porcentaje",
        "valor": 11.0,
        "cuenta_destino": "gasto_imp_jubilacion",
    },
    {
        "nombre": "Ley 19032",
        "tipo": "porcentaje",
        "valor": 3.0,
        "cuenta_destino": "gasto_imp_ley19032",
    },
    {
        "nombre": "Obra Social",
        "tipo": "porcentaje",
        "valor": 3.0,
        "cuenta_destino": "gasto_imp_obrasocial",
    },
    {
        "nombre": "Descuento Prestamo",
        "tipo": "fijo",
        "valor": 17470.00,
        "cuenta_destino": "pasivo_prestamo_allaria",
    },
    {
        "nombre": "Redondeo",
        "tipo": "fijo",
        "valor": 0.67,
        "cuenta_destino": "gasto_redondeo",
    },
]
