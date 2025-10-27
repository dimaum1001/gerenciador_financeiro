#!/bin/sh

# Script de inicialização do frontend
set -e

echo "🚀 Iniciando frontend do Gerenciador Financeiro..."

# Verificar se os arquivos foram buildados
if [ ! -f "/usr/share/nginx/html/index.html" ]; then
    echo "❌ Erro: Arquivos de build não encontrados!"
    exit 1
fi

echo "✅ Arquivos de build encontrados"

# Substituir variáveis de ambiente no runtime (se necessário)
if [ -n "$VITE_API_URL" ]; then
    echo "🔧 Configurando URL da API: $VITE_API_URL"
    # Aqui poderia ter lógica para substituir variáveis em runtime
fi

# Verificar conectividade com o backend (opcional)
if [ -n "$BACKEND_HOST" ]; then
    echo "🔍 Verificando conectividade com backend..."
    until nc -z "$BACKEND_HOST" 8000; do
        echo "⏳ Aguardando backend ficar disponível..."
        sleep 2
    done
    echo "✅ Backend disponível"
fi

echo "🌐 Iniciando servidor web..."

# Executar comando passado como argumento
exec "$@"
