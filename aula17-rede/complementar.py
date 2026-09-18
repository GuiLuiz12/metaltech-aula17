#!/usr/bin/env python3
import subprocess,json,datetime,pathlib,shlex,sys,os
B=pathlib.Path(__file__).resolve().parent
E=B/'evidencias'; E.mkdir(exist_ok=True)

DC=['docker','compose','-p','metaltech-aula17','-f',str(B/'docker-compose.yml')]
def now(): return datetime.datetime.now().astimezone().isoformat()
def run(name,args,check=True):
 start=now()
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=180)
  out,err,code=p.stdout,p.stderr,p.returncode
 except subprocess.TimeoutExpired as ex:
  out=ex.stdout or b'';err=ex.stderr or b''
  if isinstance(out,bytes):out=out.decode(errors='replace')
  if isinstance(err,bytes):err=err.decode(errors='replace')
  err+='\nTIMEOUT 180s';code=124
 (E/(name+'.stdout')).write_text(out)
 (E/(name+'.stderr')).write_text(err)
 (E/(name+'.meta.json')).write_text(json.dumps(dict(command=args,command_shell=shlex.join(args),start=start,end=now(),exit_code=code),indent=2))
 print(name,code,flush=True)
 if check and code: raise RuntimeError(name+': '+err)
 return out

def client(name,args,check=True): return run(name,DC+['exec','-T','cliente']+args,check)

# Complemento após falha anterior, sem sobrescrever a tentativa falha.
if (E/'complemento_concluido.json').exists():raise SystemExit('Complemento já executado')
(E/'falhas').mkdir(exist_ok=True)
for p in list(E.glob('degradado_udp10_3.*')):p.rename(E/'falhas'/p.name)
owned=False;netem=False;errors=[];cleanup={}
try:
 for typ,args in [('containers',['docker','ps','-aq','--filter','label=com.docker.compose.project=metaltech-aula17']),('redes',['docker','network','ls','-q','--filter','label=com.docker.compose.project=metaltech-aula17'])]:
  if run('complemento_pre_'+typ,args).strip():raise RuntimeError('Projeto preexistente')
 owned=True;run('complemento_up',DC+['up','-d'])
 ids=run('complemento_ids',DC+['ps','-q']).split()
 data=json.loads(run('complemento_inspect',['docker','inspect']+ids))
 srv=next(c for c in data if c['Config']['Labels']['com.docker.compose.service']=='servidor')
 ip=srv['NetworkSettings']['Networks']['metaltech-aula17_lab']['IPAddress']
 run('complemento_rede',['docker','network','inspect','metaltech-aula17_lab'])
 client('complemento_netem_add',['tc','qdisc','add','dev','eth0','root','netem','delay','100ms','loss','5%']);netem=True
 client('complemento_qdisc',['tc','-s','qdisc','show','dev','eth0'])
 for mode,i in [('udp10',3),('udp50',1),('udp50',2),('udp50',3)]:
  name=f'degradado_{mode}_{i}'
  for attempt in range(1,4):
   raw=client(name,['iperf3','-c',ip,'-t','10','-J','--get-server-output','-u','-b','10M' if mode=='udp10' else '50M'],False)
   j=json.loads(raw)
   if 'error' not in j:
    (E/(name+'.json')).write_text(raw);break
   for p in list(E.glob(name+'.*')):p.rename(E/'falhas'/(name+f'.complemento_tentativa{attempt}'+p.name[len(name):]))
  else:raise RuntimeError('Três tentativas falharam: '+name)
except Exception as ex:errors.append(str(ex))
finally:
 if owned:
  if netem:
   try:client('complemento_netem_del',['tc','qdisc','del','dev','eth0','root']);cleanup['netem_removido']=True
   except Exception as ex:errors.append(str(ex))
  try:
   client('complemento_qdisc_final',['tc','qdisc','show','dev','eth0'])
   client('complemento_recuperacao_ping',['ping','-n','-c','20',ip])
   run('complemento_logs',DC+['logs','--no-color','servidor'])
  except Exception as ex:errors.append(str(ex))
  try:
   run('complemento_down',DC+['down','--timeout','10']);cleanup['down_sucesso']=True
   cleanup['containers_restantes']=run('complemento_containers_apos_down',['docker','ps','-aq','--filter','label=com.docker.compose.project=metaltech-aula17']).split()
   cleanup['redes_restantes']=run('complemento_redes_apos_down',['docker','network','ls','-q','--filter','label=com.docker.compose.project=metaltech-aula17']).split()
  except Exception as ex:errors.append(str(ex))
 (E/'complemento_concluido.json').write_text(json.dumps({'end':now(),'errors':errors,'cleanup':cleanup},indent=2))
 sys.exit(bool(errors))
