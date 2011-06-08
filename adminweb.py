#!/usr/bin/python
import string,time,subprocess
import os,sys,cgi,base64,socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#Program developed to control tha main administration function in a web fashion
#AUThOR : ROBERTO RIBEIRO - PRODASEN SSA
#DATE : 31/05/2011

#START  CONFIGURATION
#Configuracao do servico - ip (coloque 0.0.0.0 e fica generico), porta , hostname( deprecado,mas mantenha a string vazia) , usuario , senha
baseConfig = ['0.0.0.0','10500','','admin','Pardal','PRODASEN - SSA -','Main Panel','Save','Are you sure?']
#racao
#Voce deve acrescentar um array Config que possui N Arrays para cada conjunto de botoes no seguinte formato:
#1 elemento com o  nome do conjunto
#N Elementos com a possibilidade dos seguintes formatos dependendo do tipo de botao (4 tipos):
#Formato "Call   com Tela":
 #Label do Botao
 #Tipo do botao : no caso Tipo 1
 #Array com o comando e parametros
 #Se tem confirmacao ou nao
 #A mensagem quando o comando for finalizado(quer tenha sucesso ou fracasso e normalmente pedindo para visualizar o log)
#Formato "System com Tela":
 #Label do Botao
 #Tipo do botao : no caso Tipo 2
 #String com o comando
 #Se tem confirmacao ou nao
 #A mensagem quando o comando der status 0
 #A mensagem quando o comando der status 1
#Formato "Edicao de arquivo":
 #Label do Botao
 #Tipo do botao : no caso Tipo 3
 #String com o arquivo
 #Se tem confirmacao ou nao
#Formato "Visualizador de arquivos":
 #Label do Botao
 #Tipo do botao : no caso Tipo 4
 #String com o comando que sera pipeado para o arquivo temporario que sera lido
 #Se tem confirmacao ou nao
#Formato "Upload de arquivos":
 #Label do Botao
 #Tipo do botao : no caso Tipo 5
 #Diretorio onde o arquivo fica
 #Se tem confirmacao ou nao
 #Mensagem para a tela onde se escolhe o arquivo
 #Tamanho do edit onde mostra o arquivo
 #Mensagem qdo o upload concluir ok


config = [
         
           [
            'SQUID',
            ['Stop','1',['/etc/init.d/squid3','stop'],'1','Check the log after this operation.'],
            ['Start','1',['/etc/init.d/squid3','start'],'1','Check the log after this operation.'],
            ['Status','2','ps -ef | grep -i squid3| grep -vi grep','0','Squid ON','Squid OFF'],
            ['Reload','1',['/usr/sbin/squid3','-k','reconfigure'],'1','Check the log after this operation.'],
            ['Configuration','3','/etc/squid3/squid.conf','0'],
            ['Access Log','4','tail -500 /var/log/squid3/access.log','0'],
            ['Error Log','4','tail -500 /var/log/squid3/cache.log','0'],
           ],

           [
            'POUND',
            ['Stop','1',['/etc/init.d/pound','stop'],'1','Check the log after this operation.'],
            ['Start','1',['/etc/init.d/pound','start'],'1','Check the log after this operation.'],
            ['Status','2','ps -ef | grep -i pound| grep -vi grep','0','Pound ON','Pound OFF'],
            ['Configuration','3','/etc/pound/pound.cfg','0'],
            ['Error Log','4','tail -500 /var/log/syslog','0'],
           # ['Upload','5','/home/webadmin/','0','File to upload','40','File Upload OK'],
           ],

           [
            'HEARTBEAT',
            ['Stop','1',['/etc/init.d/heartbeat','stop'],'1','Check the log after this operation.'],
            ['Start','1',['/etc/init.d/heartbeat','start'],'1','Check the log after this operation.'],
            ['Status','2','ps -ef | grep -i heartbeat| grep -vi grep','0','Heartbeat ON','Heartbeat OFF'],
            ['Reload','1',['/etc/init.d/heartbeat','reload'],'1','Check the log after this operation.'],
            ['Configuration','3','/etc/ha.d/ha.cf','0'],
            ['Error Log','4','tail -500 /var/log/ha-log','0'],
            ['Active/Passive','2','ifconfig|grep -i 172\.31\.0\.24','0','Host status : ACTIVE','Host status: Passive'],
            ['Set Active','1',['/usr/lib/heartbeat/hb_takeover'],'1','Check the log after this operation.'],
            ['Set Passive','1',['/usr/lib/heartbeat/hb_standby'],'1','Check the log after this operation.'],
           ],



         ]
#END - CONFIGURATION























# Initial point of the program - DO NOT CHANGE ANYTHING FROM THIS POINT
bstyle="style='color:white;background-color:#55575c;font-color:white;width:120;height:35;border:1px solid;'"
hostname = socket.gethostname()
global result
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        caminho = os.path.realpath(os.path.dirname(sys.argv[0]))
        try:
           basic = base64.b64encode(baseConfig[3]+":"+baseConfig[4])           
           if self.headers.getheader('Authorization') == None or self.headers.getheader('Authorization') != 'Basic '+basic:
              self.send_response(401)
              self.send_header('WWW-Authenticate', 'Basic realm=\"adminWeb\"')
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              self.wfile.write("<html><head></head><body style='color:white;background-color:grey'><center>"+baseConfig[5]+" AdminWeb 1.0</center>") 
              self.wfile.write("<center><br><br>Acesso nao autorizado</center></body></html>") 
              return
           self.send_response(200)
           self.send_header('Content-type','text/html') 
           self.end_headers()
           self.wfile.write("<html><head></head><body style='color:white;background-color:grey'><center>"+baseConfig[5]+" AdminWeb 1.0</center><br><center>Server : "+hostname+"</center>") 
           if self.path.endswith("editaarquivo") or  self.path.endswith("executaTarefa") or self.path.endswith("logtail")or self.path.endswith("uploadprepara"):
             linha=self.path[1]
             coluna=self.path[2]

           if self.path.endswith("editaarquivo"):
             temp = config[int(linha)][int(coluna)]
             f = open(temp[2],"rb") 
             self.wfile.write("<center><form name='arquivoedit' method='POST' action='http://"+hostname+":"+baseConfig[1]+"/"+linha+coluna+"salvaarquivo'><textarea name='texto' COLS=145 ROWS=20>"+f.read()+"</textarea><br><br><button "+bstyle+" onclick=\"javascript:if (confirm('"+baseConfig[8]+"')){document.arquivoupload.submit()};return false;\">"+baseConfig[7]+"</button></form><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center>")
             f.close()

           elif self.path.endswith("logtail"):
             temp = config[int(linha)][int(coluna)]
             os.system(temp[2]+" >"+caminho+"/logtail.log")             
             f = open(caminho+"/logtail.log","r")
             self.wfile.write("<center><form name='xxx' method='POST' action=''><textarea name='texto' COLS=145 ROWS=20>"+f.read()+"</textarea><br><br></form><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center>")
             f.close()
           elif self.path.endswith("uploadprepara"):
             temp = config[int(linha)][int(coluna)]
             self.wfile.write("<center><form name='arquivoupload' method='POST' enctype=\"multipart/form-data\" action='http://"+hostname+":"+baseConfig[1]+"/"+linha+coluna+"uploadarquivo'><br>"+temp[4]+"<br><input type=\"file\" name=\"file\" size=\""+temp[5]+"\"><br><br><button "+bstyle+" onclick=\"javascript:if (confirm('"+baseConfig[8]+"')){document.arquivoupload.submit()};return false;\">Upload</button></form><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center>")
           elif self.path.endswith("executaTarefa"):
             # EVOCACAO DO COMANDO
             result=0
             temp = config[int(linha)][int(coluna)]
             tipo = str(temp[1])
             if (tipo == "1"):
               print "Comando call executado: "+str(temp[2])
               subprocess.call(temp[2],close_fds=True)
             elif (tipo == "2"):
               print "Comando normal executado: "+str(temp[2])
               result=os.system(temp[2])

             # TRATAMENTO DA APRESENTACAO
             if tipo == "2":
                if result == 0:                    
                   self.wfile.write("<center><br> "+temp[4]+"<br><br><button "+bstyle+" onclick='javascript:history.go(-1)'>"+baseConfig[6]+"</button></center>")  
                else:
                   self.wfile.write("<center><br> "+temp[5]+"<br><br><button "+bstyle+" onclick='javascript:history.go(-1)'>"+baseConfig[6]+"</button></center>")
             if tipo == "1":
                self.wfile.write("<center><br>"+temp[4]+"<br><br><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center>")   


           else:
             for x in range(len(config)):
                 linha = config[x]
                 grupo = linha[0]
                 self.wfile.write("<br><br><center>")
                 for y in range(len(linha)):
                   if (y == 0):
                      self.wfile.write(linha[0])
                      self.wfile.write("<br>")
                   else:
                      botao=linha[y]
                      if (str(botao[3])=='1'):
                        confirm='confirm(\''+baseConfig[8]+'\')'
                      else:
                        confirm='true'
                    
                      if (str(botao[1])=='1'):
                        acao='executaTarefa'
                      elif (str(botao[1])=='2'):
                        acao='executaTarefa'
                      elif (str(botao[1])=='3'):
                        acao='editaarquivo'
                      elif (str(botao[1])=='4'):
                        acao='logtail'
                      elif (str(botao[1])=='5'): 
                        acao='uploadprepara'
                         
                      self.wfile.write("<button "+bstyle+" onclick=\"javascript:if ("+confirm+"){window.document.location='http://"+hostname+":"+baseConfig[1]+"/"+str(x)+str(y)+acao+"'}\">"+botao[0]+"</button>&nbsp;")
                                            
 
                      
              #     if (y == 4):   
              #       self.wfile.write("<button>"+Start+"</button>")
              #     if (y == 4):   
              #       self.wfile.write("<button>"+Start+"</button>")
             self.wfile.write("</center></body></html>") 
             #f = open(caminho+'/adminWeb.cfg', 'r')
             #self.wfile.write(f.read())
             #f.close()
           return

        except Exception , e:
            print e
            self.send_error(500,e)


    #POST USADO PARA SALVAR O ARQUIVO DE CONFIGURACAO
    def do_POST(self):
      try:
        if self.path.endswith("salvaarquivo"):
           form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
           self.send_response(200)
           #self.send_header('Content-type','text/html')
           linha=self.path[1]
           coluna=self.path[2]
           temp = config[int(linha)][int(coluna)]
           print "Arquivo salvo: "+str(temp[2])
           f = open(temp[2],"wb") 
           f.write(form.getvalue("texto").replace("\r\n","\n"))
           f.close()
           self.end_headers()
           self.wfile.write("<html><head></head><body style='color:white;background-color:grey'><center>"+baseConfig[5]+" AdminWeb 1.0</center>") 
           self.wfile.write("</center><br><br><center>Arquivo Salvo<br><br><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center></body></html>") 
        elif self.path.endswith("uploadarquivo"):
           linha=self.path[1]
           coluna=self.path[2]
           temp = config[int(linha)][int(coluna)]
           form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
           fileitem = form['file'] 
           print "nome arquivo:"+fileitem.filename
           f = open(str(temp[2])+fileitem.filename,"wb")
           f.write(fileitem.file.read())
           f.close()
           self.send_response(200)
           self.end_headers()
           self.wfile.write("<html><head></head><body style='color:white;background-color:grey'><center>"+baseConfig[5]+" AdminWeb 1.0</center>")
           self.wfile.write("</center><br><br><center>"+temp[6]+"<br><br><button "+bstyle+" onclick='javascript:window.document.location=\"http://"+hostname+":"+baseConfig[1]+"/\"'>"+baseConfig[6]+"</button></center></body></html>")

      except Exception , e:
          print e
          self.send_error(500,e)          


def main ():
    try:
        server = HTTPServer(('',int(baseConfig[1])), Handler)
        server.serve_forever()
    except Exception , e:
        server.socket.close()
        print e


if __name__ == '__main__':
    main()
            
