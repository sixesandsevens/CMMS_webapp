from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from app import db
from app.forms import LoginForm, RegistrationForm, AssetForm, WorkOrderForm
from app.models import User, Asset, WorkOrder

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    process_recurring_workorders()
    return render_template('index.html', title='Home')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


def process_recurring_workorders():
    """Create next work order for completed recurring tasks."""
    for wo in WorkOrder.query.filter(WorkOrder.recurring_interval_days != None, WorkOrder.status == 'Completed').all():
        next_due = wo.due_date + timedelta(days=wo.recurring_interval_days)
        exists = WorkOrder.query.filter_by(
            asset_id=wo.asset_id,
            title=wo.title,
            due_date=next_due,
        ).first()
        if not exists:
            new_wo = WorkOrder(
                title=wo.title,
                description=wo.description,
                asset_id=wo.asset_id,
                assigned_to=wo.assigned_to,
                status='Open',
                priority=wo.priority,
                due_date=next_due,
                recurring_interval_days=wo.recurring_interval_days,
            )
            db.session.add(new_wo)
    db.session.commit()


@bp.route('/assets')
@login_required
def assets():
    asset_list = Asset.query.all()
    return render_template('assets.html', title='Assets', assets=asset_list)


@bp.route('/asset/create', methods=['GET', 'POST'])
@login_required
def create_asset():
    form = AssetForm()
    if form.validate_on_submit():
        asset = Asset(
            name=form.name.data,
            location=form.location.data,
            serial_number=form.serial_number.data,
            description=form.description.data,
        )
        db.session.add(asset)
        db.session.commit()
        flash('Asset created')
        return redirect(url_for('main.assets'))
    return render_template('asset_form.html', title='Create Asset', form=form)


@bp.route('/asset/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_asset(id):
    asset = Asset.query.get_or_404(id)
    form = AssetForm(obj=asset)
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.location = form.location.data
        asset.serial_number = form.serial_number.data
        asset.description = form.description.data
        db.session.commit()
        flash('Asset updated')
        return redirect(url_for('main.assets'))
    return render_template('asset_form.html', title='Edit Asset', form=form)


@bp.route('/asset/<int:id>/delete', methods=['POST'])
@login_required
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted')
    return redirect(url_for('main.assets'))


@bp.route('/work_orders')
@login_required
def work_orders():
    process_recurring_workorders()
    orders = WorkOrder.query.order_by(WorkOrder.due_date).all()
    return render_template('work_orders.html', title='Work Orders', work_orders=orders)


def _populate_workorder_choices(form):
    form.asset_id.choices = [(a.id, a.name) for a in Asset.query.all()]
    form.assigned_to.choices = [(u.id, u.username) for u in User.query.all()]


@bp.route('/work_order/create', methods=['GET', 'POST'])
@login_required
def create_work_order():
    form = WorkOrderForm()
    _populate_workorder_choices(form)
    if form.validate_on_submit():
        due = form.due_date.data
        if due:
            due_datetime = datetime.combine(due, datetime.min.time())
        else:
            due_datetime = None
        wo = WorkOrder(
            title=form.title.data,
            description=form.description.data,
            asset_id=form.asset_id.data,
            assigned_to=form.assigned_to.data,
            priority=form.priority.data,
            status=form.status.data,
            due_date=due_datetime,
            recurring_interval_days=form.recurring_interval_days.data,
        )
        db.session.add(wo)
        db.session.commit()
        flash('Work order created')
        return redirect(url_for('main.work_orders'))
    return render_template('work_order_form.html', title='Create Work Order', form=form)


@bp.route('/work_order/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_work_order(id):
    wo = WorkOrder.query.get_or_404(id)
    form = WorkOrderForm(obj=wo)
    _populate_workorder_choices(form)
    if form.validate_on_submit():
        due = form.due_date.data
        wo.title = form.title.data
        wo.description = form.description.data
        wo.asset_id = form.asset_id.data
        wo.assigned_to = form.assigned_to.data
        wo.priority = form.priority.data
        wo.status = form.status.data
        wo.due_date = datetime.combine(due, datetime.min.time()) if due else None
        wo.recurring_interval_days = form.recurring_interval_days.data
        db.session.commit()
        flash('Work order updated')
        return redirect(url_for('main.work_orders'))
    # set defaults
    if wo.due_date:
        form.due_date.data = wo.due_date.date()
    return render_template('work_order_form.html', title='Edit Work Order', form=form)


@bp.route('/work_order/<int:id>/delete', methods=['POST'])
@login_required
def delete_work_order(id):
    wo = WorkOrder.query.get_or_404(id)
    db.session.delete(wo)
    db.session.commit()
    flash('Work order deleted')
    return redirect(url_for('main.work_orders'))
