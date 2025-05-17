#!/bin/bash
set -e

NAMESPACE=threadfit

echo "=============================================================="
echo "NOTA:"
echo "Si necesitas construir imágenes Docker locales para Minikube,"
echo "ejecuta primero:"
echo "    eval \$(minikube -p minikube docker-env)"
echo "y luego construye tu imagen con:"
echo "    docker build -t fastapi-server:latest ."
echo "=============================================================="
echo ""
echo ""
echo "Recuerda:"
echo "- Si usas Minikube, ejecuta: minikube tunnel"
echo "- Añade '127.0.0.1 threadfit.local' a tu archivo hosts para acceder al Ingress"
echo "- Accede a https://threadfit.local en tu navegador"
echo ""
echo "Para demostrar el funcionamiento del HPA, puedes generar carga con:"
echo "kubectl run -i --tty load-generator --rm --image=busybox -- /bin/sh"
echo "y dentro del pod ejecutar:"
echo "while true; do wget -q -O- http://threadfit-service:8000/; done"
echo ""
echo "Luego observa el HPA con:"
echo "kubectl get hpa -n $NAMESPACE"
echo "y los pods con:"
echo "kubectl get pods -n $NAMESPACE"

echo "Creando namespace (si no existe)..."
kubectl get namespace $NAMESPACE >/dev/null 2>&1 || kubectl create namespace $NAMESPACE

echo "Estableciendo 'threadfit' como namespace por defecto en el contexto actual..."
kubectl config set-context --current --namespace=$NAMESPACE

echo "Aplicando Secret..."
kubectl apply -f k8s/secret.yaml -n $NAMESPACE

echo "Aplicando ConfigMap, PVC, Deployments y Job..."
kubectl apply -f k8s/deployments.yaml -n $NAMESPACE

echo "Aplicando Services..."
kubectl apply -f k8s/services.yaml -n $NAMESPACE

echo "Aplicando Ingress..."
kubectl apply -f k8s/ingress.yaml -n $NAMESPACE

echo "Aplicando Horizontal Pod Autoscaler..."
kubectl apply -f k8s/hpa.yaml -n $NAMESPACE

echo "Recursos desplegados:"
kubectl get all -n $NAMESPACE

