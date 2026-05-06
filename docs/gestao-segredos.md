# Gestão de Segredos e Credenciais — HábitoPlus (CarePlus)

## 1. Visão Geral

Este documento descreve a política de gestão de segredos e credenciais adotada no desenvolvimento e operação do módulo HábitoPlus, estabelecendo como segredos são armazenados, como a exposição de credenciais no código é prevenida, e quais são as regras de rotação e controle de acesso aplicáveis a cada categoria de credencial utilizada pelo serviço.

A necessidade desta política deriva diretamente dos riscos identificados na análise de ameaças STRIDE do projeto, especificamente o risco de Information Disclosure por exposição de credenciais no código-fonte, onde uma credencial versionada em um repositório representa a divulgação de informação privilegiada que permite acesso não autorizado a sistemas internos, com o agravante de que credenciais commitadas permanecem acessíveis no histórico de versões do Git mesmo após serem removidas do código atual, tornando a rotação imediata obrigatória em qualquer caso de exposição confirmada ou suspeita.

---

## 2. Arquitetura de Armazenamento de Segredos

O HábitoPlus adota uma arquitetura em camadas para o armazenamento de segredos, onde cada camada corresponde a um ambiente de execução com requisitos de segurança e praticidade distintos, e nenhuma camada compartilha credenciais com outra, garantindo que um comprometimento em um ambiente não resulte automaticamente no comprometimento dos demais.

### 2.1 Ambiente de Desenvolvimento Local

No ambiente de desenvolvimento local de cada desenvolvedor, os segredos são armazenados em um arquivo chamado `.env`, que contém as variáveis de ambiente necessárias para executar o serviço localmente e que nunca é versionado no repositório, estando explicitamente listado no arquivo `.gitignore` do projeto para que o Git o ignore automaticamente em todas as operações de commit.

Para que novos desenvolvedores saibam quais variáveis de ambiente precisam configurar sem ter acesso aos valores reais, o repositório contém um arquivo `.env.example` que lista todas as variáveis necessárias com valores fictícios e instruções de preenchimento, sendo este o único arquivo relacionado a configuração de ambiente que é versionado, e qualquer desenvolvedor que entre no projeto deve copiar este arquivo, renomeá-lo para `.env` e preencher os valores reais obtidos por um canal seguro fora do repositório, como um gerenciador de senhas corporativo ou comunicação direta com o responsável pelo ambiente.

### 2.2 Ambiente de CI/CD (Pipeline GitHub Actions)

No ambiente de integração e entrega contínua, os segredos são armazenados como GitHub Secrets, que é o cofre de segredos nativo do GitHub, e são referenciados no arquivo de pipeline usando a sintaxe `${{ secrets.NOME_DO_SEGREDO }}`, garantindo que o valor nunca apareça literalmente no código do pipeline, e que o GitHub os mascare automaticamente em todos os logs de execução, tornando impossível que um observador do log recupere o valor real de qualquer segredo mesmo que o log seja inadvertidamente compartilhado.

Os segredos configurados no GitHub Actions para o HábitoPlus são organizados em quatro categorias funcionais, sendo a primeira as credenciais de banco de dados (DATABASE_URL), que contém a string de conexão completa com host, porta, usuário, senha e nome do banco de dados do ambiente de produção, a segunda a chave de assinatura de tokens JWT (JWT_SECRET_KEY), que é usada pelo servidor para assinar e verificar a autenticidade de todos os tokens de sessão dos usuários, a terceira as chaves de API de serviços externos de notificações (API_KEY_NOTIFICACOES) e a quarta a chave de API do sistema de recompensas parceiro (API_KEY_RECOMPENSAS), sendo que cada serviço externo possui sua própria chave dedicada, de modo que o comprometimento de uma chave não afeta os demais serviços.

### 2.3 Ambiente de Produção

No ambiente de produção, a solução recomendada para o HábitoPlus é o uso de um serviço dedicado de gerenciamento de segredos, sendo as opções principais o HashiCorp Vault, que é uma solução open source amplamente adotada que oferece armazenamento centralizado de segredos com controle de acesso granular, auditoria de todos os acessos e rotação automática de credenciais, e o AWS Secrets Manager ou equivalente do provedor de nuvem utilizado, que oferece integração nativa com os demais serviços da nuvem e rotação automática para tipos de credenciais suportados, como senhas de banco de dados RDS.

Em qualquer um dos casos, o princípio fundamental é que a aplicação em produção nunca lê credenciais de variáveis de ambiente configuradas manualmente ou de arquivos em disco, mas sim consulta o cofre de segredos em tempo de execução usando uma identidade de serviço (como uma IAM Role da AWS ou um AppRole do Vault) para se autenticar, e recebe o valor do segredo dinamicamente, de modo que uma rotação de credencial no cofre se reflete automaticamente na aplicação sem necessidade de redeploy ou alteração de configuração.

---

## 3. Como a Exposição de Credenciais no Código é Prevenida

A prevenção da exposição de credenciais no código-fonte do HábitoPlus é garantida por três controles complementares que atuam em momentos distintos do ciclo de desenvolvimento, de modo que uma credencial precisaria passar por três barreiras independentes para chegar ao repositório sem ser detectada.

### 3.1 Controle Cultural e de Processo

O primeiro controle é cultural e consiste na regra absoluta de que nenhuma credencial, independentemente do ambiente a que pertença (desenvolvimento, homologação ou produção) ou do nível de sensibilidade percebido, deve ser inserida diretamente no código-fonte, em comentários, em mensagens de commit ou em qualquer arquivo que seja versionado no repositório, com a única exceção do arquivo `.env.example`, que contém exclusivamente valores fictícios sem qualquer validade operacional.

Esta regra se estende a práticas comuns que parecem inofensivas mas representam risco real, como comentar uma credencial antiga no código com a intenção de removê-la depois, inserir uma credencial temporariamente para testar uma funcionalidade com a intenção de removê-la antes do commit, ou usar credenciais reais em testes automatizados que são versionados no repositório.

### 3.2 Controle Técnico Preventivo: .gitignore

O segundo controle é o arquivo `.gitignore` configurado no repositório, que instrui o Git a ignorar automaticamente todos os arquivos que tipicamente contêm credenciais, incluindo arquivos `.env` em qualquer variante de nome, arquivos de chave privada com extensões `.pem`, `.key`, `.p12` e `.pfx`, arquivos de configuração de banco de dados e arquivos de credenciais de provedores de nuvem, garantindo que mesmo que um desenvolvedor crie um arquivo com credenciais reais na pasta do repositório, o Git não o incluirá em nenhum commit a menos que o desenvolvedor explicitamente force a adição com o comando `git add --force`, o que seria uma ação consciente e não um acidente.

### 3.3 Controle Técnico Detectivo: Gitleaks no Pipeline

O terceiro controle é a ferramenta Gitleaks integrada ao pipeline de CI/CD, que atua como uma rede de segurança para capturar qualquer credencial que tenha passado pelos dois controles anteriores, varrendo todos os arquivos do repositório em cada execução do pipeline usando um conjunto extenso de regras que identificam padrões conhecidos de credenciais, como o formato de chaves de acesso da AWS, tokens de API de mais de cem serviços diferentes, chaves privadas em formato PEM e strings de alta entropia que frequentemente correspondem a senhas ou tokens mesmo sem corresponder a um serviço específico, e sinalizando qualquer detecção para que a equipe possa agir imediatamente.

---

## 4. Política de Rotação e Acesso Mínimo

### 4.1 Rotação de Credenciais

A política de rotação do HábitoPlus estabelece prazos máximos de validade para cada categoria de credencial, após os quais a rotação é obrigatória independentemente de qualquer suspeita de comprometimento, e a rotação imediata é obrigatória em qualquer situação onde haja confirmação ou suspeita razoável de que uma credencial foi exposta, incluindo mas não se limitando à detecção pelo Gitleaks, ao acesso não autorizado suspeito a qualquer sistema, ao desligamento de um colaborador com acesso a credenciais e à exposição acidental em logs ou comunicações.

As credenciais de banco de dados devem ser rotacionadas a cada noventa dias, com o processo de rotação realizado preferencialmente de forma automatizada pelo serviço de gerenciamento de segredos do ambiente de produção para garantir continuidade do serviço durante a rotação, e os tokens JWT de longa duração usados para refresh tokens devem ser rotacionados a cada cento e oitenta dias, enquanto os tokens de acesso de curta duração têm validade máxima de sessenta minutos por design e são naturalmente substituídos a cada renovação de sessão, não exigindo processo formal de rotação.

As chaves de API de serviços externos, como o serviço de notificações e o sistema de recompensas, devem ser rotacionadas a cada trinta dias ou sempre que um colaborador com acesso a essas credenciais deixar a equipe, e o processo de rotação deve ser coordenado com o provedor do serviço externo para garantir que a nova chave seja ativada antes que a antiga seja desativada, evitando interrupção do serviço.

### 4.2 Princípio do Menor Privilégio

O princípio do menor privilégio estabelece que cada componente do sistema HábitoPlus deve ter acesso apenas às credenciais e permissões estritamente necessárias para executar sua função específica, sem acesso a recursos adicionais que não sejam necessários para aquela função, de modo que um comprometimento de qualquer componente resulte no menor impacto possível sobre o sistema como um todo.

Na prática, isso significa que o serviço de registro de hábitos possui credenciais de banco de dados com permissão de leitura e escrita exclusivamente nas tabelas de hábitos, pontuações e desafios, sem acesso às tabelas de dados financeiros ou de configuração corporativa, e que o serviço de geração de relatórios possui credenciais de banco de dados com permissão somente de leitura nas tabelas de dados agregados, sem qualquer permissão de escrita.

O pipeline de CI/CD possui acesso apenas aos segredos necessários para executar o build e os testes de segurança, sem acesso a credenciais de banco de dados de produção ou a chaves de API de serviços externos, e o acesso ao ambiente de produção a partir do pipeline é feito exclusivamente por meio de uma identidade de serviço dedicada com permissão restrita à operação de deploy, sem capacidade de ler ou modificar dados de usuários.

### 4.3 Controle de Acesso a Segredos de Produção

O acesso a credenciais do ambiente de produção do HábitoPlus é restrito a um número mínimo de pessoas, seguindo o princípio de que nenhum desenvolvedor individual deve ter acesso irrestrito e unilateral a todas as credenciais de produção simultaneamente, e qualquer operação que exija acesso direto a credenciais de produção deve ser realizada com o conhecimento e aprovação de pelo menos um segundo responsável, implementando o princípio dos quatro olhos (four-eyes principle) que garante rastreabilidade e reduz o risco de abuso de acesso privilegiado.

Todo acesso a segredos armazenados no cofre de credenciais de produção deve ser registrado automaticamente com identificação do solicitante, timestamp, motivo declarado e resultado da operação, gerando um log de auditoria imutável que permite a detecção de padrões de acesso anômalos e fornece evidências para investigações em caso de incidente de segurança, conectando-se diretamente ao controle de não-repúdio identificado como requisito na análise de ameaças STRIDE da Fase 1 deste projeto.
