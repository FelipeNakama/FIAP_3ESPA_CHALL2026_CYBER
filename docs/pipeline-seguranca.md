# Pipeline de Segurança CI/CD — HábitoPlus (CarePlus)

## Visão Geral

Este documento descreve o pipeline de segurança automatizado configurado para o módulo HábitoPlus, detalhando as três ferramentas integradas ao processo de integração contínua via GitHub Actions, sua função técnica, e a relação direta de cada uma com os riscos identificados na análise de ameaças STRIDE produzida na Fase 1 deste projeto.

O pipeline é acionado automaticamente a cada push ou pull request direcionado à branch principal do repositório, garantindo que nenhuma alteração de código chegue ao ambiente de produção sem ter passado por todas as verificações de segurança configuradas, o que implementa na prática o princípio de "shift left security", que consiste em antecipar as verificações de segurança para as etapas mais iniciais do ciclo de desenvolvimento, reduzindo o custo e o impacto de corrigir vulnerabilidades descobertas tardiamente.

---

## Ferramenta 1: Bandit — Análise Estática de Segurança (SAST)

### O que é e como funciona

O Bandit é uma ferramenta de análise estática de segurança (SAST, do inglês Static Application Security Testing) desenvolvida especificamente para código Python, mantida pela organização PyCQA (Python Code Quality Authority), e seu funcionamento consiste em percorrer o código-fonte do projeto sem executá-lo, construindo uma árvore de sintaxe abstrata (AST) de cada arquivo analisado e aplicando sobre essa estrutura um conjunto de regras (plugins) que identificam padrões conhecidos de código inseguro.

Cada ocorrência detectada recebe duas classificações independentes: uma classificação de severidade (Alta, Média ou Baixa), que indica o quão grave seria a exploração daquela vulnerabilidade, e uma classificação de confiança (Alta, Média ou Baixa), que indica o quão certo o Bandit está de que aquilo realmente é uma vulnerabilidade e não um falso positivo, e a combinação dessas duas dimensões permite que a equipe de desenvolvimento priorize as correções de forma racional, começando pelas ocorrências de severidade Alta e confiança Alta.

### O que o Bandit detecta no código do HábitoPlus

No arquivo `habitoplus_api.py`, o Bandit detectará as seguintes vulnerabilidades, todas intencionalmente inseridas para demonstração e diretamente relacionadas aos riscos mapeados na Fase 1:

**Uso de MD5 para hash de senhas (B303 — Use of MD5)**
A função `hash_senha_usuario` utiliza o algoritmo MD5, que é computacionalmente barato e não foi projetado para hash de senhas, sendo vulnerável a ataques de força bruta e rainbow tables, e o Bandit sinaliza qualquer uso de MD5 em contextos criptográficos com severidade Média, recomendando o uso de algoritmos modernos como bcrypt, scrypt ou Argon2, que são propositalmente lentos para dificultar ataques de força bruta.

**SQL Injection por concatenação de string (B608 — Possible SQL injection)**
A função `buscar_pontos_usuario` concatena diretamente o parâmetro `user_id` na query SQL sem qualquer sanitização ou uso de parâmetros preparados, e o Bandit identifica esse padrão como uma potencial vulnerabilidade de injeção SQL, que no contexto do HábitoPlus poderia ser explorada para quebrar o isolamento entre tenants descrito na Fase 1, onde um atacante poderia injetar condições SQL que retornariam dados de usuários de outras empresas clientes.

**Command Injection via subprocess com shell=True (B602 — subprocess call with shell=True)**
A função `gerar_relatorio_empresa` passa entrada externa diretamente para um comando shell, e o Bandit classifica o uso de `shell=True` combinado com concatenação de variáveis como vulnerabilidade de alta severidade, pois permite que um atacante injete comandos arbitrários no sistema operacional do servidor, o que no contexto do HábitoPlus corresponderia ao risco de Elevation of Privilege mapeado na Fase 1.

**Uso de assert para controle de acesso (B101 — Use of assert detected)**
A função `validar_acesso_admin` utiliza a instrução `assert` para verificar permissões de acesso, e o Bandit sinaliza esse padrão com severidade Média porque instruções `assert` são completamente removidas quando o interpretador Python é executado em modo otimizado (com a flag `-O`), o que tornaria o controle de acesso completamente inoperante sem nenhuma indicação de erro.

### Como o Bandit reduz os riscos do HábitoPlus

Ao ser executado em cada ciclo do pipeline antes que o código chegue a qualquer ambiente, o Bandit garante que vulnerabilidades de código introduzidas durante o desenvolvimento sejam detectadas e sinalizadas imediatamente, criando uma barreira automatizada que previne especificamente os riscos de Tampering (adulteração de dados via SQL injection), Elevation of Privilege (execução remota de comandos via command injection) e falhas de controle de acesso identificados na análise STRIDE da Fase 1.

---

## Ferramenta 2: pip-audit — Análise de Composição de Software (SCA)

### O que é e como funciona

O pip-audit é uma ferramenta de análise de composição de software (SCA, do inglês Software Composition Analysis) desenvolvida pela Python Packaging Authority (PyPA), e seu funcionamento consiste em ler o arquivo de declaração de dependências do projeto (`requirements.txt`), instalar ou resolver as dependências declaradas, e consultar o banco de dados público de vulnerabilidades do Python (PyPI Advisory Database) e a base de dados OSV (Open Source Vulnerabilities, mantida pelo Google) para verificar se alguma das versões declaradas possui CVEs (Common Vulnerabilities and Exposures) registrados.

Para cada vulnerabilidade encontrada, o pip-audit retorna o nome do pacote afetado, a versão vulnerável declarada no projeto, o identificador único do CVE, uma descrição da vulnerabilidade e a versão mínima que corrige o problema, fornecendo à equipe de desenvolvimento todas as informações necessárias para realizar a atualização corretiva de forma precisa.

### O que o pip-audit detecta nas dependências do HábitoPlus

O arquivo `requirements.txt` do projeto declara versões intencionalmente desatualizadas de bibliotecas reais, e o pip-audit identificará os seguintes CVEs catalogados publicamente:

**requests==2.18.0**
A versão 2.18.0 da biblioteca requests, amplamente utilizada para realizar requisições HTTP em Python, possui a vulnerabilidade CVE-2023-32681, que permite que credenciais de autenticação sejam encaminhadas inadvertidamente para hosts diferentes do destino original em caso de redirecionamentos HTTP de cross-origin, o que no contexto do HábitoPlus poderia resultar no vazamento de tokens de autenticação para sistemas externos durante integrações com APIs de RH ou sistemas de recompensas previstos no escopo da solução.

**Pillow==9.0.0**
A versão 9.0.0 da biblioteca Pillow, utilizada para processamento de imagens em Python, possui múltiplas vulnerabilidades relacionadas ao processamento de arquivos de imagem maliciosamente construídos, e no contexto do HábitoPlus esta biblioteca seria utilizada para processar as imagens enviadas como comprovantes de exames e vacinação pelos usuários, exatamente o vetor de ataque de upload de arquivos maliciosos identificado na Fase 1 como risco de Elevation of Privilege.

**PyJWT==1.7.0**
A versão 1.7.0 da biblioteca PyJWT, utilizada para geração e verificação de tokens JWT em Python, possui a vulnerabilidade CVE-2022-29217, que permite que tokens com algoritmo definido como "none" contornem a verificação de assinatura, o que significa que um atacante poderia forjar tokens JWT válidos sem conhecer a chave secreta do servidor, comprometendo completamente o mecanismo de autenticação do HábitoPlus e permitindo acesso não autorizado a qualquer conta da plataforma.

### Como o pip-audit reduz os riscos do HábitoPlus

A integração do pip-audit no pipeline automatiza o mapeamento contínuo de ameaças à cadeia de suprimentos descrito na Seção 2 da análise de ameaças, garantindo que nenhuma versão de dependência com CVE crítico chegue ao ambiente de produção sem conhecimento da equipe, e que atualizações de segurança sejam identificadas e aplicadas sistematicamente em vez de descobertas apenas após um incidente.

---

## Ferramenta 3: Gitleaks — Varredura de Segredos Expostos (Secret Scan)

### O que é e como funciona

O Gitleaks é uma ferramenta de varredura de segredos para repositórios Git, desenvolvida e mantida como projeto open source, e seu funcionamento diferencia-se das ferramentas anteriores por não analisar apenas os arquivos no estado atual do repositório, mas sim todo o histórico de commits, incluindo arquivos que já foram deletados ou modificados em commits anteriores, o que é especialmente relevante porque um segredo commitado por engano e depois removido permanece acessível no histórico do Git para qualquer pessoa com acesso ao repositório.

O Gitleaks opera por meio de um conjunto extenso de expressões regulares (regras) que identificam padrões conhecidos de segredos, incluindo chaves de API de mais de 100 serviços diferentes (AWS, Google Cloud, GitHub, Stripe, Twilio e outros), tokens de autenticação em formatos padronizados, strings de conexão de banco de dados, chaves privadas em formato PEM e padrões genéricos de alta entropia que frequentemente correspondem a segredos mesmo sem corresponder a um serviço específico.

### O que o Gitleaks detecta no repositório do HábitoPlus

No arquivo `habitoplus_api.py`, o Gitleaks detectará as seguintes credenciais intencionalmente inseridas para demonstração:

A variável `AWS_SECRET_ACCESS_KEY` contém um padrão que corresponde exatamente ao formato de chaves secretas da AWS (Amazon Web Services), e o Gitleaks possui uma regra específica para esse padrão (identificada como `aws-secret-access-key`) por ser um dos tipos de credencial mais frequentemente expostos acidentalmente em repositórios públicos, onde uma chave AWS válida exposta pode resultar em uso não autorizado de infraestrutura de nuvem com custos potencialmente ilimitados para a organização.

A variável `JWT_SECRET` contém uma string que corresponde a padrões de segredos genéricos de alta entropia, e em um sistema real a exposição da chave secreta usada para assinar tokens JWT comprometeria completamente o mecanismo de autenticação, pois qualquer pessoa de posse dessa chave poderia gerar tokens válidos para qualquer usuário da plataforma, incluindo administradores.

### Como o Gitleaks reduz os riscos do HábitoPlus

O Gitleaks endereça diretamente o risco de Information Disclosure por exposição de credenciais no código mapeado na Fase 1, criando uma barreira automatizada que detecta esse tipo de exposição antes que o código seja mesclado à branch principal e antes que o repositório seja eventualmente tornado público, e sua capacidade de varrer o histórico completo de commits garante que exposições acidentais que já ocorreram em commits anteriores sejam detectadas retroativamente, permitindo a rotação imediata das credenciais comprometidas.

---

## Relação entre o Pipeline e a Análise de Ameaças STRIDE

O conjunto das três ferramentas integradas ao pipeline cobre, de forma complementar e sem sobreposição de escopo, cinco das seis categorias STRIDE identificadas na análise de ameaças da Fase 1, conforme descrito a seguir:

A categoria Spoofing é endereçada indiretamente pela detecção do Gitleaks, que previne a exposição de chaves JWT que, se comprometidas, permitiriam falsificação de identidade dentro do sistema, e pela detecção do Bandit de padrões de autenticação inseguros no código.

A categoria Tampering é endereçada pelo Bandit, que detecta vulnerabilidades de SQL injection que poderiam ser usadas para adulterar registros de pontos e hábitos no banco de dados, e pelo pip-audit, que identifica versões vulneráveis de bibliotecas de validação de dados.

A categoria Information Disclosure é endereçada pelo Gitleaks, que previne a exposição de credenciais que dariam acesso direto aos dados dos usuários, e pelo pip-audit, que identifica vulnerabilidades em bibliotecas de criptografia e autenticação.

A categoria Elevation of Privilege é endereçada pelo Bandit, que detecta padrões de command injection e falhas de controle de acesso, e pelo pip-audit, que identifica vulnerabilidades críticas em bibliotecas de processamento de arquivos como o Pillow, utilizado no fluxo de upload de comprovantes.

A categoria relacionada aos ataques via cadeia de suprimentos, mapeada na Seção 2 da análise de ameaças, é endereçada integralmente pelo pip-audit, que automatiza a verificação contínua de todas as dependências contra o banco de dados público de vulnerabilidades conhecidas.
