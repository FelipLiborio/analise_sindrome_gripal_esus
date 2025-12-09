import pandas as pd
import psycopg2
from unidecode import unidecode


# -----------------------------
# Função para tratar valores nulos
# -----------------------------
def pg(v):
    if pd.isnull(v) or v == "":
        return None
    return v


# -----------------------------
# 1. Carregar CSV
# -----------------------------
df = pd.read_csv("data/main/data_tratado.csv")


# -----------------------------
# 2. Conectar ao banco
# -----------------------------
conn = psycopg2.connect(
    dbname="esus_gripal",
    user="esus_user",
    password="esus_password",
    host="localhost",
    port=5432,
)
cur = conn.cursor()


# ============================================================
# 3. PRÉ-POPULAR TABELAS ESTÁTICAS
# ============================================================

# ----- Localização -----
locs = df[["estado", "municipio"]].drop_duplicates()

for _, r in locs.iterrows():
    cur.execute(
        """INSERT INTO Localizacao (estado, municipio)
           VALUES (%s, %s)
           ON CONFLICT (municipio) DO NOTHING;""",
        (pg(r["estado"]), pg(r["municipio"])),
    )

# ----- Sintomas -----
todos_sintomas = set()

for s in df["sintomas"]:
    if pd.notnull(s):
        sintomas = [unidecode(x.strip().lower()) for x in s.split(",") if x.strip()]
        todos_sintomas.update(sintomas)

for sintoma in todos_sintomas:
    cur.execute(
        "INSERT INTO Sintoma (nome_sintoma) VALUES (%s) ON CONFLICT DO NOTHING;",
        (sintoma,),
    )

conn.commit()


# ============================================================
# 4. CARREGAR ID's EM CACHE PARA EVITAR SELECT E REPETIÇÃO
# ============================================================

# ---- Localização -----
cur.execute("SELECT id_localizacao, municipio FROM Localizacao;")
cache_loc = {m: i for i, m in cur.fetchall()}

# ---- Sintoma -----
cur.execute("SELECT id_sintoma, nome_sintoma FROM Sintoma;")
cache_sint = {nome: sid for sid, nome in cur.fetchall()}

# ---- Pessoa (cache será preenchido on-demand) -----
cache_pessoa = {}


# ============================================================
# 5. LOOP PRINCIPAL — UMA NOTIFICAÇÃO POR LINHA
# ============================================================

for idx, row in df.iterrows():

    # -------------------------
    # LOCALIZAÇÃO
    # -------------------------
    municipio = pg(row["municipio"])
    id_localizacao = cache_loc[municipio]

    cur.execute(
        """
        INSERT INTO Pessoa (
            idade, sexo, raca_cor,
            codigo_contem_comunidade_tradicional,
            profissional_saude, profissional_seguranca
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_pessoa;
        """,
        (
            pg(row["idade"]),
            pg(row["sexo"]),
            pg(row["racaCor"]),
            pg(row["codigoContemComunidadeTradicional"]),
            pg(row["profissionalSaude"]),
            pg(row["profissionalSeguranca"]),
        )
    )

    id_pessoa = cur.fetchone()[0]

    # -------------------------
    # NOTIFICAÇÃO (tabela principal)
    # -------------------------
    cur.execute(
        """
        INSERT INTO Notificacao (
            id_pessoa, id_localizacao,
            data_notificacao, data_inicio_sintomas, data_encerramento,
            evolucao_caso, classificacao_final,
            codigo_estrategia_covid, codigo_local_realizacao_testagem,
            origem, excluido, validado
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_notificacao;
    """,
        (
            id_pessoa,
            id_localizacao,
            pg(row["dataNotificacao"]),
            pg(row["dataInicioSintomas"]),
            pg(row["dataEncerramento"]),
            pg(row["evolucaoCaso"]),
            pg(row["classificacaoFinal"]),
            pg(row["codigoEstrategiaCovid"]),
            pg(row["codigoLocalRealizacaoTestagem"]),
            pg(row["origem"]),
            pg(row["excluido"]),
            pg(row["validado"]),
        ),
    )

    id_notificacao = cur.fetchone()[0]

    # -------------------------
    # VACINAÇÃO (1:1)
    # -------------------------
    cur.execute(
        """
        INSERT INTO Vacinacao (
            id_notificacao, codigo_recebeu_vacina, codigo_doses_vacina,
            data_primeira_dose, codigo_laboratorio_primeira_dose, lote_primeira_dose,
            data_segunda_dose, codigo_laboratorio_segunda_dose, lote_segunda_dose
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            id_notificacao,
            pg(row["codigoRecebeuVacina"]),
            pg(row["codigoDosesVacina"]),
            pg(row["dataPrimeiraDose"]),
            pg(row["codigoLaboratorioPrimeiraDose"]),
            pg(row["lotePrimeiraDose"]),
            pg(row["dataSegundaDose"]),
            pg(row["codigoLaboratorioSegundaDose"]),
            pg(row["loteSegundaDose"]),
        ),
    )

    # -------------------------
    # TESTE LABORATORIAL (1 por linha)
    # -------------------------
    cur.execute(
        """
        INSERT INTO TesteLaboratorial (
            id_notificacao, numero_teste, total_testes_realizados,
            codigo_estado_teste, codigo_tipo_teste, codigo_resultado_teste,
            codigo_fabricante_teste, data_coleta_teste
        ) VALUES (%s, 1, %s, %s, %s, %s, %s, %s)
    """,
        (
            id_notificacao,
            pg(row["totalTestesRealizados"]),
            pg(row["codigoEstadoTeste1"]),
            pg(row["codigoTipoTeste1"]),
            pg(row["codigoResultadoTeste1"]),
            pg(row["codigoFabricanteTeste1"]),
            pg(row["dataColetaTeste1"]),
        ),
    )

    # -------------------------
    # SINTOMAS (N:N)
    # -------------------------
    if pd.notnull(row["sintomas"]):
        sintomas = [
            unidecode(x.strip().lower())
            for x in row["sintomas"].split(",")
            if x.strip()
        ]

        for sintoma in sintomas:
            id_sintoma = cache_sint[sintoma]
            cur.execute(
                """
                INSERT INTO Notificacao_Sintoma (id_notificacao, id_sintoma)
                VALUES (%s, %s)
            """,
                (id_notificacao, id_sintoma),
            )

    # Commit a cada 2000 linhas
    if idx % 2000 == 0:
        conn.commit()
        print("Processadas:", idx, "linhas")


conn.commit()
cur.close()
conn.close()

print("Banco populado com sucesso!")
