CREATE TABLE Pessoa (
    id_pessoa SERIAL PRIMARY KEY,
    
    idade INTEGER, 
    sexo VARCHAR(20) NOT NULL,
    raca_cor VARCHAR(50) NOT NULL,
    codigo_contem_comunidade_tradicional BOOLEAN NOT NULL,
    profissional_saude BOOLEAN NOT NULL,
    profissional_seguranca BOOLEAN NOT NULL
);

---

CREATE TABLE Localizacao (
    id_localizacao SERIAL PRIMARY KEY,
    estado VARCHAR(50) NOT NULL,
    municipio VARCHAR(100) NOT NULL UNIQUE 
);

---

CREATE TABLE Sintoma (
    id_sintoma SERIAL PRIMARY KEY,
    nome_sintoma VARCHAR(100) NOT NULL UNIQUE
);

---

CREATE TABLE Notificacao (
    id_notificacao SERIAL PRIMARY KEY,
    
    id_pessoa INTEGER NOT NULL REFERENCES Pessoa(id_pessoa),
    id_localizacao INTEGER NOT NULL REFERENCES Localizacao(id_localizacao),

    data_notificacao DATE , 
    data_inicio_sintomas DATE , 
    data_encerramento DATE, 
    
    evolucao_caso VARCHAR(50) NOT NULL,
    classificacao_final VARCHAR(50) NOT NULL,
    
    codigo_estrategia_covid NUMERIC(1) NOT NULL, 
    codigo_local_realizacao_testagem NUMERIC(1) NOT NULL,
    origem VARCHAR(50) NOT NULL,
    excluido VARCHAR(10) NOT NULL,
    validado VARCHAR(10) NOT NULL
);

---

CREATE TABLE Vacinacao (
    
    id_notificacao INTEGER PRIMARY KEY REFERENCES Notificacao(id_notificacao),

    codigo_recebeu_vacina VARCHAR(10) NOT NULL, 
    codigo_doses_vacina VARCHAR(10), 
    
    data_primeira_dose DATE, 
    codigo_laboratorio_primeira_dose TEXT,
    lote_primeira_dose TEXT,

    data_segunda_dose DATE, 
    codigo_laboratorio_segunda_dose TEXT,
    lote_segunda_dose TEXT
);

---

CREATE TABLE TesteLaboratorial (
    id_teste SERIAL PRIMARY KEY, 
    
    id_notificacao INTEGER NOT NULL REFERENCES Notificacao(id_notificacao),
    numero_teste INTEGER NOT NULL,

    total_testes_realizados INTEGER NOT NULL,

    codigo_estado_teste FLOAT,
    codigo_tipo_teste FLOAT,
    codigo_resultado_teste FLOAT,
    codigo_fabricante_teste FLOAT,
    data_coleta_teste DATE
);

---

CREATE TABLE Notificacao_Sintoma (
    id_notificacao_sintoma SERIAL PRIMARY KEY, 
    id_notificacao INTEGER NOT NULL REFERENCES Notificacao(id_notificacao),
    id_sintoma INTEGER NOT NULL REFERENCES Sintoma(id_sintoma)
);



--- Parte de controle 


--- tabela de logs de alteracoes
CREATE TABLE log_alteracoes (
    id_log SERIAL PRIMARY KEY,
    tabela VARCHAR(50) NOT NULL,
    operacao VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    registro_id INTEGER, -- id do registro da tabela
    dados_antes JSONB,   -- antes da operação (UPDATE e DELETE)
    dados_depois JSONB,  -- depois da operação (UPDATE e INSERT)
    data_operacao TIMESTAMP DEFAULT NOW()
);

-- Trigger function para auditar alteracoes
CREATE OR REPLACE FUNCTION fx_auditar_alteracoes()
RETURNS TRIGGER AS $$
DECLARE
    pk_name TEXT := TG_ARGV[0];     -- Nome da PK da tabela
    registro_id INTEGER;            -- Valor da PK
BEGIN
    -- Captura dinâmica da PK
    IF (TG_OP = 'INSERT') THEN
        EXECUTE format('SELECT ($1).%I', pk_name) INTO registro_id USING NEW;

        INSERT INTO log_alteracoes(tabela, operacao, registro_id, dados_depois)
        VALUES (TG_TABLE_NAME, TG_OP, registro_id, row_to_json(NEW));

        RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN
        EXECUTE format('SELECT ($1).%I', pk_name) INTO registro_id USING NEW;

        INSERT INTO log_alteracoes(tabela, operacao, registro_id, dados_antes, dados_depois)
        VALUES (TG_TABLE_NAME, TG_OP, registro_id, row_to_json(OLD), row_to_json(NEW));

        RETURN NEW;

    ELSIF (TG_OP = 'DELETE') THEN
        EXECUTE format('SELECT ($1).%I', pk_name) INTO registro_id USING OLD;

        INSERT INTO log_alteracoes(tabela, operacao, registro_id, dados_antes)
        VALUES (TG_TABLE_NAME, TG_OP, registro_id, row_to_json(OLD));

        RETURN OLD;
    END IF;

END;
$$ LANGUAGE plpgsql;

-- Tabelas que vao ter triggers de auditoria
CREATE TRIGGER trg_audit_pessoa
AFTER INSERT OR UPDATE OR DELETE ON Pessoa
FOR EACH ROW EXECUTE FUNCTION fx_auditar_alteracoes('id_pessoa');

CREATE TRIGGER trg_audit_vacinacao
AFTER INSERT OR UPDATE OR DELETE ON Vacinacao
FOR EACH ROW EXECUTE FUNCTION fx_auditar_alteracoes('id_notificacao');

CREATE TRIGGER trg_audit_notificacao
AFTER INSERT OR UPDATE OR DELETE ON Notificacao
FOR EACH ROW EXECUTE FUNCTION fx_auditar_alteracoes('id_notificacao');

CREATE TRIGGER trg_audit_teste_laboratorial
AFTER INSERT OR UPDATE OR DELETE ON TesteLaboratorial
FOR EACH ROW EXECUTE FUNCTION fx_auditar_alteracoes('id_teste');


-- Tabela de indicadores regionais
CREATE TABLE indicadores_regionais (
    id_indicador SERIAL PRIMARY KEY,
    municipio VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    taxa_positividade NUMERIC(5,2),
    total_testes INTEGER,
    total_positivos INTEGER,
    atualizado_em TIMESTAMP DEFAULT NOW()
);


CREATE OR REPLACE FUNCTION fx_calcular_taxa_positividade(
    data_ini DATE,
    data_fim DATE
)
RETURNS VOID AS $$
BEGIN

    INSERT INTO indicadores_regionais (
        municipio,
        data_inicio,
        data_fim,
        taxa_positividade,
        total_testes,
        total_positivos
    )
    SELECT
        l.municipio,
        data_ini,
        data_fim,
        (COUNT(*) FILTER (WHERE t.codigo_resultado_teste = 1)::NUMERIC / COUNT(*)) * 100 AS taxa_positividade,
        COUNT(*) AS total_testes,
        COUNT(*) FILTER (WHERE t.codigo_resultado_teste = 1) AS total_positivos
    FROM
        TesteLaboratorial t
        JOIN Notificacao n ON n.id_notificacao = t.id_notificacao
        JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
    WHERE
        t.data_coleta_teste BETWEEN data_ini AND data_fim
    GROUP BY
        l.municipio;

END;
$$ LANGUAGE plpgsql;