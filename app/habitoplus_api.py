# habitoplus_api.py
# Simulação do backend do módulo HábitoPlus — CarePlus
#
# AVISO: Este arquivo contém vulnerabilidades INTENCIONAIS
# inseridas exclusivamente para fins de demonstração acadêmica
# de ferramentas de segurança (SAST, SCA, Secret Scan).
# Cada vulnerabilidade corresponde a um risco mapeado na
# análise de ameaças STRIDE do projeto.

import hashlib
import sqlite3
import subprocess
import os

# ==============================================================
# VULNERABILIDADE 1 — Credencial hardcoded (Gitleaks + Bandit)
# Risco STRIDE: Information Disclosure
# Risco mapeado na Fase 1: Exposição de credenciais no código
# ==============================================================
DATABASE_PASSWORD = "habitoplus_admin_2024"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
JWT_SECRET = "minha-chave-jwt-super-secreta-habitoplus"

# ==============================================================
# VULNERABILIDADE 2 — Hash de senha com MD5 (algoritmo inseguro)
# Risco STRIDE: Tampering
# Risco mapeado na Fase 1: Manipulação do sistema de pontos
# ==============================================================
def hash_senha_usuario(senha):
    """
    INSEGURO: MD5 não deve ser usado para hash de senhas,
    pois é computacionalmente barato e suscetível a ataques
    de dicionário e rainbow tables.
    """
    return hashlib.md5(senha.encode()).hexdigest()


# ==============================================================
# VULNERABILIDADE 3 — SQL Injection por concatenação direta
# Risco STRIDE: Tampering / Elevation of Privilege
# Risco mapeado na Fase 1: Endpoints sem validação de entrada
# ==============================================================
def buscar_pontos_usuario(user_id):
    """
    INSEGURO: O valor de user_id é concatenado diretamente
    na query SQL sem sanitização, permitindo que um atacante
    injete comandos SQL arbitrários — por exemplo, passando
    o valor: 1 OR 1=1 --
    o que retornaria todos os registros de todos os usuários,
    quebrando o isolamento entre tenants mapeado na Fase 1.
    """
    conn = sqlite3.connect("habitoplus.db")
    cursor = conn.cursor()
    query = "SELECT pontos FROM usuarios WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchall()


# ==============================================================
# VULNERABILIDADE 4 — Command Injection via subprocess
# Risco STRIDE: Elevation of Privilege
# Risco mapeado na Fase 1: Upload e processamento de arquivos
# ==============================================================
def gerar_relatorio_empresa(nome_empresa):
    """
    INSEGURO: O valor de nome_empresa é passado diretamente
    para um comando shell, permitindo que um atacante injete
    comandos adicionais — por exemplo, passando o valor:
    Empresa XYZ && del /f /q C:\\*
    o que executaria comandos destrutivos no servidor.
    """
    subprocess.call(
        "echo Gerando relatorio para: " + nome_empresa,
        shell=True
    )


# ==============================================================
# VULNERABILIDADE 5 — Uso de assert para controle de acesso
# Risco STRIDE: Elevation of Privilege
# Risco mapeado na Fase 1: Escalada de privilégios
# ==============================================================
def validar_acesso_admin(usuario):
    """
    INSEGURO: Usar assert para validações de segurança é
    perigoso pois asserts são desativados quando Python roda
    em modo otimizado (flag -O), tornando o controle de acesso
    completamente inoperante.
    """
    assert usuario.get("perfil") == "admin", "Acesso negado"
    return True


# ==============================================================
# Função legítima: registrar hábito do usuário
# Esta função representa a funcionalidade central do HábitoPlus
# ==============================================================
def registrar_habito(usuario_id, tipo_habito, valor, empresa_id):
    """
    Registra um hábito saudável do usuário e retorna
    a pontuação concedida. Em um sistema real, esta função
    aplicaria todas as mitigações descritas na Fase 1:
    validação server-side, rate limiting e isolamento por tenant.
    """
    if not usuario_id or not tipo_habito or not empresa_id:
        return {"erro": "Dados obrigatórios ausentes"}

    habitos_validos = [
        "agua", "sono", "alongamento", "caminhada",
        "meditacao", "alimentacao", "sol"
    ]

    if tipo_habito not in habitos_validos:
        return {"erro": "Tipo de hábito não reconhecido"}

    return {
        "status": "registrado",
        "usuario_id": usuario_id,
        "empresa_id": empresa_id,
        "habito": tipo_habito,
        "pontos_concedidos": 10,
        "mensagem": "Parabéns! Continue assim."
    }