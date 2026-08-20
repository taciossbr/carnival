from pathlib import Path
import re
import sys


INCLUDE = re.compile(
    r'^[ \t]*(?:'
    r'<!--\s*#include\s+(.+?)\s*-->|'
    r'/\*\s*#include\s+(.+?)\s*\*/|'
    r'//\s*#include\s+(.+?)\s*|'
    r'\#\s*#include\s+(.+?)\s*'
    r')[ \t]*$',
    re.MULTILINE
)


def build(path, root):
    path = Path(path)

    text = path.read_text(
        encoding="utf-8"
    )

    def replace(match):

        filename = next(
            group
            for group in match.groups()
            if group is not None
        ).strip()

        included = root / filename

        if not included.exists():
            raise FileNotFoundError(
                f"Include não encontrado: "
                f"{filename}\n"
                f"Referenciado por: {path}"
            )

        return build(
            included,
            root
        )

    return INCLUDE.sub(
        replace,
        text
    )


source = Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else "app/index.html"
)

output = Path(
    sys.argv[2]
    if len(sys.argv) > 2
    else "dist/tool.html"
)

source = source.resolve()
output = output.resolve()

# A raiz é o diretório do arquivo de entrada.
root = source.parent


output.parent.mkdir(
    parents=True,
    exist_ok=True
)

output.write_text(
    build(source, root),
    encoding="utf-8"
)

print(
    f"{source} -> {output}"
)