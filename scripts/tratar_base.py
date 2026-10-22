"""Prepara a base de vendas Porsche para a dashboard.

Uso: python scripts/tratar_base.py caminho/base_porshe.xlsx
Gera data/vendas_porsche_tratada.csv e data/vendas.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

ORIGEM = Path(sys.argv[1])
SAIDA = Path(__file__).resolve().parent.parent / "data"

COLUNAS = {
    "sale_id": "id_venda",
    "SaleDateSanitized": "data_venda",
    "PorscheModelSanitized": "modelo",
    "ModelYearSanitized": "ano_modelo",
    "SalesPriceSanitized": "preco_usd",
    "VehicleMileageSanitized": "quilometragem_mi",
    "PayMethodSanitized": "pagamento",
    "CitySanitized": "cidade",
    "StateSanitized": "estado",
    "DeliveryStatusSanitized": "status_entrega",
}

# Agrupa os 10 status em 4 etapas legiveis
ETAPA = {
    "Delivered": "Entregue",
    "In Transit": "Em transporte",
    "Shipped": "Em transporte",
    "Awaiting Delivery": "Em transporte",
    "Awaiting Pickup": "Em transporte",
    "Pending": "Pendente",
    "Pending Approval": "Pendente",
    "Pending Review": "Pendente",
    "Awaiting Review": "Pendente",
    "Cancelled": "Cancelada",
}

PAGAMENTO_PT = {
    "Wire Transfer": "Transferência bancária",
    "Bank Transfer": "Transferência bancária",
    "ACH Payment": "Transferência bancária",
    "Credit Card": "Cartão de crédito",
    "Debit Card": "Cartão de débito",
    "Financing": "Financiamento",
    "Lease": "Leasing",
    "Cash": "À vista (dinheiro)",
    "Crypto Payment": "Criptomoeda",
}

# 1. So as colunas sanitizadas (nome do cliente e vendedor ficam de fora)
df = pd.read_excel(ORIGEM, dtype=str)[list(COLUNAS)].rename(columns=COLUNAS)

# 2. Tipos numericos
df["id_venda"] = df["id_venda"].astype(int)
df["ano_modelo"] = pd.to_numeric(df["ano_modelo"], errors="coerce").astype("Int64")
df["preco_usd"] = pd.to_numeric(df["preco_usd"], errors="coerce")
df["quilometragem_mi"] = pd.to_numeric(df["quilometragem_mi"], errors="coerce").astype("Int64")

# 3. Datas INVALID viram vazio (a venda continua valendo, so sem data)
df["data_venda"] = pd.to_datetime(df["data_venda"], format="%Y-%m-%d", errors="coerce").dt.strftime("%Y-%m-%d")

# 4. Colunas derivadas para os filtros e graficos
df["familia"] = df["modelo"].str.split().str[0]
df["etapa_entrega"] = df["status_entrega"].map(ETAPA)
df["forma_pagamento"] = df["pagamento"].map(PAGAMENTO_PT)

assert df["etapa_entrega"].notna().all(), "status sem mapeamento"
assert df["forma_pagamento"].notna().all(), "pagamento sem mapeamento"

SAIDA.mkdir(exist_ok=True)
df.to_csv(SAIDA / "vendas_porsche_tratada.csv", index=False, encoding="utf-8")
registros = json.loads(df.to_json(orient="records", force_ascii=False))
(SAIDA / "vendas.json").write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")

print(f"{len(df)} vendas | {df['data_venda'].isna().sum()} sem data valida | "
      f"{df['preco_usd'].isna().sum()} sem preco")
print(df["familia"].value_counts().to_dict())
