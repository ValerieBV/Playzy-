from django.apps import AppConfig


class KhohangConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Khohang'
    verbose_name = "Kho hàng"
    
    def ready(self):
        import Khohang.signals  # Đăng ký signals