#!/usr/bin/env python3

import os
import yaml
import time
from kubernetes import client, config
    
config.load_kube_config()


def createPersistentVolume():
    with open(os.path.join(os.path.dirname(__file__), "persistentVolume.yaml"), 'r') as f:
        for pvFile in yaml.safe_load_all(f):
            pvApiInstance = client.CoreV1Api()
            try:
                resp = pvApiInstance.create_persistent_volume(body=pvFile)
                print("Created pv %s"%resp.metadata.name)
            except client.rest.ApiException as e:
                print("Exception when calling CoreV1Api->create_persistent_volume: %s\n" % e)

def createPersistentVolumeClaim():
    with open(os.path.join(os.path.dirname(__file__), "persistentVolumeClaim.yaml")) as f:
        for pvcFile in yaml.safe_load_all(f):
            pvcApiInstance = client.CoreV1Api()
            try:
                resp = pvcApiInstance.create_namespaced_persistent_volume_claim(namespace='default', body=pvcFile)
                print("created pvc %s"%resp.metadata.name)
            except client.rest.ApiException as e:
                print("Exception when calling CoreV1Api->create_namespaced_persistent_volume_claim: %s\n" % e)

def createMasterService():
    with open(os.path.join(os.path.dirname(__file__), "masterService.yaml")) as f:
        masterServiceFile = yaml.safe_load(f)
        masterServiceApiInstance = client.CoreV1Api()
        try:
            resp = masterServiceApiInstance.create_namespaced_service(namespace='default', body=masterServiceFile)
            print("created pvc %s"%resp.metadata.name)
        except client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

def createMasterJob():
    with open(os.path.join(os.path.dirname(__file__), "master.yaml")) as f:
        masterFile = yaml.safe_load(f)
        masterApiInstance = client.BatchV1Api()
        try:
            resp = masterApiInstance.create_namespaced_job(namespace="default", body=masterFile)
            print("Created Job %s"%resp.metadata.name)
        except ApiException as e:
            print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
    

def createDeployment():
    with open(os.path.join(os.path.dirname(__file__), "worker.yaml")) as f:
        workerFile = yaml.safe_load(f)
        workerApiInstance = client.AppsV1Api()
        resp = workerApiInstance.create_namespaced_deployment(body=workerFile, namespace="default")
        print("Created deployment %s"%resp.metadata.name)

def deletePersistentVolume():
    pvApiInstance = client.CoreV1Api()
    pvNames = ["builder", "logs", "specs", "rpms", "publishrpms", "publishxrpms", "photon"]
    for name in pvNames:
        try:
            resp = pvApiInstance.delete_persistent_volume(name)
            print("Deleted pv %s"%name)
        except client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->delete_persistent_volume: %s\n" % e)

def deletePersistentVolumeClaim():
    pvcApiInstance = client.CoreV1Api()
    pvcNames = ["builder", "logs", "specs", "rpms", "publishrpms", "publishxrpms", "photon"]
    for name in pvcNames:
        try:
            resp = pvcApiInstance.delete_namespaced_persistent_volume_claim(name, namespace="default")
            print("Deleted pvc %s"%name)
        except client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_persistent_volume_claim: %s\n" % e)

def deleteMasterJob():
   masterApiInstance = client.BatchV1Api()
   try:
       resp = masterApiInstance.delete_namespaced_job(name="master", namespace="default")
       print("deleted job master")
   except client.rest.ApiException as e:
       print("Exception when calling BatchV1Api->delete_namespaced_job: %s\n" % e)

def deleteMasterService():
   masterServiceApiInstance = client.CoreV1Api()
   try:
       resp = masterServiceApiInstance.delete_namespaced_service(name="master-service", namespace="default")
       print("deleted master service")
   except client.rest.ApiException as e:
       print("Exception when calling BatchV1Api->delete_namespaced_service %s\n" % e)

def deleteDeployment():
    workerApiInstance = client.AppsV1Api()
    try:
        resp = workerApiInstance.delete_namespaced_deployment(name="worker", namespace="default")
        print("deleted worker deployment ")
    except client.rest.ApiException as e:
        print("Exception when calling AppsV1Api->delete_namespaced_deployment: %s\n" % e)

def monitorStatus():
    podApiInstance = client.CoreV1Api()
    resp = podApiInstance.list_namespaced_pod('default',watch=False)
    status = None
    pod = None
    for pod in resp.items:
        if "master" in pod.metadata.name:
            print("%s\t%s\t%s" % (pod.status.pod_ip,  pod.metadata.name, pod.status.phase))
            break
    print("pod.status.pod_ip=",pod.status.pod_ip)
    while status != "Completed":
        status = pod.status.phase
        print("master pod status = %s"%status)
        time.sleep(10)

def clean():
    deleteMasterJob()
    deleteMasterService()
    deleteDeployment()
    time.sleep(10)
    deletePersistentVolumeClaim()
    deletePersistentVolume()

def create():
    print("-"*45)
    print("Creating ")
    createPersistentVolume()
    createPersistentVolumeClaim()
    createMasterService()
    createMasterJob()
    createDeployment()

if __name__ == "__main__":
    clean()
    time.sleep(10)
    create()
    time.sleep(10)
    monitorStatus()
    clean()
