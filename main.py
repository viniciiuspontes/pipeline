from pathlib import Path

from src.duplicates import (
    analisar_duplicados,
    carregar_csv,
    gerar_relatorio_html,
)


ARQUIVO_ENTRADA = Path("data/duplicates.csv")
PASTA_RESULTADOS = Path("output")
PASTA_SITE = Path("site")


def main() -> None:
    print(f"Carregando arquivo: {ARQUIVO_ENTRADA}")

    dataframe = carregar_csv(ARQUIVO_ENTRADA)
    resultado = analisar_duplicados(dataframe)

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    PASTA_SITE.mkdir(parents=True, exist_ok=True)

    caminho_limpo = PASTA_RESULTADOS / "duplicates_clean.csv"
    caminho_duplicados = (
        PASTA_RESULTADOS / "duplicate_records.csv"
    )
    caminho_relatorio = PASTA_SITE / "index.html"

    resultado["dados_limpos"].to_csv(
        caminho_limpo,
        index=False,
        encoding="utf-8-sig",
    )

    resultado["duplicados"].to_csv(
        caminho_duplicados,
        index=False,
        encoding="utf-8-sig",
    )

    gerar_relatorio_html(
        resultado,
        caminho_relatorio,
    )

    print("\nResultado da validação")
    print("-----------------------")
    print(
        "Registros analisados:",
        resultado["total_registros"],
    )
    print(
        "Ocorrências em grupos duplicados:",
        resultado["ocorrencias_duplicadas"],
    )
    print(
        "Duplicados removíveis:",
        resultado["duplicados_removiveis"],
    )
    print(
        "Grupos duplicados:",
        resultado["grupos_duplicados"],
    )
    print(
        "Registros após limpeza:",
        resultado["registros_unicos"],
    )
    print(
        "Percentual removível:",
        f'{resultado["percentual_removivel"]}%',
    )

    print(f"\nBase limpa: {caminho_limpo}")
    print(f"Duplicados encontrados: {caminho_duplicados}")
    print(f"Relatório HTML: {caminho_relatorio}")


if __name__ == "__main__":
    main()
