from .models import Mentorados


def valida_token(token):
    return Mentorados.objects.filter(
        token=token
    ).first()  # caso a funcao retorne uma lista vazia [] será None
