#!/usr/bin/python
# -*- coding: latin-1 -*-
#sarakha63 for jeedom
import glob, os
import requests
import shutil
import json

#Initilaisation de l'environnement
count_modules=0
count_manuf=0
count_error=0
count_ignore=0
list_coming_soon=[]
coming_soon=''
text_to_write=''
curdir=os.path.dirname(os.path.abspath(__file__))
list_git=["git@github.com:jeedom/plugin-openzwave.git","git@github.com:jeedom/doc-zwave-modules.git"]
list_dir=[os.path.join(curdir,'plugin-openzwave'),os.path.join(curdir,'doc-zwave-modules')]
for directory in list_dir:
    if os.path.exists(directory):
        print "Suppression de " +directory
        shutil.rmtree(directory)
os.system("ssh-keyscan github.com >> ~/.ssh/known_hosts")
for git_url in list_git:
    print "Recuperation du git "+git_url
    os.system("git clone "+git_url)
    
#Initialisation du fichier asciidoc

outfile=os.path.join(curdir, 'equipement.compatible.asciidoc')
if os.path.exists(outfile):
    os.remove(outfile)
fichier = open(outfile,'a')
fichier.write('= Liste des équipements compatibles Z-Wave \n:linkattrs:\n\n')#ecriture de la premiere ligne

#Analyse des confs OZW

conf_directory=os.path.join(curdir,'plugin-openzwave/core/config/devices')
list_manuf=os.listdir(conf_directory)#liste des marques
list_manuf.sort()#tri alphabetique
for manuf in list_manuf:
    print "Analysing "+manuf
    list_module_parsed=[]
    if os.path.isdir(os.path.join(conf_directory,manuf)):#si c'est bien un rep
        manuf_name=manuf.split("_")[0].title().encode('utf-8') #nom de marque
        manuf_dir=os.path.join(conf_directory,manuf) #repertoire de la marque
        list_module=[ f for f in os.listdir(manuf_dir) if os.path.isfile(os.path.join(manuf_dir,f)) and f.endswith(".json")]#liste des fichiers dans le rep qui finisse par json
        if len(list_module) != 0:
            text_to_write+='== ' +manuf_name +'\n\n[cols=".^3a,.^1s,.^6,.^2,.^10,.^3", options="header"]\n|===\n|Image|Marque|Nom|Type|Remarque|Lien\n\n'#ecriture du debut du tableau
            count_manuf+=1
        else:
            print "No conf file found for manuf : "+manuf+" skipping."
            continue
        for module_file in list_module:
            with open(os.path.join(manuf_dir,module_file)) as data_file:#on ouvre le json
                print "Parsing " +module_file
                try:
                    data = json.load(data_file)#on charge le json
                except:
                    count_error+=1
                    print 'ERROR : '+module_file+ ' is an invalid json'
                    continue
                ignore=data.get("ignore", '')
                name_module=data.get("name", '').replace(manuf_name+' ','')#on lit le nom en enlevant la marque
                doc_module=data.get("doc", '')#on lit la doc
                if doc_module != '':
                    doc_module='link:++https://jeedom.fr/doc/documentation/zwave-modules/fr_FR/doc-zwave-modules-'+doc_module+'.html++[Documentation^]'#on construit le lien doc
                type_module=data.get("type", '')#on lit le type
                remark_module=data.get("remark", '')#on lit la remarque
                com_link=data.get("comlink", '')#on lit le lien com
                image_module=data.get("imglink", '')
                battery_type=data.get("battery_type", '')
                if battery_type != '':
                    if remark_module.strip() != '' :
                        battery_type='\n\n_[small]#Piles : '+battery_type+'#_'
                    else:
                        battery_type='_[small]#Piles : '+battery_type+'#_'
                if image_module != '':
                    image_module='image:../images/'+image_module+'/module.jpg[width=150,align="center"]'
                if com_link != '':
                    com_link='link:++http://www.domadoo.fr/fr/peripheriques/'+com_link+'.html++[Acheter^]'
                if ignore==1:
                    list_coming_soon.append(manuf_name+'|'+name_module+'|'+image_module+'|'+type_module+'|'+remark_module+'|'+doc_module+'|'+com_link+'|'+battery_type+'|'+module_file)
                else:
                    list_module_parsed.append(name_module+'|'+image_module+'|'+manuf_name+'|'+type_module+'|'+remark_module+'|'+doc_module+'|'+com_link+'|'+battery_type+'|'+module_file)
    list_module_parsed.sort()#on tri la liste
    treated_module=[]
    for module in list_module_parsed:
        detail_module=module.split('|')
        if detail_module[0] not in treated_module:
            count_modules+=1
            text_to_write+='|' +detail_module[1].encode('utf-8')+'|'+detail_module[2].encode('utf-8')+'|'+detail_module[0].encode('utf-8')+'|'+detail_module[3].encode('utf-8')+'|'+detail_module[4].encode('utf-8')+' '+detail_module[7].encode('utf-8')+'|'+detail_module[5].encode('utf-8')+' '+detail_module[6].encode('utf-8')+'\n// '+ detail_module[8].encode('utf-8')+'\n\n'
            treated_module.append(detail_module[0])
        else:
            print "Already a module with this name. Skipping"
    text_to_write+='\n|===\n\n'
list_coming_soon.sort()
fichier.write('[green]*Actuellement Jeedom est compatible avec* [red]*'+str(count_manuf)+'* [green]*marques de modules différentes, soit un total de* [red]*'+str(count_modules)+'* [green]*modules.*\n\nD’autres modules non présents sur cette liste peuvent être compatibles. Pour une demande de compatibilité : link:++https://www.jeedom.fr/forum/viewtopic.php?f=100&t=8607++[Cliquez-ici^]\n\n')
fichier.write(text_to_write)
for soon in list_coming_soon:
    detail_soon=soon.split('|')
    if detail_soon[1] not in treated_module:
        count_ignore+=1
        coming_soon+='|' +detail_soon[2].encode('utf-8')+'|'+detail_soon[0].encode('utf-8')+'|'+detail_soon[1].encode('utf-8')+'|'+detail_soon[3].encode('utf-8')+'|'+detail_soon[4].encode('utf-8')+' '+detail_soon[7].encode('utf-8')+'|'+detail_soon[5].encode('utf-8')+' '+detail_soon[6].encode('utf-8')+'\n// '+ detail_soon[8].encode('utf-8')+'\n\n'
        treated_module.append(detail_soon[1])
    else:
        print "Already a module with this name. Skipping"
if count_ignore !=0:
    fichier.write('== Non compatible pour le moment\n\n[cols=".^3a,.^1s,.^6,.^2,.^10,.^3", options="header"]\n|===\n|Image|Marque|Nom|Type|Remarque|Lien\n\n')
    fichier.write(coming_soon)
    fichier.write('\n|===\n\n')
fichier.write('\n[NOTE]\nCette liste est basée sur des retours utilisateurs, l\'équipe Jeedom ne peut donc garantir que tous les modules de cette liste sont 100% fonctionnels\n')
fichier.close()
directoryfinal=os.path.join(curdir,'doc-zwave-modules/doc/fr_FR')
targetfile=os.path.join(directoryfinal,'equipement.compatible.asciidoc')
if os.path.exists(targetfile):
    os.remove(targetfile)
shutil.copy2(outfile,targetfile)
os.chdir(os.path.join(curdir,'doc-zwave-modules'))
os.system('git add -A')
os.system('git commit -a -m "Auto Compatibility List Generation"')
os.system('git push')
print "Génération terminée avec " +str(count_error)+ " erreur(s)"
print str(count_ignore)+ " confs sont marquées comme ignoré"
        
        
        
        
