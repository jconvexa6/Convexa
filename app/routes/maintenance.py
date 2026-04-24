"""
Plan de mantenimiento preventivo (CMMS) — modelo simplificado.
CRUD habilitado para Maquinas, Activos y Mantenimientos.
Historico solo lectura.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.maintenance_service import MaintenanceService

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/mantenimiento')

FULL_ACCESS_USERS = {"admin", "juanosorno", "oscarvelez", "danielsaenz"}
LIMITED_MTTO_EDIT_FIELDS = {"estado", "actividad", "tipo_mtto", "observaciones"}


def _labels():
    return {
        'maquinas': 'Máquinas',
        'activos': 'Activos mantenibles',
        'mantenimientos': 'Mantenimientos',
        'historico': 'Histórico de mantenimientos',
    }


def _is_full_access_user() -> bool:
    username = str(getattr(current_user, "username", "")).strip().lower()
    return username in FULL_ACCESS_USERS


def _can_create(section: str) -> bool:
    return _is_full_access_user() and section in MaintenanceService.CRUD_SECTIONS


def _can_edit(section: str) -> bool:
    if section not in MaintenanceService.CRUD_SECTIONS:
        return False
    if _is_full_access_user():
        return True
    return section == "mantenimientos"


def _can_delete(section: str) -> bool:
    return _is_full_access_user() and section in MaintenanceService.CRUD_SECTIONS


def _can_close_mantenimiento() -> bool:
    return _is_full_access_user()


def _is_limited_mantenimiento_editor(section: str) -> bool:
    return (not _is_full_access_user()) and section == "mantenimientos"


def _enforce_permission_or_redirect(section: str, action: str):
    allowed = False
    if action == "create":
        allowed = _can_create(section)
    elif action == "edit":
        allowed = _can_edit(section)
    elif action == "delete":
        allowed = _can_delete(section)
    elif action == "close":
        allowed = _can_close_mantenimiento()

    if allowed:
        return None

    flash("No tienes permisos para realizar esta acción.", "error")
    return redirect(url_for(f"maintenance.{section}" if action != "close" else "maintenance.mantenimientos"))


def _section(active_key: str, description: str, extra_note: str = ''):
    table_columns, table_rows, error_message = [], [], None
    id_col_index = None
    estado_col_index = None
    try:
        table_columns, table_rows = MaintenanceService.read_table(active_key)
        cols_norm = [str(c).strip().lower() for c in table_columns]
        # Detectar columna ID según sección
        id_candidates = {
            'maquinas': ['id_maquina', 'id'],
            'activos': ['id_activo', 'id'],
            'mantenimientos': ['id_mtto', 'id'],
            'historico': ['id_hist', 'id'],
        }.get(active_key, ['id'])
        for cand in id_candidates:
            if cand in cols_norm:
                id_col_index = cols_norm.index(cand)
                break
        # Detectar columna estado (solo si existe)
        if 'estado' in cols_norm:
            estado_col_index = cols_norm.index('estado')
    except Exception as e:
        error_message = f"Error al cargar datos: {e}"
    return render_template(
        'maintenance/section.html',
        active_section=active_key,
        section_title=_labels().get(active_key, active_key.title()),
        section_description=description,
        table_columns=table_columns,
        table_rows=table_rows,
        extra_note=extra_note,
        error_message=error_message,
        can_create=_can_create(active_key),
        can_edit=_can_edit(active_key),
        can_delete=_can_delete(active_key),
        can_close_mantenimiento=_can_close_mantenimiento(),
        id_col_index=id_col_index,
        estado_col_index=estado_col_index,
    )


def _crud_form(section: str, mode: str, record_id: str = None):
    action = "create" if mode == "crear" else "edit"
    denied = _enforce_permission_or_redirect(section, action)
    if denied:
        return denied

    if request.method == 'POST':
        payload = request.form.to_dict()
        if _is_limited_mantenimiento_editor(section):
            payload = {
                k: v for k, v in payload.items()
                if str(k).strip().lower() in LIMITED_MTTO_EDIT_FIELDS
            }
        if mode == 'crear':
            ok, msg = MaintenanceService.create_record(section, payload)
        else:
            ok, msg = MaintenanceService.update_record(section, record_id, payload)
        flash(msg, 'success' if ok else 'error')
        return redirect(url_for(f'maintenance.{section}'))

    fields = MaintenanceService.get_form_fields(section)
    record = {}
    if mode == 'editar':
        record = MaintenanceService.get_record(section, record_id) or {}
        if not record:
            flash(f'No se encontró el registro {record_id}.', 'error')
            return redirect(url_for(f'maintenance.{section}'))
        if _is_limited_mantenimiento_editor(section):
            fields = [
                f for f in fields
                if str(f).strip().lower() in LIMITED_MTTO_EDIT_FIELDS
            ]

    return render_template(
        'maintenance/form.html',
        active_section=section,
        mode=mode,
        section_key=section,
        section_label=_labels().get(section, section.title()),
        fields=fields,
        record=record,
        record_id=record_id,
    )


@maintenance_bp.route('/')
@login_required
def dashboard():
    kpis = MaintenanceService.compute_kpis()
    return render_template('maintenance/dashboard.html', active_section='dashboard', kpis=kpis)


@maintenance_bp.route('/maquinas')
@login_required
def maquinas():
    return _section('maquinas', 'Listado de máquinas con su ubicación, responsable y estado.')


@maintenance_bp.route('/maquinas/crear', methods=['GET', 'POST'])
@login_required
def maquinas_crear():
    return _crud_form('maquinas', 'crear')


@maintenance_bp.route('/maquinas/<record_id>/editar', methods=['GET', 'POST'])
@login_required
def maquinas_editar(record_id: str):
    return _crud_form('maquinas', 'editar', record_id)


@maintenance_bp.route('/maquinas/<record_id>/eliminar', methods=['POST'])
@login_required
def maquinas_eliminar(record_id: str):
    denied = _enforce_permission_or_redirect('maquinas', 'delete')
    if denied:
        return denied
    ok, msg = MaintenanceService.delete_record('maquinas', record_id)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('maintenance.maquinas'))


@maintenance_bp.route('/activos')
@login_required
def activos():
    return _section(
        'activos',
        'Elementos que requieren mantenimiento preventivo (máquina completa o componente).',
        extra_note='Tabla clave: id_activo, id_maquina, frecuencia_dias, ultima_fecha, proxima_fecha.',
    )


@maintenance_bp.route('/activos/crear', methods=['GET', 'POST'])
@login_required
def activos_crear():
    return _crud_form('activos', 'crear')


@maintenance_bp.route('/activos/<record_id>/editar', methods=['GET', 'POST'])
@login_required
def activos_editar(record_id: str):
    return _crud_form('activos', 'editar', record_id)


@maintenance_bp.route('/activos/<record_id>/eliminar', methods=['POST'])
@login_required
def activos_eliminar(record_id: str):
    denied = _enforce_permission_or_redirect('activos', 'delete')
    if denied:
        return denied
    ok, msg = MaintenanceService.delete_record('activos', record_id)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('maintenance.activos'))


@maintenance_bp.route('/mantenimientos')
@login_required
def mantenimientos():
    return _section(
        'mantenimientos',
        'Tabla viva editable con estados: PROGRAMADO, PENDIENTE, EN_PROCESO, HECHO, OMITIDO, REPROGRAMADO.',
        extra_note='Cuando un registro está en HECHO puede cerrarse para moverlo a histórico.',
    )


@maintenance_bp.route('/mantenimientos/crear', methods=['GET', 'POST'])
@login_required
def mantenimientos_crear():
    return _crud_form('mantenimientos', 'crear')


@maintenance_bp.route('/mantenimientos/<record_id>/editar', methods=['GET', 'POST'])
@login_required
def mantenimientos_editar(record_id: str):
    return _crud_form('mantenimientos', 'editar', record_id)


@maintenance_bp.route('/mantenimientos/<record_id>/eliminar', methods=['POST'])
@login_required
def mantenimientos_eliminar(record_id: str):
    denied = _enforce_permission_or_redirect('mantenimientos', 'delete')
    if denied:
        return denied
    ok, msg = MaintenanceService.delete_record('mantenimientos', record_id)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('maintenance.mantenimientos'))


@maintenance_bp.route('/historico')
@login_required
def historico():
    return _section(
        'historico',
        'Auditoría inmutable de mantenimientos cerrados.',
        extra_note='No debe editarse desde operación diaria.',
    )


@maintenance_bp.route('/mantenimiento/<mtto_id>/cerrar', methods=['POST'])
@login_required
def cerrar_mantenimiento(mtto_id: str):
    denied = _enforce_permission_or_redirect('mantenimientos', 'close')
    if denied:
        return denied
    cerrado_por = request.form.get('cerrado_por', '').strip() or getattr(current_user, 'username', 'Sistema')
    ok, msg = MaintenanceService.close_mantenimiento(mtto_id, cerrado_por)
    flash(msg, 'success' if ok else 'error')
    return redirect(url_for('maintenance.mantenimientos'))


# Estructura legacy removida intencionalmente:
# - /componentes
# - /componentes-maquina
# - /plan-mantenimiento
# - /ordenes
# - /historial
