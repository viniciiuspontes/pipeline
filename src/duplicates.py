from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import pandas as pd


def carregar_csv(caminho: Path) -> pd.DataFrame:
    """Carrega um CSV tentando identificar o delimitador."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    if caminho.stat().st_size == 0:
        raise ValueError("O arquivo CSV está vazio.")

    try:
        dataframe = pd.read_csv(
            caminho,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
        )
    except (UnicodeDecodeError, pd.errors.ParserError):
        dataframe = pd.read_csv(
            caminho,
            sep=None,
            engine="python",
            encoding="latin-1",
        )

    if dataframe.empty:
        raise ValueError("O CSV não possui registros.")

    if len(dataframe.columns) == 0:
        raise ValueError("O CSV não possui colunas.")

    return dataframe


def analisar_duplicados(
    dataframe: pd.DataFrame,
    colunas: list[str] | None = None,
) -> dict[str, Any]:
    """
    Analisa registros duplicados.

    Quando colunas não é informado, todas as colunas são usadas.
    """

    if colunas:
        inexistentes = [
            coluna
            for coluna in colunas
            if coluna not in dataframe.columns
        ]

        if inexistentes:
            raise ValueError(
                "Colunas não encontradas: "
                + ", ".join(inexistentes)
            )

    mascara_todas_ocorrencias = dataframe.duplicated(
        subset=colunas,
        keep=False,
    )

    mascara_excedentes = dataframe.duplicated(
        subset=colunas,
        keep="first",
    )

    registros_duplicados = dataframe[
        mascara_todas_ocorrencias
    ].copy()

    registros_sem_duplicados = dataframe.drop_duplicates(
        subset=colunas,
        keep="first",
    ).copy()

    total = len(dataframe)
    ocorrencias_duplicadas = int(
        mascara_todas_ocorrencias.sum()
    )
    duplicados_removiveis = int(mascara_excedentes.sum())
    grupos_duplicados = 0

    if ocorrencias_duplicadas:
        grupos_duplicados = (
            registros_duplicados
            .groupby(
                colunas or list(dataframe.columns),
                dropna=False,
            )
            .ngroups
        )

    percentual = (
        round((duplicados_removiveis / total) * 100, 2)
        if total
        else 0.0
    )

    return {
        "total_registros": total,
        "total_colunas": len(dataframe.columns),
        "ocorrencias_duplicadas": ocorrencias_duplicadas,
        "duplicados_removiveis": duplicados_removiveis,
        "grupos_duplicados": grupos_duplicados,
        "registros_unicos": len(registros_sem_duplicados),
        "percentual_removivel": percentual,
        "colunas_analisadas": (
            colunas or list(dataframe.columns)
        ),
        "duplicados": registros_duplicados,
        "dados_limpos": registros_sem_duplicados,
    }


def gerar_relatorio_html(
    resultado: dict[str, Any],
    destino: Path,
) -> None:
    """Gera relatório HTML apenas com informações agregadas."""

    destino.parent.mkdir(parents=True, exist_ok=True)

    colunas = ", ".join(
        escape(str(coluna))
        for coluna in resultado["colunas_analisadas"]
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Relatório de dados duplicados</title>

    <style>
        body {{
            margin: 0;
            padding: 32px;
            font-family: Arial, sans-serif;
            color: #1f2328;
            background: #f6f8fa;
        }}

        main {{
            width: min(900px, 100%);
            margin: auto;
        }}

        h1 {{
            color: #0969da;
        }}

        .aviso {{
            padding: 16px;
            margin-bottom: 24px;
            background: #fff8c5;
            border-left: 5px solid #bf8700;
        }}

        .cards {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
        }}

        .card {{
            padding: 24px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgb(31 35 40 / 10%);
        }}

        .numero {{
            display: block;
            margin-bottom: 8px;
            color: #0969da;
            font-size: 32px;
            font-weight: bold;
        }}

        .detalhes {{
            margin-top: 24px;
            padding: 24px;
            overflow-wrap: anywhere;
            background: white;
            border-radius: 12px;
        }}
    </style>
</head>
<body>
    <main>
        <h1>Relatório de dados duplicados</h1>

        <div class="aviso">
            Este relatório apresenta apenas informações agregadas.
            Nenhum registro do CSV é publicado nesta página.
        </div>

        <section class="cards">
            <article class="card">
                <span class="numero">
                    {resultado["total_registros"]}
                </span>
                Registros analisados
            </article>

            <article class="card">
                <span class="numero">
                    {resultado["duplicados_removiveis"]}
                </span>
                Duplicados removíveis
            </article>

            <article class="card">
                <span class="numero">
                    {resultado["grupos_duplicados"]}
                </span>
                Grupos duplicados
            </article>

            <article class="card">
                <span class="numero">
                    {resultado["registros_unicos"]}
                </span>
                Registros após limpeza
            </article>

            <article class="card">
                <span class="numero">
                    {resultado["percentual_removivel"]}%
                </span>
                Percentual removível
            </article>
        </section>

        <section class="detalhes">
            <h2>Critério da análise</h2>
            <p>
                Foram comparadas as seguintes colunas:
                <strong>{colunas}</strong>.
            </p>
        </section>
    </main>
</body>
</html>
"""

    destino.write_text(html, encoding="utf-8")
