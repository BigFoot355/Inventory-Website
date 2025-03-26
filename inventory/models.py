from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nome da sala, ex: Sala 1")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cabinet(models.Model):
    name = models.CharField(max_length=100, help_text="Nome do armário, ex: Armário A")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='cabinets')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.room.name})"

class Component(models.Model):
    curso = models.CharField(max_length=100)
    disciplina = models.CharField(max_length=100)
    nome_equipamento = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    sub_categoria = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField()
    data_registo = models.DateField(auto_now_add=True)
    sala_arrumacao = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='components')
    armario = models.ForeignKey(Cabinet, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='components')
    gaveta = models.CharField(max_length=50, blank=True, null=True)
    localizacao_aberta = models.CharField(max_length=200, blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[('ativo', 'Ativo'), ('baixa', 'Baixa')], default='ativo')
    foto = models.ImageField(upload_to='fotos_componentes/', blank=True, null=True)

    def __str__(self):
        return self.nome_equipamento