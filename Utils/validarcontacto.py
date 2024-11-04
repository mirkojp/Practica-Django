import re

def validar_contacto(contacto):
    # Comprobamos si el número ya comienza con +15 y tiene la longitud completa (14 caracteres)
    if re.fullmatch(r"\+15\d{11}", contacto):
        return contacto

    # Comprobamos si el número comienza con un 0 y tiene la longitud de 11 dígitos sin +15
    elif re.fullmatch(r"0\d{10}", contacto):
        return f"+15{contacto}"

    # Si no cumple con ningún formato válido, retornamos un mensaje de error
    else:
        raise ValueError("Número de contacto no válido. Debe ser +15 seguido del código de área de 5 dígitos y el número de 6 dígitos.")
    
print(validar_contacto("03445470994"))