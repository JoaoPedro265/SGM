from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Mentorados, Navigators, DisponibilidadedeHorarios, Reuniao
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
import locale
from .auth import valida_token

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
        data = request.POST.get("data")  # é uma str
        data = datetime.strptime(data, "%Y-%m-%dT%H:%M")  # converter str para data

        disponibilidades = DisponibilidadedeHorarios.objects.filter(
            mentor=request.user,
            data_inicial__gte=(
                data - timedelta(minutes=50)
            ),  # já existe algum horario que seja MAIOR ou igual a data do agendamento - 50?
            data_inicial__lte=(
                data + timedelta(minutes=50)
            ),  # já existe algum horario que seja MENOR ou igual a data do agendamento + 50?
        )

        if disponibilidades.exists():
            messages.add_message(
                request, constants.ERROR, "Você já possui uma reunião em aberto."
            )
            return redirect("reunioes")
        disponibilidades = DisponibilidadedeHorarios(
            data_inicial=data, mentor=request.user
        )

        disponibilidades.save()
        messages.add_message(
            request, constants.SUCCESS, "Horário disponibilizado com sucesso."
        )
        return redirect("reunioes")


def auth(request):
    if request.method == "GET":
        return render(request, "auth_mentorado.html")
    elif request.method == "POST":
        token = request.POST.get("token")
        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request, constants.ERROR, "Token invalido")
            return redirect("auth_mentorado")
        response = redirect("mentorados")
        response.set_cookie("auth_token", token, max_age=3600)

        return response


# Tabelas com nomes em português
nomes_dias = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}

nomes_meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def escolher_dia(request):
    # Verifica se o usuário está logado
    if not valida_token(request.COOKIES.get("auth_token")):
        return redirect("auth_mentorado")

    if request.method == "GET":
        # Pega o mentorado com base no token
        mentorado = valida_token(request.COOKIES.get("auth_token"))
        # Pega as datas disponíveis a partir de hoje
        disponibilidades = DisponibilidadedeHorarios.objects.filter(
            data_inicial__gte=datetime.now(), agendado=False, mentor=mentorado.user
        ).values_list("data_inicial", flat=True)

        # Criar lista com informações organizadas
        datas = []
        datas_unicas = set([d.date() for d in disponibilidades])
        for data in datas_unicas:
            datas.append(
                {
                    "data_completa": data.strftime("%d-%m-%Y"),
                    "mes": nomes_meses[data.month],
                    "dia_semana": nomes_dias[data.weekday()],
                }
            )
        return render(request, "escolher_dia.html", {"horarios": datas})


def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get("auth_token")):
        return redirect("auth_mentorado")
    if request.method == "GET":
        data = request.GET.get("data")
        data = datetime.strptime(data, "%d-%m-%Y")  # converter str para formato data
        mentorado = valida_token(request.COOKIES.get("auth_token"))
        horarios = DisponibilidadedeHorarios.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False,
            mentor=mentorado.user,
        )

        return render(request, "agendar_reuniao.html", {"horarios": horarios})
