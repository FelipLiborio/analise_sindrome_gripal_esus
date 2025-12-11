Q_BASE_TEMPORAL = """
SELECT
    n.id_notificacao,
    n.data_notificacao,
    n.classificacao_final,
    l.municipio,
    t.data_coleta_teste,
    t.codigo_resultado_teste
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
LEFT JOIN TesteLaboratorial t ON t.id_notificacao = n.id_notificacao
WHERE n.data_notificacao IS NOT NULL;
"""

# Evolução temporal dos casos confirmados por município
Q_EVOLUCAO_CONFIRMADOS = """
SELECT
    TO_CHAR(DATE_TRUNC('month', n.data_notificacao), 'YYYY-MM') AS mes,
    l.municipio,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.data_notificacao IS NOT NULL
    AND n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY mes, l.municipio
ORDER BY mes, l.municipio;
"""

# Evolução temporal dos casos suspeitos por município
Q_EVOLUCAO_SUSPEITOS = """
SELECT
    TO_CHAR(DATE_TRUNC('month', n.data_notificacao), 'YYYY-MM') AS mes,
    l.municipio,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.data_notificacao IS NOT NULL
    AND n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY mes, l.municipio
ORDER BY mes, l.municipio;
"""

# Evolução temporal de óbitos por município
Q_EVOLUCAO_OBITOS = """
SELECT
    TO_CHAR(DATE_TRUNC('month', n.data_notificacao), 'YYYY-MM') AS mes,
    l.municipio,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.data_notificacao IS NOT NULL
    AND n.evolucao_caso = 'Óbito'
GROUP BY mes, l.municipio
ORDER BY mes, l.municipio;
"""

# Evolução temporal de total notificações por município
Q_EVOLUCAO_TOTAL = """
SELECT
    TO_CHAR(DATE_TRUNC('month', n.data_notificacao), 'YYYY-MM') AS mes,
    l.municipio,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.data_notificacao IS NOT NULL
GROUP BY mes, l.municipio
ORDER BY mes, l.municipio;
"""

# Distribuição de casos confirmados por sexo
Q_DISTRIBUICAO_CONFIRMADOS_SEXO = """
SELECT
    p.sexo,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY p.sexo;
"""

# Distribuição de casos suspeitos por sexo
Q_DISTRIBUICAO_SUSPEITOS_SEXO = """
SELECT
    p.sexo,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY p.sexo;
"""

# Distribuição de notificações totais por sexo
Q_DISTRIBUICAO_TOTAL_SEXO = """
SELECT
    p.sexo,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
GROUP BY p.sexo;
"""

# Distribuição de óbitos por sexo
Q_DISTRIBUICAO_OBITOS_SEXO = """
SELECT
    p.sexo,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.evolucao_caso = 'Óbito'
GROUP BY p.sexo;
"""

# Distribuição de casos confirmados por faixa etária
Q_DISTRIBUICAO_CONFIRMADOS_IDADE = """
SELECT
    CASE
        WHEN p.idade < 18 THEN '0-17'
        WHEN p.idade BETWEEN 18 AND 29 THEN '18-29'
        WHEN p.idade BETWEEN 30 AND 39 THEN '30-39'
        WHEN p.idade BETWEEN 40 AND 49 THEN '40-49'
        WHEN p.idade BETWEEN 50 AND 59 THEN '50-59'
        WHEN p.idade >= 60 THEN '60+'
        ELSE 'Desconhecido'
    END AS faixa_etaria,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY faixa_etaria;
"""

# Distribuição de casos suspeitos por faixa etária
Q_DISTRIBUICAO_SUSPEITOS_IDADE = """
SELECT
    CASE
        WHEN p.idade < 18 THEN '0-17'
        WHEN p.idade BETWEEN 18 AND 29 THEN '18-29'
        WHEN p.idade BETWEEN 30 AND 39 THEN '30-39'
        WHEN p.idade BETWEEN 40 AND 49 THEN '40-49'
        WHEN p.idade BETWEEN 50 AND 59 THEN '50-59'
        WHEN p.idade >= 60 THEN '60+'
        ELSE 'Desconhecido'
    END AS faixa_etaria,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY faixa_etaria;
"""

# Distribuição de notificações totais por faixa etária
Q_DISTRIBUICAO_TOTAL_IDADE = """
SELECT
    CASE
        WHEN p.idade < 18 THEN '0-17'
        WHEN p.idade BETWEEN 18 AND 29 THEN '18-29'
        WHEN p.idade BETWEEN 30 AND 39 THEN '30-39'
        WHEN p.idade BETWEEN 40 AND 49 THEN '40-49'
        WHEN p.idade BETWEEN 50 AND 59 THEN '50-59'
        WHEN p.idade >= 60 THEN '60+'
        ELSE 'Desconhecido'
    END AS faixa_etaria,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
GROUP BY faixa_etaria;
"""

# Distribuição de óbitos por faixa etária
Q_DISTRIBUICAO_OBITOS_IDADE = """
SELECT
    CASE
        WHEN p.idade < 18 THEN '0-17'
        WHEN p.idade BETWEEN 18 AND 29 THEN '18-29'
        WHEN p.idade BETWEEN 30 AND 39 THEN '30-39'
        WHEN p.idade BETWEEN 40 AND 49 THEN '40-49'
        WHEN p.idade BETWEEN 50 AND 59 THEN '50-59'
        WHEN p.idade >= 60 THEN '60+'
        ELSE 'Desconhecido'
    END AS faixa_etaria,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.evolucao_caso = 'Óbito'
GROUP BY faixa_etaria;
"""

# Distribuição de casos confirmados por raça/cor
Q_DISTRIBUICAO_CONFIRMADOS_RACA = """
SELECT
    p.raca_cor,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY p.raca_cor;
"""

# Distribuição de casos suspeitos por raça/cor
Q_DISTRIBUICAO_SUSPEITOS_RACA = """
SELECT
    p.raca_cor,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY p.raca_cor;
"""

# Distribuição de notificações totais por raça/cor
Q_DISTRIBUICAO_TOTAL_RACA = """
SELECT
    p.raca_cor,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
GROUP BY p.raca_cor;
"""

# Distribuição de óbitos por raça/cor
Q_DISTRIBUICAO_OBITOS_RACA = """
SELECT
    p.raca_cor,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.evolucao_caso = 'Óbito'
GROUP BY p.raca_cor;
"""

# Distribuição de casos confirmados por ocupação
Q_DISTRIBUICAO_CONFIRMADOS_OCUPACAO = """
SELECT
    CASE
        WHEN p.profissional_saude THEN 'Profissional de Saúde'
        WHEN p.profissional_seguranca THEN 'Profissional de Segurança'
        ELSE 'Outros'
    END AS ocupacao,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY ocupacao;
"""

# Distribuição de casos suspeitos por ocupação
Q_DISTRIBUICAO_SUSPEITOS_OCUPACAO = """
SELECT
    CASE
        WHEN p.profissional_saude THEN 'Profissional de Saúde'
        WHEN p.profissional_seguranca THEN 'Profissional de Segurança'
        ELSE 'Outros'
    END AS ocupacao,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY ocupacao;
"""

# Distribuição de notificações totais por ocupação
Q_DISTRIBUICAO_TOTAL_OCUPACAO = """
SELECT
    CASE
        WHEN p.profissional_saude THEN 'Profissional de Saúde'
        WHEN p.profissional_seguranca THEN 'Profissional de Segurança'
        ELSE 'Outros'
    END AS ocupacao,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
GROUP BY ocupacao;
"""

# Distribuição de óbitos por ocupação
Q_DISTRIBUICAO_OBITOS_OCUPACAO = """
SELECT
    CASE
        WHEN p.profissional_saude THEN 'Profissional de Saúde'
        WHEN p.profissional_seguranca THEN 'Profissional de Segurança'
        ELSE 'Outros'
    END AS ocupacao,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Pessoa p ON p.id_pessoa = n.id_pessoa
WHERE n.evolucao_caso = 'Óbito'
GROUP BY ocupacao;
"""

# Relação entre vacinação e taxa de confirmação laboratorial
Q_VACINACAO_CONFIRMACAO = """
SELECT
    CASE
        WHEN v.codigo_recebeu_vacina = '1' THEN 'Sim'
        WHEN v.codigo_recebeu_vacina = '2' THEN 'Não'
        WHEN v.codigo_recebeu_vacina = '3' THEN 'Ignorado'
        WHEN v.codigo_recebeu_vacina = 'True' THEN 'Sim'
        WHEN v.codigo_recebeu_vacina = 'False' THEN 'Não'
        WHEN v.codigo_recebeu_vacina = 'true' THEN 'Sim'
        WHEN v.codigo_recebeu_vacina = 'false' THEN 'Não'
        WHEN v.codigo_recebeu_vacina IS NULL THEN 'Não Informado'
        ELSE 'Outro'
    END AS recebeu_vacina,
    CASE
        WHEN n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Confirmado Clínico-Imagem', 'Confirmado por Critério Clínico') THEN 'Confirmado'
        WHEN n.classificacao_final = 'Descartado' THEN 'Descartado'
        ELSE 'Em Aberto'
    END AS status_confirmacao,
    COUNT(*) AS total
FROM Notificacao n
LEFT JOIN Vacinacao v ON v.id_notificacao = n.id_notificacao
WHERE n.classificacao_final IS NOT NULL
GROUP BY recebeu_vacina, status_confirmacao;
"""

# Proporção de testes realizados por tipo e fabricante, e taxa de positividade
Q_TESTES_TIPO_FABRICANTE = """
SELECT
    CASE
        WHEN t.codigo_tipo_teste = 1 THEN 'RT-PCR'
        WHEN t.codigo_tipo_teste = 4 THEN 'Teste rápido de antígeno'
        WHEN t.codigo_tipo_teste = 9 THEN 'Anticorpos totais'
        ELSE CAST(t.codigo_tipo_teste AS TEXT)
    END AS tipo_teste,
    CAST(t.codigo_fabricante_teste AS TEXT) AS fabricante,
    COUNT(*) AS total_testes,
    SUM(CASE WHEN t.codigo_resultado_teste = 1 THEN 1 ELSE 0 END) AS positivos,
    (SUM(CASE WHEN t.codigo_resultado_teste = 1 THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 AS taxa_positividade
FROM TesteLaboratorial t
GROUP BY t.codigo_tipo_teste, t.codigo_fabricante_teste;
"""

# Mapa de calor: densidade de notificações por município
Q_MAPA_CALOR = """
SELECT
    l.municipio,
    COUNT(*) AS total_notificacoes
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
GROUP BY l.municipio;
"""

# Mapa de calor para casos confirmados por município
Q_MAPA_CALOR_CONFIRMADOS = """
SELECT
    l.municipio,
    COUNT(*) AS total_confirmados
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.classificacao_final IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada')
GROUP BY l.municipio;
"""

# Mapa de calor para casos suspeitos por município
Q_MAPA_CALOR_SUSPEITOS = """
SELECT
    l.municipio,
    COUNT(*) AS total_suspeitos
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.classificacao_final NOT IN ('Confirmado Laboratorial', 'Confirmado Clínico-Epidemiológico', 'Síndrome Gripal não Especificada', 'Descartado')
GROUP BY l.municipio;
"""

# Mapa de calor para óbitos por município
Q_MAPA_CALOR_OBITOS = """
SELECT
    l.municipio,
    COUNT(*) AS total_obitos
FROM Notificacao n
JOIN Localizacao l ON l.id_localizacao = n.id_localizacao
WHERE n.evolucao_caso = 'Óbito'
GROUP BY l.municipio;
"""
