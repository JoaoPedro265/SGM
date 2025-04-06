from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Mentorados, Navigators
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.


def mentorados(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "GET":
        navigators = Navigators.objects.filter(user=request.user)
        mentorados = Mentorados.objects.filter(user=request.user)

        estagios_flat = []
        qtd_estagios = []
        for item in Mentorados.estado_choices:
            estagios_flat.append(item[1])
        for i, j in Mentorados.estado_choices:
            x = Mentorados.objects.filter(estagio=i, user=request.user).count()
            qtd_estagios.append(x)
        return render(
            request,
            "mentorados.html",
            {
                "estagios": Mentorados.estado_choices,
                "navigators": navigators,
                "mentorados": mentorados,
                "estagios_flat": estagios_flat,
                "qtd_estagios": qtd_estagios,
            },
        )
    elif request.method == "POST":
        nome = request.POST.get("nome")
        foto = request.FILES.get("foto")  # .FILES formato de busca de arquivos
        estagio = request.POST.get("estagio")
        navigator = request.POST.get("navigator")

        mentorado = Mentorados(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user,
        )

        mentorado.save()

        messages.add_message(
            request, constants.SUCCESS, "Mentorado cadastrado com sucesso."
        )
        return redirect("mentorados")


def reunioes(request):
    if request.method == "GET":
        return render(request, "reunioes.html")
    elif request.method == "POST":
        pass
