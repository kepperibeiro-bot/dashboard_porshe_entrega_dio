# Injeta data/vendas.json no template e gera index.html (arquivo unico)
from pathlib import Path
raiz = Path(__file__).resolve().parent.parent
tpl = (raiz / "scripts" / "template.html").read_text(encoding="utf-8")
dados = (raiz / "data" / "vendas.json").read_text(encoding="utf-8")
(raiz / "index.html").write_text(tpl.replace("/*__DADOS__*/[]", dados), encoding="utf-8")
print("index.html gerado")
