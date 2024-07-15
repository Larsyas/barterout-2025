from django.contrib.auth import get_user_model

from accounts.models import Account


def tcm_wallet(request):
    TCM_wallet = 0  # Valor padrão se o usuário não estiver logado ou se não houver TCM_wallet definido

    if request.user.is_authenticated:
        user = Account.objects.get(pk=request.user.pk)
        TCM_wallet = user.TCM_wallet

    return {'TCM_wallet': TCM_wallet}
