# Prática de redes — MetalTech

Guilherme Luiz da Silva e Risiane Izabel de Souza Santos.

Coleta real em 18/09/2026; horários completos e fuso UTC−03:00 nos metadados. Dois containers no mesmo host, bridge interna, tráfego cliente → servidor. NET_ADMIN apenas no cliente. O contexto MetalERP/CNC orienta a discussão, mas nenhum desses ativos reais foi testado.

## Interrupção documentada

A terceira tentativa UDP de 10 Mbps no cenário degradado falhou antes da medição, com erro unable to read from stream socket: Resource temporarily unavailable e código 1. Não foi tratada como throughput zero nem como perda de 100%. A saída e os metadados estão em evidencias/falhas/. O finally removeu o netem, executou recuperação e encerrou o projeto. Uma etapa complementar recriou apenas o projeto exclusivo, reaplicou os mesmos 100 ms/5% e completou UDP 10 teste 3 e os três UDP 50. As sementes aleatórias e os IDs dos containers diferem e estão registrados; não há continuidade temporal entre essas etapas. Essa diferença limita a comparação entre os ensaios. A causa exata da falha de inicialização não foi demonstrada. Consulte failed_attempts em resultados.json para todas as tentativas falhas preservadas.

## Baseline experimental normal

| metrica | unidade | teste_1 | teste_2 | teste_3 | referencia | observacao |
| --- | --- | --- | --- | --- | --- | --- |
| Latência média | ms | 0.052 | 0.052 | 0.052 | 0.052 | Mediana de 3 execuções normais. |
| Perda ICMP | % | 0 | 0 | 0 | 0 | Referência agregada 0/60; mediana individual 0.0%. |
| Jitter UDP 10 Mbps | ms | 0.0212052 | 0.0261465 | 0.0560712 | 0.0261465 | Mediana de 3 execuções normais. |
| Jitter UDP 50 Mbps | ms | 0.00128036 | 0.00401482 | 0.00549503 | 0.00401482 | Mediana de 3 execuções normais. |
| Throughput TCP | Mbps | 68856.6 | 69394.9 | 69243.5 | 69243.5 | Mediana de 3 execuções normais. |
| Throughput UDP 10 Mbps | Mbps | 9.99988 | 9.99985 | 10.0001 | 9.99988 | Mediana de 3 execuções normais. |
| Throughput UDP 50 Mbps | Mbps | 49.9989 | 49.9989 | 49.9989 | 49.9989 | Mediana de 3 execuções normais. |

A referência de latência, jitter e throughput é a mediana das três execuções normais: reduz a influência de um ensaio extremo, mas três amostras não estimam a variabilidade operacional de longo prazo. Para perda, a razão agregada preserva os denominadores; a mediana individual consta na observação. O P95 usa nearest-rank sobre RTTs individuais recebidos, sem imputar RTT aos pacotes perdidos. O P95 agregado usa todas as respostas, não a média dos P95 de cada teste. A precisão do P95 é limitada pelo texto das respostas: ping arredondou os RTT degradados para milissegundos inteiros; min/média/max vêm do resumo de maior precisão.

## Comparação normal × degradado

| metrica | normal | degradado | variacao_absoluta | unidade_variacao | variacao_percentual | classificacao |
| --- | --- | --- | --- | --- | --- | --- |
| Latência média | 0.052 | 100.218 | 100.166 | ms | 192627 | Crítico |
| Perda ICMP | 0 | 5 | 5 | p.p. |  | Crítico |
| Jitter UDP 10 Mbps | 0.0261465 | 0.0861464 | 0.0599999 | ms | 229.476 | Normal |
| Jitter UDP 50 Mbps | 0.00401482 | 0.00539826 | 0.00138344 | ms | 34.4582 | Normal |
| Throughput TCP | 69243.5 | 0.726611 | -69242.8 | Mbps | -99.999 | Crítico |
| Throughput UDP 10 Mbps | 9.99988 | 9.42381 | -0.576072 | Mbps | -5.76078 | Normal |
| Throughput UDP 50 Mbps | 49.9989 | 47.0319 | -2.96706 | Mbps | -5.93425 | Normal |

Variação absoluta = degradado − normal; percentual = 100 × (degradado − normal) / normal, somente quando normal ≠ 0. Perda é comparada em pontos percentuais, sem variação percentual. Campo vazio indica não aplicável. As classes são critérios propostos para este laboratório, sem atribuição a norma: latência média e jitter normais até max(1 ms, 1,2×referência), atenção até max(5 ms, 2×referência), críticos acima; perda ICMP normal ≤0,1%, atenção >0,1% até 1%, crítica >1%; throughput normal ≥90% da referência, atenção ≥70% e <90%, crítico <70%. Os pisos absolutos evitam alarmes por diferenças minúsculas em referências próximas de zero. Uma classe normal de jitter ou throughput UDP não elimina risco indicado por perda.

## Detalhes e consistência


**normal**: ICMP perdeu 0/60 (0.000%); P95 agregado de RTT 0.080 ms. MTR: 1 salto(s), [{'hop': 1, 'ip': '172.30.0.3', 'loss_pct': 0.0, 'sent': 20, 'avg_ms': 0.1, 'worst_ms': 0.2}]. TCP: retransmissões do emissor por teste [0, 21, 0]; durações recebidas [10.009553, 10.001255, 10.001444] s.

udp10: perda percentual recebida por teste [0, 0, 0]; perdidos/total [(0, 8634), (0, 8634), (0, 8634)]. Consulte resultados.json para cada jitter, throughput e duração.

udp50: perda percentual recebida por teste [0, 0, 0]; perdidos/total [(0, 43168), (0, 43167), (0, 43166)]. Consulte resultados.json para cada jitter, throughput e duração.

**degradado**: ICMP perdeu 3/60 (5.000%); P95 agregado de RTT 100.000 ms. MTR: 1 salto(s), [{'hop': 1, 'ip': '172.30.0.3', 'loss_pct': 5.0, 'sent': 20, 'avg_ms': 100.3, 'worst_ms': 100.4}]. TCP: retransmissões do emissor por teste [26, 48, 50]; durações recebidas [10.101765, 10.101731, 10.101487] s.

udp10: perda percentual recebida por teste [5.1425, 4.8182, 4.5054]; perdidos/total [(444, 8634), (416, 8634), (389, 8634)]. Consulte resultados.json para cada jitter, throughput e duração.

udp50: perda percentual recebida por teste [4.8141, 4.9921, 4.9365]; perdidos/total [(2078, 43165), (2155, 43168), (2131, 43168)]. Consulte resultados.json para cada jitter, throughput e duração.

A inspeção da versão e do código oficial 3.21 está documentada em evidencias/semantica_iperf3.md. Foram usadas as somas recebidas, nunca o jitter zerado do emissor UDP. Os arquivos legíveis são derivados dos mesmos JSONs. O MTR identifica apenas o caminho local de um salto; não localiza segmentos da fábrica.

## Indicadores propostos

São exatamente três KPIs e dois KRIs, calculados para cada cenário. Não substituem os indicadores mensais da Aula 16.

| indicador | nome | cenario | formula | unidade | meta_faixa_proposta | periodo | valor_observado | responsavel_sugerido |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KPI 1 | RTT ICMP P95 | normal | nearest-rank P95 de todos os RTT recebidos | ms | ≤1 ms no laboratório | Bateria curta do cenário; horários individuais nos metadados | 0.08 | Infraestrutura |
| KPI 2 | Entrega ICMP | normal | 100 × recebidos / enviados | % | 100% no laboratório | Bateria curta do cenário; horários individuais nos metadados | 100 | Infraestrutura |
| KPI 3 | Retenção de throughput TCP | normal | 100 × mediana TCP cenário / mediana TCP normal | % | ≥90% | Bateria curta do cenário; horários individuais nos metadados | 100 | Infraestrutura |
| KRI 1 | Ensaios ICMP com perda | normal | 100 × testes ping com perda >0 / 3 | % | Normal 0; Atenção >0 a 33,34; Crítico >33,34 | Bateria curta do cenário; horários individuais nos metadados | 0 | Infraestrutura e automação |
| KRI 2 | Ensaios UDP com perda >1% | normal | 100 × testes UDP com perda >1% / 6 | % | Normal 0; Atenção >0 a 33,34; Crítico >33,34 | Bateria curta do cenário; horários individuais nos metadados | 0 | Infraestrutura |
| KPI 1 | RTT ICMP P95 | degradado | nearest-rank P95 de todos os RTT recebidos | ms | ≤1 ms no laboratório | Bateria curta do cenário; horários individuais nos metadados | 100 | Infraestrutura |
| KPI 2 | Entrega ICMP | degradado | 100 × recebidos / enviados | % | 100% no laboratório | Bateria curta do cenário; horários individuais nos metadados | 95 | Infraestrutura |
| KPI 3 | Retenção de throughput TCP | degradado | 100 × mediana TCP cenário / mediana TCP normal | % | ≥90% | Bateria curta do cenário; horários individuais nos metadados | 0.00104936 | Infraestrutura |
| KRI 1 | Ensaios ICMP com perda | degradado | 100 × testes ping com perda >0 / 3 | % | Normal 0; Atenção >0 a 33,34; Crítico >33,34 | Bateria curta do cenário; horários individuais nos metadados | 66.6667 | Infraestrutura e automação |
| KRI 2 | Ensaios UDP com perda >1% | degradado | 100 × testes UDP com perda >1% / 6 | % | Normal 0; Atenção >0 a 33,34; Crítico >33,34 | Bateria curta do cenário; horários individuais nos metadados | 100 | Infraestrutura |

## Relação com a Aula 16

O DOCX anterior foi consultado e seu texto extraído foi preservado. MetalERP: RTT P95 ≤20 ms; atenção >30 ms por duas janelas de 5 min; perda ≤0,1%, atenção >1% em 5 min; jitter de RTT P95 ≤5 ms, atenção >10 ms por duas janelas de 5 min; utilização P95 ≤60%, atenção >80% por 5 min; disponibilidade mensal ≥99,9%.

O RTT ICMP P95 foi 0.080 ms no normal e 100.000 ms no degradado. Essa comparação numérica ilustra o impacto sobre a referência de RTT do ERP, mas o destino era o servidor de laboratório. Não demonstra desempenho do MetalERP nem persistência em duas janelas. A perda agregada foi 0.000% versus 5.000%, com apenas 60 pacotes por cenário.

CNC: resposta P95 ≤5 ms, atenção >10 ms por 3 min; perda esperada 0%, atenção >0,1% em 5 min ou timeout; jitter de requisição/resposta P95 ≤1 ms, atenção >2 ms por 3 min; utilização P95 ≤40%, atenção >60% por 5 min; disponibilidade ≥99,95% por máquina no mês. RTT ICMP não mede processamento de controlador, resposta do protocolo industrial, perda de mensagens CNC ou timeout operacional. Portanto não há validação desses limites neste ensaio.

Não foi calculado jitter de RTT P95 da Aula 16: jitter UDP do iperf3 não é essa métrica. Utilização e disponibilidade também não foram medidas. Os indicadores deste pacote são novos indicadores experimentais adequados aos dados disponíveis.

## Limitações obrigatórias

- Containers no mesmo host não reproduzem enlaces, switches, cabeamento, interferências, carga e aplicações da fábrica.
- Coleta curta não valida a baseline de 30 dias nem limites persistentes de 3 ou 5 minutos. Cada iperf solicita 10 s; ping e MTR usam 20 sondagens/ciclos.
- RTT ICMP, tempo de resposta de aplicação e jitter UDP são métricas diferentes; seus limiares não são intercambiáveis.
- Throughput iperf3 não equivale à utilização de enlace físico: a capacidade desse enlace não foi medida. Dezenas de Gbps locais refletem o caminho virtual no host.
- Ping e sucesso das execuções não permitem derivar disponibilidade mensal nem disponibilidade funcional do ERP.
- Atraso fixo de 100 ms não implica jitter de 100 ms. O netem atua na saída do cliente; não foram aplicados 100 ms em cada sentido.
- A perda aleatória configurada em 5% pode diferir da observada, especialmente nos 60 ICMP por cenário. Filas, temporização, protocolo e amostragem também influenciam resultados.
- O TCP se adapta ao RTT e às perdas por controle de congestionamento e retransmissão; UDP mantém a oferta configurada e permite observar perdas sem a mesma adaptação.
- Os ensaios são sequenciais, porém outros processos do host não foram controlados. Não se atribui toda flutuação pequena ao netem.


## Conclusão técnica

1. O cenário normal estabeleceu uma referência experimental local, com mediana de RTT médio 0.052 ms; isso não representa a rede de produção.
2. A introdução de netem elevou a mediana de RTT médio para 100.218 ms, coerente com atraso aplicado na saída do cliente.
3. O throughput TCP recebido passou de 69243.518 para 0.727 Mbps; maior RTT e perdas restringem a progressão da janela TCP e provocam retransmissões.
4. As medições UDP devem ser lidas junto com suas perdas: uma taxa recebida próxima da oferta e jitter pequeno não comprovam entrega integral nem adequação a protocolos industriais.
5. A amostra ICMP e os datagramas UDP possuem tamanhos de amostra diferentes; não se espera exatamente 5% observado em todas as execuções.
6. O ping de recuperação recebeu 20/20 respostas, com média 0.050 ms; o qdisc final documenta a retirada do netem.
7. Os containers e a rede exclusivos foram removidos, conforme as consultas após down; as evidências foram preservadas para montagem do DOCX.
8. Recomenda-se validar as hipóteses na coleta de 30 dias da Aula 16, por turno e ativo, com sondagens do ERP e medições passivas dos protocolos CNC, respeitando os limites dos fabricantes.
