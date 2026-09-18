# MetalTech — pacote de evidências da Aula 17

Integrantes: Guilherme Luiz da Silva; Risiane Izabel de Souza Santos.

Leia `analise.md`, `resultados.json` e os três CSVs. Evidências originais estão em `evidencias/`; cada execução possui `.stdout`, `.stderr` e `.meta.json` (comando, início, fim com fuso e código de saída). Os `.json` do iperf são cópias integrais do stdout; `.legivel.txt` é derivado do mesmo teste e inclui o texto retornado pelo servidor. Não houve repetição para gerar a versão legível.

## Reprodução

Requer Linux, Docker Engine, Docker Compose, Python 3 e acesso autorizado ao daemon. Não altere permissões do socket. Use o fluxo de aprovação do seu CLI se necessário.

1. Copie `docker-compose.yml`, `coletar.py` e `processar.py` para uma NOVA pasta vazia. Preserve esta coleta.
2. Execute `TZ=America/Sao_Paulo python3 coletar.py`.
3. Execute `python3 processar.py` após a conclusão bem-sucedida.

O coletor recusa recursos preexistentes do projeto `metaltech-aula17`, executa os testes em sequência e usa `finally` para remover netem, testar recuperação e executar `docker compose down`. Não execute duas coletas simultâneas. Encerramento forçado com SIGKILL ou queda do host não pode ser tratado por `finally`; nesse caso verifique os rótulos do projeto antes de limpar. Limpeza manual exclusiva: `docker compose -p metaltech-aula17 -f docker-compose.yml exec -T cliente tc qdisc del dev eth0 root`, depois `docker compose -p metaltech-aula17 -f docker-compose.yml down`.

Apenas o cliente recebe NET_ADMIN. A rede é bridge interna, sem publicação de portas, sem modo host, sem montagem do socket e sem privileged. O único destino dos testes é o IP do servidor do projeto. As tags utilizadas na coleta e seus digests/IDs estão no inspect das imagens. `docker-compose.fixado.yml` permite repetir usando esses mesmos digests (substitua o compose principal na nova pasta).

## Captura e auditoria

Não foi produzida captura de tela de um terminal. A saída integral de uma execução real está em `evidencias/normal_ping_1.stdout`, com comando e horários no metadado correspondente; pode ser inserida como bloco monoespaçado no DOCX. Não há imagem simulada de terminal.

O MTR apresenta horários em UTC; os metadados do coletor usam America/Sao_Paulo (UTC−03:00). Use os metadados para ordenar as execuções. Os JSONs preservam os números originais; CSVs usam ponto decimal e vírgula como separador.

Verificação: na pasta do laboratório execute `sha256sum -c SHA256SUMS`. `validacao_pacote.json` registra conferência do ZIP, hashes e quantitativos. O manifesto cobre todos os arquivos do pacote, exceto ele próprio e o registro final de validação.

## Falha e etapa complementar desta coleta

O terceiro UDP 10 Mbps degradado falhou na inicialização (código 1). Os arquivos originais estão em evidencias/falhas/. A primeira etapa foi encerrada e limpa; `complementar.py` completou esse teste e os três UDP 50 Mbps em containers recriados com a mesma configuração de netem. Os metadados com prefixo complemento documentam essa etapa. Esse script é específico para o estado interrompido desta coleta; não execute novamente sobre o pacote entregue. Duas recuperações foram registradas. O processador aceita a coleta integral ou a coleta com complemento e mantém os erros originais no JSON.
