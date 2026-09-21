# Runbook — Verificação manual de cotações

A recolha é **híbrida**: a Wise é recolhida automaticamente (API pública, `source="auto"`), mas os
restantes provedores ainda são verificados à mão e registados no admin. Este documento define o
procedimento manual para que os valores sejam comparáveis entre provedores.

## Princípios

1. **O valor recebido em CVE é a fonte de verdade.** Registar sempre o valor final que o
   destinatário recebe, tal como apresentado no simulador do provedor.
2. **Usar o mesmo método de pagamento em todos os provedores.** Se o método diferir, os
   custos não são comparáveis. Regista o método usado nos campos da ronda.
3. **Registar a fonte.** Guardar o URL exato da página/simulação consultada.
4. **Uma ronda = um momento.** Preenche todos os montantes de referência disponíveis de uma
   só vez; a data/hora é aplicada a toda a ronda.

## Montantes de referência

100, 250, 500, 1000 e 2000 EUR. Preenche os que o provedor aceitar; deixa vazios os que não
se aplicam. O sistema interpola linearmente os valores intermédios.

## Procedimento

1. Abre o simulador do provedor e escolhe o corredor **Portugal → Cabo Verde (EUR → CVE)**.
2. Define o método de pagamento padrão (ver abaixo) e o método de recebimento pretendido.
3. Para cada montante de referência:
   - insere o valor a enviar;
   - lê o **valor recebido** final em CVE e o custo total apresentado;
   - anota comissão e taxa de câmbio, se exibidas (opcional).
4. No admin, abre **Nova verificação**, escolhe o provedor e preenche:
   - URL da fonte, notas (promoções, método usado);
   - método de pagamento, método de recebimento e tempo de entrega;
   - os valores recebidos por montante.
5. Guarda a ronda. O histórico fica preservado e a nova ronda passa a ser a atual.

## Método de pagamento padrão por provedor

| Provedor | Método padrão a usar | Notas |
|---|---|---|
| Wise | Transferência/cartão de débito | Registar qual foi usado |
| Remitly | Cartão de débito | Confirmar taxa promocional vs. padrão |
| WorldRemit | Cartão de débito | |
| Ria | Cartão de débito | |
| Western Union | Cartão de débito | |
| MoneyGram | Cartão de débito | |

Se um provedor cobrar diferente por método, registar o método nas notas.

## Frequência

- Rever os provedores ativos **pelo menos semanalmente**.
- Após o prazo de `STALE_AFTER_DAYS` (7 dias), as cotações passam a mostrar aviso de
  desatualizado na calculadora.

## Qualidade dos dados

- Não estimar valores: se não for possível simular, não registar aquele montante.
- Não copiar valores de terceiros; usar sempre o simulador oficial do provedor.
- Se um provedor mudar de condições, registar nas notas da ronda.
