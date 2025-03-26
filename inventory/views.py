# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
from .models import Component, Room, Cabinet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

# Homepage (acessível a todos)
def homepage(request):
    return render(request, 'inventory/homepage.html')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos!')
            return redirect('login')
    return render(request, 'inventory/login.html')

# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('homepage')

# Dashboard (protegido)
@login_required
def dashboard(request):
    query = request.GET.get('q')
    if query:
        # Filtra por nome do equipamento ou nome da sala
        componentes = Component.objects.filter(
            nome_equipamento__icontains=query
        ) | Component.objects.filter(
            sala_arrumacao__name__icontains=query
        )
    else:
        componentes = Component.objects.all()
    rooms = Room.objects.all()
    cabinets = Cabinet.objects.all()
    return render(request, 'inventory/dashboard.html', {
        'componentes': componentes,
        'rooms': rooms,
        'cabinets': cabinets
    })

# Registro de Componentes (protegido)
@login_required
def register_component(request):
    if request.method == 'POST':
        curso = request.POST.get('curso')
        disciplina = request.POST.get('disciplina')
        nome_equipamento = request.POST.get('nome_equipamento')
        categoria = request.POST.get('categoria')
        sub_categoria = request.POST.get('sub_categoria')
        descricao = request.POST.get('descricao')
        sala_arrumacao_id = request.POST.get('sala_arrumacao')
        armario_id = request.POST.get('armario')
        gaveta = request.POST.get('gaveta')
        localizacao_aberta = request.POST.get('localizacao_aberta')
        quantidade = request.POST.get('quantidade', 1)
        status = request.POST.get('status', 'ativo')
        foto = request.FILES.get('foto')

        # Validação dos campos obrigatórios
        if not all([curso, disciplina, nome_equipamento, categoria, descricao, sala_arrumacao_id, armario_id, quantidade]):
            messages.error(request, 'Preencha todos os campos obrigatórios!')
            return redirect('register_component')

        try:
            # Obter os objetos Room e Cabinet a partir dos IDs
            sala_arrumacao = Room.objects.get(id=sala_arrumacao_id)
            armario = Cabinet.objects.get(id=armario_id)

            # Validação: Verificar se o armário pertence à sala selecionada
            if armario.room != sala_arrumacao:
                messages.error(request, f'O armário "{armario.name}" pertence à sala "{armario.room.name}", mas você selecionou a sala "{sala_arrumacao.name}". Escolha um armário da mesma sala.')
                return redirect('register_component')

            # Criar o componente
            component = Component(
                curso=curso,
                disciplina=disciplina,
                nome_equipamento=nome_equipamento,
                categoria=categoria,
                sub_categoria=sub_categoria,
                descricao=descricao,
                sala_arrumacao=sala_arrumacao,
                armario=armario,
                gaveta=gaveta,
                localizacao_aberta=localizacao_aberta,
                quantidade=int(quantidade),
                status=status,
                foto=foto
            )
            component.save()
            messages.success(request, 'Equipamento criado com sucesso!')
            return redirect('dashboard')
        except Room.DoesNotExist:
            messages.error(request, 'Sala de arrumação não encontrada!')
            return redirect('register_component')
        except Cabinet.DoesNotExist:
            messages.error(request, 'Armário não encontrado!')
            return redirect('register_component')
        except ValueError:
            messages.error(request, 'Quantidade deve ser um número válido!')
            return redirect('register_component')
    else:
        rooms = Room.objects.all()
        cabinets = Cabinet.objects.all()
        return render(request, 'inventory/register_component.html', {
            'rooms': rooms,
            'cabinets': cabinets
        })

# Editar Componente (protegido)
@login_required
def edit_component(request, component_id):
    component = get_object_or_404(Component, id=component_id)
    if request.method == 'POST':
        curso = request.POST.get('curso', component.curso)
        disciplina = request.POST.get('disciplina', component.disciplina)
        nome_equipamento = request.POST.get('nome_equipamento', component.nome_equipamento)
        categoria = request.POST.get('categoria', component.categoria)
        sub_categoria = request.POST.get('sub_categoria', component.sub_categoria)
        descricao = request.POST.get('descricao', component.descricao)
        sala_arrumacao_id = request.POST.get('sala_arrumacao', component.sala_arrumacao.id)
        armario_id = request.POST.get('armario', component.armario.id)
        gaveta = request.POST.get('gaveta', component.gaveta)
        localizacao_aberta = request.POST.get('localizacao_aberta', component.localizacao_aberta)
        quantidade = request.POST.get('quantidade', component.quantidade)
        status = request.POST.get('status', component.status)
        foto = request.FILES.get('foto', component.foto)

        # Validação dos campos obrigatórios
        if not all([curso, disciplina, nome_equipamento, categoria, descricao, sala_arrumacao_id, armario_id, quantidade]):
            messages.error(request, 'Preencha todos os campos obrigatórios!')
            return redirect('edit_component', component_id=component_id)

        try:
            # Obter os objetos Room e Cabinet a partir dos IDs
            sala_arrumacao = Room.objects.get(id=sala_arrumacao_id)
            armario = Cabinet.objects.get(id=armario_id)

            # Validação: Verificar se o armário pertence à sala selecionada
            if armario.room != sala_arrumacao:
                messages.error(request, f'O armário "{armario.name}" pertence à sala "{armario.room.name}", mas você selecionou a sala "{sala_arrumacao.name}". Escolha um armário da mesma sala.')
                return redirect('edit_component', component_id=component_id)

            # Atualizar o componente
            component.curso = curso
            component.disciplina = disciplina
            component.nome_equipamento = nome_equipamento
            component.categoria = categoria
            component.sub_categoria = sub_categoria
            component.descricao = descricao
            component.sala_arrumacao = sala_arrumacao
            component.armario = armario
            component.gaveta = gaveta
            component.localizacao_aberta = localizacao_aberta
            component.quantidade = int(quantidade)
            component.status = status
            if foto:
                component.foto = foto
            component.save()
            messages.success(request, 'Equipamento atualizado com sucesso!')
            return redirect('dashboard')
        except Room.DoesNotExist:
            messages.error(request, 'Sala de arrumação não encontrada!')
            return redirect('edit_component', component_id=component_id)
        except Cabinet.DoesNotExist:
            messages.error(request, 'Armário não encontrado!')
            return redirect('edit_component', component_id=component_id)
        except ValueError:
            messages.error(request, 'Quantidade deve ser um número válido!')
            return redirect('edit_component', component_id=component_id)
    else:
        rooms = Room.objects.all()
        cabinets = Cabinet.objects.all()
        return render(request, 'inventory/edit_component.html', {
            'component': component,
            'rooms': rooms,
            'cabinets': cabinets
        })

# Apagar Componente (protegido)
@login_required
def delete_component(request, component_id):
    component = get_object_or_404(Component, id=component_id)
    if request.method == 'POST':
        component.delete()
        messages.success(request, 'Equipamento apagado com sucesso!')
        return redirect('dashboard')
    return render(request, 'inventory/delete_component.html', {'component': component})

# Dar Baixa (protegido)
@login_required
def give_low(request, component_id):
    component = get_object_or_404(Component, id=component_id)
    if request.method == 'POST':
        component.status = 'baixa'
        component.save()
        messages.success(request, 'Status alterado para baixa com sucesso!')
        return redirect('dashboard')
    return render(request, 'inventory/give_low.html', {'component': component})

# Criar Sala (protegido)
@login_required
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if Room.objects.filter(name=room_name).exists():
            messages.error(request, 'Esta sala já existe!')
        else:
            Room.objects.create(name=room_name)
            messages.success(request, 'Sala criada com sucesso!')
        return redirect('dashboard')
    return redirect('dashboard')

# Criar Armário (protegido)
@login_required
def create_cabinet(request):
    if request.method == 'POST':
        cabinet_name = request.POST.get('cabinet_name')
        room_id = request.POST.get('room_id')
        if not room_id:
            messages.error(request, 'Selecione uma sala!')
        elif Cabinet.objects.filter(name=cabinet_name, room_id=room_id).exists():
            messages.error(request, 'Este armário já existe nesta sala!')
        else:
            Cabinet.objects.create(name=cabinet_name, room_id=room_id)
            messages.success(request, 'Armário criado com sucesso!')
        return redirect('dashboard')
    return redirect('dashboard')

# Exportação para Excel (protegido)
@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventário"
    headers = ['Curso', 'Disciplina', 'Nome', 'Categoria', 'Sub-categoria', 'Descrição', 'Data de Registro', 'Sala', 'Armário', 'Gaveta', 'Localização', 'Quantidade', 'Status']
    ws.append(headers)
    for comp in Component.objects.all():
        ws.append([
            comp.curso, comp.disciplina, comp.nome_equipamento, comp.categoria, comp.sub_categoria,
            comp.descricao, str(comp.data_registo), comp.sala_arrumacao.name if comp.sala_arrumacao else '',
            comp.armario.name if comp.armario else '', comp.gaveta, comp.localizacao_aberta, comp.quantidade, comp.status
        ])
    wb.save(response)
    return response

# Exportação para PDF (protegido)
@login_required
def export_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(30, 800, "Relatório de Inventário")
    p.setFont("Helvetica", 10)
    y = 750
    headers = ['Curso', 'Disciplina', 'Nome', 'Categoria', 'Sub-categoria', 'Descrição', 'Data', 'Sala', 'Armário', 'Gaveta', 'Localização', 'Qtd', 'Status']
    x_positions = [30, 70, 110, 150, 190, 230, 270, 310, 350, 390, 430, 470, 510]
    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y, header)
    p.setFillColor(colors.grey)
    p.rect(30, y - 5, 540, 20, fill=True, stroke=False)
    p.setFillColor(colors.black)
    y -= 30

    for comp in Component.objects.all():
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 800
            for i, header in enumerate(headers):
                p.drawString(x_positions[i], y, header)
            p.setFillColor(colors.grey)
            p.rect(30, y - 5, 540, 20, fill=True, stroke=False)
            p.setFillColor(colors.black)
            y -= 30
        values = [
            comp.curso, comp.disciplina, comp.nome_equipamento, comp.categoria, comp.sub_categoria,
            comp.descricao[:20], str(comp.data_registo), comp.sala_arrumacao.name if comp.sala_arrumacao else '',
            comp.armario.name if comp.armario else '', comp.gaveta, comp.localizacao_aberta, str(comp.quantidade), comp.status
        ]
        for i, value in enumerate(values):
            p.drawString(x_positions[i], y, str(value))
        y -= 20

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventario.pdf"'
    response.write(pdf)
    return response

# Página de Exclusão (protegido)
@login_required
def delete_page(request):
    rooms = Room.objects.all()
    cabinets = Cabinet.objects.all()
    return render(request, 'inventory/delete.html', {
        'rooms': rooms,
        'cabinets': cabinets
    })

# Apagar Sala (protegido)
@login_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Verificar se há componentes associados à sala
    if Component.objects.filter(sala_arrumacao=room).exists():
        messages.error(request, f'Não é possível apagar a sala "{room.name}" porque ela tem componentes associados.')
    else:
        room.delete()
        messages.success(request, f'Sala "{room.name}" apagada com sucesso!')
    return redirect('delete_page')

# Apagar Armário (protegido)
@login_required
def delete_cabinet(request, cabinet_id):
    cabinet = get_object_or_404(Cabinet, id=cabinet_id)
    # Verificar se há componentes associados ao armário
    if Component.objects.filter(armario=cabinet).exists():
        messages.error(request, f'Não é possível apagar o armário "{cabinet.name}" porque ele tem componentes associados.')
    else:
        cabinet.delete()
        messages.success(request, f'Armário "{cabinet.name}" apagado com sucesso!')
    return redirect('delete_page')
