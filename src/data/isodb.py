import os
from datetime import datetime
from types import TracebackType
from typing import Callable, Dict, List, Literal, Optional, Self, Tuple

import psycopg
from dotenv import load_dotenv
from psycopg import Connection, ServerCursor
from psycopg.rows import TupleRow
from rich import print

from ..core import MC8583
from ..models import (
    TypeCycleIpm,
    TypeIpmDb,
    TypeParseIpmDb,
)
from ..utils import print_custom_text


class DB8583:
    load_dotenv()
    _host: Optional[str] = os.getenv("DB_HOST")
    _port: Optional[str] = os.getenv("DB_PORT")
    _db_name: Optional[str] = os.getenv("DB_NAME")
    _user: Optional[str] = os.getenv("DB_USERNAME")
    _password: Optional[str] = os.getenv("DB_PASSWORD")

    _FILE_EXISTS_SQL = """SELECT 1 
                        FROM hdg.tb_master_arquivo tma 
                       WHERE tma.data_referencia = %s 
                         AND tma.ciclo = %s"""

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
        self._conn: Optional[Connection[TupleRow]] = None
        self._cur: Optional[ServerCursor[TupleRow]] = None
        self._parse: MC8583 = MC8583()

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:

        if exc_type and self._conn:
            self._conn.rollback()

        if exc_type is None:
            self.close()

    def connect(
        self,
    ) -> Optional[ServerCursor[TupleRow]]:

        if self._conn:
            return self._cur

        self._conn = psycopg.connect(
            host=self._host,
            port=self._port,
            dbname=self._db_name,
            user=self._user,
            password=self._password,
        )
        self._cur = self._conn.cursor()
        return self._cur

    def close(
        self,
    ) -> None:
        exec: Optional[List[Callable[[], None]]] = None
        if self._conn and self._cur:
            exec = [
                self._conn.commit,
                self._cur.close,
                self._conn.close,
            ]
            for exe in exec:
                exe()
        self._conn, self._cur = None, None

    def iso_db(
        self,
        file_date: str,
        cycle: TypeCycleIpm,
        logging: bool = True,
    ) -> None:

        file_name: Optional[str] = None
        reference_date: Optional[str] = None
        arq_parse: Optional[List[List[TypeIpmDb]]] = None
        self._parse.search_ipm(file_date=file_date, cycle=cycle)

        parse: TypeParseIpmDb = self._parse.parse_ipm_db(logging=logging)

        if parse:
            arq_parse, file_name = parse
            file_name += ".TXT"

        if arq_parse and file_name:
            reference_date = self._file_reference_date(file_name)

            self._transaction_db(
                file_name=file_name,
                cycle=cycle,
                reference_date=reference_date,
                parse=arq_parse,
            )

        return None

    def _file_reference_date(self, file_name: str) -> str:

        file_name_split: List[str] = file_name.split("_")

        reference_date: str = datetime.strptime(file_name_split[-2], "%d%m%Y").strftime(
            "%d/%m/%Y"
        )

        return reference_date

    def _logging(
        self, data: Dict[str, str], model: Literal["insert", "select"]
    ) -> None:

        rows_insert: List[str] = ["🗂️ Inserted ", " rows into database (from ", ")."]
        rows_select: List[str] = ["📄 File ", " already in DB."]

        if model == "select":
            print_custom_text(
                "    ◉ ",
                color_foreground="White",
                end="",
            )

            for idx, row in enumerate(rows_select):
                print_custom_text(
                    row,
                    color_foreground="Red",
                    end="",
                )
                if not idx:
                    print_custom_text(
                        f"'{data['file_name']}'",
                        color_foreground="White",
                        end="",
                    )
            print("\n\n")

        if model == "insert":
            print_custom_text(
                "    ◉ ",
                color_foreground="White",
                end="",
            )
            for idx, row in enumerate(rows_insert):
                print_custom_text(
                    row,
                    color_foreground="Red",
                    end="",
                )
                if not idx:
                    print_custom_text(
                        data["row_count_insert"],
                        color_foreground="White",
                        end="",
                    )
                if idx == len(rows_insert) - 2:
                    print_custom_text(
                        f"'{data['file_name']}'",
                        color_foreground="White",
                        end="",
                    )
            print("\n\n")

    def _exists_file_master(
        self,
        file_name: str,
        cycle: str,
        reference_date: str,
    ) -> bool:

        cur_result: Optional[ServerCursor] = None

        if self._conn and self._cur:
            cur_result = self._cur.execute(
                self._FILE_EXISTS_SQL, (reference_date, cycle)
            )
            if cur_result.fetchone():
                self._logging(data={"file_name": file_name}, model="select")
                return True
        return False

    def _insert_file_db(
        self,
        file_name: str,
        cycle: str,
        reference_date: str,
        parse: List[List[TypeIpmDb]],
    ) -> None:

        arq_parse = parse
        row_id: Optional[Tuple[int]] = None
        new_id: Optional[int] = None
        row_count_insert: Optional[str] = None

        if self._conn and self._cur:
            try:
                self._cur.executemany(
                    query=DB8583._INSERT_SQL,
                    params_seq=[(file_name, cycle, reference_date)],
                    returning=True,
                )

                row_id = self._cur.fetchone()
                new_id = row_id[0] if row_id else 0

                with self._cur.copy(DB8583._COPY_SQL) as copy:
                    for row in arq_parse:
                        row.append(new_id)
                        copy.write_row(row)

                row_count_insert = f"{len(arq_parse):,}".replace(",", ".")

                self._logging(
                    data={"file_name": file_name, "row_count_insert": row_count_insert},
                    model="insert",
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
        reference_date: str,
        parse: List[List[TypeIpmDb]],
    ) -> None:

        if not self._exists_file_master(
            file_name=file_name, cycle=cycle, reference_date=reference_date
        ):
            self._insert_file_db(
                file_name=file_name,
                cycle=cycle,
                reference_date=reference_date,
                parse=parse,
            )

        return None
