from database import get_connection

print("Antes de conectar")
conn = get_connection()
print("Conectado OK")
conn.close()
print("Fin")
