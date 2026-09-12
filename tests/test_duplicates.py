from pathlib import Path

import pandas as pd
import pytest

from src.duplicates import (
    analisar_duplicados,
    carregar_csv,
    gerar_relatorio_html,
)


def criar_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 1, 2, 3, 3, 3],
            "nome": [
                "Ana",
                "Ana",
                "Bruno",
                "Carla",
                "Carla",
                "Carla",
            ],
        }
    )


def test_identificar_duplicados() -> None:
    resultado = analisar_duplicados(criar_dataframe())

    assert resultado["total_registros"] == 6
    assert resultado["duplicados_removiveis"] == 3
    assert resultado["registros_unicos"] == 3
    assert resultado["grupos_duplicados"] == 2


def test_remover_duplicados() -> None:
    resultado = analisar_duplicados(criar_dataframe())

    dados_limpos = resultado["dados_limpos"]

    assert len(dados_limpos) == 3
    assert not dados_limpos.duplicated().any()


def test_analisar_colunas_especificas() -> None:
    dataframe = pd.DataFrame(
        {
            "id": [1, 1],
            "nome": ["Ana", "Maria"],
        }
    )

    resultado = analisar_duplicados(
        dataframe,
        colunas=["id"],
    )

    assert resultado["duplicados_removiveis"] == 1


def test_rejeitar_coluna_inexistente() -> None:
    with pytest.raises(ValueError):
        analisar_duplicados(
            criar_dataframe(),
            colunas=["email"],
        )


def test_carregar_arquivo_inexistente() -> None:
    with pytest.raises(FileNotFoundError):
        carregar_csv(Path("arquivo-inexistente.csv"))


def test_gerar_relatorio_sem_expor_registros(
    tmp_path: Path,
) -> None:
    resultado = analisar_duplicados(criar_dataframe())
    destino = tmp_path / "index.html"

    gerar_relatorio_html(resultado, destino)

    conteudo = destino.read_text(encoding="utf-8")

    assert "Registros analisados" in conteudo
    assert "Dados duplicados" not in conteudo
    assert "Ana" not in conteudo
    assert "Carla" not in conteudo
