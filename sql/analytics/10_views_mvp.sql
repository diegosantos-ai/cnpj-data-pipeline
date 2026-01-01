CREATE OR REPLACE VIEW analytics.v_distribuicao_natureza AS
SELECT natureza_juridica, COUNT(*) AS qtd
FROM public.empresas
GROUP BY natureza_juridica
ORDER BY COUNT(*) DESC;

CREATE OR REPLACE VIEW analytics.v_distribuicao_municipio AS
SELECT municipio, COUNT(*) AS qtd
FROM public.estabelecimentos
GROUP BY municipio
ORDER BY COUNT(*) DESC;

CREATE OR REPLACE VIEW analytics.v_distribuicao_socios AS
SELECT qualificacao_socio, COUNT(*) AS qtd
FROM public.socios
GROUP BY qualificacao_socio
ORDER BY COUNT(*) DESC;
