#!/usr/bin/env python3
import subprocess,json,datetime,pathlib,shlex,sys,os
B=pathlib.Path(__file__).resolve().parent
E=B/'evidencias'; E.mkdir(exist_ok=True)
if (E/'concluido.json').exists(): raise SystemExit('Coleta existente: use uma pasta nova para preservar evidências.')
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
owned=False;netem=False;errors=[];cleanup={}
try:
 for typ,cmd in [('containers',['docker','ps','-aq','--filter','label=com.docker.compose.project=metaltech-aula17']),('networks',['docker','network','ls','-q','--filter','label=com.docker.compose.project=metaltech-aula17'])]:
  if run('preexistentes_'+typ,cmd).strip():raise RuntimeError('Projeto já existe; abortando sem interferir.')
 run('docker_version',['docker','version']);run('compose_version',['docker','compose','version'])
 run('host',['uname','-a']);run('compose_resolvido',DC+['config'])
 run('pull',DC+['pull']);owned=True
 run('up',DC+['up','-d']);run('estado_inicial',DC+['ps','--format','json'])
 ids=run('ids',DC+['ps','-q']).split()
 run('containers_inspect',['docker','inspect']+ids)
 run('rede_inspect',['docker','network','inspect','metaltech-aula17_lab'])
 run('imagens_inspect',['docker','image','inspect','networkstatic/iperf3:latest','nicolaka/netshoot:latest'])
 client('versoes',['sh','-c','ping -V; mtr --version; iperf3 --version; tc -V; ip -j address show eth0'])
 run('servidor_versao',DC+['exec','-T','servidor','iperf3','--version'])
 inspect=json.loads((E/'containers_inspect.stdout').read_text())
 srv=next(c for c in inspect if c['Config']['Labels']['com.docker.compose.service']=='servidor')
 ip=srv['NetworkSettings']['Networks']['metaltech-aula17_lab']['IPAddress']
 (E/'destino.json').write_text(json.dumps({'server_ip':ip,'start':now(),'timezone':str(datetime.datetime.now().astimezone().tzinfo)},indent=2))
 client('qdisc_inicial',['tc','qdisc','show','dev','eth0'])
 for scenario in ['normal','degradado']:
  if scenario=='degradado':
   client('netem_add',['tc','qdisc','add','dev','eth0','root','netem','delay','100ms','loss','5%']);netem=True
   client('qdisc_degradado',['tc','-s','qdisc','show','dev','eth0'])
  for i in range(1,4):client(f'{scenario}_ping_{i}',['ping','-n','-c','20',ip])
  client(f'{scenario}_mtr',['mtr','-r','-w','-n','-c','20',ip])
  for mode in ['tcp','udp10','udp50']:
   for i in range(1,4):
    args=['iperf3','-c',ip,'-t','10','-J','--get-server-output']
    if mode!='tcp':args+=['-u','-b','10M' if mode=='udp10' else '50M']
    name=f'{scenario}_{mode}_{i}'
    raw=client(name,args)
    (E/(name+'.json')).write_text(raw)
    j=json.loads(raw)
    if 'error' in j:raise RuntimeError(j['error'])
 client('qdisc_antes_remocao',['tc','-s','qdisc','show','dev','eth0'])
except Exception as ex:
 errors.append(str(ex));print('ERRO',ex,flush=True)
finally:
 if owned:
  if netem:
   try:client('netem_del',['tc','qdisc','del','dev','eth0','root']);cleanup['netem_removido']=True
   except Exception as ex:errors.append(str(ex));cleanup['netem_removido']=False
  try:
   client('qdisc_final',['tc','qdisc','show','dev','eth0'])
   if 'ip' in globals():client('recuperacao_ping',['ping','-n','-c','20',ip])
   run('logs_servidor',DC+['logs','--no-color','servidor'])
   run('estado_final_antes_down',DC+['ps','--format','json'])
  except Exception as ex:errors.append(str(ex))
  try:
   run('down',DC+['down','--timeout','10']);cleanup['down_sucesso']=True
   cleanup['containers_restantes']=run('containers_apos_down',['docker','ps','-aq','--filter','label=com.docker.compose.project=metaltech-aula17']).split()
   cleanup['redes_restantes']=run('redes_apos_down',['docker','network','ls','-q','--filter','label=com.docker.compose.project=metaltech-aula17']).split()
  except Exception as ex:errors.append(str(ex))
 (E/'concluido.json').write_text(json.dumps({'end':now(),'errors':errors,'cleanup':cleanup},indent=2))
 sys.exit(bool(errors))
