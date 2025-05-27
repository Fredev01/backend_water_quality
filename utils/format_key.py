import sys


def escape_newlines(text: str) -> str:
    return text.replace("\n", "\\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python escape_key.py '<string_con_saltos>'")
        sys.exit(1)

    raw_input = sys.argv[1]
    escaped = escape_newlines(raw_input)
    # Para mostrar la salida de forma literal sin que el print la interprete
    print(repr(escaped)[1:-1])
