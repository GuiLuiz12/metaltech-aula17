import json,pathlib,statistics
B=pathlib.Path(__file__).resolve().parent;R=json.loads((B/'resultados.json').read_text());N=R['scenarios']['normal'];D=R['scenarios']['degradado']
def table(rows,cols):
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(f'{r[c]:.6g}' if isinstance(r[c],float) else str(r[c]) for c in cols)+' |' for r in rows)
p=[]
p.append('# Prática de redes — MetalTech\n\nGuilherme Luiz da Silva e Risiane Izabel de Souza Santos.\n\nColeta real em 18/09/2026; horários completos e fuso UTC−03:00 nos metadados. Dois containers no mesmo host, bridge interna, tráfego cliente → servidor. NET_ADMIN apenas no cliente. O contexto MetalERP/CNC orienta a discussão, mas nenhum desses ativos reais foi testado.')
p.append('## Interrupção documentada\n\nA terceira tentativa UDP de 10 Mbps no cenário degradado falhou antes da medição, com erro unable to read from stream socket: Resource temporarily unavailable e código 1. Não foi tratada como throughput zero nem como perda de 100%. A saída e os metadados estão em evidencias/falhas/. O finally removeu o netem, executou recuperação e encerrou o projeto. Uma etapa complementar recriou apenas o projeto exclusivo, reaplicou os mesmos 100 ms/5% e completou UDP 10 teste 3 e os três UDP 50. As sementes aleatórias e os IDs dos containers diferem e estão registrados; não há continuidade temporal entre essas etapas. Essa diferença limita a comparação entre os ensaios. A causa exata da falha de inicialização não foi demonstrada. Consulte failed_attempts em resultados.json para todas as tentativas falhas preservadas.')
p.append('## Baseline experimental normal\n\n'+table(R['baseline'],['metrica','unidade','teste_1','teste_2','teste_3','referencia','observacao']))
p.append('A referência de latência, jitter e throughput é a mediana das três execuções normais: reduz a influência de um ensaio extremo, mas três amostras não estimam a variabilidade operacional de longo prazo. Para perda, a razão agregada preserva os denominadores; a mediana individual consta na observação. O P95 usa nearest-rank sobre RTTs individuais recebidos, sem imputar RTT aos pacotes perdidos. O P95 agregado usa todas as respostas, não a média dos P95 de cada teste. A precisão do P95 é limitada pelo texto das respostas: ping arredondou os RTT degradados para milissegundos inteiros; min/média/max vêm do resumo de maior precisão.')
p.append('## Comparação normal × degradado\n\n'+table(R['comparison'],['metrica','normal','degradado','variacao_absoluta','unidade_variacao','variacao_percentual','classificacao']))
p.append('Variação absoluta = degradado − normal; percentual = 100 × (degradado − normal) / normal, somente quando normal ≠ 0. Perda é comparada em pontos percentuais, sem variação percentual. Campo vazio indica não aplicável. As classes são critérios propostos para este laboratório, sem atribuição a norma: latência média e jitter normais até max(1 ms, 1,2×referência), atenção até max(5 ms, 2×referência), críticos acima; perda ICMP normal ≤0,1%, atenção >0,1% até 1%, crítica >1%; throughput normal ≥90% da referência, atenção ≥70% e <90%, crítico <70%. Os pisos absolutos evitam alarmes por diferenças minúsculas em referências próximas de zero. Uma classe normal de jitter ou throughput UDP não elimina risco indicado por perda.')
p.append('## Detalhes e consistência\n')
for s,d in R['scenarios'].items():
 a=d['ping_aggregate'];p.append(f"**{s}**: ICMP perdeu {a['lost']}/{a['sent']} ({a['loss_pct']:.3f}%); P95 agregado de RTT {a['p95_ms']:.3f} ms. MTR: {d['mtr']['hop_count']} salto(s), {d['mtr']['hops']}. TCP: retransmissões do emissor por teste {[x['sender_retransmits'] for x in d['tcp']]}; durações recebidas {[round(x['receiver_seconds'],6) for x in d['tcp']]} s.")
 for mode in ['udp10','udp50']:
  p.append(f"{mode}: perda percentual recebida por teste {[round(x['loss_pct'],4) for x in d[mode]]}; perdidos/total {[(x['lost_packets'],x['total_packets']) for x in d[mode]]}. Consulte resultados.json para cada jitter, throughput e duração.")
p.append('A inspeção da versão e do código oficial 3.21 está documentada em evidencias/semantica_iperf3.md. Foram usadas as somas recebidas, nunca o jitter zerado do emissor UDP. Os arquivos legíveis são derivados dos mesmos JSONs. O MTR identifica apenas o caminho local de um salto; não localiza segmentos da fábrica.')
p.append('## Indicadores propostos\n\nSão exatamente três KPIs e dois KRIs, calculados para cada cenário. Não substituem os indicadores mensais da Aula 16.\n\n'+table(R['indicators'],['indicador','nome','cenario','formula','unidade','meta_faixa_proposta','periodo','valor_observado','responsavel_sugerido']))
p.append(f'''## Relação com a Aula 16

O DOCX anterior foi consultado e seu texto extraído foi preservado. MetalERP: RTT P95 ≤20 ms; atenção >30 ms por duas janelas de 5 min; perda ≤0,1%, atenção >1% em 5 min; jitter de RTT P95 ≤5 ms, atenção >10 ms por duas janelas de 5 min; utilização P95 ≤60%, atenção >80% por 5 min; disponibilidade mensal ≥99,9%.

O RTT ICMP P95 foi {N['ping_aggregate']['p95_ms']:.3f} ms no normal e {D['ping_aggregate']['p95_ms']:.3f} ms no degradado. Essa comparação numérica ilustra o impacto sobre a referência de RTT do ERP, mas o destino era o servidor de laboratório. Não demonstra desempenho do MetalERP nem persistência em duas janelas. A perda agregada foi {N['ping_aggregate']['loss_pct']:.3f}% versus {D['ping_aggregate']['loss_pct']:.3f}%, com apenas 60 pacotes por cenário.

CNC: resposta P95 ≤5 ms, atenção >10 ms por 3 min; perda esperada 0%, atenção >0,1% em 5 min ou timeout; jitter de requisição/resposta P95 ≤1 ms, atenção >2 ms por 3 min; utilização P95 ≤40%, atenção >60% por 5 min; disponibilidade ≥99,95% por máquina no mês. RTT ICMP não mede processamento de controlador, resposta do protocolo industrial, perda de mensagens CNC ou timeout operacional. Portanto não há validação desses limites neste ensaio.

Não foi calculado jitter de RTT P95 da Aula 16: jitter UDP do iperf3 não é essa métrica. Utilização e disponibilidade também não foram medidas. Os indicadores deste pacote são novos indicadores experimentais adequados aos dados disponíveis.''')
p.append('''## Limitações obrigatórias

- Containers no mesmo host não reproduzem enlaces, switches, cabeamento, interferências, carga e aplicações da fábrica.
- Coleta curta não valida a baseline de 30 dias nem limites persistentes de 3 ou 5 minutos. Cada iperf solicita 10 s; ping e MTR usam 20 sondagens/ciclos.
- RTT ICMP, tempo de resposta de aplicação e jitter UDP são métricas diferentes; seus limiares não são intercambiáveis.
- Throughput iperf3 não equivale à utilização de enlace físico: a capacidade desse enlace não foi medida. Dezenas de Gbps locais refletem o caminho virtual no host.
- Ping e sucesso das execuções não permitem derivar disponibilidade mensal nem disponibilidade funcional do ERP.
- Atraso fixo de 100 ms não implica jitter de 100 ms. O netem atua na saída do cliente; não foram aplicados 100 ms em cada sentido.
- A perda aleatória configurada em 5% pode diferir da observada, especialmente nos 60 ICMP por cenário. Filas, temporização, protocolo e amostragem também influenciam resultados.
- O TCP se adapta ao RTT e às perdas por controle de congestionamento e retransmissão; UDP mantém a oferta configurada e permite observar perdas sem a mesma adaptação.
- Os ensaios são sequenciais, porém outros processos do host não foram controlados. Não se atribui toda flutuação pequena ao netem.
''')
p.append(f'''## Conclusão técnica

1. O cenário normal estabeleceu uma referência experimental local, com mediana de RTT médio {R['baseline'][0]['referencia']:.3f} ms; isso não representa a rede de produção.
2. A introdução de netem elevou a mediana de RTT médio para {R['comparison'][0]['degradado']:.3f} ms, coerente com atraso aplicado na saída do cliente.
3. O throughput TCP recebido passou de {R['comparison'][4]['normal']:.3f} para {R['comparison'][4]['degradado']:.3f} Mbps; maior RTT e perdas restringem a progressão da janela TCP e provocam retransmissões.
4. As medições UDP devem ser lidas junto com suas perdas: uma taxa recebida próxima da oferta e jitter pequeno não comprovam entrega integral nem adequação a protocolos industriais.
5. A amostra ICMP e os datagramas UDP possuem tamanhos de amostra diferentes; não se espera exatamente 5% observado em todas as execuções.
6. O ping de recuperação recebeu {R['recovery']['received']}/{R['recovery']['sent']} respostas, com média {R['recovery']['avg_ms']:.3f} ms; o qdisc final documenta a retirada do netem.
7. Os containers e a rede exclusivos foram removidos, conforme as consultas após down; as evidências foram preservadas para montagem do DOCX.
8. Recomenda-se validar as hipóteses na coleta de 30 dias da Aula 16, por turno e ativo, com sondagens do ERP e medições passivas dos protocolos CNC, respeitando os limites dos fabricantes.
''')
(B/'analise.md').write_text('\n\n'.join(p))
