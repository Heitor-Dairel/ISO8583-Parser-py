import os
from datetime import datetime
from typing import List, Optional, Tuple

import psycopg
from dotenv import load_dotenv
from psycopg import Connection, ServerCursor
from psycopg.rows import TupleRow
from rich import print

from ..core import MastercardIso8583Parse
from ..models import TypeCycleIpm, TypeIpmDb, TypeParseIpmDb

load_dotenv()

host: Optional[str] = os.getenv("DB_HOST")
port: Optional[str] = os.getenv("DB_PORT")
db_name: Optional[str] = os.getenv("DB_NAME")
user: Optional[str] = os.getenv("DB_USERNAME")
password: Optional[str] = os.getenv("DB_PASSWORD")


class DbOutgouing:
    _EXISTS_FILE = "SELECT 1 FROM hdg.tb_master_arquivo tma WHERE tma.nome_arquivo = %s"

    _INSERT_SQL = """
    INSERT INTO hdg.tb_master_arquivo (nome_arquivo, ciclo, data_referencia) 
    VALUES (%s, %s, %s) RETURNING id
    """

    _COPY_SQL = """
    COPY hdg.tb_master_arquivo_detalhado (
        mti,
        numero_cartao,
        codigo_de_processamento,
        valor,
        data_transacao,
        data_vencimento_cartao,
        modo_de_entrada_pos,
        numero_seq_cartao,
        codigo_funcao,
        codigo_razao_mensagem,
        codigo_mcc,
        dados_referencia_adquirente,
        codigo_instituicao_remetente,
        codigo_aprovacao,
        codigo_servico,
        id_terminal_aceitante,
        id_aceitante,
        nome_local_aceitante,
        codigo_moeda,
        id_ciclo_vida_transacao,
        id_destino_instituicao_transacao,
        id_originadora_instituicao_transacao,
        tipo_terminal,
        ind_nivel_seguranca_comercio_eletronico,
        expoente_moeada,
        atividade_comercial,
        ind_liquidacao,
        info_consulta_aceitante,
        id_fiscal_est_comercial_brasil,
        ind_1_conciliacao_membro,
        produto,
        ird,
        tb_master_arquivo_id
    )
    FROM STDIN
    """

    def __init__(self) -> None:
        self._conn: Connection[TupleRow] = psycopg.connect(
            host=host,
            port=port,
            dbname=db_name,
            user=user,
            password=password,
        )
        self._cur: ServerCursor[TupleRow] = self._conn.cursor()
        self._parse: MastercardIso8583Parse = MastercardIso8583Parse()

    def _date_reference_file(self, file_name: str) -> str:

        file_name_split: List[str] = file_name.split("_")

        date_reference: str = datetime.strptime(file_name_split[-2], "%d%m%Y").strftime(
            "%d/%m/%Y"
        )

        return date_reference

    def iso_db(
        self,
        date_file: str,
        cycle: TypeCycleIpm,
        logging: bool = True,
    ) -> None:

        file_name: Optional[str] = None
        date_reference: Optional[str] = None
        arq_parse: Optional[List[List[TypeIpmDb]]] = None
        self._parse.search_ipm(date_file=date_file, cycle=cycle)

        parse: TypeParseIpmDb = self._parse.parse_ipm_db(logging=logging)

        if parse:
            arq_parse, file_name = parse
            file_name += ".TXT"

        if arq_parse and file_name:
            date_reference = self._date_reference_file(file_name)

            self._transaction_db(
                file_name=file_name,
                cycle=cycle,
                date_reference=date_reference,
                parse=arq_parse,
            )

        return None

    def _exists_file_master(self, file_name: str) -> bool:

        cur_result = self._cur.execute(self._EXISTS_FILE, (file_name,))

        if cur_result.fetchone():
            self._cur.close()

            self._conn.close()

            print(f"O arquivo {file_name}, já foi inserido no banco.")

            return True

        return False

    def _insert_file_db(
        self,
        file_name: str,
        cycle: str,
        date_reference: str,
        parse: List[List[TypeIpmDb]],
    ) -> None:

        arq_parse = parse

        try:
            self._cur.executemany(
                DbOutgouing._INSERT_SQL,
                [(file_name, cycle, date_reference)],
                returning=True,
            )

            row_id: Optional[Tuple[int]] = self._cur.fetchone()
            new_id = row_id[0] if row_id else 0

            with self._cur.copy(DbOutgouing._COPY_SQL) as copy:
                for row in arq_parse:
                    row.append(new_id)
                    copy.write_row(row)

            self._conn.commit()
            self._cur.close()
            self._conn.close()

            qtd_rows_insert: str = f"{len(arq_parse):,}".replace(",", ".")

            print(
                f"{qtd_rows_insert} de linhas do arquivo {file_name}, foram inseridas com sucesso na tabela TB_MASTER_ARQUIVO_DETALHADO."
            )

        except Exception as e:
            self._conn.rollback()

            self._cur.close()

            self._conn.close()

            print(f"Error: {e}")

        return None

    def _transaction_db(
        self,
        file_name: str,
        cycle: str,
        date_reference: str,
        parse: List[List[TypeIpmDb]],
    ) -> None:

        if not self._exists_file_master(file_name=file_name):
            self._insert_file_db(
                file_name=file_name,
                cycle=cycle,
                date_reference=date_reference,
                parse=parse,
            )

        return None
