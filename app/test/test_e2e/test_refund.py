import datetime

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, RefundRequest, User
from app.test.test_e2e.base import BaseE2ETest


class RefundBaseTest(BaseE2ETest):
    """Clase base específica para tests de solicitudes de reembolso"""

    def setUp(self):
        super().setUp()

        # Crear usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear usuario regular
        self.regular_user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="password123",
            is_organizer=False,
        )

        # Crear evento de prueba
        event_date = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 10))
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento",
            scheduled_at=event_date,
            organizer=self.organizer,
        )

    def _create_refund_request(self, user, ticket_code='12345', reason='Motivo de prueba', status='pendiente'):
        """Método auxiliar para crear solicitudes de reembolso"""
        return RefundRequest.objects.create(
            user=user,
            ticket_code=ticket_code,
            reason=reason,
            status=status,
        )


class RefundPendingValidationTest(RefundBaseTest):
    """Tests relacionados con la validación de solicitudes pendientes"""

    def setUp(self):
        super().setUp()
        
        # Crear una solicitud pendiente para el usuario regular
        self.pending_refund = self._create_refund_request(
            user=self.regular_user,
            ticket_code='12345',
            reason='Motivo de prueba inicial',
            status='pendiente'
        )

    def test_cannot_create_refund_with_pending_request(self):
        """Test que verifica que no se puede crear una nueva solicitud cuando ya existe una pendiente"""
        # Iniciar sesión como usuario regular
        self.login_user("usuario", "password123")
        
        # Ir a la lista de solicitudes de reembolso
        self.page.goto(f"{self.live_server_url}/refunds/")
        
        # Verificar que la página se carga correctamente
        header = self.page.locator("h1")
        expect(header).to_have_text("Solicitudes de Reembolso")
        expect(header).to_be_visible()
        
        # Verificar que existe una solicitud pendiente en la tabla
        rows = self.page.locator("table tbody tr")
        expect(rows).to_have_count(1)
        
        # Verificar que la solicitud tiene estado pendiente
        status_badge = self.page.locator(".badge.bg-warning")
        expect(status_badge).to_be_visible()
        expect(status_badge).to_have_text("Pendiente")
        
        # Intentar crear una nueva solicitud clickeando el botón "Nueva Solicitud"
        new_refund_button = self.page.locator("#btn-new-refund")
        expect(new_refund_button).to_be_visible()
        new_refund_button.click()
        
        # Verificar que permanecemos en la página de lista (no redirige al formulario)
        expect(self.page).to_have_url(f"{self.live_server_url}/refunds/")
        
        # Verificar que aparece el mensaje de advertencia
        warning_alert = self.page.locator(".alert.alert-warning")
        expect(warning_alert).to_be_visible()
        expect(warning_alert).to_have_text("Ya tienes una solicitud de reembolso pendiente.")
        
        # Verificar que el formulario no se muestra
        expect(self.page.locator("#refund-form")).not_to_be_visible()
        
        # Verificar que el botón de cerrar alerta funciona
        close_button = warning_alert.locator(".btn-close")
        expect(close_button).to_be_visible()
        close_button.click()
        expect(warning_alert).not_to_be_visible()

    def test_can_create_refund_when_no_pending_request(self):
        """Test que verifica que SÍ se puede crear una solicitud cuando no hay ninguna pendiente"""
        # Cambiar el estado de la solicitud existente a 'aprobado'
        self.pending_refund.status = 'aprobado'
        self.pending_refund.save()
        
        # Iniciar sesión como usuario regular
        self.login_user("usuario", "password123")
        
        # Ir a la lista de solicitudes
        self.page.goto(f"{self.live_server_url}/refunds/")
        
        # Verificar que la solicitud existente ya no está pendiente
        status_badge = self.page.locator(".badge.bg-success")
        expect(status_badge).to_be_visible()
        expect(status_badge).to_have_text("Aprobado")
        
        # Clickear el botón "Nueva Solicitud"
        self.page.locator("#btn-new-refund").click()
        
        # Verificar que nos redirige al formulario de creación
        expect(self.page).to_have_url(f"{self.live_server_url}/refunds/create/")
        
        # Verificar que el formulario se muestra correctamente
        form_header = self.page.locator("h2")
        expect(form_header).to_have_text("Solicitar Reembolso")
        expect(form_header).to_be_visible()
        
        # Verificar elementos del formulario
        expect(self.page.locator("#refund-form")).to_be_visible()
        expect(self.page.locator("#id_ticket_code")).to_be_visible()
        expect(self.page.locator("#id_reason")).to_be_visible()
        expect(self.page.locator("#btn-submit-refund")).to_be_visible()

    def test_can_create_refund_when_previous_rejected(self):
        """Test que verifica que se puede crear una nueva solicitud cuando la anterior fue rechazada"""
        # Cambiar el estado a 'rechazado'
        self.pending_refund.status = 'rechazado'
        self.pending_refund.save()
        
        # Iniciar sesión como usuario regular
        self.login_user("usuario", "password123")
        
        # Ir a la lista de solicitudes
        self.page.goto(f"{self.live_server_url}/refunds/")
        
        # Verificar estado rechazado
        status_badge = self.page.locator(".badge.bg-danger")
        expect(status_badge).to_be_visible()
        expect(status_badge).to_have_text("Rechazado")
        
        # Intentar crear nueva solicitud - debería funcionar
        self.page.locator("#btn-new-refund").click()
        expect(self.page).to_have_url(f"{self.live_server_url}/refunds/create/")

    def test_multiple_refunds_only_pending_blocks(self):
        """Test que verifica que solo las solicitudes pendientes bloquean la creación de nuevas"""
        # Crear solicitudes adicionales con diferentes estados
        self._create_refund_request(
            user=self.regular_user,
            ticket_code='54321',
            reason='Segunda solicitud',
            status='aprobado'
        )
        
        self._create_refund_request(
            user=self.regular_user,
            ticket_code='67890',
            reason='Tercera solicitud',
            status='rechazado'
        )
        
        # Iniciar sesión como usuario regular
        self.login_user("usuario", "password123")
        
        # Ir a la lista de solicitudes
        self.page.goto(f"{self.live_server_url}/refunds/")
        
        # Verificar que hay 3 solicitudes en la tabla
        rows = self.page.locator("table tbody tr")
        expect(rows).to_have_count(3)
        
        # Verificar que los diferentes estados están presentes
        expect(self.page.locator(".badge.bg-warning")).to_have_count(1)  # Pendiente
        expect(self.page.locator(".badge.bg-success")).to_have_count(1)  # Aprobado
        expect(self.page.locator(".badge.bg-danger")).to_have_count(1)   # Rechazado
        
        # Intentar crear nueva solicitud - debería estar bloqueado por la pendiente
        self.page.locator("#btn-new-refund").click()
        
        # Verificar que permanece en la lista y muestra el mensaje de advertencia
        expect(self.page).to_have_url(f"{self.live_server_url}/refunds/")
        warning_alert = self.page.locator(".alert.alert-warning")
        expect(warning_alert).to_be_visible()
        expect(warning_alert).to_have_text("Ya tienes una solicitud de reembolso pendiente.")


