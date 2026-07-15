--categoria de produtos mastercard
SELECT
	*
FROM
	hdg.tb_master_categoria_produto;


--flag mcc mastercard
SELECT
	*
FROM
	hdg.tb_master_flag_mcc;


--grupo de produtos mastercard
SELECT
	*
FROM
	hdg.tb_master_grupo_produto;

--ird mastercard
SELECT
	*
FROM
	hdg.tb_master_ird;


--mcc mastercard
SELECT
	*
FROM
	hdg.tb_master_mcc;


--preços mastercard
SELECT
	*
FROM
	hdg.tb_master_preco;


--produtos mastercard
SELECT
	*
FROM
	hdg.tb_master_produto;


--segmentos mastercard
SELECT
	*
FROM
	hdg.tb_master_segmento;


--sub categoria de produtos mastercard
SELECT
	*
FROM
	hdg.tb_master_sub_categoria_produto;


CREATE OR REPLACE
FUNCTION hdg.Calc_mastercard_interchange (p_codigo_processamento VARCHAR,
p_ird VARCHAR,
p_produto VARCHAR,
p_sub_produto VARCHAR,
p_mcc VARCHAR,
p_valor VARCHAR)
    RETURNS NUMERIC
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_produto VARCHAR := CASE
	WHEN p_codigo_processamento IN ('002000', '001000') THEN
        COALESCE(p_sub_produto, p_produto)
	ELSE
        p_produto
END;

v_custo_bandeira NUMERIC(16, 2);

v_teto_bandeira NUMERIC(16, 2);

v_mcc INTEGER := p_mcc::INTEGER;

v_valor NUMERIC(16, 2) := (p_valor::NUMERIC) / 100;

BEGIN
    SELECT
	Round(tmp.taxa_incremental + (v_valor * (tmp.percentual_custo_bandeira + tmp.ajuste_percentual_custo_bandeira + tmp.ajuste_parcela + tmp.ajuste_digital_parcela)) / 100, 2),
	tmp.custo_teto_bandeira
    INTO
	v_custo_bandeira,
	v_teto_bandeira
FROM
	hdg.tb_master_preco tmp
INNER JOIN hdg.tb_master_produto tmp2 ON
	tmp2.ird_id = tmp.ird_id
	AND tmp2.grupo_produto_id = tmp.grupo_produto_id
	AND tmp2.categoria_produto_id = tmp.categoria_produto_id
	AND tmp2.sub_categoria_produto_id = tmp.sub_categoria_produto_id
	AND tmp2.deletado = 0
INNER JOIN hdg.tb_master_mcc tmm ON
	tmm.segmento_id = tmp.segmento_id
	AND tmm.flag_mcc_id = tmp.flag_mcc_id
	AND tmm.deletado = 0
INNER JOIN hdg.tb_master_ird tmi ON
	tmi.id = tmp.ird_id
	AND tmi.deletado = 0
WHERE
	1 = 1
	AND tmp.deletado = 0
	AND tmm.codigo = v_mcc
	AND tmp2.produto = v_produto
	AND tmi.ird = p_ird
	AND v_valor BETWEEN tmp.valor_transacao_inicial AND tmp.valor_transacao_final
ORDER BY
	tmp.especial DESC
LIMIT 1;

IF v_teto_bandeira > 0
AND v_custo_bandeira > v_teto_bandeira THEN
        RETURN v_teto_bandeira;
END IF;

RETURN v_custo_bandeira;
END;

$$;