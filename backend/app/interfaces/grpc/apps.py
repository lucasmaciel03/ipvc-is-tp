from django.apps import AppConfig


class GrpcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.interfaces.grpc'
    verbose_name = 'gRPC Interface'
