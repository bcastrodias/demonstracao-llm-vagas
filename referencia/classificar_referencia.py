# -*- coding: utf-8 -*-
"""Script de REFERÊNCIA (gabarito do workshop): classifica os anúncios com o modelo de linguagem.

Nada do que define a tarefa está escrito aqui dentro. O script lê tudo dos arquivos da pasta:
  1_banco_de_dados/vagas_amostra_1000.csv   os anúncios
  2_prompt/prompt_sistema.txt               mensagem de sistema (as regras)
  2_prompt/modelo_mensagem_usuario.txt      molde da mensagem do usuário; {coluna} = coluna do banco
  3_schema_json/schema_saida.json           formato obrigatório da resposta
  configuracao_api.json                     modelo, endereço, parâmetros e preço

Uso (a partir da pasta Demonstração):
  python referencia/classificar_referencia.py --simular     # mostra o que seria enviado, sem chamar o modelo
  python referencia/classificar_referencia.py --limite 5    # classifica 5 anúncios (teste)
  python referencia/classificar_referencia.py               # classifica todos

A chave vem da variável de ambiente indicada em configuracao_api.json (ou de um arquivo .env nesta pasta).
Saída: 4_saida/minha_saida.csv. Interrompido, continua de onde parou ao rodar de novo.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent.parent
ENTRADA = PASTA / "1_banco_de_dados" / "vagas_amostra_1000.csv"
SAIDA = PASTA / "4_saida" / "minha_saida.csv"
SISTEMA = (PASTA / "2_prompt" / "prompt_sistema.txt").read_text(encoding="utf-8")
MOLDE = (PASTA / "2_prompt" / "modelo_mensagem_usuario.txt").read_text(encoding="utf-8")
SCHEMA = json.loads((PASTA / "3_schema_json" / "schema_saida.json").read_text(encoding="utf-8"))
CFG = json.loads((PASTA / "configuracao_api.json").read_text(encoding="utf-8"))
CAMPOS = ["vacancy_id", "vaga_ti", "justificativa_ti", "skills", "temas", "tokens_in", "tokens_out", "erro"]


def mensagem_usuario(vaga):
    """Preenche o molde com as colunas do anúncio. Linha cujo campo está vazio não entra."""
    linhas = []
    for linha in MOLDE.strip().split("\n"):
        cols = re.findall(r"\{(\w+)\}", linha)
        if cols and not all(str(vaga.get(c, "")).strip() for c in cols):
            continue
        for c in cols:
            linha = linha.replace("{" + c + "}", str(vaga[c]).strip())
        linhas.append(linha)
    return "\n".join(linhas)


def ler_json(texto):
    try:
        return json.loads(texto)
    except Exception:  # noqa: BLE001
        m = re.search(r"\{.*\}", texto or "", re.DOTALL)
        if not m:
            raise ValueError("nenhum JSON na resposta")
        return json.loads(m.group(0))


def conferir(resposta):
    """Confere a resposta contra o schema: campos obrigatórios, nenhum campo a mais, tipos e opções.
    Resposta fora do formato vira erro e a chamada é repetida; nada é corrigido em silêncio."""
    if not isinstance(resposta, dict):
        raise ValueError("a resposta não é um objeto JSON")
    props = SCHEMA["properties"]
    faltam = [k for k in SCHEMA["required"] if k not in resposta]
    sobram = [k for k in resposta if k not in props]
    if faltam or sobram:
        raise ValueError(f"campos faltando {faltam} ou a mais {sobram}")
    for k, regra in props.items():
        v = resposta[k]
        if regra["type"] == "string":
            if not isinstance(v, str):
                raise ValueError(f"{k} deve ser texto")
            if "enum" in regra and v not in regra["enum"]:
                raise ValueError(f"{k} fora das opções: {v!r}")
        elif regra["type"] == "array":
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                raise ValueError(f"{k} deve ser uma lista de textos")
    return resposta


def classificar(cliente, vaga):
    erro = ""
    for tentativa in range(CFG["tentativas_por_anuncio"]):
        try:
            r = cliente.chat.completions.create(
                model=CFG["modelo"], temperature=CFG["temperature"], max_tokens=CFG["max_tokens"],
                response_format=CFG["response_format"],
                messages=[{"role": "system", "content": SISTEMA},
                          {"role": "user", "content": mensagem_usuario(vaga)}])
            j = conferir(ler_json(r.choices[0].message.content))
            return {"vacancy_id": vaga["vacancy_id"], "vaga_ti": j["vaga_ti"], "justificativa_ti": j["justificativa_ti"],
                    "skills": "; ".join(j["skills"]), "temas": "; ".join(j["temas"]),
                    "tokens_in": r.usage.prompt_tokens, "tokens_out": r.usage.completion_tokens, "erro": ""}
        except Exception as e:  # noqa: BLE001
            erro = str(e)[:200]
            time.sleep(2 * (tentativa + 1))
    return {"vacancy_id": vaga["vacancy_id"], "vaga_ti": "", "justificativa_ti": "", "skills": "", "temas": "",
            "tokens_in": 0, "tokens_out": 0, "erro": erro}


def chave_de_acesso():
    nome = CFG["variavel_da_chave"]
    if not os.environ.get(nome) and (PASTA / ".env").exists():
        for linha in (PASTA / ".env").read_text(encoding="utf-8").splitlines():
            if linha.startswith(nome + "="):
                os.environ[nome] = linha.split("=", 1)[1].strip()
    if not os.environ.get(nome):
        sys.exit(f"Defina a variável de ambiente {nome} (ou crie o arquivo .env) antes de rodar. Veja o LEIAME.md.")
    return os.environ[nome]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(ENTRADA))
    ap.add_argument("--saida", default=str(SAIDA))
    ap.add_argument("--limite", type=int, default=0, help="classifica só os N primeiros anúncios pendentes")
    ap.add_argument("--simular", action="store_true", help="mostra o que seria enviado, sem chamar o modelo")
    a = ap.parse_args()
    vagas = pd.read_csv(a.entrada, dtype=str).fillna("").to_dict("records")

    if a.simular:
        print("===== MENSAGEM DE SISTEMA (igual para todos os anúncios) =====\n" + SISTEMA)
        print("\n===== MENSAGEM DO USUÁRIO (muda a cada anúncio) =====\n" + mensagem_usuario(vagas[0]))
        print(f"\nmodelo: {CFG['modelo']} | temperatura: {CFG['temperature']} | anúncios no arquivo: {len(vagas)}")
        return

    from openai import OpenAI
    cliente = OpenAI(api_key=chave_de_acesso(), base_url=CFG["base_url"], timeout=120)
    saida = Path(a.saida)
    feitos = set()
    if saida.exists():   # retomada: quem já tem resposta sem erro não é chamado de novo
        ant = pd.read_csv(saida, dtype=str).fillna("")
        feitos = set(ant[ant.erro == ""].vacancy_id)
    pendentes = [v for v in vagas if v["vacancy_id"] not in feitos]
    if a.limite:
        pendentes = pendentes[:a.limite]
    print(f"anúncios: {len(vagas)} | já feitos: {len(feitos)} | a classificar agora: {len(pendentes)}")
    if not pendentes:
        return

    novo = not saida.exists()
    tin = tout = erros = 0
    with saida.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        with ThreadPoolExecutor(CFG["chamadas_simultaneas"]) as pool:
            futuros = [pool.submit(classificar, cliente, v) for v in pendentes]
            for i, fut in enumerate(as_completed(futuros), 1):
                r = fut.result()
                w.writerow(r)       # grava a cada resposta: se cair no meio, o que foi feito fica
                f.flush()
                tin, tout, erros = tin + r["tokens_in"], tout + r["tokens_out"], erros + bool(r["erro"])
                if i % 50 == 0 or i == len(pendentes):
                    print(f"  {i}/{len(pendentes)} | erros: {erros}")
    p = CFG["preco_usd_por_milhao_de_tokens"]
    print(f"tokens de entrada: {tin} | de saída: {tout} | custo estimado: US$ "
          f"{tin / 1e6 * p['entrada'] + tout / 1e6 * p['saida']:.4f} | erros: {erros}")
    print(f"resultado em {saida}")


if __name__ == "__main__":
    main()
