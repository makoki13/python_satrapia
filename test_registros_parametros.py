# test_registro_parametros.py
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro

print(f"✅ Registro cargado: {len(REGISTRO_PARAMETROS)} parámetros")

for _,param in sorted(REGISTRO_PARAMETROS.items()):
    print(f"   {param}")

# Verificar acceso seguro
try:
    p = get_parametro("prod_comida_granja")
    print(f"\n✅ Acceso OK: {p.nombre} → max={p.valor_maximo}, ini={p.porcentaje_inicial:.0%}")
except KeyError as e:
    print(f"❌ Error: {e}")

# Verificar que un lógico funciona
logico = get_parametro("pesca_aguas_profundas")
assert logico.es_logico
assert logico.valor_maximo == 1.0
print(f"✅ Lógico validado: {logico.nombre}")
