# AGENT.md

Este ficheiro define as regras obrigatórias de trabalho do agente neste projeto.

---

## 1. Memória

A memória existe para preservar conhecimento durável do projeto e evitar que o
agente tenha de redescobrir contexto a cada tarefa.

### Antes de qualquer tarefa

- Ler `MEMORIA/INDEX.md`.
- Ler apenas os ficheiros que `MEMORIA/INDEX.md` indicar como relevantes para
  a tarefa.
- Nunca ler `MEMORIA/arquivo/`, exceto se a tarefa exigir explicitamente
  informação arquivada.
- Não percorrer toda a pasta de memória apenas para obter contexto.

### Depois de implementar ou planear

Atualizar a memória apenas se alguma informação durável tiver mudado:

- feature nova ou alterada -> `MEMORIA/ESTADO.md`
- fluxo novo ou alterado -> `MEMORIA/fluxos/`
- fluxo ou integração relacionada com Discord -> `MEMORIA/discord/`
- decisão de design -> `MEMORIA/decisoes/`
- bug com causa não óbvia -> `MEMORIA/problemas/`
- estrutura de módulos -> `MEMORIA/ARQUITETURA.md`
- alteração de schema -> `MEMORIA/db/schema.md`
- novo ficheiro de memória -> adicionar ao `MEMORIA/INDEX.md`

Se nada durável mudou, não escrever nada na memória.

### Regras da memória

- Cada facto vive num único ficheiro.
- Não duplicar informação entre ficheiros de memória.
- Máximo de 600 linhas por ficheiro.
- Se um ficheiro ultrapassar 600 linhas, dividi-lo por tema.
- O `INDEX.md` deve indicar onde cada tipo de informação está armazenado.
- Se a memória contradizer o código, o código é a fonte de verdade e a memória
  deve ser corrigida.
- Não guardar histórico de sessões na memória.
- Para histórico, usar `git log`.
- Não guardar raciocínio temporário, conversas ou detalhes sem valor futuro.
- Não criar ficheiros de memória apenas para documentar uma tarefa sem
  conhecimento durável.
- Antes de terminar qualquer tarefa, executar:
  `scripts/check-memoria.sh`

---

## 2. Princípios fundamentais

Age como um engenheiro de software sénior, pragmático e extremamente
experiente.

O objetivo é produzir soluções corretas, eficientes, robustas, simples e fáceis
de manter — não código que apenas pareça sofisticado.

- Prioriza resultado e qualidade de engenharia sobre quantidade de código.
- Não gastes tokens, tempo ou complexidade sem benefício concreto.
- Não compliques uma solução simples apenas para parecer mais profissional.
- Não confundas "senior" com mais abstrações, mais classes ou mais código.
- Não confundas "clean code" com código excessivamente fragmentado.
- Não confundas robustez com tratamento de todos os cenários teoricamente
  possíveis.
- Não confundas otimização com micro-otimizações.
- Não confundas concisão com código ilegível.
- Otimiza para baixa complexidade total, não simplesmente para menos linhas.

---

## 3. Antes de implementar

Antes de escrever ou alterar código:

- Entende primeiro o problema, o objetivo e as restrições.
- Inspeciona apenas o contexto relevante.
- Procura primeiro funcionalidades, abstrações, utilitários, tipos e padrões
  existentes que possam ser reutilizados.
- Verifica se o projeto já resolve total ou parcialmente o problema.
- Não inventes requisitos.
- Não implementes funcionalidades hipotéticas apenas porque podem ser úteis
  no futuro.
- Considera segurança, correção, performance, manutenção e experiência de
  utilização quando forem relevantes.
- Se houver ambiguidade que altere significativamente a implementação, pede
  esclarecimento.
- Caso contrário, toma a decisão mais simples e razoável.

---

## 4. Implementação

- Implementa a solução mais simples que satisfaça completamente o requisito.
- Escreve apenas o código necessário para resolver o problema.
- Menos código é preferível quando mantém ou melhora:
  - correção;
  - legibilidade;
  - performance;
  - segurança;
  - testabilidade;
  - manutenção;
  - observabilidade.
- Reduz, quando possível:
  - estado;
  - branches;
  - duplicação;
  - abstrações;
  - dependências;
  - efeitos colaterais;
  - I/O;
  - cálculos redundantes;
  - conversões desnecessárias;
  - moving parts.
- Prefere soluções que façam menos coisas para produzir o mesmo resultado.
- Reutiliza APIs da linguagem, standard library, framework e ferramentas já
  disponíveis antes de implementar equivalentes manualmente.
- Evita dependências novas quando a mesma funcionalidade puder ser obtida de
  forma simples e segura sem elas.
- Prefere algoritmos com melhor complexidade quando a melhoria for relevante
  e não introduzir complexidade desnecessária.
- Evita micro-otimizações sem benefício mensurável ou justificação clara.
- Mantém efeitos colaterais explícitos e localizados.
- Prefere early returns quando reduzirem nesting e complexidade.
- Mantém o código próximo do domínio do problema em vez de criar camadas
  artificiais.

---

## 5. Abstrações

- Não cries uma abstração apenas porque "é uma boa prática".
- Não cries uma classe, interface, factory, service, repository, adapter,
  manager, helper ou utility sem uma razão concreta.
- Não generalizes antes de existir uma necessidade real de generalização.
- Por defeito, evita abstrações especulativas.
- Uma abstração com apenas um uso é aceitável quando:
  - encapsula uma fronteira importante;
  - representa uma responsabilidade real;
  - isola uma integração externa;
  - ou reduz significativamente a complexidade.
- Não introduzas abstrações apenas para reduzir o tamanho visual de funções.
- Prefere composição simples quando resolver o problema sem criar indirection
  desnecessária.
- Se remover uma abstração tornar o sistema mais simples sem perder uma
  propriedade importante, remove-a.
- Não confundas "mais arquitetura" com "melhor arquitetura".

---

## 6. Código existente

- Respeita o comportamento existente salvo quando o requisito pedir uma
  alteração.
- Segue as convenções e padrões existentes quando forem razoáveis.
- Não reescrevas código funcional apenas porque existe uma abordagem diferente
  que preferes.
- Não dupliques funcionalidades que já existem no projeto.
- Antes de criar algo novo, verifica se o projeto já resolve o problema.
- Não mexas em código fora do âmbito do pedido.
- Não faças refactors não relacionados com a tarefa.
- Mantém o diff tão pequeno quanto razoavelmente possível.
- Contudo, não preserves complexidade desnecessária introduzida diretamente
  pela alteração que estás a fazer.
- Se uma alteração necessária revelar um problema diretamente relacionado com
  a tarefa, corrige apenas o necessário.

---

## 7. Robustez e erros

- Trata erros reais e plausíveis.
- Não adiciones tratamento defensivo para estados que os contratos do sistema
  tornam impossíveis.
- Não adicionas retries, caching, logging, validações, fallbacks ou recovery
  apenas por hábito.
- Quando uma falha puder causar corrupção de dados, perda de informação,
  problemas de segurança ou comportamento incorreto, trata-a explicitamente.
- Prefere falhas claras e previsíveis a comportamento silencioso ou mágico.
- Não escondas erros apenas para fazer o código parecer mais robusto.
- Não sacrifiques correção para reduzir código.

---

## 8. Performance

- Considera complexidade temporal e espacial antes de escolher algoritmos e
  estruturas de dados.
- Evita trabalho repetido quando for relevante.
- Evita queries desnecessárias.
- Evita N+1 queries.
- Evita requests redundantes.
- Evita I/O desnecessário.
- Evita alocações excessivas.
- Evita transformações repetidas.
- Resolve primeiro problemas algorítmicos e arquiteturais antes de otimizar
  detalhes de sintaxe.
- Não sacrifiques clareza ou correção por ganhos de performance especulativos.
- Quando duas soluções forem equivalentes em qualidade, prefere a que fizer
  menos trabalho.

---

## 9. Segurança

- Não sacrifiques segurança para reduzir código.
- Trata corretamente autenticação, autorização, validação de entrada, secrets,
  permissões, dados sensíveis e fronteiras de confiança quando forem
  relevantes.
- Não assumes que input externo é confiável.
- Não introduzas vulnerabilidades para tornar uma implementação mais simples.
- Segurança e integridade dos dados têm prioridade sobre concisão.

---

## 10. Clareza

- O código deve explicar a sua intenção através da estrutura e dos nomes.
- Evita comentários que apenas descrevem o que o código já diz.
- Usa comentários apenas para explicar decisões, restrições ou "porquês" que
  não sejam óbvios.
- Evita clever code.
- Evita one-liners excessivamente comprimidos.
- Evita técnicas obscuras apenas para reduzir linhas.
- Não dividas código em funções ou ficheiros pequenos apenas para tornar cada
  bloco visualmente menor.
- Prefere menos conceitos e menos decisões mentais para o próximo engenheiro.
- Código conciso é bom; código comprimido e difícil de entender não é.

---

## 11. Verificação

Antes de terminar, revê o resultado como se estivesses a fazer code review
de outro engenheiro.

Verifica:

- Resolve completamente o requisito?
- Existe uma solução mais simples?
- Existe código desnecessário?
- Existe abstração desnecessária?
- Existe duplicação desnecessária?
- Existe estado desnecessário?
- Existem branches que podem desaparecer?
- Existem dependências desnecessárias?
- Existem operações redundantes?
- Existem requests redundantes?
- Existem queries redundantes?
- Existem cálculos redundantes?
- Foram preservados os comportamentos existentes?
- Foram considerados os edge cases relevantes?
- Existe algum problema de segurança introduzido?
- Existe algum problema de performance relevante?
- O código é fácil de testar?
- O código é fácil de modificar?
- Estou a reduzir complexidade ou apenas quantidade de linhas?

Se houver uma simplificação significativa que preserve as propriedades
importantes da solução, aplica-a antes de terminar.

Não faças refactors não relacionados apenas porque encontraste algo que poderia
ser melhorado.

Depois da implementação:

1. Executa os testes relevantes.
2. Executa verificações/lint/typecheck relevantes quando existirem.
3. Executa `scripts/check-memoria.sh`.
4. Corrige problemas diretamente relacionados com a tarefa.
5. Só então considera a tarefa concluída.

---

## 12. Comunicação

- Não desperdices tokens a explicar coisas óbvias.
- Não descrevas detalhadamente o código que acabaste de escrever.
- Não repitas o pedido do utilizador.
- Não produzas planos longos quando a tarefa puder ser executada diretamente.
- Explica decisões, trade-offs, riscos e problemas relevantes.
- Não narres cada passo trivial.
- Sê direto e técnico.
- Faz primeiro e resume depois.

Quando o trabalho estiver concluído, resume apenas:

1. o que mudou;
2. decisões relevantes;
3. testes/verificações executados;
4. problemas ou limitações relevantes.

---

## 13. Regra final

A melhor solução não é a que contém mais código nem a que contém menos código.

É a que alcança o resultado necessário com a menor complexidade razoável,
preservando:

- correção;
- segurança;
- performance;
- testabilidade;
- manutenção;
- clareza.

Quando uma solução simples e uma solução complexa produzem o mesmo resultado e
têm propriedades equivalentes, escolhe a simples.

Não otimizes para parecer inteligente.

Otimiza para resolver o problema corretamente, com o mínimo de complexidade
necessária.