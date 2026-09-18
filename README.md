# MetalTech — Aula 17: prática de redes

Integrantes: Guilherme Luiz da Silva e Risiane Izabel de Souza Santos.

Pacote de evidências reais de ping, MTR e iperf3 em dois containers Docker, comparando os cenários normal e degradado com netem. Coleta realizada em 18/09/2026.

- [Instruções e reprodução](aula17-rede/README.md)
- [Análise técnica e limitações](aula17-rede/analise.md)
- [Resultados estruturados](aula17-rede/resultados.json)
- [Baseline](aula17-rede/baseline.csv), [comparação](aula17-rede/comparacao.csv) e [indicadores](aula17-rede/indicadores.csv)
- [Evidências originais](aula17-rede/evidencias/)
- [Pacote ZIP](MetalTech_Aula17_Evidencias.zip)

Uma tentativa UDP falhou antes da medição e está preservada. Os testes pendentes foram concluídos em etapa complementar documentada. Netem, containers e rede exclusivos foram removidos ao final das duas etapas. O relatório Word não faz parte deste repositório.

Para verificar a integridade:

```bash
sha256sum -c MetalTech_Aula17_Evidencias.zip.sha256
cd aula17-rede
sha256sum -c SHA256SUMS
```
