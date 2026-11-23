# -*- coding: utf-8 -*-
"""Confere uma planilha de saída e compara com a saída de referência. Não chama o modelo e não tem custo.

Uso (a partir da pasta Demonstração):
  python conferir_saida.py                          # confere 4_saida/minha_saida.csv
  python conferir_saida.py 4_saida/outra_saida.csv  # confere outro arquivo

O que confere:
  1. colunas esperadas; um anúncio por linha; todos os códigos existem no banco;
  2. cada linha contra 3_schema_json/schema_saida.json (opções de vaga_ti, campos preenchidos);
  3. quanto a saída concorda com 4_saida/saida_classificacao_1000.csv (a rodada de agosto de 2026).
A referência NÃO é gabarito: é só outra rodada do mesmo modelo. Diferença pequena é esperada.
"""
import json
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
SCHEMA = json.loads((PASTA / "3_schema_json" / "schema_saida.json").read_text(encoding="utf-8"))
COLUNAS = ["vacancy_id", "vaga_ti", "justificativa_ti", "skills", "temas", "tokens_in", "tokens_out", "erro"]


def lista(s):
    return {x.strip().lower() for x in str(s).split(";") if x.strip()}


def main(arq):
    banco = pd.read_csv(PASTA / "1_banco_de_dados" / "vagas_amostra_1000.csv", dtype=str).fillna("")
    ref = pd.read_csv(PASTA / "4_saida" / "saida_classificacao_1000.csv", dtype=str).fillna("")
    if not Path(arq).exists():
        sys.exit(f"Não achei {arq}. Rode primeiro o script de classificação, ou informe o arquivo a conferir.")
    s = pd.read_csv(arq, dtype=str).fillna("")
    problemas = []
    faltam = [c for c in COLUNAS if c not in s.columns]
    if faltam:
        sys.exit(f"PROBLEMA: faltam colunas na saída: {faltam}")
    if not s.vacancy_id.is_unique:
        problemas.append(f"{s.vacancy_id.duplicated().sum()} anúncios repetidos")
    fora = set(s.vacancy_id) - set(banco.vacancy_id)
    if fora:
        problemas.append(f"{len(fora)} códigos que não estão no banco")
    ok = s[s.erro == ""]
    opcoes = SCHEMA["properties"]["vaga_ti"]["enum"]
    ruins = ok[~ok.vaga_ti.isin(opcoes)]
    if len(ruins):
        problemas.append(f"{len(ruins)} linhas com vaga_ti fora de {opcoes}: {sorted(set(ruins.vaga_ti))[:5]}")
    print(f"arquivo: {arq}")
    print(f"anúncios no banco: {len(banco)} | na saída: {len(s)} | sem erro: {len(ok)} | com erro: {(s.erro != '').sum()} | "
          f"ainda não classificados: {len(set(banco.vacancy_id) - set(ok.vacancy_id))}")
    print("vaga_ti:", ok.vaga_ti.value_counts().to_dict())
    print(f"com skills: {(ok.skills != '').sum()} | com temas: {(ok.temas != '').sum()} | "
          f"sem justificativa: {(ok.justificativa_ti == '').sum()}")
    m = ok.merge(ref, on="vacancy_id", suffixes=("", "_ref"))
    if len(m):
        igual = (m.vaga_ti == m.vaga_ti_ref).mean()
        jac = [len(lista(a) & lista(b)) / len(lista(a) | lista(b)) if lista(a) | lista(b) else 1.0
               for a, b in zip(m.skills, m.skills_ref)]
        print(f"\ncomparação com a rodada de referência ({len(m)} anúncios em comum):")
        print(f"  mesma resposta em vaga_ti: {igual:.1%}")
        print(f"  semelhança média das listas de skills (0 a 1): {sum(jac) / len(jac):.2f}")
        dif = m[m.vaga_ti != m.vaga_ti_ref][["vacancy_id", "title", "vaga_ti", "vaga_ti_ref"]]
        if len(dif):
            print("  anúncios em que vaga_ti mudou (até 10):")
            print(dif.head(10).to_string(index=False))
    print("\n" + ("PROBLEMAS: " + "; ".join(problemas) if problemas else "formato conferido: sem problemas"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(PASTA / "4_saida" / "minha_saida.csv"))
