# Análise de Ameaças e Cadeia de Suprimentos — HábitoPlus (CarePlus)

## 1. Identificação de Riscos Específicos ao Serviço

O HábitoPlus é um módulo digital a ser incorporado ao aplicativo já existente da CarePlus, com o propósito de incentivar, registrar e recompensar comportamentos preventivos e saudáveis por meio de um sistema de pontos com valor real de troca, gamificação e engajamento em escala organizacional, envolvendo colaboradores, departamentos e empresas clientes, o que resulta em uma superfície de ataque significativa e multidimensional que precisa ser analisada com rigor.

A natureza do serviço combina três elementos que, individualmente, já representariam riscos consideráveis, mas que juntos amplificam a exposição do sistema: dados de saúde comportamental dos usuários (registros de hábitos como qualidade do sono, ingestão de água, pausas de alongamento, alimentação e atividade física), dados corporativos sensíveis (vínculo do usuário com empresas, departamentos e metas organizacionais) e um sistema de incentivos com valor econômico real (pontos conversíveis em recompensas, cujas regras e pesos podem ser configurados pelas próprias empresas clientes).

Os riscos identificados, descritos a seguir, derivam diretamente das funcionalidades previstas no escopo da solução e das interações entre os atores envolvidos, sendo eles os usuários finais (colaboradores), as empresas clientes (que configuram regras e validam comprovantes), a plataforma CarePlus e os sistemas de terceiros integrados.

**Manipulação do Sistema de Pontos**

O risco de maior criticidade operacional do HábitoPlus reside na possibilidade de um usuário registrar hábitos que não realizou, acumulando pontos de forma fraudulenta, especialmente quando as recompensas atreladas ao sistema tiverem valor econômico significativo, situação que o próprio escopo da solução reconhece ao prever passos adicionais de verificação para recompensas mais valiosas, mas que, enquanto esses controles não estiverem implementados de forma robusta, representa uma vulnerabilidade central do serviço.

**Exposição de Dados de Saúde Comportamental com Vínculo Corporativo**

Os dados registrados pelos usuários, como qualidade do sono, pausas de descanso e consumo alimentar, ainda que sejam autoavaliações subjetivas e não diagnósticos clínicos, constituem dados relacionados à saúde e ao comportamento pessoal, e quando vinculados à identidade corporativa do usuário (empresa, departamento, cargo), criam um perfil sensível que, se exposto, poderia ser utilizado de forma discriminatória por empregadores ou terceiros, configurando risco regulatório sob a Lei Geral de Proteção de Dados Pessoais (LGPD), especificamente em relação ao artigo 11 que trata de dados sensíveis.

**Submissão de Arquivos Maliciosos Disfarçados de Comprovantes**

A funcionalidade de engajamento anual prevê que usuários enviem comprovantes de exames de rotina, vacinação e checkups para validação, o que significa que o sistema precisa aceitar uploads de arquivos provenientes de dispositivos de usuários finais, representando um vetor de ataque clássico em que um arquivo malicioso (executável disfarçado de PDF, imagem com payload embutido ou arquivo com extensão falsificada) pode ser enviado ao servidor com o objetivo de comprometer a infraestrutura ou escalar privilégios.

**Quebra de Isolamento entre Tenants (Empresas Clientes)**

O HábitoPlus opera em um modelo multitenancy, onde múltiplas empresas clientes e seus respectivos colaboradores coexistem na mesma plataforma, criando o risco de que, por falha de controle de acesso ou lógica de negócio mal implementada, uma empresa consiga acessar dados de usuários de outra empresa, ou que um colaborador consiga visualizar dados individuais de colegas de outros departamentos que deveriam permanecer agregados e anonimizados.

**Exposição de Credenciais no Código-Fonte**

Durante o desenvolvimento do módulo, há o risco de que desenvolvedores, por descuido ou falta de processos estabelecidos, incluam credenciais diretamente no código-fonte versionado no repositório, como senhas de banco de dados, chaves de API de serviços externos ou tokens de acesso, expondo esses segredos a qualquer pessoa com acesso ao repositório e, no caso de repositórios públicos, a toda a internet.

**Dependências de Software com Vulnerabilidades Conhecidas**

O desenvolvimento do módulo inevitavelmente fará uso de bibliotecas e frameworks de terceiros para funcionalidades como autenticação, notificações push, processamento de arquivos e comunicação com APIs externas, e cada uma dessas dependências representa um elo na cadeia de suprimentos de software que pode conter vulnerabilidades conhecidas (CVEs) ou até mesmo ter sido comprometida por atacantes, conforme demonstrado em casos históricos relevantes como o do pacote event-stream do ecossistema npm em 2018.

**Ausência de Autenticação e Autorização nos Endpoints da API**

O backend do HábitoPlus precisará expor endpoints de API para que o aplicativo móvel registre hábitos, consulte pontos e envie comprovantes, e cada um desses endpoints, se não protegido adequadamente por mecanismos de autenticação e autorização, pode ser chamado diretamente por atacantes, permitindo desde o registro fraudulento de hábitos em nome de outros usuários até a extração em massa de dados da plataforma.

**Ausência de Logs Auditáveis para o Sistema de Recompensas**

O sistema de pontos e recompensas, por envolver valor econômico real, exige rastreabilidade completa de todas as transações, e a ausência de logs auditáveis imutáveis cria o risco de repúdio, onde um usuário pode negar ter recebido uma recompensa, ou uma empresa pode contestar uma pontuação concedida, sem que o sistema consiga apresentar evidências concretas do que ocorreu e quando.

---

## 2. Mapeamento de Ameaças à Cadeia de Suprimentos

A cadeia de suprimentos de software do HábitoPlus compreende todos os elementos externos sobre os quais a equipe de desenvolvimento não possui controle direto, mas dos quais o serviço depende para funcionar, e uma falha em qualquer um desses elos pode comprometer a segurança do sistema como um todo, mesmo que o código desenvolvido internamente esteja livre de vulnerabilidades.

### 2.1 Dependências de Software (Bibliotecas de Terceiros)

O desenvolvimento do módulo HábitoPlus utilizará bibliotecas de terceiros para cobrir funcionalidades essenciais como autenticação de usuários, geração e validação de tokens JWT, envio de notificações push, manipulação de arquivos de imagem e PDF para os comprovantes, comunicação HTTP com APIs externas e possivelmente frameworks de backend para construção dos endpoints da API, e cada uma dessas bibliotecas, por sua vez, possui suas próprias dependências transitivas, criando uma árvore de dependências que pode ser extensa e difícil de auditar manualmente.

O risco central nessa categoria é o de uma biblioteca amplamente utilizada conter uma vulnerabilidade conhecida e catalogada publicamente no banco de dados CVE (Common Vulnerabilities and Exposures), que pode variar desde uma vulnerabilidade de baixa severidade até falhas críticas que permitem execução remota de código, como foi o caso da vulnerabilidade Log4Shell (CVE-2021-44228) descoberta em 2021 na biblioteca Log4j, amplamente utilizada em aplicações Java em todo o mundo, que permitia execução remota de código arbitrário com apenas uma linha de texto malicioso em um campo de input.

Além da vulnerabilidade acidental, existe o risco de ataque deliberado à cadeia de suprimentos, em que um atacante publica um pacote malicioso com nome semelhante a um pacote legítimo (typosquatting), ou compromete a conta de um mantenedor de um pacote popular e injeta código malicioso em uma nova versão, como ocorreu com o pacote xz-utils em 2024, onde um atacante passou anos construindo confiança na comunidade antes de inserir uma backdoor que afetava sistemas de autenticação SSH em distribuições Linux.

### 2.2 APIs Externas e Integrações

O escopo do HábitoPlus prevê integrações com sistemas externos em pelo menos duas dimensões, sendo a primeira a integração com sistemas de RH ou de gestão de pessoas das empresas clientes, para validar o vínculo do colaborador e possivelmente sincronizar dados de departamento e cargo, e a segunda a integração com sistemas de recompensas ou parceiros comerciais para a conversão de pontos acumulados.

Cada uma dessas integrações representa um ponto de entrada de dados externos no sistema, e a segurança do HábitoPlus passa a depender parcialmente da segurança das APIs com as quais se integra, criando o risco de que, caso uma dessas APIs externas seja comprometida, os dados trocados nessa integração sejam interceptados ou adulterados, ou que uma API retorne dados maliciosos que o HábitoPlus processa sem a devida validação, configurando o que é conhecido como ataque de injeção via resposta de terceiros.

Existe também o risco de indisponibilidade da API externa, que em um sistema com recompensas de valor real pode gerar disputas entre usuários e a plataforma, além do risco de mudanças não comunicadas nos contratos de API (breaking changes), que podem introduzir comportamentos inesperados no processamento de dados.

### 2.3 Pipeline de Desenvolvimento e Infraestrutura CI/CD

O pipeline de integração e entrega contínua, que automatiza a construção, teste e deploy do código, é em si mesmo um vetor de ataque relevante, pois tem acesso privilegiado ao código-fonte, às credenciais de produção e aos ambientes de deploy, e uma comprometimento do pipeline pode resultar em um atacante injetando código malicioso em cada versão do sistema implantada em produção, sem que os desenvolvedores percebam.

No contexto do projeto, que utilizará GitHub Actions como plataforma de CI/CD, os riscos específicos incluem o uso de GitHub Actions de terceiros (actions criadas por desenvolvedores externos e disponíveis no marketplace) sem auditoria do código dessas actions, o que significa que uma action maliciosa ou comprometida poderia exfiltrar os secrets armazenados no repositório durante a execução do pipeline, e o risco de que segredos sejam inadvertidamente impressos nos logs do pipeline, tornando-se visíveis para qualquer pessoa com acesso ao repositório.

### 2.4 Infraestrutura de Nuvem e Serviços de Hospedagem

A infraestrutura que hospedará o HábitoPlus, seja em nuvem pública como AWS, Azure ou Google Cloud, seja em infraestrutura gerenciada, representa um componente da cadeia de suprimentos sobre o qual a equipe tem controle de configuração mas não de operação física, e os riscos nessa camada incluem configurações incorretas que expõem dados inadvertidamente, como um bucket de armazenamento de objetos configurado como público que contenha comprovantes de exames enviados pelos usuários, além de vulnerabilidades nos próprios serviços gerenciados utilizados, cuja correção depende inteiramente do provedor de nuvem.

---

## 3. Classificação de Riscos pela Metodologia STRIDE

A metodologia STRIDE, desenvolvida pela Microsoft, organiza as ameaças de segurança em seis categorias, sendo elas Spoofing (falsificação de identidade), Tampering (adulteração de dados), Repudiation (repúdio de ações), Information Disclosure (exposição de informações), Denial of Service (negação de serviço) e Elevation of Privilege (escalada de privilégios), e cada uma dessas categorias mapeia diretamente para propriedades de segurança que o sistema precisa garantir, respectivamente autenticidade, integridade, não-repúdio, confidencialidade, disponibilidade e autorização.

A seguir, cada risco identificado na Seção 1 é classificado dentro das categorias STRIDE pertinentes, com justificativa baseada na natureza técnica do risco.

### Spoofing (Falsificação de Identidade)

O risco de acesso não autenticado aos endpoints da API do HábitoPlus se enquadra diretamente na categoria de Spoofing, pois um atacante que consegue chamar um endpoint sem apresentar credenciais válidas está essencialmente operando sem identidade verificada dentro do sistema, podendo registrar hábitos, consultar pontos ou submeter comprovantes como se fosse um usuário legítimo, sem que o sistema tenha como distinguir a requisição maliciosa de uma legítima, violando a propriedade de autenticidade que o STRIDE busca proteger.

O risco de quebra de isolamento entre tenants também apresenta uma dimensão de Spoofing quando ocorre por meio de manipulação de identificadores de sessão ou tokens, onde um usuário de uma empresa consegue se apresentar ao sistema como pertencente a outra empresa, ultrapassando os limites de acesso previstos pelo modelo de dados.

### Tampering (Adulteração de Dados)

A manipulação do sistema de pontos constitui o exemplo mais direto de Tampering no contexto do HábitoPlus, pois envolve a adulteração dos registros de hábitos e das transações de pontos armazenados no sistema, seja por meio de requisições forjadas à API que registram hábitos não realizados, seja por meio de ataques diretos ao banco de dados caso os controles de acesso sejam insuficientes, comprometendo a integridade dos dados que fundamentam todo o sistema de recompensas.

A submissão de arquivos maliciosos disfarçados de comprovantes também se enquadra parcialmente em Tampering, pois representa uma tentativa de adulterar o processo de validação de eventos preventivos, fazendo com que o sistema processe e aceite como legítimo um arquivo que não é o que aparenta ser.

### Repudiation (Repúdio)

A ausência de logs auditáveis para o sistema de recompensas representa o risco de Repudiation mais evidente do HábitoPlus, pois sem um registro imutável e verificável de cada transação de pontos, cada validação de hábito e cada concessão de recompensa, não é possível provar de forma conclusiva o que aconteceu no sistema em um determinado momento, permitindo que qualquer ator envolvido, seja o usuário, seja a empresa cliente, negue ações que realizou ou afirme ter realizado ações que não ocorreram, sem que o sistema possa refutar essa negação com evidências concretas.

### Information Disclosure (Exposição de Informações)

A exposição de dados de saúde comportamental com vínculo corporativo enquadra-se diretamente na categoria de Information Disclosure, representando o risco de maior gravidade regulatória do sistema, pois os dados de hábitos de saúde dos colaboradores, quando associados à sua identidade e vínculo empregatício, constituem dados sensíveis sob a LGPD e, se expostos, podem causar dano direto aos titulares dos dados, além de resultar em sanções administrativas e danos reputacionais severos para a CarePlus.

A exposição de credenciais no código-fonte também se enquadra nessa categoria, pois credenciais versionadas em um repositório representam a divulgação de informações privilegiadas que permitem acesso não autorizado a sistemas internos, e o risco é amplificado pelo fato de que, uma vez que uma credencial é commitada em um repositório, ela permanece no histórico de versões mesmo após ser removida do código atual, exigindo uma rotação imediata da credencial comprometida.

### Denial of Service (Negação de Serviço)

O sistema de registro de hábitos, por operar em escala organizacional com potencial de milhares de usuários ativos simultaneamente, apresenta risco de Denial of Service caso não existam controles de rate limiting nos endpoints da API, pois um atacante poderia realizar um volume massivo de requisições ao endpoint de registro de hábitos ou de consulta de pontos, consumindo os recursos de processamento e memória do servidor até torná-lo indisponível para os usuários legítimos, o que em um contexto corporativo onde o engajamento diário é o produto central do serviço representa um impacto direto no valor entregue.

As dependências de software com vulnerabilidades conhecidas também podem conter falhas do tipo Denial of Service, onde uma entrada maliciosamente construída causa o travamento ou consumo excessivo de recursos de uma biblioteca utilizada pelo sistema, como ocorre em vulnerabilidades de ReDoS (Regular Expression Denial of Service), onde expressões regulares mal escritas em bibliotecas de validação podem ser exploradas para consumir tempo de CPU de forma desproporcional.

### Elevation of Privilege (Escalada de Privilégios)

A submissão de arquivos maliciosos disfarçados de comprovantes representa o risco de Elevation of Privilege de maior impacto potencial no HábitoPlus, pois um arquivo executável ou script malicioso que consiga ser processado pelo servidor pode, dependendo das vulnerabilidades presentes no ambiente de execução, permitir que o atacante execute código arbitrário no servidor com as permissões do processo que processou o arquivo, obtendo acesso a dados de todos os usuários da plataforma e potencialmente ao ambiente de infraestrutura.

A quebra de isolamento entre tenants também apresenta uma dimensão de Elevation of Privilege quando um usuário com permissões restritas ao escopo de sua própria empresa consegue acessar funcionalidades administrativas ou dados de outras empresas, ultrapassando o nível de autorização que lhe foi concedido pelo sistema.

---

## 4. Propostas de Mitigação

As mitigações apresentadas a seguir foram desenvolvidas especificamente para os riscos identificados no contexto do HábitoPlus, considerando a realidade de um módulo integrado a um aplicativo existente, com base de usuários corporativa, e a ausência de telemedicina ou diagnósticos clínicos no escopo, o que delimita tanto os dados processados quanto as obrigações regulatórias aplicáveis.

### Mitigação da Manipulação do Sistema de Pontos

O controle principal para este risco é a implementação de validação server-side rigorosa para todos os registros de hábitos, garantindo que nenhum ponto seja concedido com base apenas na afirmação do cliente (aplicativo móvel), pois qualquer lógica de concessão de pontos executada exclusivamente no lado do cliente pode ser manipulada, e toda concessão de pontos deve ser processada e confirmada pelo servidor com base em regras de negócio que incluam limites de frequência por usuário por período (não é possível registrar o mesmo hábito mais de uma vez por janela de tempo definida), validação de sequência lógica (um hábito não pode ser registrado retroativamente além de um período razoável) e, para recompensas de valor significativo conforme previsto no escopo, a implementação de um fluxo de dupla verificação onde um segundo agente, seja o sistema de RH da empresa ou um administrador designado, confirma a elegibilidade antes da concessão da recompensa.

Complementarmente, todos os registros de hábitos e transações de pontos devem ser armazenados em logs auditáveis com carimbo de tempo, endereço IP de origem e identificador de sessão, tornando qualquer padrão de fraude detectável por análise retrospectiva e fornecendo evidências para o tratamento de disputas.

### Mitigação da Exposição de Dados de Saúde Comportamental

A proteção dos dados de hábitos de saúde dos usuários exige uma abordagem em camadas que começa no design do sistema, onde a regra fundamental é que dados de hábitos individuais nunca devem ser acessíveis por representantes da empresa empregadora, pois isso criaria um risco real de uso discriminatório dos dados, e os painéis de gestão oferecidos às empresas devem apresentar exclusivamente dados agregados e anonimizados, como taxa de engajamento por departamento ou percentual de colaboradores que completaram o desafio semanal, sem possibilidade de drill-down até o nível individual.

No nível técnico, os dados devem ser criptografados em repouso no banco de dados e em trânsito via TLS em todas as comunicações entre o aplicativo e o servidor, e o isolamento entre tenants deve ser implementado em nível de banco de dados, garantindo que cada consulta ao sistema inclua obrigatoriamente um filtro pelo identificador da empresa do usuário autenticado, tornando estruturalmente impossível que dados de uma empresa sejam retornados em consultas de outra.

### Mitigação de Upload de Arquivos Maliciosos

O processo de recebimento de comprovantes deve implementar múltiplas camadas de validação antes que qualquer arquivo seja processado ou armazenado definitivamente, sendo a primeira camada a validação do tipo MIME real do arquivo no servidor (não apenas a extensão informada pelo cliente, que pode ser facilmente falsificada), aceitando exclusivamente formatos esperados como JPEG, PNG e PDF, a segunda camada a varredura do arquivo por um serviço de detecção de malware antes do armazenamento, e a terceira o armazenamento dos comprovantes em um ambiente de armazenamento isolado que não tenha execução de código habilitada e que seja inacessível diretamente pela internet, sendo servido apenas por URLs temporárias e assinadas com expiração curta.

### Mitigação da Quebra de Isolamento entre Tenants

O isolamento entre empresas clientes deve ser tratado como um requisito de segurança fundamental no design da arquitetura de dados, e não como uma feature adicionada posteriormente, o que na prática significa que o identificador da empresa deve ser parte integrante de todas as entidades do modelo de dados (usuário, hábito, desafio, pontuação, comprovante) e que todos os endpoints da API devem extrair o contexto de empresa exclusivamente do token de autenticação do usuário, nunca de parâmetros controlados pelo cliente, pois parâmetros podem ser manipulados enquanto o conteúdo de um token JWT assinado pelo servidor não pode.

Testes automatizados de controle de acesso, que tentam explicitamente acessar recursos de um tenant usando credenciais de outro, devem ser parte do conjunto de testes do sistema e executados em cada ciclo do pipeline de CI/CD.

### Mitigação da Exposição de Credenciais no Código

A prevenção da exposição de credenciais requer tanto controles técnicos quanto culturais, sendo o controle técnico primário a implementação de secret scanning automatizado no pipeline de CI/CD, que analisa cada commit em busca de padrões que correspondem a credenciais conhecidas (chaves de API, strings de conexão de banco de dados, tokens JWT, chaves privadas) e bloqueia o merge caso algum seja encontrado, e o controle cultural a adoção do princípio de que nenhuma credencial, mesmo que de um ambiente de desenvolvimento ou teste, jamais deve ser inserida diretamente no código-fonte.

Todas as credenciais devem ser armazenadas em um cofre de segredos dedicado (como GitHub Secrets para o pipeline de CI/CD, e HashiCorp Vault ou o serviço de gerenciamento de segredos do provedor de nuvem para o ambiente de produção) e referenciadas no código por meio de variáveis de ambiente, garantindo que o código-fonte possa ser compartilhado ou tornado público sem expor nenhuma credencial.

### Mitigação de Dependências Vulneráveis

A gestão de vulnerabilidades em dependências de terceiros deve ser automatizada por meio de uma ferramenta de Software Composition Analysis (SCA) integrada ao pipeline de CI/CD, que verifica em cada build se alguma das dependências utilizadas possui CVEs conhecidos com severidade acima de um limiar definido (por exemplo, CVSS score igual ou superior a 7.0), bloqueando o deploy caso vulnerabilidades críticas sejam detectadas e gerando um relatório detalhado para a equipe de desenvolvimento.

Complementarmente, as dependências devem ter suas versões fixadas explicitamente no arquivo de manifesto do projeto (como requirements.txt, package.json ou pom.xml) para evitar que atualizações automáticas para versões comprometidas ocorram sem revisão, e deve ser estabelecida uma política de revisão periódica das dependências, com frequência mínima mensal, para identificar e atualizar pacotes com vulnerabilidades corrigidas em versões mais recentes.

### Mitigação de Endpoints de API sem Autenticação

Todos os endpoints da API do HábitoPlus devem exigir um token de autenticação válido para qualquer operação, sem exceções, utilizando o padrão OAuth 2.0 com tokens JWT assinados com algoritmo RS256, onde o servidor é a única entidade capaz de emitir tokens válidos, e a validade de cada token deve ser limitada a um período curto (como 15 a 60 minutos) com mecanismo de refresh token para sessões prolongadas, garantindo que tokens comprometidos tenham janela de uso limitada.

Além da autenticação, cada endpoint deve implementar autorização granular, verificando não apenas se o usuário está autenticado mas se possui permissão para executar a operação específica sobre o recurso específico solicitado, e controles de rate limiting devem ser aplicados para limitar a frequência de requisições por usuário autenticado, protegendo simultaneamente contra abuso do sistema de pontos e contra ataques de negação de serviço.
