"""
Servicios de mantenimiento preventivo (modelo simplificado):
MAQUINAS -> ACTIVOS_MANTENIBLES -> MANTENIMIENTOS -> HISTORICO_MANTENIMIENTOS
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple, Optional

import pandas as pd
from googleapiclient.discovery import build

from config import Config
from app.services.sheets_service import SheetsService
from app.services.sheets_writer import get_credentials, get_sheet_id_from_url


class MaintenanceService:
    CRUD_SECTIONS = {"maquinas", "activos", "mantenimientos"}

    @staticmethod
    def sheet_urls() -> Dict[str, str]:
        return {
            "maquinas": Config.MAINTENANCE_SHEET_MAQUINAS,
            "activos": Config.MAINTENANCE_SHEET_ACTIVOS,
            "mantenimientos": Config.MAINTENANCE_SHEET_MANTENIMIENTOS,
            "historico": Config.MAINTENANCE_SHEET_HISTORICO_MANTENIMIENTOS,
        }

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> Dict[str, str]:
        return {str(c).strip().lower(): c for c in df.columns}

    @staticmethod
    def _col_letter(index: int) -> str:
        # 0 -> A, 25 -> Z, 26 -> AA
        result = ""
        index += 1
        while index > 0:
            index, rem = divmod(index - 1, 26)
            result = chr(65 + rem) + result
        return result

    @staticmethod
    def _get_sheet_service():
        creds = get_credentials()
        return build("sheets", "v4", credentials=creds)

    @staticmethod
    def _get_sheet_headers(section: str) -> List[str]:
        urls = MaintenanceService.sheet_urls()
        sheet_id = get_sheet_id_from_url(urls[section])
        service = MaintenanceService._get_sheet_service()
        resp = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range="A1:ZZ1")
            .execute()
        )
        headers = resp.get("values", [[]])[0]
        return [str(h).strip() for h in headers]

    @staticmethod
    def _read_df(section: str) -> pd.DataFrame:
        urls = MaintenanceService.sheet_urls()
        return SheetsService.read_google_sheet(urls[section])

    @staticmethod
    def _find_record_row(section: str, record_id: str) -> Tuple[Optional[int], Optional[str], Optional[pd.DataFrame]]:
        df = MaintenanceService._read_df(section)
        if df is None or df.empty:
            return None, None, df
        cols = MaintenanceService._normalize_columns(df)
        id_col = cols.get("id_maquina") or cols.get("id_activo") or cols.get("id_mtto") or cols.get("id")
        if not id_col:
            return None, None, df
        record_id = str(record_id).strip()
        matches = df[df[id_col].astype(str).str.strip() == record_id]
        if matches.empty:
            return None, id_col, df
        row_pos = int(matches.index[0]) + 2  # 1-based + header
        return row_pos, id_col, df

    @staticmethod
    def get_form_fields(section: str) -> List[str]:
        headers = MaintenanceService._get_sheet_headers(section)
        # campos de auditoría gestionados por backend
        hidden = {"fecha_creacion", "fecha_actualizacion"}
        return [h for h in headers if str(h).strip().lower() not in hidden]

    @staticmethod
    def get_record(section: str, record_id: str) -> Optional[Dict[str, str]]:
        row_pos, id_col, df = MaintenanceService._find_record_row(section, record_id)
        if not row_pos or df is None:
            return None
        row = df.iloc[row_pos - 2]
        result = {}
        for col in df.columns:
            result[str(col)] = "" if pd.isna(row[col]) else str(row[col]).strip()
        return result

    @staticmethod
    def _auto_fill_fields(section: str, data: Dict[str, str], is_update: bool = False) -> Dict[str, str]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        out = dict(data)
        keys_norm = {str(k).strip().lower(): k for k in out.keys()}
        if not is_update:
            if "fecha_creacion" in keys_norm:
                out[keys_norm["fecha_creacion"]] = now
        if "fecha_actualizacion" in keys_norm:
            out[keys_norm["fecha_actualizacion"]] = now
        return out

    @staticmethod
    def create_record(section: str, data: Dict[str, str]) -> Tuple[bool, str]:
        if section not in MaintenanceService.CRUD_SECTIONS:
            return False, "Sección no habilitada para crear."
        headers = MaintenanceService._get_sheet_headers(section)
        if not headers:
            return False, "No se encontraron encabezados en la hoja."
        payload = MaintenanceService._auto_fill_fields(section, data, is_update=False)
        values = []
        for h in headers:
            value = ""
            for k, v in payload.items():
                if str(k).strip().lower() == str(h).strip().lower():
                    value = "" if v is None else str(v)
                    break
            values.append(value)

        service = MaintenanceService._get_sheet_service()
        sheet_id = get_sheet_id_from_url(MaintenanceService.sheet_urls()[section])
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A:ZZ",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [values]},
        ).execute()
        return True, "Registro creado correctamente."

    @staticmethod
    def update_record(section: str, record_id: str, data: Dict[str, str]) -> Tuple[bool, str]:
        if section not in MaintenanceService.CRUD_SECTIONS:
            return False, "Sección no habilitada para editar."
        row_pos, id_col, df = MaintenanceService._find_record_row(section, record_id)
        if not row_pos:
            return False, f"No se encontró el registro {record_id}."
        headers = [str(c).strip() for c in df.columns]
        payload = MaintenanceService._auto_fill_fields(section, data, is_update=True)

        # preservar ID original
        if id_col:
            for k in list(payload.keys()):
                if str(k).strip().lower() == str(id_col).strip().lower():
                    payload[k] = record_id

        values = []
        row_current = df.iloc[row_pos - 2]
        for h in headers:
            found = False
            for k, v in payload.items():
                if str(k).strip().lower() == str(h).strip().lower():
                    values.append("" if v is None else str(v))
                    found = True
                    break
            if not found:
                cur = row_current[h]
                values.append("" if pd.isna(cur) else str(cur))

        service = MaintenanceService._get_sheet_service()
        sheet_id = get_sheet_id_from_url(MaintenanceService.sheet_urls()[section])
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"A{row_pos}:ZZ{row_pos}",
            valueInputOption="RAW",
            body={"values": [values]},
        ).execute()
        return True, "Registro actualizado correctamente."

    @staticmethod
    def delete_record(section: str, record_id: str) -> Tuple[bool, str]:
        if section not in MaintenanceService.CRUD_SECTIONS:
            return False, "Sección no habilitada para eliminar."
        row_pos, _, _ = MaintenanceService._find_record_row(section, record_id)
        if not row_pos:
            return False, f"No se encontró el registro {record_id}."

        service = MaintenanceService._get_sheet_service()
        spreadsheet_id = get_sheet_id_from_url(MaintenanceService.sheet_urls()[section])
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        first_sheet = meta["sheets"][0]["properties"]
        sheet_gid = first_sheet["sheetId"]
        start_index = row_pos - 1
        end_index = row_pos
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": sheet_gid,
                                "dimension": "ROWS",
                                "startIndex": start_index,
                                "endIndex": end_index,
                            }
                        }
                    }
                ]
            },
        ).execute()
        return True, "Registro eliminado correctamente."

    @staticmethod
    def read_table(key: str) -> Tuple[List[str], List[List[str]]]:
        urls = MaintenanceService.sheet_urls()
        df = SheetsService.read_google_sheet(urls[key])
        if df is None or df.empty:
            return [], []
        df = df.where(pd.notna(df), "")
        columns = [str(c).strip() for c in df.columns.tolist()]
        rows = [[str(row[c]).strip() for c in df.columns] for _, row in df.iterrows()]
        return columns, rows

    @staticmethod
    def compute_kpis() -> Dict[str, int]:
        kpis = {
            "total_maquinas": 0,
            "total_activos": 0,
            "programados": 0,
            "pendientes": 0,
            "en_proceso": 0,
            "hechos": 0,
            "historicos": 0,
        }
        urls = MaintenanceService.sheet_urls()
        try:
            maq_df = SheetsService.read_google_sheet(urls["maquinas"])
            if maq_df is not None and not maq_df.empty:
                kpis["total_maquinas"] = len(maq_df.index)

            act_df = SheetsService.read_google_sheet(urls["activos"])
            if act_df is not None and not act_df.empty:
                kpis["total_activos"] = len(act_df.index)

            mtto_df = SheetsService.read_google_sheet(urls["mantenimientos"])
            if mtto_df is not None and not mtto_df.empty:
                cols = MaintenanceService._normalize_columns(mtto_df)
                estado_col = cols.get("estado")
                if estado_col:
                    estados = mtto_df[estado_col].astype(str).str.strip().str.upper()
                    kpis["programados"] = int((estados == "PROGRAMADO").sum())
                    kpis["pendientes"] = int((estados == "PENDIENTE").sum())
                    kpis["en_proceso"] = int((estados == "EN_PROCESO").sum())
                    kpis["hechos"] = int((estados == "HECHO").sum())

            hist_df = SheetsService.read_google_sheet(urls["historico"])
            if hist_df is not None and not hist_df.empty:
                kpis["historicos"] = len(hist_df.index)
        except Exception:
            pass
        return kpis

    @staticmethod
    def close_mantenimiento(mtto_id: str, cerrado_por: str) -> Tuple[bool, str]:
        """
        Cierra un mantenimiento HECHO:
        1) Copia snapshot al histórico
        2) Marca estado operativo como CERRADO_EN_HISTORICO (no editable)
        """
        urls = MaintenanceService.sheet_urls()
        df = SheetsService.read_google_sheet(urls["mantenimientos"])
        if df is None or df.empty:
            return False, "No hay mantenimientos para cerrar."

        cols = MaintenanceService._normalize_columns(df)
        id_col = cols.get("id_mtto") or cols.get("id")
        estado_col = cols.get("estado")
        if not id_col or not estado_col:
            return False, "La hoja de mantenimientos debe tener columnas id_mtto e estado."

        mtto_id = str(mtto_id).strip()
        match = df[df[id_col].astype(str).str.strip() == mtto_id]
        if match.empty:
            return False, f"No se encontró el mantenimiento {mtto_id}."

        row = match.iloc[0]
        row_pos = int(match.index[0]) + 2  # +2: header + 1-index
        estado = str(row[estado_col]).strip().upper()
        if estado != "HECHO":
            return False, "Solo se puede cerrar un mantenimiento con estado HECHO."

        # Construir snapshot para histórico
        snapshot = {
            "id_mtto_original": row.get(id_col, ""),
            "id_activo": row.get(cols.get("id_activo", ""), ""),
            "fecha_programada": row.get(cols.get("fecha_programada", ""), ""),
            "fecha_ejecucion": row.get(cols.get("fecha_ejecucion", ""), ""),
            "tipo_mtto": row.get(cols.get("tipo_mtto", ""), ""),
            "tecnico": row.get(cols.get("tecnico", ""), ""),
            "actividad": row.get(cols.get("actividad", ""), ""),
            "observaciones": row.get(cols.get("observaciones", ""), ""),
            "cerrado_por": cerrado_por,
            "fecha_cierre": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": 1,
        }

        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        # 1) Append en histórico respetando headers reales
        hist_id = get_sheet_id_from_url(urls["historico"])
        hist_headers_resp = service.spreadsheets().values().get(
            spreadsheetId=hist_id,
            range="A1:ZZ1",
        ).execute()
        hist_headers = hist_headers_resp.get("values", [[]])[0]
        if not hist_headers:
            return False, "La hoja de histórico no tiene encabezados."

        hist_values = []
        for h in hist_headers:
            hv = str(h).strip().lower()
            value = ""
            for k, v in snapshot.items():
                if str(k).strip().lower() == hv:
                    value = "" if pd.isna(v) else str(v)
                    break
            hist_values.append(value)

        service.spreadsheets().values().append(
            spreadsheetId=hist_id,
            range="A:ZZ",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [hist_values]},
        ).execute()

        # 2) Bloquear el registro operativo cambiando estado
        mtto_sheet_id = get_sheet_id_from_url(urls["mantenimientos"])
        estado_col_idx = list(df.columns).index(cols["estado"])
        estado_letter = chr(ord("A") + estado_col_idx)
        service.spreadsheets().values().update(
            spreadsheetId=mtto_sheet_id,
            range=f"{estado_letter}{row_pos}",
            valueInputOption="RAW",
            body={"values": [["CERRADO_EN_HISTORICO"]]},
        ).execute()

        # fecha_actualizacion si existe
        fecha_act_col = cols.get("fecha_actualizacion")
        if fecha_act_col:
            fecha_idx = list(df.columns).index(fecha_act_col)
            fecha_letter = chr(ord("A") + fecha_idx)
            service.spreadsheets().values().update(
                spreadsheetId=mtto_sheet_id,
                range=f"{fecha_letter}{row_pos}",
                valueInputOption="RAW",
                body={"values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]},
            ).execute()

        return True, f"Mantenimiento {mtto_id} cerrado y movido al histórico."

