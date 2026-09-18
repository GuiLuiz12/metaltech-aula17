#!/usr/bin/env python3
import pathlib,json,re,csv,statistics,math,hashlib,zipfile
B=pathlib.Path(__file__).resolve().parent;E=B/'evidencias'
def read(n):return (E/n).read_text()
def p95(v):return sorted(v)[math.ceil(.95*len(v))-1] if v else None
def ping(n):
 s=read(n+'.stdout');m=re.search(r'(\d+) packets transmitted, (\d+) received,.*?([\d.]+)% packet loss',s);r=re.search(r'= ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms',s)
 samples=[{'seq':int(a),'rtt_ms':float(b)} for a,b in re.findall(r'icmp_seq=(\d+).*?time=([\d.]+) ms',s)]
 return dict(source=n+'.stdout',sent=int(m[1]),received=int(m[2]),lost=int(m[1])-int(m[2]),loss_pct=float(m[3]),min_ms=float(r[1]),avg_ms=float(r[2]),max_ms=float(r[3]),p95_ms=p95([x['rtt_ms'] for x in samples]),samples=samples)
R={'integrantes':['Guilherme Luiz da Silva','Risiane Izabel de Souza Santos'],'percentile_method':'nearest-rank: sorted[ceil(0.95*n)-1], apenas respostas recebidas','scenarios':{}}
for s in ['normal','degradado']:
 d={'ping':[ping(f'{s}_ping_{i}') for i in range(1,4)]}
 hops=[]
 for line in read(s+'_mtr.stdout').splitlines():
  m=re.match(r'\s*(\d+)\.\|--\s+(\S+)\s+([\d.]+)%\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',line)
  if m:hops.append(dict(hop=int(m[1]),ip=m[2],loss_pct=float(m[3]),sent=int(m[4]),avg_ms=float(m[6]),worst_ms=float(m[8])))
 assert hops,'MTR não interpretado'
 d['mtr']={'hops':hops,'hop_count':len(hops),'source':s+'_mtr.stdout'}
 for mode in ['tcp','udp10','udp50']:
  d[mode]=[]
  for i in range(1,4):
   n=f'{s}_{mode}_{i}';j=json.loads(read(n+'.json'));rx=j['end']['sum_received'];tx=j['end']['sum_sent']
   assert abs(rx['bits_per_second']-rx['bytes']*8/rx['seconds'])<1
   t=dict(source=n+'.json',receiver_mbps=rx['bits_per_second']/1e6,receiver_seconds=rx['seconds'],sender_seconds=tx['seconds'])
   if mode=='tcp':t['sender_retransmits']=tx['retransmits']
   else:
    assert rx['sender'] is False
    t.update(requested_mbps=10 if mode=='udp10' else 50,jitter_ms=rx['jitter_ms'],lost_packets=rx['lost_packets'],total_packets=rx['packets'],loss_pct=rx['lost_percent'])
    assert abs(t['loss_pct']-100*t['lost_packets']/t['total_packets'])<1e-6
   d[mode].append(t)
   (E/(n+'.legivel.txt')).write_text('Resumo derivado do MESMO teste; fonte: '+n+'.json\n'+json.dumps(t,indent=2,ensure_ascii=False)+'\n\nSaída do servidor incluída no JSON:\n'+j.get('server_output_text','(ver server_output_json no JSON original)'))
 d['ping_aggregate']={'sent':sum(x['sent'] for x in d['ping']),'lost':sum(x['lost'] for x in d['ping'])}
 a=d['ping_aggregate'];a['loss_pct']=100*a['lost']/a['sent'];a['p95_ms']=p95([p['rtt_ms'] for t in d['ping'] for p in t['samples']])
 R['scenarios'][s]=d
R['recovery_initial']=ping('recuperacao_ping');R['recovery']=ping('complemento_recuperacao_ping' if (E/'complemento_recuperacao_ping.stdout').exists() else 'recuperacao_ping');R['execution_initial']=json.loads(read('concluido.json'));R['execution']=json.loads(read('complemento_concluido.json' if (E/'complemento_concluido.json').exists() else 'concluido.json'));R['failed_attempts']=[dict(metadata=str(p.relative_to(E)),**json.loads(p.read_text())) for p in (E/'falhas').glob('*.meta.json')]
metrics=[('Latência média','ms','ping','avg_ms'),('Perda ICMP','%','ping','loss_pct'),('Jitter UDP 10 Mbps','ms','udp10','jitter_ms'),('Jitter UDP 50 Mbps','ms','udp50','jitter_ms'),('Throughput TCP','Mbps','tcp','receiver_mbps'),('Throughput UDP 10 Mbps','Mbps','udp10','receiver_mbps'),('Throughput UDP 50 Mbps','Mbps','udp50','receiver_mbps')]
def csvwrite(name,rows):
 with (B/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base=[];comp=[]
for label,unit,group,key in metrics:
 vs={s:[x[key] for x in d[group]] for s,d in R['scenarios'].items()};refs={s:statistics.median(v) for s,v in vs.items()}
 note='Mediana de 3 execuções normais.'
 if group=='ping' and key=='loss_pct':
  refs={s:d['ping_aggregate']['loss_pct'] for s,d in R['scenarios'].items()};a=R['scenarios']['normal']['ping_aggregate'];note=f"Referência agregada {a['lost']}/{a['sent']}; mediana individual {statistics.median(vs['normal'])}%."
 n,g=refs['normal'],refs['degradado'];delta=g-n;pct=100*delta/n if n else None
 if key=='loss_pct':cl='Normal' if g<=.1 else ('Atenção' if g<=1 else 'Crítico');criterion='Normal ≤0,1%; Atenção >0,1 a 1%; Crítico >1%'
 elif key=='avg_ms':cl='Normal' if g<=max(1,n*1.2) else ('Atenção' if g<=max(5,n*2) else 'Crítico');criterion='Normal ≤max(1 ms,1,2×ref); Atenção até max(5 ms,2×ref); Crítico acima'
 elif key=='jitter_ms':cl='Normal' if g<=max(1,n*1.2) else ('Atenção' if g<=max(5,n*2) else 'Crítico');criterion='Normal ≤max(1 ms,1,2×ref); Atenção até max(5 ms,2×ref); Crítico acima'
 else:cl='Normal' if g>=n*.9 else ('Atenção' if g>=n*.7 else 'Crítico');criterion='Normal ≥90% da ref; Atenção ≥70% e <90%; Crítico <70%'
 base.append(dict(metrica=label,unidade=unit,teste_1=vs['normal'][0],teste_2=vs['normal'][1],teste_3=vs['normal'][2],referencia=n,observacao=note))
 comp.append(dict(metrica=label,unidade=unit,normal=n,degradado=g,variacao_absoluta=delta,unidade_variacao='p.p.' if key=='loss_pct' else unit,variacao_percentual=pct if key!='loss_pct' and pct is not None else '',classificacao=cl,criterio=criterion))
R['baseline']=base;R['comparison']=comp
csvwrite('baseline.csv',base);csvwrite('comparacao.csv',comp)
ind=[]
for s,d in R['scenarios'].items():
 n=R['scenarios']['normal'];tcpref=statistics.median(x['receiver_mbps'] for x in n['tcp'])
 vals=[('KPI 1','RTT ICMP P95','nearest-rank P95 de todos os RTT recebidos','ms','≤1 ms no laboratório',d['ping_aggregate']['p95_ms'],'Infraestrutura'),('KPI 2','Entrega ICMP','100 × recebidos / enviados','%','100% no laboratório',100-d['ping_aggregate']['loss_pct'],'Infraestrutura'),('KPI 3','Retenção de throughput TCP','100 × mediana TCP cenário / mediana TCP normal','%','≥90%',100*statistics.median(x['receiver_mbps'] for x in d['tcp'])/tcpref,'Infraestrutura'),('KRI 1','Ensaios ICMP com perda','100 × testes ping com perda >0 / 3','%','Normal 0; Atenção >0 a 33,34; Crítico >33,34',100*sum(x['lost']>0 for x in d['ping'])/3,'Infraestrutura e automação'),('KRI 2','Ensaios UDP com perda >1%','100 × testes UDP com perda >1% / 6','%','Normal 0; Atenção >0 a 33,34; Crítico >33,34',100*sum(x['loss_pct']>1 for mode in ['udp10','udp50'] for x in d[mode])/6,'Infraestrutura')]
 for code,name,formula,unit,target,value,owner in vals:ind.append(dict(indicador=code,nome=name,cenario=s,formula=formula,unidade=unit,meta_faixa_proposta=target,periodo='Bateria curta do cenário; horários individuais nos metadados',valor_observado=value,responsavel_sugerido=owner))
R['indicators']=ind;csvwrite('indicadores.csv',ind)
assert all(len(x['samples'])==x['received'] and x['sent']==20 for d in R['scenarios'].values() for x in d['ping'])
assert all(h['sent']==20 for d in R['scenarios'].values() for h in d['mtr']['hops'])
R['validation']={'ping_tests':6,'ping_packets_sent':sum(d['ping_aggregate']['sent'] for d in R['scenarios'].values()),'mtr_tests':2,'mtr_cycles_each':20,'tcp_tests':6,'udp10_tests':6,'udp50_tests':6,'recovery_tests':len(list(E.glob('*recuperacao_ping.meta.json'))),'failed_iperf_attempts':len(R['failed_attempts'])}
for s in R['scenarios']:
 for mode in ['tcp','udp10','udp50']:
  for i in range(1,4):
   j=json.loads(read(f'{s}_{mode}_{i}.json'));assert j['start']['test_start']['duration']==10
for pattern,expected in [('normal_ping_*.meta.json',3),('degradado_ping_*.meta.json',3),('*_mtr.meta.json',2),('*_tcp_*.meta.json',6),('*_udp10_*.meta.json',6),('*_udp50_*.meta.json',6)]:
 assert len(list(E.glob(pattern)))==expected,(pattern,expected)
for f in E.glob('*.meta.json'):assert json.loads(f.read_text())['exit_code']==0,f
assert not R['execution']['errors'];assert R['execution']['cleanup']['netem_removido'];assert not R['execution']['cleanup']['containers_restantes'];assert not R['execution']['cleanup']['redes_restantes']
(B/'resultados.json').write_text(json.dumps(R,indent=2,ensure_ascii=False))
print(json.dumps({'comparison':comp,'validation':R['validation'],'recovery':R['recovery'],'execution':R['execution']},indent=2,ensure_ascii=False))
