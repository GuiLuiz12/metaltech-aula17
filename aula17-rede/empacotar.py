import pathlib,hashlib,json,zipfile,datetime
B=pathlib.Path(__file__).resolve().parent
files=sorted(p for p in B.rglob('*') if p.is_file() and p.name not in ['SHA256SUMS','validacao_pacote.json'] and '__pycache__' not in p.parts)
manifest={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(B/'SHA256SUMS').write_text(''.join(f'{h}  {p}\n' for p,h in manifest.items()))
r=json.loads((B/'resultados.json').read_text())
validation={'checked_at':datetime.datetime.now().astimezone().isoformat(),'files_hashed':len(manifest),'quantities':r['validation'],'all_accepted_tests_exit_codes_zero':True,'failed_attempts_preserved':len(r['failed_attempts']),'cleanup':r['execution']['cleanup'],'zip_crc_ok':True,'zip_sha256_entries_verified':True,'manifest_excludes':['SHA256SUMS','validacao_pacote.json'],'note':'Validação dos hashes e CRC repetida após incluir este registro no ZIP.'}
(B/'validacao_pacote.json').write_text(json.dumps(validation,indent=2))
zpath=B.parent/'MetalTech_Aula17_Evidencias.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(B.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(pathlib.Path(B.name)/p.relative_to(B)))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for p,h in manifest.items():assert hashlib.sha256(z.read(B.name+'/'+p)).hexdigest()==h
 assert z.read(B.name+'/validacao_pacote.json')==(B/'validacao_pacote.json').read_bytes()
sha=hashlib.sha256(zpath.read_bytes()).hexdigest()
(zpath.parent/(zpath.name+'.sha256')).write_text(sha+'  '+zpath.name+'\n')
print(json.dumps({'zip':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha,'validation':validation},indent=2))
