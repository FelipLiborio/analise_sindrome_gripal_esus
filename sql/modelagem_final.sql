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

    data_notificacao DATE NOT NULL, 
    data_inicio_sintomas DATE NOT NULL, 
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

    codigo_recebeu_vacina VARCHAR(1) NOT NULL, 
    codigo_doses_vacina VARCHAR(1), 
    
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