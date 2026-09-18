# Semântica verificada — iperf3 3.21

Cliente e servidor informaram 3.21 (`versoes.stdout` e `servidor_versao.stdout`). Código oficial da tag 3.21 preservado em `iperf_api_3.21.c`, obtido de https://raw.githubusercontent.com/esnet/iperf/3.21/src/iperf_api.c em 2026-09-18.

- TCP: `end.sum_received.bits_per_second` usa bytes recebidos e duração do receptor (linhas 4471–4479). `end.sum_received.seconds` é a duração do receptor. `end.sum_sent.retransmits` contém as retransmissões do emissor (linha 4447).
- Nesta versão, o booleano `sender` da soma TCP reflete o papel do fluxo local; pode ser `true` dentro de `sum_received`. Não se deve descartar o resumo recebido por esse booleano. A seleção é pelo nome e pelo cálculo bytes × 8 / seconds.
- UDP: `end.sum_received` contém bytes, bitrate, jitter, contagem de perdas, total de datagramas e percentual do receptor, com `sender:false` (linhas 4506–4514). `end.sum_sent` tem estatísticas do emissor, incluindo jitter/perda zerados; não foi usado para medir perdas recebidas.
- O campo legado `end.sum` mistura informações e não foi usado. `packets` no resumo recebido é o total contabilizado pela sequência no receptor, incluindo perdidos; perda = lost_packets / packets × 100. Não substituímos esse denominador pela contagem enviada.
- O processador verifica bitrate = bytes × 8 / seconds e perda = lost_packets / packets × 100 em cada teste. A banda solicitada vem do comando (-b 10M ou 50M), distinta da taxa recebida.
- O tempo solicitado é 10 s; durações reais de emissor e receptor podem diferir e são preservadas. Jitter UDP é uma estimativa de variação de trânsito do iperf, não P95 de diferenças de RTT ICMP.
